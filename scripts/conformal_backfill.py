"""Back-fill the Conformal Risk Control Condor state from the assembled history so the agent starts calibrated.

Reads state/history/daily.csv (scripts/history_data.py), takes the configured score column
(strategy.yaml conformal.horizon, default ratio_1030 = |close / p_10:30 - 1| / VIX-implied move) together with
the session's wing in implied-move units (omega = wing_pct / impl_move_cc), replays both online tracks
(coverage: ACI on alpha; risk: Rolling RC on beta) with the pre-registered parameters, and writes

    state/conformal.json          the agent's state (alpha_t, beta_t, trailing scores, ledger)
    docs/conformal_backfill.md    coverage, realised payout ratio and radius by year, the fixed-rule counterfactual

Deterministic: the same CSV and parameters give byte-identical output.

    python scripts/conformal_backfill.py [--force] [--out state/conformal.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.core import conformal as conf  # noqa: E402
from agent.core.config import ROOT, STATE_DIR, Settings  # noqa: E402

FIXED_K = 0.70          # research/G convention: the 1.10 x straddle rule == 0.70 x VIX-implied move on the observed chain
EVAL_SINCE = "2024-12-30"   # research/G horizon-A evaluation sample (after a 250-session warm-up)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="overwrite an existing state file")
    ap.add_argument("--out", default=str(STATE_DIR / "conformal.json"))
    ap.add_argument("--csv", default=str(STATE_DIR / "history" / "daily.csv"))
    ap.add_argument("--json", default="", help="also write the summary statistics as JSON to this path")
    args = ap.parse_args()

    s = Settings()
    p = conf.ConformalParams.from_config(s.strategy.get("conformal"))
    wing_pct = 100.0 * max(float(s.strategy["structure"]["wing_width_pct_of_spot"]),
                           float(s.strategy["structure"]["min_wing_usd"]) / 600.0)   # % of spot; the $3 floor is below 0.5 % for SPY > 600
    df = pd.read_csv(args.csv, parse_dates=["date"]).sort_values("date")
    col = p.horizon
    rows = [(d.strftime("%Y-%m-%d"), float(r), wing_pct / float(m))
            for d, r, m in zip(df["date"], df[col], df["impl_move_cc"]) if pd.notna(r) and pd.notna(m) and m > 0]
    if len(rows) < p.min_scores + 10:
        raise SystemExit(f"only {len(rows)} usable rows in {col}")
    source = (f"{Path(args.csv).name}:{col} {rows[0][0]}..{rows[-1][0]} ({len(rows)} sessions), wing {wing_pct:.2f} % of spot, "
              f"replayed {datetime.now(tz=timezone.utc).isoformat()[:19]}Z")
    st = conf.backfill(rows, p, source=source)

    out = Path(args.out)
    if out.exists() and not args.force:
        existing = conf.ConformalState.load(out)
        print(f"state exists ({out}); updated_through {existing.updated_through}, alpha_t {existing.alpha_t:.4f}, "
              f"beta_t {existing.beta_t:.4f}. Use --force to overwrite.")
    else:
        st.save(out)
        print(f"wrote {out}")

    # ---- report
    all_stats = conf.coverage_stats(st.ledger)
    eval_stats = conf.coverage_stats(st.ledger, since=EVAL_SINCE)
    by_date = {d: (r, om) for d, r, om in rows}
    fixed: dict[str, dict] = {}
    for rec in st.ledger:
        r, om = by_date[rec["date"]]
        f = fixed.setdefault(rec["date"][:4], {"n": 0, "err": 0, "loss": 0.0})
        f["n"] += 1
        f["err"] += 1 if r > FIXED_K else 0
        f["loss"] += conf.crc_loss(r, FIXED_K, om)
    fixed_all = {"n": sum(f["n"] for f in fixed.values()), "err": sum(f["err"] for f in fixed.values()),
                 "loss": sum(f["loss"] for f in fixed.values())}
    lines = [
        "# Conformal Risk Control Condor: back-fill from history",
        "",
        f"Source: `{source}`.",
        f"Parameters (config/strategy.yaml `conformal`): rule {p.rule}, beta_target {p.beta_target}, alpha_target {p.alpha_target}, "
        f"gamma {p.gamma}, window {p.window}, clip [{p.k_min}, {p.k_max}], margin {p.margin}, min_scores {p.min_scores}. "
        "Score = |close / p_10:30 - 1| / VIX_prev-implied expected absolute daily move (identical unit live and in history); "
        "payout ratio = min((score - k)+, omega) / omega with omega = wing / implied move.",
        "",
        f"State written: beta_t = **{st.beta_t:.4f}**, alpha_t = **{st.alpha_t:.4f}** after {len(st.ledger)} calibrated sessions; "
        f"{len(st.scores[-p.window:])} scores in the window; updated through {st.updated_through}.",
        "",
        "## Risk track (conformal risk control + Rolling RC): realised payout ratio vs the beta target",
        "",
        "| sample | n | realised payout ratio | target beta | mean k_crc | fixed rule k=0.70 payout ratio |",
        "|---|---|---|---|---|---|",
        f"| all calibrated sessions | {all_stats['n']} | {all_stats['realized_risk']:.4f} | {p.beta_target:.2f} | {all_stats['k_crc_mean']:.3f} | {fixed_all['loss'] / fixed_all['n']:.4f} |",
        f"| since {EVAL_SINCE} (research/G sample) | {eval_stats['n']} | {eval_stats['realized_risk']:.4f} | {p.beta_target:.2f} | {eval_stats['k_crc_mean']:.3f} | "
        f"{sum(conf.crc_loss(by_date[r['date']][0], FIXED_K, by_date[r['date']][1]) for r in st.ledger if r['date'] >= EVAL_SINCE) / max(1, eval_stats['n']):.4f} |",
        "",
        "## Coverage track (split conformal + ACI): coverage vs the 1 - alpha target",
        "",
        "| sample | n | coverage | target | mean k_cov | sd k_cov | fixed rule k=0.70 coverage |",
        "|---|---|---|---|---|---|---|",
        f"| all calibrated sessions | {all_stats['n']} | {all_stats['coverage']:.3f} | {1 - p.alpha_target:.2f} | {all_stats['k_cov_mean']:.3f} | {all_stats['k_cov_sd']:.3f} | {1 - fixed_all['err'] / fixed_all['n']:.3f} |",
        f"| since {EVAL_SINCE} (research/G sample) | {eval_stats['n']} | {eval_stats['coverage']:.3f} | {1 - p.alpha_target:.2f} | {eval_stats['k_cov_mean']:.3f} | - | - |",
        "",
        "## By year",
        "",
        "| year | n | CRC payout ratio | mean k_crc | fixed-rule payout ratio | conformal coverage | mean k_cov | fixed-rule coverage |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for y, b in all_stats["by_year"].items():
        f = fixed[y]
        lines.append(f"| {y} | {b['n']} | {b['realized_risk']:.4f} | {b['k_crc_mean']:.3f} | {f['loss'] / f['n']:.4f} | "
                     f"{b['coverage']:.3f} | {b['k_cov_mean']:.3f} | {1 - f['err'] / f['n']:.3f} |")
    lines += [
        "",
        "Read: the risk track moves the radius so that the realised payout ratio stays near beta in every year, which is",
        "the quantity the gate certifies; the coverage track does the same for the miss frequency; the fixed rule's",
        "payout ratio and coverage are whatever the year's realised-to-implied ratio makes them. Both quantities have",
        "a finite-sample guarantee under exchangeability (docs/THEORY.md); P&L does not (research/G, sections 5.3 and 5.8).",
        "No option prices exist in this history, so the P-versus-Q gate cannot be back-tested here; it is evaluated live,",
        "per session, from the audit record (`conformal` events: credit/wing, certified payout, gap, decision).",
        "",
        "## Level paths (last 20 calibrated sessions)",
        "",
        "| date | k_crc | k_cov | ratio | payout ratio | beta after | miss | alpha after |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in st.ledger[-20:]:
        lines.append(f"| {r['date']} | {r['k_crc']:.3f} | {r['k_cov']:.3f} | {r['ratio']:.3f} | {r['loss']:.3f} | {r['beta_after']:.4f} | {r['err']} | {r['alpha_after']:.4f} |")
    doc = ROOT / "docs" / "conformal_backfill.md"
    doc.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {doc}")
    summary = {"alpha_t": st.alpha_t, "beta_t": st.beta_t, "n_ledger": len(st.ledger), "n_rows": len(rows),
               "first": rows[0][0], "last": rows[-1][0], "wing_pct": wing_pct,
               "all": {k: v for k, v in all_stats.items() if k != "by_year"}, "by_year": all_stats["by_year"],
               "eval": {k: v for k, v in eval_stats.items() if k != "by_year"},
               "fixed_all": {"coverage": 1 - fixed_all["err"] / fixed_all["n"], "payout_ratio": fixed_all["loss"] / fixed_all["n"]},
               "fixed_by_year": {y: {"coverage": 1 - f["err"] / f["n"], "payout_ratio": f["loss"] / f["n"]} for y, f in fixed.items()}}
    if args.json:
        Path(args.json).write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("alpha_t", "beta_t", "n_ledger", "all", "eval", "fixed_all")}, indent=1))


if __name__ == "__main__":
    main()

"""Back-fill the Conformal Condor state from the assembled history so the agent starts calibrated.

Reads state/history/daily.csv (scripts/history_data.py), takes the configured score column
(strategy.yaml conformal.horizon, default ratio_1030 = |close / p_10:30 - 1| / VIX-implied move), replays
adaptive conformal inference through it with the pre-registered parameters, and writes

    state/conformal.json          the agent's state (alpha_t, trailing scores, ledger)
    docs/conformal_backfill.md    coverage and sharpness by year, the fixed-rule counterfactual, the alpha path

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
    args = ap.parse_args()

    s = Settings()
    p = conf.ConformalParams.from_config(s.strategy.get("conformal"))
    df = pd.read_csv(args.csv, parse_dates=["date"]).sort_values("date")
    col = p.horizon
    rows = [(d.strftime("%Y-%m-%d"), float(r)) for d, r in zip(df["date"], df[col]) if pd.notna(r)]
    if len(rows) < p.min_scores + 10:
        raise SystemExit(f"only {len(rows)} usable rows in {col}")
    source = f"{Path(args.csv).name}:{col} {rows[0][0]}..{rows[-1][0]} ({len(rows)} sessions), replayed {datetime.now(tz=timezone.utc).isoformat()[:19]}Z"
    st = conf.backfill(rows, p, source=source)

    out = Path(args.out)
    if out.exists() and not args.force:
        existing = conf.ConformalState.load(out)
        print(f"state exists ({out}); updated_through {existing.updated_through}, alpha_t {existing.alpha_t:.4f}. Use --force to overwrite.")
    else:
        st.save(out)
        print(f"wrote {out}")

    # ---- report
    all_stats = conf.coverage_stats(st.ledger)
    eval_stats = conf.coverage_stats(st.ledger, since=EVAL_SINCE)
    ratio_by_date = dict(rows)
    by_year_fixed: dict[str, list[int]] = {}          # same sessions as the conformal ledger (after warm-up)
    for rec in st.ledger:
        by_year_fixed.setdefault(rec["date"][:4], []).append(1 if ratio_by_date[rec["date"]] > FIXED_K else 0)
    lines = [
        "# Conformal Condor: back-fill from history",
        "",
        f"Source: `{source}`.",
        f"Parameters (config/strategy.yaml `conformal`): alpha_target {p.alpha_target}, gamma {p.gamma}, window {p.window}, "
        f"clip [{p.k_min}, {p.k_max}], margin {p.margin}, min_scores {p.min_scores}. Score = |close / p_10:30 - 1| / "
        "VIX_prev-implied expected absolute daily move (identical unit live and in history).",
        "",
        f"State written: alpha_t = **{st.alpha_t:.4f}** after {len(st.ledger)} calibrated sessions; "
        f"{len(st.scores[-p.window:])} scores in the window; updated through {st.updated_through}.",
        "",
        "## Coverage and sharpness (split conformal + ACI, out of sample by construction)",
        "",
        "| sample | n | coverage | target | mean k | sd k | alpha at end |",
        "|---|---|---|---|---|---|---|",
        f"| all calibrated sessions | {all_stats['n']} | {all_stats['coverage']:.3f} | {1 - p.alpha_target:.2f} | {all_stats['k_mean']:.3f} | {all_stats['k_sd']:.3f} | {all_stats['alpha_last']:.4f} |",
        f"| since {EVAL_SINCE} (research/G sample) | {eval_stats['n']} | {eval_stats['coverage']:.3f} | {1 - p.alpha_target:.2f} | {eval_stats['k_mean']:.3f} | {eval_stats['k_sd']:.3f} | {eval_stats['alpha_last']:.4f} |",
        "",
        f"## By year: conformal vs the fixed rule (k = {FIXED_K} x VIX-implied move, the live 1.10 x straddle geometry)",
        "",
        "| year | n | conformal coverage | mean k | fixed-rule coverage |",
        "|---|---|---|---|---|",
    ]
    for y, b in all_stats["by_year"].items():
        fy = by_year_fixed[y]
        lines.append(f"| {y} | {b['n']} | {b['coverage']:.3f} | {b['k_mean']:.3f} | {1 - sum(fy) / len(fy):.3f} |")
    lines += [
        "",
        "Read: the conformal radius moves with the calibration window and alpha_t so that coverage stays near the",
        "target in every year; the fixed rule's coverage is whatever the year's realised-to-implied ratio makes it.",
        "Coverage is the quantity with a guarantee; P&L is not (research/G, sections 5.3 and 5.8). No option prices",
        "exist in this history, so the P-versus-Q gate cannot be back-tested here; it is evaluated live, per session,",
        "from the audit record (`conformal` events: Q_mid, P_mid, gap, decision).",
        "",
        "## Alpha path (last 20 calibrated sessions)",
        "",
        "| date | k | ratio | err | alpha after |",
        "|---|---|---|---|---|",
    ]
    for r in st.ledger[-20:]:
        lines.append(f"| {r['date']} | {r['k']:.3f} | {r['ratio']:.3f} | {r['err']} | {r['alpha_after']:.4f} |")
    doc = ROOT / "docs" / "conformal_backfill.md"
    doc.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {doc}")
    print(json.dumps({"alpha_t": st.alpha_t, "n_ledger": len(st.ledger), "all": {k: v for k, v in all_stats.items() if k != 'by_year'},
                      "eval": {k: v for k, v in eval_stats.items() if k != 'by_year'}}, indent=1))


if __name__ == "__main__":
    main()

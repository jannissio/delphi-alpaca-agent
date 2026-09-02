"""Anytime-valid evidence report (docs/THEORY.md section 9): the risk e-process over every calibrated session,
the profit e-process over the sessions actually traded, and the evidence ceiling. Reported, never used to halt.

    python scripts/evidence.py                      # -> docs/evidence.md
    python scripts/evidence.py --json out.json      # machine-readable summary (used by scripts/reproduce.py)
    python scripts/evidence.py --state path.json    # another conformal state (reproduce.py passes a temp one)
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.core.config import ROOT, STATE_DIR  # noqa: E402
from agent.core.evidence import evidence_ceiling, profit_wealth, risk_wealth, sessions_for_alpha  # noqa: E402

LAMBDA = 1.0          # pre-registered constant bet for the risk process (admissible range [0, 1/beta*])
ETA = 1.0             # pre-registered constant bet for the profit process (capped at 1/(1-g) per session)


def traded_pairs(audit_path: Path) -> list[dict]:
    """(session, g, l) for every session with an opened position: g = entry credit / wing / ratio from the
    position_opened record, l = the payout ratio of the committed interval from that session's conformal_eod."""
    if not audit_path.exists():
        return []
    opened: dict[str, dict] = {}
    eod: dict[str, float] = {}
    for line in audit_path.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("kind") == "position_opened" and r.get("session") not in opened:
            pos, exp = r.get("position", {}), r.get("expected", {})
            legs = pos.get("legs", [])
            wing = None
            try:
                calls = sorted(l["strike"] for l in legs if l["right"] == "call")
                wing = calls[1] - calls[0] if len(calls) == 2 else None
            except (KeyError, TypeError):
                wing = None
            ratio = max([int(l.get("ratio", 1)) for l in legs] or [1])
            if wing and wing > 0:
                opened[r["session"]] = {"session": r["session"], "credit": pos.get("entry_credit"), "wing": wing,
                                        "ratio": ratio, "g": float(pos["entry_credit"]) / ratio / wing,
                                        "credit_mid_at_decision": exp.get("credit_mid")}
        if r.get("kind") == "conformal_eod":
            rec = r.get("record", {})
            if "loss" in rec:
                eod[r.get("session") or rec.get("date")] = float(rec["loss"])
    out = []
    for s, o in sorted(opened.items()):
        if s in eod:
            out.append({**o, "l": eod[s]})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default=str(STATE_DIR / "conformal.json"))
    ap.add_argument("--audit", default=str(STATE_DIR / "audit.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "docs" / "evidence.md"))
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    st = json.loads(Path(args.state).read_text(encoding="utf-8"))
    beta_star = float(st.get("params", {}).get("beta_target", 0.10))
    ledger = [r for r in st.get("ledger", []) if r.get("rule") == "crc" or "loss" in r]
    losses = [float(r["loss"]) for r in ledger]
    risk = risk_wealth(losses, beta_star, LAMBDA)
    by_year: dict[str, list[float]] = defaultdict(list)
    for r in ledger:
        by_year[r["date"][:4]].append(float(r["loss"]))
    risk_years = {y: risk_wealth(ls, beta_star, LAMBDA) for y, ls in sorted(by_year.items())}
    pairs = traded_pairs(Path(args.audit))
    profit = profit_wealth([(p["g"], p["l"]) for p in pairs], ETA) if pairs else None
    profit_max = profit_wealth([(p["g"], p["l"]) for p in pairs], None) if pairs else None
    gs = [0.15, 0.20, 0.25]
    Ts = [1, 2, 3, 5, 10, 14, 20]
    ceiling = {f"{g:.2f}": {str(T): evidence_ceiling(g, T) for T in Ts} for g in gs}
    t_min = {f"{g:.2f}": sessions_for_alpha(g, 0.05) for g in gs}

    lines = [
        "# Anytime-valid evidence (docs/THEORY.md section 9)",
        "",
        f"Source: `{Path(args.state).name}` ledger ({len(losses)} calibrated sessions, "
        f"{ledger[0]['date'] if ledger else '-'}..{ledger[-1]['date'] if ledger else '-'}), audit log "
        f"({len(pairs)} traded sessions with a closed payout ratio). Bets pre-registered: lambda = {LAMBDA} "
        f"(admissible [0, {1 / beta_star:.0f}]), eta = {ETA} (capped at 1/(1-g)). Reported, never used to halt.",
        "",
        "## Risk process (evidence against the certificate)",
        "",
        f"Null: E[l_t | past] <= beta* = {beta_star}. W_T = {risk['W_T']:.4g}, running maximum {risk['W_max']:.4g}, "
        f"anytime-valid p-value {risk['p_anytime']:.3f} (a value below 0.05 would reject the certificate at level 5 %).",
        "",
        "| Year | sessions | mean payout ratio | W_T | max W | anytime p |",
        "|---|---|---|---|---|---|",
    ]
    for y, rw in risk_years.items():
        ls = by_year[y]
        lines.append(f"| {y} | {len(ls)} | {sum(ls) / len(ls):.3f} | {rw['W_T']:.3g} | {rw['W_max']:.3g} | {rw['p_anytime']:.3f} |")
    lines += ["", "## Profit process (evidence for profitability, live sessions only)", ""]
    if pairs:
        lines.append("| Session | credit at fill | wing | ratio | g = credit/wing | payout ratio l | Y = g - l |")
        lines.append("|---|---|---|---|---|---|---|")
        for p in pairs:
            lines.append(f"| {p['session']} | {p['credit']:.2f} | {p['wing']:.0f} | {p['ratio']} | {p['g']:.3f} | {p['l']:.3f} | {p['g'] - p['l']:+.3f} |")
        lines += ["",
                  f"W_T = {profit['W_T']:.4g} at eta = {ETA} (anytime p {profit['p_anytime']:.3f}); with the largest admissible bet "
                  f"eta_t = 1/(1-g_t) the same sessions give W_T = {profit_max['W_T']:.4g} (anytime p {profit_max['p_anytime']:.3f}). "
                  f"Null: E[g_t - l_t | past] <= 0."]
    else:
        lines.append("No traded session with a closed payout ratio yet (the pilot day ran the fixed rule without a committed "
                     "interval; the first entries arrive after the 2026-09-03 session).")
    lines += ["", "## Evidence ceiling", "",
              "T maximal wins at credit/wing g cannot produce more than (1/(1-g))^T; the smallest anytime-valid p-value is its reciprocal.",
              "", "| g | " + " | ".join(f"T={T}" for T in Ts) + " | sessions for p <= 0.05 |",
              "|---|" + "---|" * len(Ts) + "---|"]
    for g in gs:
        row = " | ".join(f"{ceiling[f'{g:.2f}'][str(T)]:.2f}" for T in Ts)
        lines.append(f"| {g:.2f} | {row} | {t_min[f'{g:.2f}']} |")
    lines += ["", "At g = 0.20 three perfect sessions reach 1.95, i.e. p >= 0.51; p <= 0.05 needs 14 consecutive perfect packages. "
              "Evidence accrues per package, so two smaller packages per session raise the three-session ceiling to 3.81 at an "
              "unchanged risk budget.", ""]
    Path(args.out).write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {args.out}")
    summary = {"beta_star": beta_star, "n_sessions": len(losses), "risk_W_T": risk["W_T"], "risk_W_max": risk["W_max"],
               "risk_p_anytime": risk["p_anytime"], "lambda": LAMBDA,
               "risk_by_year": {y: {"n": rw["n"], "W_T": rw["W_T"], "W_max": rw["W_max"]} for y, rw in risk_years.items()},
               "traded_sessions": len(pairs), "profit_W_T": profit["W_T"] if profit else None,
               "profit_p_anytime": profit["p_anytime"] if profit else None,
               "ceiling_g020_T3": evidence_ceiling(0.20, 3), "sessions_for_p005_g020": sessions_for_alpha(0.20, 0.05)}
    if args.json:
        Path(args.json).write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "risk_by_year"}))


if __name__ == "__main__":
    main()

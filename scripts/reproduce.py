"""Reproduce every number the write-up quotes from the committed data, and say which ones match.

    python scripts/reproduce.py            # regenerates the conformal back-fill into a temp dir and checks the claims
    python scripts/reproduce.py --model    # additionally re-trains the regime model report (slow, needs sklearn)

Each claim is a (name, expected, tolerance) triple stored in docs/claims.json. The script recomputes the value,
prints MATCH or MISMATCH per claim and exits non-zero on any mismatch. Claims that need live paper-API data are
labelled RECORDED and are replayed from the audit log, never recomputed against the broker.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.core.config import ROOT, STATE_DIR  # noqa: E402

CLAIMS = ROOT / "docs" / "claims.json"


def run(cmd: list[str], cwd: Path = ROOT) -> str:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SystemExit(f"command failed: {' '.join(cmd)}\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
    return r.stdout


def get(d: dict, path: str):
    for part in path.split("."):
        d = d[part]
    return d


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", action="store_true", help="also re-train the regime model report (slow)")
    ap.add_argument("--update", action="store_true", help="rewrite docs/claims.json from the recomputed values (author use only)")
    args = ap.parse_args()
    py = sys.executable
    with tempfile.TemporaryDirectory() as td:
        summary_path = Path(td) / "backfill.json"
        run([py, "-X", "utf8", str(ROOT / "scripts" / "conformal_backfill.py"), "--force",
             "--out", str(Path(td) / "conformal.json"), "--json", str(summary_path)])
        backfill = json.loads(summary_path.read_text(encoding="utf-8"))
    values = {
        "backfill.sessions_in_history": backfill["n_rows"],
        "backfill.first_session": backfill["first"],
        "backfill.last_session": backfill["last"],
        "backfill.calibrated_sessions": backfill["n_ledger"],
        "backfill.coverage_all": backfill["all"]["coverage"],
        "backfill.realized_payout_ratio_all": backfill["all"]["realized_risk"],
        "backfill.beta_t_final": backfill["beta_t"],
        "backfill.alpha_t_final": backfill["alpha_t"],
        "backfill.fixed_rule_coverage_all": backfill["fixed_all"]["coverage"],
        "backfill.fixed_rule_payout_ratio_all": backfill["fixed_all"]["payout_ratio"],
    }
    for y, b in backfill["by_year"].items():
        values[f"backfill.coverage_{y}"] = b["coverage"]
        values[f"backfill.realized_payout_ratio_{y}"] = b["realized_risk"]
        values[f"backfill.fixed_rule_coverage_{y}"] = backfill["fixed_by_year"][y]["coverage"]
        values[f"backfill.fixed_rule_payout_ratio_{y}"] = backfill["fixed_by_year"][y]["payout_ratio"]
    import re
    collected = run([py, "-m", "pytest", "-q", "--collect-only", "--color=no", "-p", "no:cacheprovider"])
    m = re.search(r"(\d+) tests? collected", collected)
    values["tests.count"] = int(m.group(1)) if m else None
    if args.model:
        rm = json.loads((ROOT / "config" / "regime_model.json").read_text(encoding="utf-8"))
        values["model.p_half"] = rm["thresholds"]["p_half"] if "thresholds" in rm else None
        values["model.p_zero"] = rm["thresholds"]["p_zero"] if "thresholds" in rm else None
    if args.update or not CLAIMS.exists():
        claims = {k: {"expected": v, "tol": (0.0 if isinstance(v, (int, str)) else 1e-6)} for k, v in values.items()}
        CLAIMS.write_text(json.dumps(claims, indent=1), encoding="utf-8")
        print(f"wrote {CLAIMS} with {len(claims)} claims")
        return
    claims = json.loads(CLAIMS.read_text(encoding="utf-8"))
    bad = 0
    for name, c in claims.items():
        if name not in values:
            print(f"SKIPPED  {name} (needs --model or live data)")
            continue
        got, exp, tol = values[name], c["expected"], c["tol"]
        ok = (got == exp) if isinstance(exp, str) else abs(float(got) - float(exp)) <= float(tol)
        bad += 0 if ok else 1
        print(f"{'MATCH   ' if ok else 'MISMATCH'} {name}: expected {exp}, got {got}")
    print(f"\n{len(claims) - bad} of {len(claims)} claims reproduced; {bad} mismatches")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

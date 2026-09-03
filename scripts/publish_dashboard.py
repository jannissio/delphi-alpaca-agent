"""Regenerate the public ledger: docs/index.html (the dashboard) and docs/ledger.json (every conformal record).

The P-versus-Q ledger is the evaluation object of the submission: one row per evaluation, traded or not, with the
market's price of the interval, the certified payout, the gap, the decision and the fixed-rule counterfactual.
Publishing it after every session (GitHub Pages serves docs/) makes it checkable by anyone without our keys.

    python scripts/publish_dashboard.py [--push]     # --push commits docs/index.html + docs/ledger.json and pushes
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.core.config import ROOT, STATE_DIR  # noqa: E402

KEEP = ("conformal_interval", "conformal", "conformal_eod", "conformal_error", "position_opened", "position_closed",
        "no_trade", "halt", "kill_switch")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--push", action="store_true")
    args = ap.parse_args()
    py = sys.executable
    subprocess.run([py, str(ROOT / "scripts" / "dashboard.py")], cwd=ROOT, check=True)
    html = (ROOT / "docs" / "dashboard.html").read_text(encoding="utf-8")
    (ROOT / "docs" / "index.html").write_text(html, encoding="utf-8")
    audit = STATE_DIR / "audit.jsonl"
    rows = []
    if audit.exists():
        for line in audit.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("kind") in KEEP:
                r.pop("prompt", None)
                rows.append(r)
    (ROOT / "docs" / "ledger.json").write_text(json.dumps(rows, indent=0), encoding="utf-8")
    print(f"wrote docs/index.html and docs/ledger.json ({len(rows)} records)")
    if args.push:
        subprocess.run(["git", "add", "docs/index.html", "docs/ledger.json", "docs/dashboard.html"], cwd=ROOT, check=True)
        r = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
        if r.returncode == 0:
            print("nothing to publish")
            return
        ident = subprocess.run(["git", "log", "-1", "--format=%an%n%ae"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
        name, email = (ident[0] if ident and ident[0] else "delphi-publisher"), (ident[1] if len(ident) > 1 and ident[1] else "delphi-publisher@users.noreply.github.com")
        subprocess.run(["git", "-c", f"user.name={name}", "-c", f"user.email={email}", "commit", "-q", "-m", "Publish ledger and dashboard"], cwd=ROOT, check=True)
        subprocess.run(["git", "push", "-q", "origin", "main"], cwd=ROOT, check=True)
        print("pushed")


if __name__ == "__main__":
    main()

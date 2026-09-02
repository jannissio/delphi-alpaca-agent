"""Kill switch (gate 19). One command: cancels every open order, writes the KILL flag the
loop checks each cycle, and (with --flatten) closes every package with escalating limits.

    python scripts/kill.py            # cancel all + set flag; the running agent flattens on its next cycle
    python scripts/kill.py --flatten  # additionally flatten right here, without the agent
    python scripts/kill.py --clear    # remove the flag (manual re-enable, gate 9 semantics)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.core.config import ROOT, STATE_DIR, Settings  # noqa: E402
from agent.data.alpaca_data import AlpacaData  # noqa: E402
from agent.execution.flatten import kill_all  # noqa: E402
from agent.reporting.audit import AuditLog  # noqa: E402


def main() -> None:
    s = Settings()
    flag = ROOT / s.risk["kill_switch_file"]
    if "--clear" in sys.argv:
        flag.unlink(missing_ok=True)
        print("KILL flag cleared")
        return
    s.require_alpaca()
    audit = AuditLog(STATE_DIR / "audit.jsonl", s.git_hash, s.config_hash, "manual")
    data = AlpacaData(s.alpaca_key, s.alpaca_secret, paper=s.alpaca_paper)
    flag.parent.mkdir(exist_ok=True)
    flag.write_text("kill requested by operator\n")
    res = kill_all(data.trading, audit, "operator kill.py")
    print(f"orders cancelled: {res['orders_cancelled']} in {res['latency_s']:.2f}s; KILL flag written at {flag}")
    if "--flatten" in sys.argv:
        from scripts.flatten_now import flatten_everything
        flatten_everything(s, data, audit, reason="operator kill.py --flatten")


if __name__ == "__main__":
    main()

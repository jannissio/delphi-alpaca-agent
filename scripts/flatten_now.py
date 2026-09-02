"""Flatten every package in the book now, with escalating limit prices (never market).

    python scripts/flatten_now.py [--reason "text"]
"""
from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.core.config import STATE_DIR, Settings  # noqa: E402
from agent.core.models import BookPosition  # noqa: E402
from agent.data.alpaca_data import AlpacaData  # noqa: E402
from agent.execution.flatten import flatten_position  # noqa: E402
from agent.execution.orders import OrderWalker  # noqa: E402
from agent.reporting.audit import AuditLog, JsonState  # noqa: E402


def _pos(d: dict) -> BookPosition:
    d = dict(d)
    d["expiry"] = date.fromisoformat(d["expiry"])
    d["opened_ts"] = datetime.fromisoformat(d["opened_ts"])
    d["closed_ts"] = datetime.fromisoformat(d["closed_ts"]) if d.get("closed_ts") else None
    return BookPosition(**d)


def flatten_everything(s: Settings, data: AlpacaData, audit: AuditLog, reason: str) -> None:
    store = JsonState(STATE_DIR / "book.json")
    book = [_pos(p) for p in store.load([])]
    opens = [p for p in book if p.status != "closed"]
    if not opens:
        print("book has no open packages")
        return
    ex = s.strategy["execution"]
    walker = OrderWalker(data.trading, audit, float(ex["walk_step_interval_s"]), float(ex["cancel_after_s"]), dry_run=s.dry_run)
    syms = sorted({l["symbol"] for p in opens for l in p.legs})
    quotes = data.snapshots(syms)
    for p in opens:
        res = flatten_position(walker, p, quotes, float(s.risk["price_collar_pct_of_mid"]), [0.0, 0.5, 1.0], reason,
                               on_order_sent=lambda oid, px: None, requote_quotes=lambda: data.snapshots(syms))
        print(p.position_id, res["status"], res.get("avg_price"))
        if res["status"] in {"filled", "dry_run"}:
            p.status = "closed"
            p.closed_ts = datetime.now().astimezone()
            p.exit_debit = float(res.get("avg_price") or res.get("last_price") or 0.0)
    store.save([p.to_dict() for p in book])


def main() -> None:
    s = Settings()
    s.require_alpaca()
    reason = "operator flatten_now.py"
    if "--reason" in sys.argv:
        reason = sys.argv[sys.argv.index("--reason") + 1]
    audit = AuditLog(STATE_DIR / "audit.jsonl", s.git_hash, s.config_hash, "manual")
    data = AlpacaData(s.alpaca_key, s.alpaca_secret, paper=s.alpaca_paper)
    flatten_everything(s, data, audit, reason)


if __name__ == "__main__":
    main()

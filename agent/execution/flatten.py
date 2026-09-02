"""Flatten task (gate 15) and kill switch (gate 19).

Flatten: for every open package, submit a closing package order at the natural (marketable)
price and escalate through the collar; no market orders. Runs when the deadline is reached,
when a take-profit target is hit, when the kill switch file appears, or on demand.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Callable

from agent.core.models import BookPosition, OptionQuote
from agent.execution.orders import OrderWalker, build_close_legs, walk_prices

log = logging.getLogger(__name__)


def closing_prices(position: BookPosition, quotes: dict[str, OptionQuote], collar_pct: float,
                   fractions: list[float]) -> tuple[float, float, list[float]]:
    """Debit to close the package at mid and at the natural; ladder from mid toward natural
    and beyond by the collar (paying up to leave)."""
    mid = 0.0
    nat = 0.0
    for l in position.legs:
        q = quotes[l["symbol"]]
        r = int(l["ratio"])
        if l["side"] == "sell":          # we are short: buy back at ask
            mid += q.mid * r
            nat += q.ask * r
        else:                            # we are long: sell at bid
            mid -= q.mid * r
            nat -= q.bid * r
    ladder = walk_prices(mid, nat, fractions)
    # final escalation rung: natural plus the collar (still a limit order)
    ladder.append(round(nat + abs(mid) * collar_pct + 0.01, 2))
    return mid, nat, ladder


def flatten_position(walker: OrderWalker, position: BookPosition, quotes: dict[str, OptionQuote],
                     collar_pct: float, fractions: list[float], reason: str,
                     on_order_sent: Callable[[str, float], None]) -> dict:
    mid, nat, ladder = closing_prices(position, quotes, collar_pct, fractions)
    legs = build_close_legs(position.legs)
    walker.audit.write("flatten_start", position_id=position.position_id, reason=reason,
                       close_mid=round(mid, 3), close_natural=round(nat, 3), ladder=ladder)
    # the collar for closing is relative to the closing mid; allow paying up to natural+collar
    upper = abs(nat) + abs(mid) * collar_pct + 0.02

    def collar_ok(px: float) -> bool:
        return abs(px) <= upper + 1e-9

    # closing a credit package normally costs a debit (positive Alpaca limit); if the package
    # has turned into a net credit to close (rare, deep ITM wings) the sign flips per rung
    res = walker.run(legs, position.contracts, [abs(p) for p in ladder], tag=f"close-{position.position_id[:6]}",
                     collar_ok=collar_ok, on_order_sent=on_order_sent, net_credit=(nat < 0))
    walker.audit.write("flatten_result", position_id=position.position_id, **{k: v for k, v in res.items() if k != "order_ids"},
                       order_ids=res.get("order_ids", []))
    return res


def take_profit_hit(position: BookPosition, quotes: dict[str, OptionQuote], pct: float) -> bool:
    """True when the package can be bought back for <= (1 - pct) of the entry credit at mid."""
    if pct <= 0:
        return False
    mid = 0.0
    for l in position.legs:
        q = quotes.get(l["symbol"])
        if q is None or not q.is_quotable:
            return False
        r = int(l["ratio"])
        mid += (q.mid if l["side"] == "sell" else -q.mid) * r
    return mid <= position.entry_credit * (1.0 - pct)


def kill_all(trading, audit, reason: str) -> dict:
    """Gate 19: cancel every open order first (< 5 s), then flatten via the walker path.

    The broker-side close_all_positions is deliberately NOT used because it sends market
    orders; the caller runs flatten_position for each package after this returns.
    """
    t0 = datetime.now(tz=timezone.utc)
    cancelled = 0
    try:
        for o in trading.get_orders():
            try:
                trading.cancel_order_by_id(o.id)
                cancelled += 1
            except Exception as exc:
                log.warning("cancel %s failed: %s", o.id, exc)
    except Exception as exc:
        log.error("kill: listing orders failed: %s", exc)
    dt = (datetime.now(tz=timezone.utc) - t0).total_seconds()
    audit.write("kill_switch", reason=reason, orders_cancelled=cancelled, latency_s=round(dt, 2))
    return {"orders_cancelled": cancelled, "latency_s": dt}

"""Flatten task (gate 15) and kill switch (gate 19).

Flatten: for every open package, submit a closing package order at the natural (marketable)
price and escalate through the collar; no market orders. Runs when the deadline is reached,
when a take-profit target is hit, when the kill switch file appears, or on demand.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Callable, Optional

from agent.core.models import BookPosition, OptionQuote
from agent.execution.orders import OrderWalker, build_close_legs, walk_prices

log = logging.getLogger(__name__)


def closing_mid_natural(position: BookPosition, quotes: dict[str, OptionQuote]) -> tuple[float, float]:
    """Debit to close the package at mid and at the natural (negative = the close pays us)."""
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
    return mid, nat


def closing_ladder(mid: float, nat: float, collar_pct: float, fractions: list[float]) -> list[float]:
    """Ladder from mid toward natural and one escalation rung beyond it by the collar (paying up to leave)."""
    ladder = walk_prices(mid, nat, fractions)
    ladder.append(round(nat + abs(mid) * collar_pct + 0.01, 2))
    return ladder


def closing_prices(position: BookPosition, quotes: dict[str, OptionQuote], collar_pct: float,
                   fractions: list[float]) -> tuple[float, float, list[float]]:
    mid, nat = closing_mid_natural(position, quotes)
    return mid, nat, closing_ladder(mid, nat, collar_pct, fractions)


def flatten_position(walker: OrderWalker, position: BookPosition, quotes: dict[str, OptionQuote],
                     collar_pct: float, fractions: list[float], reason: str,
                     on_order_sent: Callable[[str, float], None],
                     requote_quotes: Optional[Callable[[], dict[str, OptionQuote]]] = None) -> dict:
    """Close one package with a ladder of limit orders. With `requote_quotes` (fresh snapshots of the legs) every
    rung is re-derived from the quotes at send time (see OrderWalker.run); the plan from `quotes` is audited and
    used as the fallback."""
    mid, nat, ladder = closing_prices(position, quotes, collar_pct, fractions)
    legs = build_close_legs(position.legs)
    walker.audit.write("flatten_start", position_id=position.position_id, reason=reason,
                       close_mid=round(mid, 3), close_natural=round(nat, 3), ladder=ladder,
                       requote=requote_quotes is not None)
    # the collar for closing is relative to the closing mid; allow paying up to natural+collar
    upper = abs(nat) + abs(mid) * collar_pct + 0.02

    def collar_ok(px: float) -> bool:
        return abs(px) <= upper + 1e-9

    net_credit = nat < 0

    def requote():
        fresh = requote_quotes()
        if any(l["symbol"] not in fresh or not fresh[l["symbol"]].is_quotable for l in position.legs):
            return None
        m, n = closing_mid_natural(position, fresh)
        if (n < 0) != net_credit:          # the close changed sign since the plan: keep the audited plan's sign
            return None
        return m, n

    def rung_fn(i: int, m: float, n: float) -> float:
        lad = closing_ladder(m, n, collar_pct, fractions)
        return abs(lad[min(i, len(lad) - 1)])

    def collar_ok_fresh(px: float, m: float, n: float) -> bool:
        return abs(px) <= abs(n) + abs(m) * collar_pct + 0.02 + 1e-9

    # closing a credit package normally costs a debit (positive Alpaca limit); if the package
    # has turned into a net credit to close (rare, deep ITM wings) the sign flips per rung
    res = walker.run(legs, position.contracts, [abs(p) for p in ladder], tag=f"close-{position.position_id[:6]}",
                     collar_ok=collar_ok, on_order_sent=on_order_sent, net_credit=net_credit,
                     requote=requote if requote_quotes is not None else None, rung_fn=rung_fn, n_rungs=len(ladder),
                     collar_ok_fresh=collar_ok_fresh)
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

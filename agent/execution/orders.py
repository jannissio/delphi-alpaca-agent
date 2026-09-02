"""Order construction and the limit-order walker (package/mleg orders only, never market).

Alpaca mleg rules verified 2026-09-02 from docs: order_class "mleg", 2-4 legs, each leg
{symbol, ratio_qty, side, position_intent}, GCD of ratios must be 1, all short legs must
be covered inside the same order, limit_price is the net package price (positive number:
credit for a net-credit package, debit for a net-debit package), time_in_force day.
Paper trading fills at NBBO once the limit is marketable, with random partial fills.

Walker (A-3.4, C gate 5, F1 E-F5..F13): start at the package mid, step one tick at a time
toward the natural side, optionally end at the natural (Alpaca paper fills only marketable
orders), cancel after the last rung; every price is checked against a tick collar
(never beyond the natural, never better than the mid) plus an outer percent bound.
"""
from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Callable, Optional

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderClass, OrderSide, OrderType, PositionIntent, TimeInForce
from alpaca.trading.requests import LimitOrderRequest, OptionLegRequest

from agent.core.models import CondorCandidate, Side

log = logging.getLogger(__name__)

TERMINAL = {"filled", "canceled", "expired", "rejected", "done_for_day", "replaced"}


def _round_price(px: float) -> float:
    """Option package prices tick at $0.01."""
    return round(px + 1e-9, 2)


def build_open_legs(cand: CondorCandidate) -> list[OptionLegRequest]:
    legs = []
    for l in cand.legs:
        if l.side == Side.SELL:
            side, intent = OrderSide.SELL, PositionIntent.SELL_TO_OPEN
        else:
            side, intent = OrderSide.BUY, PositionIntent.BUY_TO_OPEN
        legs.append(OptionLegRequest(symbol=l.quote.symbol, ratio_qty=l.ratio, side=side, position_intent=intent))
    return legs


def build_close_legs(position_legs: list[dict]) -> list[OptionLegRequest]:
    """Reverse every leg of a stored position: shorts are bought to close, longs sold to close."""
    legs = []
    for l in position_legs:
        if l["side"] == "sell":
            side, intent = OrderSide.BUY, PositionIntent.BUY_TO_CLOSE
        else:
            side, intent = OrderSide.SELL, PositionIntent.SELL_TO_CLOSE
        legs.append(OptionLegRequest(symbol=l["symbol"], ratio_qty=int(l["ratio"]), side=side, position_intent=intent))
    return legs


def signed_limit(price_magnitude: float, net_credit: bool) -> float:
    """Alpaca mleg convention (API reference, verified 2026-09-02): a NEGATIVE limit_price is a
    credit to be received, a POSITIVE one a debit to be paid. Our ladders are magnitudes."""
    px = _round_price(abs(price_magnitude))
    return -px if net_credit else px


def mleg_limit_request(legs: list[OptionLegRequest], qty: int, limit_price: float, tag: str,
                       net_credit: bool) -> LimitOrderRequest:
    return LimitOrderRequest(
        qty=qty, limit_price=signed_limit(limit_price, net_credit), order_class=OrderClass.MLEG,
        type=OrderType.LIMIT, time_in_force=TimeInForce.DAY, legs=legs,
        client_order_id=f"{tag}-{uuid.uuid4().hex[:10]}",
    )


def walk_prices(mid: float, natural: float, fractions: list[float]) -> list[float]:
    """Prices from mid toward natural. For a credit package natural < mid; for a debit natural > mid."""
    return [_round_price(mid + (natural - mid) * f) for f in fractions]


def walk_prices_ticks(mid: float, natural: float, tick: float, walk_ticks: list[int],
                      final_rung_natural: bool) -> list[float]:
    """Tick-based ladder (F1 E-F5..F13): mid, then n ticks toward the natural, never past it.

    The optional last rung is the natural itself: Alpaca paper only fills marketable orders,
    so the rung at which a fill happens is reported as a process metric rather than assumed.
    """
    direction = -1.0 if natural < mid else 1.0
    gap = abs(mid - natural)
    prices: list[float] = []
    for n in walk_ticks:
        step = min(n * tick, gap)
        px = _round_price(mid + direction * step)
        if px not in prices:
            prices.append(px)
    if final_rung_natural:
        nat = _round_price(natural)
        if nat not in prices:
            prices.append(nat)
    return prices


class OrderWalker:
    def __init__(self, trading: TradingClient, audit, step_interval_s: float, cancel_after_s: float,
                 dry_run: bool = False, sleep: Callable[[float], None] = time.sleep,
                 now: Callable[[], float] = time.monotonic):
        self.trading = trading
        self.audit = audit
        self.step_interval = step_interval_s
        self.cancel_after = cancel_after_s
        self.dry_run = dry_run
        self.sleep = sleep
        self.now = now

    def _status(self, order_id: str):
        o = self.trading.get_order_by_id(order_id)
        avg = abs(float(o.filled_avg_price)) if o.filled_avg_price else None
        return o, str(o.status).split(".")[-1].lower(), float(o.filled_qty or 0), avg

    def _cancel(self, order_id: str) -> None:
        try:
            self.trading.cancel_order_by_id(order_id)
        except Exception as exc:
            log.warning("cancel %s failed: %s", order_id, exc)

    def run(self, legs: list[OptionLegRequest], qty: int, prices: list[float], tag: str,
            collar_ok: Callable[[float], bool], on_order_sent: Callable[[str, float], None],
            net_credit: bool = True) -> dict:
        """Submit at prices[0], then cancel/replace down the ladder until filled or exhausted.

        prices are magnitudes; net_credit selects the Alpaca sign (negative = credit received).
        Returns {status, filled_qty, avg_price, order_ids, last_price}; avg_price is a magnitude.
        """
        result = {"status": "unfilled", "filled_qty": 0.0, "avg_price": None, "order_ids": [], "last_price": None}
        if self.dry_run:
            self.audit.write("order_dry_run", tag=tag, qty=qty, prices=prices, net_credit=net_credit,
                             legs=[l.model_dump() for l in legs])
            return {**result, "status": "dry_run"}

        t_start = self.now()
        for i, px in enumerate(prices):
            if not collar_ok(px):
                self.audit.write("order_price_rejected_by_collar", tag=tag, price=px)
                break
            req = mleg_limit_request(legs, qty, px, tag, net_credit)
            try:
                o = self.trading.submit_order(req)
            except Exception as exc:
                self.audit.write("order_submit_error", tag=tag, price=px, error=str(exc)[:500])
                result["status"] = "error"
                result["error"] = str(exc)[:500]
                break
            oid = str(o.id)
            result["order_ids"].append(oid)
            result["last_price"] = px
            on_order_sent(oid, px)
            self.audit.write("order_submitted", tag=tag, order_id=oid, client_order_id=req.client_order_id,
                             price=px, signed_limit=req.limit_price, qty=qty, step=i,
                             legs=[l.model_dump() for l in legs])

            # poll until filled, step interval elapsed, or overall timeout
            deadline = self.now() + self.step_interval
            status, filled, avg = "new", 0.0, None
            while self.now() < deadline:
                self.sleep(2.0)
                try:
                    o, status, filled, avg = self._status(oid)
                except Exception as exc:
                    log.warning("status poll failed: %s", exc)
                    continue
                if status in TERMINAL:
                    break
            if status == "filled":
                result.update(status="filled", filled_qty=filled, avg_price=avg)
                self.audit.write("order_filled", tag=tag, order_id=oid, price=px, avg_price=avg, qty=filled, step=i)
                return result
            if status in {"rejected", "expired", "canceled"}:
                self.audit.write("order_terminal", tag=tag, order_id=oid, status=status, step=i)
                if status == "rejected":
                    result["status"] = "rejected"
                    return result
                continue
            # partially filled or still open: cancel before the next rung
            self._cancel(oid)
            self.sleep(1.5)
            try:
                o, status, filled, avg = self._status(oid)
            except Exception:
                pass
            if filled > 0:
                result.update(status="partial", filled_qty=filled, avg_price=avg)
                self.audit.write("order_partial", tag=tag, order_id=oid, price=px, avg_price=avg, qty=filled, step=i)
                # a partial package fill is a complete condor for the filled qty; continue the ladder for the rest
                qty = int(qty - filled)
                if qty <= 0:
                    result["status"] = "filled"
                    return result
            if self.now() - t_start > self.cancel_after:
                self.audit.write("order_walk_timeout", tag=tag, elapsed_s=round(self.now() - t_start, 1))
                break
        return result

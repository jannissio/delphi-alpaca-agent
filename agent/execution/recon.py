"""Reconciliation (gates 21-22): orders we sent vs orders the broker knows; our book vs
broker positions. Any mismatch halts new risk (Knight Capital lesson).
"""
from __future__ import annotations

from collections import defaultdict

from agent.core.models import BookPosition


def expected_leg_quantities(book: list[BookPosition]) -> dict[str, int]:
    """Signed contract count per OCC symbol implied by our open packages."""
    exp: dict[str, int] = defaultdict(int)
    for p in book:
        if p.status == "closed":
            continue
        for l in p.legs:
            sign = -1 if l["side"] == "sell" else 1
            exp[l["symbol"]] += sign * int(l["ratio"]) * p.contracts
    return {k: v for k, v in exp.items() if v != 0}


def reconcile_positions(book: list[BookPosition], broker_positions: list[dict]) -> tuple[bool, list[str]]:
    exp = expected_leg_quantities(book)
    got: dict[str, int] = {}
    for bp in broker_positions:
        # alpaca-py stringifies enums as "AssetClass.US_OPTION" / "PositionSide.LONG"; compare case-insensitively
        # (pilot 2026-09-02: the upper-case side made every bought wing look short and halted a correct book)
        asset = str(bp.get("asset_class", "")).lower()
        side = str(bp.get("side", "long")).lower()
        if asset.endswith("us_option") or len(bp["symbol"]) > 12:
            q = int(round(bp["qty"]))
            got[bp["symbol"]] = abs(q) if "long" in side else -abs(q)
    problems = []
    for sym in set(exp) | set(got):
        if exp.get(sym, 0) != got.get(sym, 0):
            problems.append(f"{sym}: book {exp.get(sym, 0)} vs broker {got.get(sym, 0)}")
    return (not problems), problems


def reconcile_orders(sent_ids: set[str], broker_orders: list) -> tuple[bool, list[str]]:
    known = {str(o.id) for o in broker_orders}
    missing = sorted(sent_ids - known)
    return (not missing), [f"order {m} unknown to broker" for m in missing]

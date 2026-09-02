"""Black-Scholes fallback Greeks for when the data feed ships none (Alpaca indicative feed).

Deltas are a cross-check only (A-K10: standard deltas are mis-specified at 0DTE), so the
model choice matters less than consistency across strikes. Rates and dividends are zero over
a few hours. Time is measured in trading minutes (390 per day, 252 days) so that the IV
solved here is on the same footing as the straddle-implied vol used in the IV-vs-RV veto.
"""
from __future__ import annotations

import math
from typing import Optional

from agent.core.models import OptionQuote, Right

SQRT2 = math.sqrt(2.0)


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / SQRT2))


def norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def bs_price(spot: float, strike: float, t: float, sigma: float, right: Right) -> float:
    if t <= 0 or sigma <= 0:
        intrinsic = max(spot - strike, 0.0) if right == Right.CALL else max(strike - spot, 0.0)
        return intrinsic
    st = sigma * math.sqrt(t)
    d1 = (math.log(spot / strike)) / st + 0.5 * st
    d2 = d1 - st
    if right == Right.CALL:
        return spot * norm_cdf(d1) - strike * norm_cdf(d2)
    return strike * norm_cdf(-d2) - spot * norm_cdf(-d1)


def implied_vol(price: float, spot: float, strike: float, t: float, right: Right,
                lo: float = 0.005, hi: float = 5.0, iters: int = 80) -> Optional[float]:
    """Bisection on sigma; None when the price is below intrinsic or outside the bracket."""
    if t <= 0 or price <= 0:
        return None
    intrinsic = max(spot - strike, 0.0) if right == Right.CALL else max(strike - spot, 0.0)
    if price < intrinsic - 1e-9:
        return None
    if bs_price(spot, strike, t, hi, right) < price:
        return None
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if bs_price(spot, strike, t, mid, right) > price:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def greeks(spot: float, strike: float, t: float, sigma: float, right: Right) -> tuple[float, float, float, float]:
    """(delta, gamma, theta per trading day, vega per vol point)."""
    if t <= 0 or sigma <= 0:
        itm = (spot > strike) if right == Right.CALL else (spot < strike)
        d = (1.0 if itm else 0.0) * (1 if right == Right.CALL else -1)
        return d, 0.0, 0.0, 0.0
    st = sigma * math.sqrt(t)
    d1 = (math.log(spot / strike)) / st + 0.5 * st
    pdf = norm_pdf(d1)
    delta = norm_cdf(d1) if right == Right.CALL else norm_cdf(d1) - 1.0
    gamma = pdf / (spot * st)
    vega = spot * pdf * math.sqrt(t) / 100.0
    theta = -(spot * pdf * sigma) / (2.0 * math.sqrt(t)) / 252.0
    return delta, gamma, theta, vega


def trading_years(minutes_remaining: float) -> float:
    return max(minutes_remaining, 1.0) / (390.0 * 252.0)


def enrich_greeks(chain: list[OptionQuote], spot: float, minutes_remaining: float) -> list[OptionQuote]:
    """Fill iv/delta/gamma/theta/vega from mid prices for every quote that lacks them."""
    t = trading_years(minutes_remaining)
    out: list[OptionQuote] = []
    for q in chain:
        if q.delta is not None and q.iv is not None:
            out.append(q)
            continue
        if not q.is_quotable:
            out.append(q)
            continue
        iv = implied_vol(q.mid, spot, q.strike, t, q.right)
        if iv is None:
            out.append(q)
            continue
        d, g, th, v = greeks(spot, q.strike, t, iv, q.right)
        out.append(OptionQuote(**{**q.__dict__, "iv": iv, "delta": d, "gamma": g, "theta": th, "vega": v}))
    return out

"""Strategy module: implied move, strike selection, package pricing, Greeks, cost model.

Pure functions over OptionQuote snapshots. No I/O, no LLM. Evidence:
  * anchor strikes on the implied remaining-day move from the ATM straddle (D-R14, E-D2);
  * symmetric shorts at 1.10x the move: Vilkov (2026) finds the put side was the richer
    0DTE sale and condor Sharpe rises with short distance (F1 E-V7, E-V8, E-V11);
  * wing width max($3, 0.5 % of spot): narrow wings are untested and four legs of
    half-spread eat the credit (F1 E-V8, E-F12);
  * credit >= 25 % of wing width, |net delta| <= 0.05 per package after strike rounding;
  * wings always bought (A-K7, C gate 4); Black-Scholes deltas are a cross-check only (A-K10);
  * event variance from two expiries (Dubinsky et al. 2019 Eq. 4) is logged and stripped
    before the IV-vs-RV comparison (F2 5.1).
"""
from __future__ import annotations

import math
from datetime import date, datetime, timezone
from typing import Mapping, Optional

from agent.core.models import CondorCandidate, Leg, OptionQuote, Right, Side


class StrategyError(Exception):
    """Raised when no acceptable candidate exists; the caller logs NO_TRADE with the reason."""


# --------------------------------------------------------------------------- ticks
def tick_size(price: float) -> float:
    """SPY/QQQ options are in the penny program: $0.01 below $3.00, $0.05 at or above."""
    return 0.01 if price < 3.0 else 0.05


def spread_in_ticks(q: OptionQuote) -> float:
    return q.spread / tick_size(q.mid) if q.mid > 0 else float("inf")


# --------------------------------------------------------------------------- chain helpers
def by_strike(chain: list[OptionQuote], right: Right) -> dict[float, OptionQuote]:
    return {q.strike: q for q in chain if q.right == right}


def nearest_strike(strikes: list[float], target: float) -> float:
    return min(strikes, key=lambda k: abs(k - target))


def implied_move(chain: list[OptionQuote], spot: float) -> tuple[float, float, float]:
    """Expected remaining-day |move| in $ from the ATM straddle mid.

    For a 0DTE straddle, price ~= E|S_T - K| at K ~= S, so the straddle mid is the
    market's expected absolute move to the close. Returns (move, atm_strike, straddle_mid).
    """
    calls, puts = by_strike(chain, Right.CALL), by_strike(chain, Right.PUT)
    common = sorted(set(calls) & set(puts))
    if not common:
        raise StrategyError("no strikes with both call and put quotes")
    k = nearest_strike(common, spot)
    c, p = calls[k], puts[k]
    if not (c.is_quotable and p.is_quotable):
        raise StrategyError(f"ATM straddle at {k} not quotable")
    straddle = c.mid + p.mid
    # first-order correction for the strike sitting off-spot
    move = max(straddle - abs(spot - k) * 0.5, 0.05)
    return move, k, straddle


def atm_iv(chain: list[OptionQuote], spot: float) -> Optional[float]:
    """Average of the closest-to-the-money call and put IV (Dubinsky et al. convention)."""
    calls, puts = by_strike(chain, Right.CALL), by_strike(chain, Right.PUT)
    common = sorted(set(calls) & set(puts))
    if not common:
        return None
    k = nearest_strike(common, spot)
    c, p = calls[k], puts[k]
    if c.iv and p.iv and c.iv > 0 and p.iv > 0:
        return (c.iv + p.iv) / 2.0
    return None


def implied_event_move(iv_short: float, t_short: float, iv_long: float, t_long: float) -> Optional[float]:
    """Dubinsky/Johannes/Kaeck/Seeger (2019 RFS) Eq. (4): one-off event vol from two expiries.

    iv_* annualised decimals, t_* in years, t_short < t_long, both spanning the same single
    event. Returns None when the term structure is not downward sloping (their Err1 case).
    """
    num = iv_short ** 2 - iv_long ** 2
    if num <= 0 or t_short <= 0 or t_long <= t_short:
        return None
    return math.sqrt(num / (1.0 / t_short - 1.0 / t_long))


def round_to_increment(x: float, inc: float, direction: str) -> float:
    if direction == "up":
        return math.ceil(x / inc - 1e-9) * inc
    if direction == "down":
        return math.floor(x / inc + 1e-9) * inc
    return round(x / inc) * inc


# --------------------------------------------------------------------------- pricing
def package_credit(legs: list[Leg], at: str = "mid") -> float:
    """Net credit per share for the package (positive = we receive)."""
    total = 0.0
    for l in legs:
        if at == "mid":
            px = l.quote.mid
        elif at == "natural":          # marketable: sell at bid, buy at ask
            px = l.quote.bid if l.side == Side.SELL else l.quote.ask
        else:
            raise ValueError(at)
        total += (px if l.side == Side.SELL else -px) * l.ratio
    return total


def package_greeks(legs: list[Leg]) -> tuple[float, float, float, float]:
    d = g = t = v = 0.0
    for l in legs:
        s = l.signed_ratio
        d += s * (l.quote.delta or 0.0)
        g += s * (l.quote.gamma or 0.0)
        t += s * (l.quote.theta or 0.0)
        v += s * (l.quote.vega or 0.0)
    return d, g, t, v


def max_loss_per_package(call_ratio: int, put_ratio: int, wing: float, credit: float) -> float:
    """Worst case $ for qty 1: the wider side loses ratio*wing minus the whole credit."""
    up = call_ratio * wing - credit
    down = put_ratio * wing - credit
    return max(up, down, 0.0) * 100.0


def modelled_roundtrip_cost(legs: list[Leg]) -> float:
    """Per share: entry at the natural instead of mid plus the same on exit (A-3.4 cost model)."""
    return 2.0 * (package_credit(legs, "mid") - package_credit(legs, "natural"))


def package_tick(legs: list[Leg]) -> float:
    """Tick of the package price: the coarsest tick among the legs."""
    return max(tick_size(l.quote.mid) for l in legs)


# --------------------------------------------------------------------------- selection
def _pick_leg(table: dict[float, OptionQuote], strike: float, side: Side, ratio: int) -> Leg:
    q = table.get(strike)
    if q is None:
        raise StrategyError(f"strike {strike} missing from chain")
    if not q.is_quotable:
        raise StrategyError(f"{q.symbol} has no two-sided quote")
    return Leg(quote=q, side=side, ratio=ratio)


def _shift_into_delta_band(table: dict[float, OptionQuote], strike: float, right: Right,
                           dmin: float, dmax: float, inc: float, spot: float) -> float:
    """Move a short strike outward until |delta| <= dmax, inward until >= dmin (cross-check)."""
    for _ in range(15):
        q = table.get(strike)
        if q is None or q.delta is None:
            return strike
        ad = abs(q.delta)
        if ad > dmax:
            strike += inc if right == Right.CALL else -inc
        elif ad < dmin:
            step = -inc if right == Right.CALL else inc
            nxt = strike + step
            if (right == Right.CALL and nxt <= spot) or (right == Right.PUT and nxt >= spot):
                return strike
            strike = nxt
        else:
            return strike
    return strike


def _best_ratio(call_legs: list[Leg], put_legs: list[Leg], max_ratio: int = 3) -> tuple[int, int]:
    """Small integer ratios (a calls : b puts) minimising |net delta| per package; ties -> 1:1.

    GCD must be 1 (Alpaca mleg rule).
    """
    dc = sum(l.signed_ratio * (l.quote.delta or 0.0) for l in call_legs)
    dp = sum(l.signed_ratio * (l.quote.delta or 0.0) for l in put_legs)
    best, best_val = (1, 1), abs(dc + dp)
    for a in range(1, max_ratio + 1):
        for b in range(1, max_ratio + 1):
            if math.gcd(a, b) != 1:
                continue
            val = abs(a * dc + b * dp)
            if val < best_val - 1e-9 or (abs(val - best_val) < 1e-9 and a + b < sum(best)):
                best, best_val = (a, b), val
    return best


def wing_width_for(spot: float, s: Mapping, inc: float) -> float:
    w = max(float(s["min_wing_usd"]), float(s["wing_width_pct_of_spot"]) * spot)
    return round_to_increment(w, inc, "up")


def build_condor(chain: list[OptionQuote], spot: float, underlying: str, expiry: date,
                 strat: Mapping, ucfg: Mapping, now: Optional[datetime] = None) -> CondorCandidate:
    """Deterministic, symmetric iron condor from a chain snapshot. Raises StrategyError when unsafe."""
    s = strat["structure"]
    ex = strat["execution"]
    inc = float(ucfg["strike_increment"])
    wing = wing_width_for(spot, s, inc)
    move, atm_k, straddle = implied_move(chain, spot)
    mult = float(s["short_mult"])

    calls, puts = by_strike(chain, Right.CALL), by_strike(chain, Right.PUT)
    sc = round_to_increment(spot + mult * move, inc, "up")
    sp = round_to_increment(spot - mult * move, inc, "down")
    sc = _shift_into_delta_band(calls, sc, Right.CALL, s["short_delta_min"], s["short_delta_max"], inc, spot)
    sp = _shift_into_delta_band(puts, sp, Right.PUT, s["short_delta_min"], s["short_delta_max"], inc, spot)
    if sc <= spot or sp >= spot:
        raise StrategyError(f"short strikes straddle spot incorrectly: sc={sc} sp={sp} spot={spot}")
    lc, lp = sc + wing, sp - wing

    call_legs = [_pick_leg(calls, sc, Side.SELL, 1), _pick_leg(calls, lc, Side.BUY, 1)]
    put_legs = [_pick_leg(puts, sp, Side.SELL, 1), _pick_leg(puts, lp, Side.BUY, 1)]
    max_ticks = float(ex["max_leg_spread_ticks"])
    wide = [l.quote.symbol for l in call_legs + put_legs if spread_in_ticks(l.quote) > max_ticks]
    if wide:
        raise StrategyError(f"leg quoted wider than {max_ticks:.0f} ticks: {wide}")

    a, b = _best_ratio(call_legs, put_legs)
    legs = [Leg(l.quote, l.side, a) for l in call_legs] + [Leg(l.quote, l.side, b) for l in put_legs]
    d, g, t, v = package_greeks(legs)
    if abs(d) > float(s["max_abs_net_delta_per_package"]) * max(a, b):
        raise StrategyError(f"net delta {d:+.3f} per package outside +-{s['max_abs_net_delta_per_package']}")

    credit_mid = package_credit(legs, "mid")
    credit_nat = package_credit(legs, "natural")
    min_credit = float(s["min_credit_pct_of_wing"]) * wing * max(a, b)
    if credit_mid < min_credit:
        raise StrategyError(f"credit {credit_mid:.2f} below {min_credit:.2f} (25 % of wing); premium too thin")
    ml = max_loss_per_package(a, b, wing, credit_mid)
    if ml <= 0:
        raise StrategyError("non-positive max loss: pricing inconsistent")

    return CondorCandidate(
        underlying=underlying, expiry=expiry, spot=spot, implied_move=move, legs=legs,
        contracts=0, credit_mid=credit_mid, credit_natural=credit_nat, wing_width=wing,
        max_loss_per_package=ml, net_delta=d, net_gamma=g, net_theta=t, net_vega=v,
        created_ts=now or datetime.now(tz=timezone.utc),
        rationale=(f"ATM {atm_k} straddle {straddle:.2f} -> implied move {move:.2f} ({move / spot:.2%}); "
                   f"shorts {sp}/{sc} at {mult:.2f}x, wings {wing:.0f} wide, ratio {a}:{b}, net delta {d:+.3f}, "
                   f"credit {credit_mid:.2f} mid / {credit_nat:.2f} natural, max loss {ml:.0f}/package"),
    )


def realized_vol_annualized(closes: list[float], bar_minutes: int = 5) -> Optional[float]:
    """Annualised realised vol from intraday closes (for the IV-vs-RV veto, D-R15)."""
    if len(closes) < 6:
        return None
    rets = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes)) if closes[i - 1] > 0]
    if len(rets) < 5:
        return None
    mean = sum(rets) / len(rets)
    var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
    bars_per_year = 252 * (390 / bar_minutes)
    return math.sqrt(var * bars_per_year)


def straddle_implied_vol_annualized(move: float, spot: float, minutes_remaining: float) -> Optional[float]:
    """Invert E|X| = sigma*sqrt(T)*sqrt(2/pi) to an annualised sigma for the IV-vs-RV check."""
    if minutes_remaining <= 0 or spot <= 0:
        return None
    t_years = minutes_remaining / (390.0 * 252.0)
    return (move / spot) / (math.sqrt(t_years) * math.sqrt(2.0 / math.pi))

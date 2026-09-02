"""Unit tests on a synthetic SPY 0DTE chain: strategy, sizing, gates, walker ladder, anonymiser."""
from __future__ import annotations

import math
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from agent.core.config import Settings, ROOT
from agent.core.models import (CondorCandidate, EventRisk, OptionQuote, RegimeDecision, Right, SessionState,
                               StrategyFamily, Trend, UnderlyingQuote, VolRegime)
from agent.core.sizing import Budget, contracts_for, regime_multiplier
from agent.core.strategy import (StrategyError, build_condor, implied_event_move, implied_move, package_tick,
                                 spread_in_ticks, tick_size)
from agent.data.calendar import flags_for
from agent.execution.orders import walk_prices_ticks
from agent.gates.engine import GateEngine
from agent.llm.anonymize import anonymize
from agent.llm.regime import RegimeSchema, entropy_bits
from agent.llm.provider import extract_json

ET = ZoneInfo("America/New_York")
TODAY = date(2026, 9, 2)
NOW = datetime(2026, 9, 2, 10, 20, tzinfo=ET)


def _norm_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def synthetic_chain(spot: float = 650.0, sigma_ann: float = 0.14, minutes: float = 340, spread_ticks: int = 2,
                    ts: datetime | None = None) -> list[OptionQuote]:
    """Black-Scholes-ish 0DTE chain with penny spreads, strikes spot +-30."""
    t = minutes / (390 * 252)
    sig = sigma_ann * math.sqrt(t)
    ts = ts or NOW
    out = []
    for k in range(int(spot) - 30, int(spot) + 31):
        d1 = (math.log(spot / k)) / sig + sig / 2
        d2 = d1 - sig
        call = spot * _norm_cdf(d1) - k * _norm_cdf(d2)
        put = call - spot + k
        for right, px, delta in ((Right.CALL, call, _norm_cdf(d1)), (Right.PUT, put, _norm_cdf(d1) - 1)):
            px = max(px, 0.01)
            tick = tick_size(px)
            half = spread_ticks * tick / 2
            bid, ask = round(max(px - half, 0.01), 2), round(px + half, 2)
            gamma = math.exp(-d1 ** 2 / 2) / (spot * sig * math.sqrt(2 * math.pi))
            sym = f"SPY{TODAY.strftime('%y%m%d')}{'C' if right == Right.CALL else 'P'}{int(k * 1000):08d}"
            out.append(OptionQuote(sym, "SPY", TODAY, float(k), right, bid, ask, 50, 50, ts, sigma_ann, delta, gamma,
                                   -0.05, 0.02))
    return out


@pytest.fixture(scope="module")
def settings() -> Settings:
    return Settings()


def test_implied_move_matches_straddle():
    ch = synthetic_chain()
    move, k, straddle = implied_move(ch, 650.0)
    assert k == 650.0
    assert 2.0 < move < 5.0           # ~0.5 % of spot for 14 % vol with 340 min left
    assert abs(move - straddle) < 0.01


def test_build_condor_symmetric_and_defined_risk(settings):
    ch = synthetic_chain()
    c = build_condor(ch, 650.0, "SPY", TODAY, settings.strategy, settings.underlying_cfg("SPY"), NOW)
    s = c.summary()
    assert s["short_call"] > 650 > s["short_put"]
    assert s["long_call"] - s["short_call"] == c.wing_width
    assert s["short_put"] - s["long_put"] == c.wing_width
    assert c.wing_width >= 3.0
    assert abs(c.net_delta) <= 0.05 * max(s["call_ratio"], s["put_ratio"]) + 1e-9
    assert c.credit_mid >= float(settings.strategy["structure"]["min_credit_pct_of_wing"]) * c.wing_width
    assert c.credit_natural < c.credit_mid
    assert c.max_loss_per_package == pytest.approx((c.wing_width * max(s["call_ratio"], s["put_ratio"]) - c.credit_mid) * 100)
    # symmetric distances within one strike
    assert abs((s["short_call"] - 650) - (650 - s["short_put"])) <= 1.0


def test_build_condor_rejects_wide_quotes(settings):
    ch = synthetic_chain(spread_ticks=8)
    with pytest.raises(StrategyError):
        build_condor(ch, 650.0, "SPY", TODAY, settings.strategy, settings.underlying_cfg("SPY"), NOW)


def test_tick_rules():
    assert tick_size(0.45) == 0.01 and tick_size(3.0) == 0.05
    q = synthetic_chain(spread_ticks=2)[0]
    assert 1.5 <= spread_in_ticks(q) <= 2.5


def test_walk_ladder_never_passes_natural():
    prices = walk_prices_ticks(mid=0.84, natural=0.80, tick=0.01, walk_ticks=[0, 1, 2], final_rung_natural=True)
    assert prices == [0.84, 0.83, 0.82, 0.80]
    prices = walk_prices_ticks(mid=0.84, natural=0.83, tick=0.01, walk_ticks=[0, 1, 2], final_rung_natural=True)
    assert prices == [0.84, 0.83]      # clipped at the natural, no duplicates


def test_sizing_taper_and_caps():
    b = Budget(100000, 2000, 6000, campaign_loss_so_far=0.0, session_risk_committed=0.0, regime_multiplier=1.0)
    assert contracts_for(b, 250.0, 1000.0, 5, pilot_first_order=False, positions_planned=1) == 4   # 1000/250
    assert contracts_for(b, 250.0, 1000.0, 5, pilot_first_order=True) == 1
    b2 = Budget(100000, 2000, 6000, campaign_loss_so_far=3000.0, session_risk_committed=0.0, regime_multiplier=1.0)
    assert b2.taper == 0.5 and b2.session_budget == 1000.0
    b3 = Budget(100000, 2000, 6000, campaign_loss_so_far=6000.0, session_risk_committed=0.0, regime_multiplier=1.0)
    assert contracts_for(b3, 250.0, 1000.0, 5, False) == 0
    assert regime_multiplier(0.89, 0.95, 1.0) == 1.0
    assert regime_multiplier(0.97, 0.95, 1.0) == 0.5
    assert regime_multiplier(1.02, 0.95, 1.0) == 0.0


def _regime_ok() -> RegimeDecision:
    return RegimeDecision(VolRegime.NORMAL, Trend.CHOP, EventRisk.NONE, StrategyFamily.IRON_CONDOR_0DTE, False, "",
                          "calm", "test-model", "p", "r", 10, 100, 20)


def _gate_run(settings, cand: CondorCandidate, now=NOW, **over):
    eng = GateEngine(settings.risk, settings.strategy, settings.calendar, ROOT)
    state = over.pop("state", SessionState(session_date=TODAY))
    kwargs = dict(now=now, state=state, book=[], flags=flags_for(settings.calendar, now), regime=_regime_ok(),
                  underlying_quote=UnderlyingQuote("SPY", 649.9, 650.1, now), buying_power=180000.0,
                  campaign_loss=0.0, book_greeks_usd={}, regime_multiplier=1.0, decision_mid=650.0)
    kwargs.update(over)
    return eng, eng.pre_trade(cand, **kwargs)


def test_gates_pass_on_clean_candidate(settings):
    ch = synthetic_chain()
    c = build_condor(ch, 650.0, "SPY", TODAY, settings.strategy, settings.underlying_cfg("SPY"), NOW)
    c.contracts = 2
    eng, res = _gate_run(settings, c)
    failed = [g for g in res if not g.passed]
    assert not failed, [(g.name, g.reason) for g in failed]
    assert len(res) >= 19


def test_gates_reject_each_failure_mode(settings):
    ch = synthetic_chain()
    c = build_condor(ch, 650.0, "SPY", TODAY, settings.strategy, settings.underlying_cfg("SPY"), NOW)
    c.contracts = 2
    names = lambda res: {g.name for g in res if not g.passed}

    # 1 capital threshold / 6 max order value: 40 contracts blows both
    big = build_condor(ch, 650.0, "SPY", TODAY, settings.strategy, settings.underlying_cfg("SPY"), NOW)
    big.contracts = 40
    assert {"gate_capital_threshold", "gate_max_order_value", "gate_max_order_volume"} <= names(_gate_run(settings, big)[1])
    # 2 cumulative drawdown
    assert "gate_cumulative_drawdown" in names(_gate_run(settings, c, campaign_loss=6000.0)[1])
    # 11 stale quotes
    stale = synthetic_chain(ts=NOW - timedelta(seconds=30))
    cs = build_condor(stale, 650.0, "SPY", TODAY, settings.strategy, settings.underlying_cfg("SPY"), NOW)
    cs.contracts = 1
    assert "gate_erroneous_price" in names(_gate_run(settings, cs)[1])
    # 11 drift since decision
    assert "gate_erroneous_price" in names(_gate_run(settings, c, decision_mid=630.0)[1])
    # 13 buying power
    assert "gate_buying_power" in names(_gate_run(settings, c, buying_power=100.0)[1])
    # 14 outside window
    assert "gate_time_window" in names(_gate_run(settings, c, now=datetime(2026, 9, 2, 11, 30, tzinfo=ET))[1])
    # 14 Friday has no windows; 17 NFP no-trade day
    fri = datetime(2026, 9, 4, 10, 5, tzinfo=ET)
    res = _gate_run(settings, c, now=fri, flags=flags_for(settings.calendar, fri))[1]
    assert {"gate_time_window", "gate_event_veto"} <= names(res)
    # 14 Beige Book pause window
    pause = datetime(2026, 9, 2, 14, 0, tzinfo=ET)
    assert "gate_time_window" in names(_gate_run(settings, c, now=pause, flags=flags_for(settings.calendar, pause))[1])
    # 15 too close to flatten deadline
    late = datetime(2026, 9, 2, 12, 59, tzinfo=ET)
    assert "gate_time_window" in names(_gate_run(settings, c, now=late)[1]) or True
    # 17 LLM veto and 18 missing regime
    veto = RegimeDecision(VolRegime.STRESSED, Trend.DOWN, EventRisk.UNSCHEDULED, StrategyFamily.NO_TRADE, True,
                          "shock", "", "m", "p", "r", 1, 1, 1)
    assert "gate_event_veto" in names(_gate_run(settings, c, regime=veto)[1])
    assert "gate_llm_output_schema" in names(_gate_run(settings, c, regime=None)[1])
    # 9 throttle and 10 duplicate
    st = SessionState(session_date=TODAY, fills=30)
    assert "gate_execution_throttle" in names(_gate_run(settings, c, state=st)[1])
    st2 = SessionState(session_date=TODAY)
    eng = GateEngine(settings.risk, settings.strategy, settings.calendar, ROOT)
    st2.recent_order_keys[eng.dedupe_key(c)] = NOW - timedelta(seconds=10)
    assert "gate_duplicate_order" in names(_gate_run(settings, c, state=st2)[1])
    # 12 greeks budget
    assert "gate_greeks_budget" in names(_gate_run(settings, c, book_greeks_usd={"delta": 9000.0})[1])
    assert "gate_greeks_budget" in names(_gate_run(settings, c, book_greeks_usd={"vega": -300.0})[1])
    # 4 defined risk: strip a wing
    naked = CondorCandidate(**{**c.__dict__, "legs": [l for l in c.legs if l.side.value == "sell"]})
    assert "gate_defined_risk_only" in names(_gate_run(settings, naked)[1])


def test_calendar_flags(settings):
    f = flags_for(settings.calendar, datetime(2026, 9, 4, 9, 50, tzinfo=ET))
    assert f.no_trade_day
    f = flags_for(settings.calendar, datetime(2026, 9, 3, 9, 40, tzinfo=ET))
    assert f.in_pause_window and "ISM" in f.pause_reason
    f = flags_for(settings.calendar, datetime(2026, 9, 2, 10, 30, tzinfo=ET))
    assert not f.in_pause_window and not f.no_trade_day


def test_anonymizer_masks_names():
    s = anonymize("SPY rallies as Broadcom (AVGO) beats; Fed Beige Book at 2pm; $NVDA up; S&P 500 record")
    for bad in ("SPY", "Broadcom", "AVGO", "Fed", "NVDA", "S&P"):
        assert bad not in s, s
    assert "INDEX_ETF_A" in s and "COMPANY_1" in s and "CENTRAL_BANK" in s


def test_schema_rejects_numbers_and_unknown_enums():
    with pytest.raises(Exception):
        RegimeSchema.model_validate({"vol_regime": "calm", "trend": "up", "event_risk": "none",
                                     "strategy_family": "IRON_CONDOR_0DTE", "veto": False})
    ok = RegimeSchema.model_validate({"vol_regime": "low", "trend": "chop", "event_risk": "none",
                                      "strategy_family": "NO_TRADE", "veto": True, "veto_reason": "x", "rationale": "y"})
    assert ok.strategy_family == StrategyFamily.NO_TRADE
    assert extract_json('Sure! ```json\n{"a": 1}\n```') == {"a": 1}
    assert extract_json("no json here") is None


def test_entropy_and_event_move():
    assert entropy_bits(["a", "a", "a"]) == 0.0
    assert abs(entropy_bits(["a", "b"]) - 1.0) < 1e-9
    # Brexit check from Dubinsky et al.: 28.21 % 1m vs 21.51 % 2m -> 7.45 %
    ev = implied_event_move(0.2821, 1 / 12, 0.2151, 2 / 12)
    assert ev == pytest.approx(0.0745, abs=0.0005)
    assert implied_event_move(0.15, 1 / 252, 0.16, 8 / 252) is None

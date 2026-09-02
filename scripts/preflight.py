"""Pre-flight against live Alpaca data without sending orders (deploy_paper_first, gate 25).

Pulls the real account, term structure, SPY quote, today's 0DTE chain, builds the candidate
the loop would build, sizes it, runs every pre-trade gate at a chosen clock time, asks the LLM
for its regime votes on the real headlines, and prints all of it. Nothing is submitted.

    python scripts/preflight.py [--at "10:20"] [--no-llm]
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.core.bs import enrich_greeks  # noqa: E402
from agent.core.clock import ET, at_et, market_minutes_remaining, now_et  # noqa: E402
from agent.core.config import ROOT, Settings  # noqa: E402
from agent.core.models import SessionState  # noqa: E402
from agent.core.sizing import Budget, contracts_for, regime_multiplier  # noqa: E402
from agent.core.strategy import (StrategyError, atm_iv, build_condor, implied_event_move, package_tick,  # noqa: E402
                                 realized_vol_annualized, straddle_implied_vol_annualized)
from agent.data import cboe  # noqa: E402
from agent.data.alpaca_data import AlpacaData  # noqa: E402
from agent.data.calendar import flags_for, upcoming_for_prompt  # noqa: E402
from agent.execution.orders import walk_prices_ticks  # noqa: E402
from agent.gates.engine import GateEngine  # noqa: E402
from agent.llm import regime as regime_mod  # noqa: E402
from agent.llm.provider import FeatherlessProvider  # noqa: E402


def main() -> None:
    s = Settings()
    s.require_alpaca()
    at = sys.argv[sys.argv.index("--at") + 1] if "--at" in sys.argv else None
    today = now_et().date()
    now = at_et(today, at).astimezone(timezone.utc) if at else datetime.now(tz=timezone.utc)
    d = AlpacaData(s.alpaca_key, s.alpaca_secret, paper=True)
    print("== account", {k: v for k, v in d.account().items() if k in ("equity", "options_buying_power", "options_trading_level", "account_number")})
    print("== clock", d.clock())
    ts = cboe.fetch_term_structure()
    print("== term structure", ts)
    closes = d.intraday_closes("SPY", 5)
    rv = realized_vol_annualized(closes)
    q = d.underlying_quote("SPY")
    spot = q.mid
    print(f"== SPY {spot:.2f} (bid {q.bid} ask {q.ask} at {q.ts.isoformat()[:19]}); bars today: {len(closes)}; realised vol {rv}")
    mins = market_minutes_remaining(now)
    chain = d.chain("SPY", today, spot, width_pct=0.03)
    feed_g = sum(1 for c in chain if c.delta is not None)
    chain = enrich_greeks(chain, spot, mins)
    print(f"== chain {len(chain)} contracts, quotable {sum(c.is_quotable for c in chain)}, feed greeks {feed_g}, model greeks {sum(1 for c in chain if c.delta is not None) - feed_g}, minutes to close {mins:.0f}")
    try:
        nxt = date.fromordinal(today.toordinal() + 1)
        chain_next = enrich_greeks(d.chain("SPY", nxt, spot, width_pct=0.01), spot, mins + 390)
        iv0, iv1 = atm_iv(chain, spot), atm_iv(chain_next, spot)
        ev = implied_event_move(iv0, mins / (390 * 252), iv1, mins / (390 * 252) + 1 / 252) if (iv0 and iv1) else None
        print(f"== ATM IV today {iv0} / next {iv1} -> sigma_event {ev}")
    except Exception as exc:
        print("== event vol n/a:", str(exc)[:120])
    try:
        cand = build_condor(chain, spot, "SPY", today, s.strategy, s.underlying_cfg("SPY"), now)
    except StrategyError as exc:
        print("== NO CANDIDATE:", exc)
        return
    print("== candidate", json.dumps(cand.summary(), indent=1))
    print("   ", cand.rationale)
    iv_ann = straddle_implied_vol_annualized(cand.implied_move, spot, mins)
    print(f"== straddle-implied vol {iv_ann:.3f} vs realised {rv}; ratio {(iv_ann / rv) if (iv_ann and rv) else None}")
    mult = regime_multiplier(ts["vix"] / ts["vix3m"], 0.95, 1.0) if ts else 0.0
    thr = cboe.vix1d_top_tercile_threshold(60)
    half = ts and ts.get("vix1d") and thr and ts["vix1d"] >= thr
    print(f"== regime multiplier {mult} (VIX/VIX3M {ts['vix'] / ts['vix3m']:.3f}); VIX1D {ts.get('vix1d')} vs top-tercile {thr} -> half size {bool(half)}")
    if half:
        mult *= 0.5
    budget = Budget(s.capital, s.session_budget, s.campaign_budget, 0.0, 0.0, mult)
    qty = contracts_for(budget, cand.max_loss_per_package, float(s.risk["max_order_max_loss_usd"]),
                        min(int(s.risk["max_contracts_per_order"]), int(s.strategy["sizing"]["contracts_per_position_max"])),
                        pilot_first_order=True, positions_planned=3)
    qty_full = contracts_for(budget, cand.max_loss_per_package, float(s.risk["max_order_max_loss_usd"]),
                             min(int(s.risk["max_contracts_per_order"]), int(s.strategy["sizing"]["contracts_per_position_max"])),
                             pilot_first_order=False, positions_planned=3)
    cand.contracts = qty_full or 1
    print(f"== sizing: pilot {qty}, full {qty_full} contracts; session budget {budget.session_budget:.0f}; max loss/package {cand.max_loss_per_package:.0f}")
    tick = package_tick(cand.legs)
    print("== ladder", walk_prices_ticks(cand.credit_mid, cand.credit_natural, tick, [0, 1, 2], True), "tick", tick)
    flags = flags_for(s.calendar, now)
    regime = None
    if "--no-llm" not in sys.argv:
        heads = d.headlines(["SPY", "QQQ"], hours=18, limit=25)
        prompt = regime_mod.build_user_prompt(now, None if not ts else type("S", (), {
            "vix": ts["vix"], "vix3m": ts["vix3m"], "vix1d": ts["vix1d"], "slope": ts["vix"] / ts["vix3m"],
            "realized_vol_annualized": rv})(), flags, upcoming_for_prompt(s.calendar, now), heads,
            (closes[-1] / closes[0] - 1) if len(closes) > 1 else None, cand.implied_move / spot,
            (iv_ann / rv) if (iv_ann and rv) else None)
        print("== prompt (first 1200 chars)\n" + prompt[:1200] + "\n...")
        regime, meta = regime_mod.classify_regime_votes(FeatherlessProvider(s.featherless_key, s.model_strong), prompt,
                                                        int(s.strategy["regime"]["llm_votes"]))
        print("== regime", {k: (v.value if hasattr(v, "value") else v) for k, v in regime.__dict__.items()
                            if k in ("vol_regime", "trend", "event_risk", "strategy_family", "veto", "veto_reason")} if regime else None)
        print("   rationale:", regime.rationale if regime else None)
        print("   votes:", meta.get("distribution"), "entropy:", meta.get("entropy_bits"), "latency total ms:",
              sum(c.get("latency_ms", 0) for c in meta.get("calls", [])))
    eng = GateEngine(s.risk, s.strategy, s.calendar, ROOT)
    acct = d.account()
    res = eng.pre_trade(cand, now=now, state=SessionState(session_date=today), book=[], flags=flags, regime=regime,
                        underlying_quote=q, buying_power=acct["options_buying_power"], campaign_loss=0.0,
                        book_greeks_usd={}, regime_multiplier=mult, decision_mid=spot)
    print("== gates at", now.astimezone(ET).strftime("%H:%M ET"))
    for g in res:
        print(f"   {'PASS' if g.passed else 'FAIL'} {g.name:28s} {g.reason}")
    print("== ALL PASSED" if all(g.passed for g in res) else "== REJECTED by " + ", ".join(g.name for g in res if not g.passed))


if __name__ == "__main__":
    main()

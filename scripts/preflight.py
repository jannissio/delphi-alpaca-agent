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

from agent.core import conformal as conf_mod  # noqa: E402
from agent.core.bs import enrich_greeks  # noqa: E402
from agent.core.clock import ET, at_et, market_minutes_remaining, now_et  # noqa: E402
from agent.core.config import ROOT, Settings  # noqa: E402
from agent.core.models import SessionState  # noqa: E402
from agent.core.sizing import Budget, contracts_for, regime_multiplier  # noqa: E402
from agent.core.strategy import (StrategyError, atm_iv, build_condor, implied_event_move, package_tick,  # noqa: E402
                                 realized_vol_annualized, straddle_implied_vol_annualized, wing_width_for)
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
    # Conformal Condor: today's interval (not committed to disk: the agent does that at its first evaluation)
    cp = conf_mod.ConformalParams.from_config(s.strategy.get("conformal"))
    sess, st = None, None
    if cp.enabled:
        try:
            st = conf_mod.ConformalState.load(ROOT / "state" / "conformal.json")
            if st.session and st.session.get("date") == today.isoformat():
                sess = st.session
                print("== conformal interval committed earlier today:", json.dumps(sess))
            else:
                vix_prev = cboe.closes_before("VIX", today, 1)[-1]
                wing = wing_width_for(spot, s.strategy["structure"], float(s.underlying_cfg("SPY")["strike_increment"]))
                sess = conf_mod.open_session(st, cp, today, now, spot, vix_prev, wing_usd=wing)
            print(f"== conformal interval ({sess['rule']}): n {sess['n']}, VIX prev {sess['vix_prev']}, implied ref move "
                  f"{sess['impl_ref_usd']:.2f} $ ({sess['impl_ref_pct']:.3f} %), wing {sess['wing_usd']:.0f} $ -> omega {sess['omega']:.3f}; "
                  f"risk track beta* {sess['beta_star']} -> k_crc_fixed {sess['k_crc_fixed']:.3f}, beta_t {sess['beta_t']:.4f} -> "
                  f"k_crc_adaptive {sess['k_crc_adaptive']:.3f}, used k_crc {sess['k_crc']:.3f}; "
                  f"coverage track alpha_t {sess['alpha_t']:.4f} -> k_cov {sess['k_cov']:.3f}; chosen k {sess['k']:.3f} "
                  f"(clipped {sess['clipped']}) -> short distance {sess['k'] * sess['impl_ref_usd']:.2f} $; state through {st.updated_through}")
        except Exception as exc:
            print("== CONFORMAL STATE UNAVAILABLE (the agent would log NO_TRADE):", str(exc)[:200])
    short_distance = sess["k"] * sess["impl_ref_usd"] if sess else None
    try:
        cand = build_condor(chain, spot, "SPY", today, s.strategy, s.underlying_cfg("SPY"), now, short_distance=short_distance)
    except StrategyError as exc:
        print("== NO CANDIDATE:", exc)
        return
    print("== candidate", json.dumps(cand.summary(), indent=1))
    print("   ", cand.rationale)
    if sess is not None:
        led = conf_mod.ledger_for_candidate(cand, st, cp, sess)
        cand.extras["conformal"] = led
        k = led["kelly"]
        print(f"== P vs Q ({led['rule']}): credit/wing {led['q_mid']:.3f} (call {led['q_call']:.3f}, put {led['q_put']:.3f}) vs certified payout "
              f"beta* {led['beta_certified']} (empirical {led['beta_empirical']:.3f}) at k_eff {led['k_effective']:.3f} (certified_ok {led['certified_ok']}); "
              f"gap_crc {led['gap_crc']:+.3f}, gap_empirical {led['gap_empirical']:+.3f}, "
              f"gap_cov {led['gap_cov']:+.3f} (P_mid {led['p_mid']:.3f}); gate gap {led['gap']:+.3f} vs margin {led['margin']} -> "
              f"{'TRADE' if led['passes'] else 'NO_TRADE'}; EV lower bound {led['ev_lower_bound_usd_per_package']} $/package, "
              f"empirical EV {led['ev_empirical_usd_per_package']:+.1f} $/package")
        print(f"   P_short {led['p_short']:.3f} (alpha_t {led['alpha_t']:.3f}, k_eff {led['k_effective']:.3f}), strict gap {led['strict_gap']:+.3f}; "
              f"EV digital {led['ev_digital_usd_per_package']:+.1f} $/package, EV hist {led['ev_hist_usd_per_package']}; "
              f"break-even p_inside {led['break_even_p_inside']}; deltas {led['delta_short_call']}/{led['delta_short_put']}")
        print(f"   Kelly exhibit: b {k['b']:.3f}, f* two-state {k['f_two_state']:+.3f}, three-state {k['f_three_state']:+.3f}, "
              f"shrunk {k['f_shrunk']:.3f}, used {k['f_used']:.3f} ({k['binding_constraint']}); warnings {led['warnings']}")
        try:
            fixed = build_condor(chain, spot, "SPY", today, s.strategy, s.underlying_cfg("SPY"), now)
            fl = conf_mod.ledger_for_candidate(fixed, st, cp, sess)
            fs = fixed.summary()
            print(f"== counterfactual fixed rule: shorts {fs['short_put']}/{fs['short_call']} credit {fs['credit_mid']} "
                  f"Q_mid {fl['q_mid']:.3f} P_mid {fl['p_mid']:.3f} gap {fl['gap']:+.3f} -> {'TRADE' if fl['passes'] else 'NO_TRADE'}")
        except StrategyError as exc:
            print("== counterfactual fixed rule: no candidate:", str(exc)[:160])
    iv_ann = straddle_implied_vol_annualized(cand.implied_move, spot, mins)
    print(f"== straddle-implied vol {iv_ann:.3f} vs realised {rv}; ratio {(iv_ann / rv) if (iv_ann and rv) else None}")
    mult = regime_multiplier(ts["vix"] / ts["vix3m"], 0.95, 1.0) if ts else 0.0
    thr = cboe.vix1d_top_tercile_threshold(60)
    half = ts and ts.get("vix1d") and thr and ts["vix1d"] >= thr
    print(f"== regime multiplier {mult} (VIX/VIX3M {ts['vix'] / ts['vix3m']:.3f}); VIX1D {ts.get('vix1d')} vs top-tercile {thr} -> half size {bool(half)}")
    if half:
        mult *= 0.5
    rm_path = ROOT / "config" / "regime_model.json"
    if rm_path.exists():
        from agent.core.regime_model import RegimeModel
        rm = RegimeModel(rm_path)
        bars = d.daily_bars("SPY", 5)
        open_today = bars[-1]["open"] if bars and bars[-1]["ts"].astimezone(ET).date() == today else None
        prev_close = bars[-2]["close"] if (open_today is not None and len(bars) >= 2) else (bars[-1]["close"] if bars else None)
        feats = rm.market_features(cboe.recent_closes("SPX", 30), cboe.recent_closes("VIX", 5), cboe.recent_closes("VIX3M", 5), prev_close, open_today)
        feats.update(rm.calendar_flags(today))
        out = rm.predict(feats)
        print(f"== regime model {out.name}: p_inside {out.p_inside:.3f} -> multiplier {out.multiplier} ({out.reason})")
        print("   features", {k: round(v, 4) for k, v in out.features.items()})
        mult *= out.multiplier
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

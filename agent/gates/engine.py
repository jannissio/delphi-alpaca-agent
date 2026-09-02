"""The 30 risk gates (research/C_risk_management_evaluation.md, section 8) plus gate 31, the coverage
gate of the Conformal Condor (research/G_conformal_condor.md).

Pre-trade gates run on every candidate order and every gate must pass. Each gate is a
small pure function returning a GateResult so the audit log shows the value, the limit
and the reason for every accept and reject. Gates 19-22 (kill switch, daily loss kill,
reconciliation) also run on every loop cycle independent of any candidate. Gates 23-30
are process controls documented in docs/ and enforced by the audit log and review.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Mapping, Optional

from agent.core.clock import ET, at_et, age_seconds, is_friday, to_et
from agent.core.models import (BookPosition, CondorCandidate, GateResult, RegimeDecision,
                               SessionState, Side, StrategyFamily, UnderlyingQuote)
from agent.core.strategy import spread_in_ticks
from agent.data.calendar import EventFlags, ex_dividend_block


def _ok(name: str, reason: str, value=None, limit=None) -> GateResult:
    return GateResult(name, True, reason, value, limit)


def _no(name: str, reason: str, value=None, limit=None) -> GateResult:
    return GateResult(name, False, reason, value, limit)


class GateEngine:
    def __init__(self, risk: Mapping, strategy: Mapping, calendar: Mapping, root: Path):
        self.r = risk
        self.s = strategy
        self.cal = calendar
        self.root = root
        self.capital = float(risk["capital_base_usd"])

    # ------------------------------------------------------------------ cycle-level gates
    def kill_switch_engaged(self) -> bool:
        """Gate 19: a file flag the loop checks every cycle (< 5 s latency)."""
        return (self.root / self.r["kill_switch_file"]).exists()

    def daily_loss_kill(self, session_pnl: float) -> GateResult:
        """Gate 20: independent code path from gate 1; halts all new risk."""
        limit = float(self.r["daily_loss_kill_usd"])
        if -session_pnl >= limit:
            return _no("gate_daily_loss_kill", f"session loss {session_pnl:.0f} breached kill level", session_pnl, -limit)
        return _ok("gate_daily_loss_kill", "within daily loss limit", session_pnl, -limit)

    # ------------------------------------------------------------------ pre-trade gates
    def pre_trade(self, cand: CondorCandidate, *, now: datetime, state: SessionState,
                  book: list[BookPosition], flags: EventFlags, regime: Optional[RegimeDecision],
                  underlying_quote: UnderlyingQuote, buying_power: float,
                  campaign_loss: float, book_greeks_usd: dict, regime_multiplier: float,
                  decision_mid: float) -> list[GateResult]:
        r, s = self.r, self.s
        now_et = to_et(now)
        today = now_et.date()
        out: list[GateResult] = []

        # 1 gate_capital_threshold
        session_budget = self.capital * float(r["session_budget_pct"])
        campaign_budget = self.capital * float(r["campaign_budget_pct"])
        taper = max(campaign_budget - max(campaign_loss, 0.0), 0.0) / campaign_budget
        budget_today = session_budget * taper * regime_multiplier
        committed_after = state.risk_committed + cand.max_loss_total
        out.append(_ok("gate_capital_threshold", "session risk within budget", committed_after, budget_today)
                   if committed_after <= budget_today + 1e-6 else
                   _no("gate_capital_threshold", "order would exceed the session max-loss budget", committed_after, budget_today))

        # 2 gate_cumulative_drawdown
        out.append(_ok("gate_cumulative_drawdown", "campaign drawdown within budget", campaign_loss, campaign_budget)
                   if campaign_loss < campaign_budget else
                   _no("gate_cumulative_drawdown", "campaign max-loss budget exhausted", campaign_loss, campaign_budget))

        # 3 gate_drawdown_taper (informational pass; the taper is applied in gate 1 and sizing)
        out.append(_ok("gate_drawdown_taper", f"taper factor {taper:.2f} x regime {regime_multiplier:.2f}", taper, 1.0))

        # 4 gate_defined_risk_only
        shorts = [l for l in cand.legs if l.side == Side.SELL]
        covered = all(any(b.side == Side.BUY and b.quote.right == sh.quote.right and b.ratio >= sh.ratio
                          and b.quote.expiry == sh.quote.expiry for b in cand.legs) for sh in shorts)
        out.append(_ok("gate_defined_risk_only", "every short leg has a bought wing in the same package")
                   if covered and bool(r["defined_risk_only"]) else
                   _no("gate_defined_risk_only", "uncovered short leg"))

        # 5 gate_price_collar: leg spreads in ticks (F1: percent collars veto every 0DTE contract)
        max_ticks = float(r["max_leg_spread_ticks"])
        max_wing_ticks = float(self.s["execution"].get("max_wing_spread_ticks", max_ticks))
        wide = [f"{l.quote.symbol}:{spread_in_ticks(l.quote):.0f}t" for l in cand.legs
                if spread_in_ticks(l.quote) > (max_ticks if l.side == Side.SELL else max_wing_ticks)]
        out.append(_no("gate_price_collar", f"leg quoted wider than {max_ticks:.0f}/{max_wing_ticks:.0f} ticks (short/wing): {wide}", None, max_ticks)
                   if wide else _ok("gate_price_collar", f"shorts within {max_ticks:.0f} ticks, wings within {max_wing_ticks:.0f}", None, max_ticks))
        max_cost = float(r["max_roundtrip_cost_pct_of_credit"])
        rt_cost = 2.0 * (cand.credit_mid - cand.credit_natural)
        ratio = rt_cost / cand.credit_mid if cand.credit_mid > 0 else float("inf")
        out.append(_ok("gate_cost_model", f"modelled round-trip cost {ratio:.0%} of credit", ratio, max_cost)
                   if ratio <= max_cost else
                   _no("gate_cost_model", f"modelled round-trip cost {ratio:.0%} of credit exceeds limit", ratio, max_cost))

        # 6 gate_max_order_value
        lim = float(r["max_order_max_loss_usd"])
        out.append(_ok("gate_max_order_value", "order max loss within cap", cand.max_loss_total, lim)
                   if cand.max_loss_total <= lim else
                   _no("gate_max_order_value", "order max loss above per-order cap", cand.max_loss_total, lim))

        # 7 gate_max_order_volume
        lim = int(r["max_contracts_per_order"])
        total_contracts = cand.contracts * max(cand.short_call.ratio, cand.short_put.ratio)
        out.append(_ok("gate_max_order_volume", "contract count within cap", total_contracts, lim)
                   if 1 <= total_contracts <= lim else
                   _no("gate_max_order_volume", "contract count outside 1..cap", total_contracts, lim))

        # 8 gate_message_rate
        recent = [t for t in state.order_timestamps if (now - t).total_seconds() < 60]
        lim_min, lim_sess = int(r["max_orders_per_minute"]), int(r["max_orders_per_session"])
        out.append(_no("gate_message_rate", "order rate limit", len(recent), lim_min)
                   if len(recent) >= lim_min or state.orders_sent >= lim_sess else
                   _ok("gate_message_rate", "order rate within limits", len(recent), lim_min))

        # 9 gate_execution_throttle
        lim = int(r["max_fills_per_session"])
        out.append(_ok("gate_execution_throttle", "fills within throttle", state.fills, lim)
                   if state.fills < lim and not state.halted else
                   _no("gate_execution_throttle", state.halt_reason or "fill throttle reached", state.fills, lim))

        # 10 gate_duplicate_order
        key = self.dedupe_key(cand)
        win = int(r["duplicate_order_window_s"])
        last = state.recent_order_keys.get(key)
        out.append(_no("gate_duplicate_order", f"same package sent {int((now - last).total_seconds())}s ago", None, win)
                   if last and (now - last).total_seconds() < win else
                   _ok("gate_duplicate_order", "no duplicate in window", None, win))

        # 11 gate_erroneous_price: stale, crossed, zero-bid, drift since decision
        max_age = float(r["max_quote_age_s"])
        stale = [l.quote.symbol for l in cand.legs if age_seconds(l.quote.quote_ts, now) > max_age]
        bad = [l.quote.symbol for l in cand.legs if not l.quote.is_quotable]
        drift = abs(underlying_quote.mid - decision_mid) / decision_mid if decision_mid else 0.0
        max_drift = float(r["max_mid_drift_pct_since_decision"])
        if bad:
            out.append(_no("gate_erroneous_price", f"crossed/zero quotes: {bad}"))
        elif stale:
            out.append(_no("gate_erroneous_price", f"quotes older than {max_age:.0f}s: {stale}", None, max_age))
        elif drift > max_drift:
            out.append(_no("gate_erroneous_price", "underlying moved since decision", drift, max_drift))
        else:
            out.append(_ok("gate_erroneous_price", "quotes fresh, two-sided, no drift", drift, max_drift))

        # 12 gate_greeks_budget (post-trade book)
        spot = cand.spot
        d_usd = book_greeks_usd.get("delta", 0.0) + cand.net_delta * spot * 100 * cand.contracts
        g_usd = book_greeks_usd.get("gamma", 0.0) + 0.5 * cand.net_gamma * (spot * 0.01) ** 2 * 100 * cand.contracts
        v_usd = book_greeks_usd.get("vega", 0.0) + cand.net_vega * 100 * cand.contracts
        limits = (float(r["max_abs_delta_usd"]), float(r["max_abs_gamma_usd_per_1pct"]), float(r["max_abs_vega_usd_per_volpt"]))
        breaches = []
        if abs(d_usd) > limits[0]:
            breaches.append(f"delta$ {d_usd:.0f} > {limits[0]:.0f}")
        if abs(g_usd) > limits[1]:
            breaches.append(f"gamma$ {g_usd:.0f} > {limits[1]:.0f}")
        if abs(v_usd) > limits[2]:
            breaches.append(f"vega$ {v_usd:.0f} > {limits[2]:.0f}")
        out.append(_no("gate_greeks_budget", "; ".join(breaches)) if breaches else
                   _ok("gate_greeks_budget", f"delta$ {d_usd:.0f} gamma$ {g_usd:.0f} vega$ {v_usd:.0f}"))

        # 13 gate_buying_power
        need = cand.max_loss_total * float(r["buying_power_safety_multiple"])
        out.append(_ok("gate_buying_power", "buying power covers max loss x safety", buying_power, need)
                   if buying_power >= need else
                   _no("gate_buying_power", "insufficient buying power for max loss x safety", buying_power, need))

        # 14 gate_time_window: global bounds + per-day entry windows + pauses + Friday rule
        windows = self.s["entry_windows_et"].get(today.isoformat(), ())
        lo, hi = r["no_new_risk_before_et"], (r["friday_no_new_risk_after_et"] if is_friday(today) else r["no_new_risk_after_et"])
        hi = min(hi, self.s.get("no_new_entry_after_et", hi))
        in_global = at_et(today, lo) <= now_et < at_et(today, hi)
        in_entry = any(at_et(today, w[0]) <= now_et < at_et(today, w[1]) for w in windows)
        if not in_global:
            out.append(_no("gate_time_window", f"outside global window {lo}-{hi} ET"))
        elif not windows:
            out.append(_no("gate_time_window", f"no entry window configured for {today} (NO_TRADE day)"))
        elif not in_entry:
            out.append(_no("gate_time_window", f"outside entry windows {list(map(list, windows))}"))
        elif flags.in_pause_window:
            out.append(_no("gate_time_window", flags.pause_reason))
        else:
            out.append(_ok("gate_time_window", f"inside entry window at {now_et.strftime('%H:%M')} ET"))

        # 15 gate_flatten_deadline: never open within 45 min of the flatten deadline
        deadline = r["friday_flatten_deadline_et"] if is_friday(today) else r["flatten_deadline_et"]
        mins_to_flat = (at_et(today, deadline) - now_et).total_seconds() / 60.0
        out.append(_ok("gate_flatten_deadline", f"{mins_to_flat:.0f} min to flatten deadline", mins_to_flat, 45)
                   if mins_to_flat >= 45 else
                   _no("gate_flatten_deadline", "too close to the flatten deadline to open", mins_to_flat, 45))

        # 16 gate_assignment_watch
        blocked = ex_dividend_block(self.cal, cand.underlying, today, int(r["ex_dividend_block_sessions"]))
        out.append(_no("gate_assignment_watch", "ex-dividend within block window") if blocked else
                   _ok("gate_assignment_watch", "no ex-dividend in window"))

        # 17 gate_event_veto: deterministic event flags + LLM veto (one direction only)
        if flags.no_trade_day:
            out.append(_no("gate_event_veto", "scheduled major release makes today a NO_TRADE day"))
        elif flags.next_major_minutes is not None and flags.next_major_minutes < 45:
            out.append(_no("gate_event_veto", f"major scheduled event in {flags.next_major_minutes:.0f} min"))
        elif regime is not None and regime.veto:
            out.append(_no("gate_event_veto", f"LLM veto: {regime.veto_reason}"))
        elif regime is not None and regime.strategy_family == StrategyFamily.NO_TRADE:
            out.append(_no("gate_event_veto", f"LLM chose NO_TRADE: {regime.rationale[:120]}"))
        else:
            out.append(_ok("gate_event_veto", "no event veto"))

        # 18 gate_llm_output_schema: a missing or invalid regime decision means no new risk
        out.append(_ok("gate_llm_output_schema", f"validated enums from {regime.model}") if regime is not None else
                   _no("gate_llm_output_schema", "no schema-valid LLM regime decision available"))

        # positions per session cap (strategy.yaml sizing)
        cap = int(self.s["sizing"]["positions_per_session_max"])
        out.append(_ok("gate_positions_per_session", "position count within cap", state.positions_opened, cap)
                   if state.positions_opened < cap else
                   _no("gate_positions_per_session", "positions-per-session cap reached", state.positions_opened, cap))

        # 31 gate_coverage (Conformal Condor): the market must pay more for the interval than the
        # calibration says it is worth, by a pre-registered margin. Q is read off the quote
        # (credit / wing, Breeden-Litzenberger digital limit); P is the conformal p-value of the same
        # distance in the calibration scores. Both numbers are in the audit record.
        ccfg = self.s.get("conformal") or {}
        if ccfg.get("enabled", False):
            led = cand.extras.get("conformal") if hasattr(cand, "extras") else None
            margin = float(ccfg.get("margin", 0.05))
            if not led:
                out.append(_no("gate_coverage", "conformal ledger missing for this candidate", None, margin))
            elif any("non-positive" in w for w in led.get("warnings", [])):
                out.append(_no("gate_coverage", "; ".join(led["warnings"])[:200], round(led["gap"], 4), margin))
            elif led["gap"] >= margin - 1e-12:
                out.append(_ok("gate_coverage", f"Q_mid {led['q_mid']:.3f} - P_mid {led['p_mid']:.3f} = "
                                                f"{led['gap']:+.3f} >= margin {margin:.2f}", round(led["gap"], 4), margin))
            else:
                out.append(_no("gate_coverage", f"Q_mid {led['q_mid']:.3f} - P_mid {led['p_mid']:.3f} = "
                                                f"{led['gap']:+.3f} < margin {margin:.2f}: the market does not pay "
                                                f"for this interval", round(led["gap"], 4), margin))
        else:
            out.append(_ok("gate_coverage", "coverage gate disabled (fixed strike rule)"))
        return out

    @staticmethod
    def dedupe_key(cand: CondorCandidate) -> str:
        legs = "|".join(f"{l.quote.symbol}:{l.side.value}:{l.ratio}" for l in cand.legs)
        return f"{cand.underlying}:{legs}:{cand.contracts}"

    @staticmethod
    def all_passed(results: list[GateResult]) -> bool:
        return all(g.passed for g in results)

    @staticmethod
    def failures(results: list[GateResult]) -> list[GateResult]:
        return [g for g in results if not g.passed]

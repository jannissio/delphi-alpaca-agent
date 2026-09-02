"""The agent loop. Run: python -m agent.main  (AGENT_DRY_RUN=true logs orders without sending).

Cycle (every ~20 s while the market is open):
  kill switch -> reconcile -> mark book -> daily loss kill -> flatten deadline / take-profit
  -> regime data (Cboe) -> LLM regime enums (k votes, cached) -> candidate (code) -> sizing (code)
  -> risk gates (code) -> critic (LLM, veto/reduce only) -> package limit-order walker -> book + journal.
Every step writes to the append-only audit log.
"""
from __future__ import annotations

import logging
import signal
import sys
import time
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from agent.core.clock import at_et, is_friday, market_minutes_remaining, now_et, to_et
from agent.core.config import ROOT, STATE_DIR, Settings
from agent.core.models import (BookPosition, CondorCandidate, CriticVerdict, OptionQuote, RegimeDecision,
                               RegimeSnapshot, SessionState, StrategyFamily)
from agent.core.sizing import Budget, contracts_for, regime_multiplier
from agent.core.strategy import (StrategyError, atm_iv, build_condor, implied_event_move, package_tick,
                                 realized_vol_annualized, straddle_implied_vol_annualized)
from agent.data import cboe
from agent.data.alpaca_data import AlpacaData
from agent.data.calendar import flags_for, upcoming_for_prompt
from agent.execution.flatten import flatten_position, kill_all, take_profit_hit
from agent.execution.orders import OrderWalker, build_open_legs, walk_prices_ticks
from agent.execution.recon import reconcile_orders, reconcile_positions
from agent.gates.engine import GateEngine
from agent.llm import critic as critic_mod
from agent.llm import regime as regime_mod
from agent.llm.journal import Journal
from agent.llm.provider import FeatherlessProvider
from agent.reporting.audit import AuditLog, JsonState

log = logging.getLogger("agent")


class Agent:
    def __init__(self, settings: Optional[Settings] = None):
        self.s = settings or Settings()
        self.s.require_alpaca()
        today = now_et().date()
        self.session_tag = today.isoformat()
        self.audit = AuditLog(STATE_DIR / "audit.jsonl", self.s.git_hash, self.s.config_hash, self.session_tag)
        self.data = AlpacaData(self.s.alpaca_key, self.s.alpaca_secret, paper=self.s.alpaca_paper)
        self.gates = GateEngine(self.s.risk, self.s.strategy, self.s.calendar, ROOT)
        self.strong = FeatherlessProvider(self.s.featherless_key, self.s.model_strong)
        self.cheap = FeatherlessProvider(self.s.featherless_key, self.s.model_cheap)
        self.journal = Journal(STATE_DIR / "journal.jsonl", self.cheap)
        ex = self.s.strategy["execution"]
        self.walker = OrderWalker(self.data.trading, self.audit, float(ex["walk_step_interval_s"]),
                                  float(ex["cancel_after_s"]), dry_run=self.s.dry_run)
        self.book_store = JsonState(STATE_DIR / "book.json")
        self.session_store = JsonState(STATE_DIR / f"session_{self.session_tag}.json")
        self.book: list[BookPosition] = [self._pos_from_dict(p) for p in self.book_store.load([])]
        self.state = self._load_session(today)
        self.sent_order_ids: set[str] = set(self.session_store.load({}).get("sent_order_ids", []))
        self._regime_cache: Optional[tuple[datetime, Optional[RegimeDecision], dict]] = None
        self._snap_cache: Optional[tuple[datetime, Optional[RegimeSnapshot]]] = None
        self._vix1d_threshold: Optional[float] = None
        self._vix1d_threshold_ts: Optional[datetime] = None
        self._last_heartbeat = datetime.min.replace(tzinfo=timezone.utc)
        self._last_event_vol_ts = datetime.min.replace(tzinfo=timezone.utc)
        self._flattened_today = False
        self._stop = False
        self.audit.write("agent_start", settings=self.s.describe(),
                         book_open=len([p for p in self.book if p.status != "closed"]))

    # ------------------------------------------------------------------ persistence
    @staticmethod
    def _pos_from_dict(d: dict) -> BookPosition:
        d = dict(d)
        d["expiry"] = date.fromisoformat(d["expiry"])
        d["opened_ts"] = datetime.fromisoformat(d["opened_ts"])
        d["closed_ts"] = datetime.fromisoformat(d["closed_ts"]) if d.get("closed_ts") else None
        return BookPosition(**d)

    def _load_session(self, today: date) -> SessionState:
        raw = self.session_store.load({})
        st = SessionState(session_date=today)
        if raw.get("session_date") == today.isoformat():
            for k in ("orders_sent", "fills", "realized_pnl", "risk_committed", "halted", "halt_reason", "positions_opened"):
                if k in raw:
                    setattr(st, k, raw[k])
        return st

    def _persist(self) -> None:
        self.book_store.save([p.to_dict() for p in self.book])
        self.session_store.save({
            "session_date": self.state.session_date.isoformat(), "orders_sent": self.state.orders_sent,
            "fills": self.state.fills, "realized_pnl": self.state.realized_pnl,
            "risk_committed": self.state.risk_committed, "halted": self.state.halted,
            "halt_reason": self.state.halt_reason, "positions_opened": self.state.positions_opened,
            "sent_order_ids": sorted(self.sent_order_ids),
        })

    # ------------------------------------------------------------------ helpers
    def open_positions(self) -> list[BookPosition]:
        return [p for p in self.book if p.status != "closed"]

    def _leg_quotes(self, positions: list[BookPosition]) -> dict[str, OptionQuote]:
        syms = sorted({l["symbol"] for p in positions for l in p.legs})
        return self.data.snapshots(syms) if syms else {}

    def _mark(self, quotes: dict[str, OptionQuote]) -> tuple[float, dict]:
        """Unrealised P&L of open packages at mid and the book Greeks in $ terms (per 1 pt / per vol pt)."""
        unreal = 0.0
        greeks = {"delta": 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0}
        for p in self.open_positions():
            close_mid = 0.0
            for l in p.legs:
                q = quotes.get(l["symbol"])
                if q is None:
                    continue
                r = int(l["ratio"])
                sign = -1 if l["side"] == "sell" else 1
                close_mid += (q.mid if l["side"] == "sell" else -q.mid) * r
                greeks["delta"] += sign * (q.delta or 0) * 100 * p.contracts * r
                greeks["gamma"] += sign * (q.gamma or 0) * 100 * p.contracts * r
                greeks["vega"] += sign * (q.vega or 0) * 100 * p.contracts * r
                greeks["theta"] += sign * (q.theta or 0) * 100 * p.contracts * r
            unreal += (p.entry_credit - close_mid) * 100 * p.contracts
        return unreal, greeks

    def _campaign_pnl(self, unreal: float) -> float:
        realized = sum((p.entry_credit - (p.exit_debit or 0.0)) * 100 * p.contracts
                       for p in self.book if p.status == "closed")
        return realized + unreal

    def _snapshot(self, now: datetime, spot_closes: list[float]) -> Optional[RegimeSnapshot]:
        if self._snap_cache and (now - self._snap_cache[0]).total_seconds() < 300:
            return self._snap_cache[1]
        ts = cboe.fetch_term_structure()
        snap = None
        if ts:
            snap = RegimeSnapshot(ts=now, vix=ts["vix"], vix3m=ts["vix3m"], vix1d=ts["vix1d"],
                                  realized_vol_annualized=realized_vol_annualized(spot_closes), source=ts["source"])
        self._snap_cache = (now, snap)
        self.audit.write("regime_snapshot", snapshot=snap.__dict__ if snap else None)
        return snap

    def _vix1d_half_size(self, snap: RegimeSnapshot, now: datetime) -> bool:
        """F1 E-V12: half size when the 1-day implied variance sits in its trailing top tercile."""
        if not self.s.strategy["sizing"].get("half_size_if_vix1d_top_tercile") or snap.vix1d is None:
            return False
        if self._vix1d_threshold_ts is None or (now - self._vix1d_threshold_ts).total_seconds() > 3600:
            self._vix1d_threshold = cboe.vix1d_top_tercile_threshold(int(self.s.strategy["sizing"]["vix1d_tercile_lookback_sessions"]))
            self._vix1d_threshold_ts = now
            self.audit.write("vix1d_tercile", threshold=self._vix1d_threshold, current=snap.vix1d)
        return self._vix1d_threshold is not None and snap.vix1d >= self._vix1d_threshold

    def _regime(self, now: datetime, snap, flags, spot_change, implied_move_pct, iv_rv) -> Optional[RegimeDecision]:
        cache_s = float(self.s.strategy["regime"].get("llm_cache_s", 600))
        if self._regime_cache and (now - self._regime_cache[0]).total_seconds() < cache_s:
            return self._regime_cache[1]
        heads = self.data.headlines(["SPY", "QQQ"], hours=18, limit=25)
        prompt = regime_mod.build_user_prompt(now, snap, flags, upcoming_for_prompt(self.s.calendar, now), heads,
                                              spot_change, implied_move_pct, iv_rv)
        k = int(self.s.strategy["regime"].get("llm_votes", 1))
        dec, meta = regime_mod.classify_regime_votes(self.strong, prompt, k)
        self._regime_cache = (now, dec, meta)
        self.audit.write("llm_regime", decision=dec.__dict__ if dec else None, meta=meta, prompt=prompt,
                         decision_hash=regime_mod.decision_hash(dec) if dec else None)
        if dec is not None:
            self.journal.write("short", {"event": "regime", "vol_regime": dec.vol_regime.value, "trend": dec.trend.value,
                                         "event_risk": dec.event_risk.value, "family": dec.strategy_family.value,
                                         "veto": dec.veto, "veto_reason": dec.veto_reason, "rationale": dec.rationale,
                                         "votes": meta.get("votes"), "unanimous": meta.get("unanimous"),
                                         "entropy_bits": meta.get("entropy_bits")})
        return dec

    def _log_event_vol(self, underlying: str, spot: float, chain_today: list[OptionQuote], today: date, now: datetime) -> None:
        """Dubinsky et al. Eq. 4 on SPY: the event variance priced between today's and the next expiry."""
        if (now - self._last_event_vol_ts).total_seconds() < 900:
            return
        self._last_event_vol_ts = now
        try:
            nxt = today + timedelta(days=1)
            while nxt.weekday() >= 5:
                nxt += timedelta(days=1)
            chain_next = self.data.chain(underlying, nxt, spot, width_pct=0.01)
            iv0, iv1 = atm_iv(chain_today, spot), atm_iv(chain_next, spot)
            mins = market_minutes_remaining(now)
            t0 = mins / (390.0 * 252.0)
            t1 = t0 + 1.0 / 252.0
            ev = implied_event_move(iv0, t0, iv1, t1) if (iv0 and iv1) else None
            self.audit.write("event_vol", underlying=underlying, expiry_short=today.isoformat(), expiry_long=nxt.isoformat(),
                             iv_short=iv0, iv_long=iv1, t_short_years=t0, t_long_years=t1,
                             sigma_event=ev, note="Dubinsky/Johannes/Kaeck/Seeger 2019 Eq. 4; None = term structure not downward sloping")
        except Exception as exc:
            self.audit.write("event_vol_error", error=str(exc)[:300])

    def _halt(self, reason: str) -> None:
        if not self.state.halted:
            self.state.halted = True
            self.state.halt_reason = reason
            self.audit.write("halt", reason=reason)
            self.journal.write("long", {"event": "halt", "reason": reason})
            self._persist()

    # ------------------------------------------------------------------ flatten
    def _flatten_all(self, reason: str) -> None:
        opens = self.open_positions()
        if not opens:
            return
        quotes = self._leg_quotes(opens)
        for p in opens:
            self._flatten_one(p, quotes, reason)

    def _flatten_one(self, p: BookPosition, quotes: dict[str, OptionQuote], reason: str) -> None:
        if any(l["symbol"] not in quotes for l in p.legs):
            self.audit.write("flatten_skipped_no_quotes", position_id=p.position_id)
            return
        p.status = "closing"
        fractions = [0.0, 0.5, 1.0]
        res = flatten_position(self.walker, p, quotes, float(self.s.risk["price_collar_pct_of_mid"]), fractions, reason,
                               on_order_sent=self._on_order_sent)
        if res["status"] in {"filled", "dry_run"}:
            p.status = "closed"
            p.closed_ts = datetime.now(tz=timezone.utc)
            p.exit_debit = float(res.get("avg_price") or res.get("last_price") or 0.0)
            pnl = (p.entry_credit - p.exit_debit) * 100 * p.contracts
            self.state.realized_pnl += pnl
            self.state.fills += 1
            self.audit.write("position_closed", position_id=p.position_id, reason=reason, exit_debit=p.exit_debit,
                             entry_credit=p.entry_credit, pnl=round(pnl, 2), contracts=p.contracts)
            self.journal.write("mid", {"event": "position_closed", "reason": reason, "entry_credit": p.entry_credit,
                                       "exit_debit": p.exit_debit, "pnl_usd": round(pnl, 2), "contracts": p.contracts,
                                       "minutes_held": round((p.closed_ts - p.opened_ts).total_seconds() / 60)})
        else:
            p.status = "open"
            self.audit.write("flatten_failed", position_id=p.position_id, result=res)
        self._persist()

    def _on_order_sent(self, order_id: str, price: float) -> None:
        self.sent_order_ids.add(order_id)
        self.state.orders_sent += 1
        self.state.order_timestamps.append(datetime.now(tz=timezone.utc))
        self._persist()

    # ------------------------------------------------------------------ one cycle
    def cycle(self) -> None:
        now = datetime.now(tz=timezone.utc)
        et = to_et(now)
        today = et.date()
        r = self.s.risk

        # gate 19: kill switch
        if self.gates.kill_switch_engaged():
            self.audit.write("kill_switch_seen")
            kill_all(self.data.trading, self.audit, "kill file present")
            self._flatten_all("kill switch")
            self._halt("kill switch file present")
            return

        clock = self.data.clock()
        if not clock["is_open"]:
            self._heartbeat("market closed", now)
            return

        # gates 21-22: reconciliation
        broker_pos = self.data.positions()
        ok_pos, problems = reconcile_positions(self.book, broker_pos)
        if not ok_pos:
            self.audit.write("recon_position_mismatch", problems=problems, broker=broker_pos)
            self._halt("position reconciliation mismatch: " + "; ".join(problems)[:300])
        try:
            ok_ord, missing = reconcile_orders(self.sent_order_ids, self.data.orders_today())
            if not ok_ord:
                self.audit.write("recon_order_mismatch", problems=missing)
                self._halt("order echo mismatch")
        except Exception as exc:
            self.audit.write("recon_order_error", error=str(exc)[:300])

        # mark the book
        opens = self.open_positions()
        quotes = self._leg_quotes(opens)
        unreal, book_greeks = self._mark(quotes)
        session_pnl = self.state.realized_pnl + unreal
        campaign_pnl = self._campaign_pnl(unreal)
        account = self.data.account()
        self.audit.write("mark", equity=account["equity"], session_pnl=round(session_pnl, 2),
                         campaign_pnl=round(campaign_pnl, 2), open_positions=len(opens), greeks=book_greeks)

        # gate 20: daily loss kill
        dlk = self.gates.daily_loss_kill(session_pnl)
        if not dlk.passed:
            self.audit.write("gate", **dlk.__dict__)
            self._flatten_all("daily loss kill")
            self._halt(dlk.reason)
            return

        # gate 15: flatten deadline
        deadline = r["friday_flatten_deadline_et"] if is_friday(today) else r["flatten_deadline_et"]
        if et >= at_et(today, deadline):
            if opens:
                self._flatten_all(f"flatten deadline {deadline} ET")
            if not self._flattened_today:
                self._flattened_today = True
                self.audit.write("flatten_deadline_reached", deadline=deadline)
            self._heartbeat("after flatten deadline", now)
            return

        # take profit
        tp = float(self.s.strategy["structure"]["take_profit_pct_of_credit"])
        for p in opens:
            if take_profit_hit(p, quotes, tp):
                self._flatten_one(p, quotes, f"take profit {tp:.0%} of credit")

        if self.state.halted:
            self._heartbeat(f"halted: {self.state.halt_reason}", now)
            return

        # entry windows: cheap deterministic pre-check before any data or LLM cost
        flags = flags_for(self.s.calendar, now)
        windows = self.s.entry_windows(today.isoformat())
        in_window = any(at_et(today, w[0]) <= et < at_et(today, w[1]) for w in windows)
        if flags.no_trade_day or not windows:
            self._heartbeat("NO_TRADE day by calendar (NFP / no windows configured)", now, kind="no_trade")
            return
        if not in_window or flags.in_pause_window:
            self._heartbeat("outside entry window" if not in_window else flags.pause_reason, now)
            return
        if self.state.positions_opened >= int(self.s.strategy["sizing"]["positions_per_session_max"]):
            self._heartbeat("positions-per-session cap reached", now)
            return

        # regime data
        underlying = self.s.enabled_underlyings()[0]
        closes: list[float] = []
        try:
            closes = self.data.intraday_closes(underlying, 5)
        except Exception as exc:
            log.warning("bars failed: %s", exc)
        snap = self._snapshot(now, closes)
        if snap is None:
            self.audit.write("no_trade", reason="volatility term structure unavailable")
            return
        mult = regime_multiplier(snap.slope, float(self.s.strategy["regime"]["vix_vix3m_full"]),
                                 float(self.s.strategy["regime"]["vix_vix3m_half"]))
        if mult == 0.0:
            self.audit.write("no_trade", reason=f"VIX/VIX3M {snap.slope:.3f} >= 1.00: inverted term structure")
            return
        if self._vix1d_half_size(snap, now):
            mult *= 0.5

        # candidate from the live chain
        uq = self.data.underlying_quote(underlying)
        spot = uq.mid
        spot_change = (closes[-1] / closes[0] - 1.0) if len(closes) >= 2 else None
        try:
            chain = self.data.chain(underlying, today, spot, width_pct=0.03)
        except Exception as exc:
            self.audit.write("no_trade", reason=f"chain fetch failed: {str(exc)[:200]}")
            return
        self._log_event_vol(underlying, spot, chain, today, now)
        try:
            cand = build_condor(chain, spot, underlying, today, self.s.strategy, self.s.underlying_cfg(underlying), now)
        except StrategyError as exc:
            self.audit.write("no_trade", reason=f"strategy: {exc}")
            return
        mins_left = market_minutes_remaining(now)
        iv_ann = straddle_implied_vol_annualized(cand.implied_move, spot, mins_left)
        iv_rv = (iv_ann / snap.realized_vol_annualized) if (iv_ann and snap.realized_vol_annualized) else None
        if iv_rv is not None and iv_rv < float(self.s.strategy["regime"]["iv_rv_min_ratio"]):
            self.audit.write("no_trade", reason=f"IV/RV {iv_rv:.2f} below 1.0: options cheap vs realised (D-R15)")
            return

        # LLM regime enums (k votes, unanimity)
        regime = self._regime(now, snap, flags, spot_change, cand.implied_move / spot, iv_rv)
        if regime is None:
            self.audit.write("no_trade", reason="LLM regime output failed schema validation; no new risk")
            return
        if regime.veto or regime.strategy_family == StrategyFamily.NO_TRADE:
            self.audit.write("no_trade", reason=f"LLM: family={regime.strategy_family.value} veto={regime.veto} {regime.veto_reason}")
            return
        if regime.strategy_family != StrategyFamily.IRON_CONDOR_0DTE:
            self.audit.write("no_trade", reason=f"LLM chose {regime.strategy_family.value}; only IRON_CONDOR_0DTE is enabled in this build")
            return

        # sizing
        campaign_loss = max(-campaign_pnl, 0.0)
        budget = Budget(self.s.capital, self.s.session_budget, self.s.campaign_budget, campaign_loss,
                        self.state.risk_committed, mult)
        pilot = (not self.book) and int(self.s.strategy["sizing"]["first_live_order_contracts"]) == 1
        max_qty = min(int(r["max_contracts_per_order"]), int(self.s.strategy["sizing"]["contracts_per_position_max"]))
        planned = max(1, int(self.s.strategy["sizing"]["positions_per_session_max"]) - self.state.positions_opened)
        qty = contracts_for(budget, cand.max_loss_per_package, float(r["max_order_max_loss_usd"]), max_qty, pilot,
                            positions_planned=planned)
        if qty <= 0:
            self.audit.write("no_trade", reason=f"budget remaining {budget.session_remaining:.0f} < one package max loss {cand.max_loss_per_package:.0f}")
            return
        cand.contracts = qty

        # gates
        results = self.gates.pre_trade(cand, now=now, state=self.state, book=self.book, flags=flags, regime=regime,
                                       underlying_quote=uq,
                                       buying_power=account["options_buying_power"] or account["buying_power"],
                                       campaign_loss=campaign_loss, book_greeks_usd=book_greeks, regime_multiplier=mult,
                                       decision_mid=spot)
        self.audit.write("gates", candidate=cand.summary(), results=[g.__dict__ for g in results],
                         passed=self.gates.all_passed(results))
        if not self.gates.all_passed(results):
            self.audit.write("no_trade", reason="gate reject: " + "; ".join(f"{g.name}: {g.reason}" for g in self.gates.failures(results)))
            return

        # critic
        cprompt = critic_mod.build_user_prompt(cand, regime, results,
                                               {"open_positions": len(opens), "session_pnl": round(session_pnl, 2)})
        cdec, cmeta = critic_mod.critique(self.strong, cprompt)
        self.audit.write("llm_critic", decision=cdec.__dict__, meta=cmeta, prompt=cprompt)
        if cdec.verdict == CriticVerdict.BLOCK:
            self.audit.write("no_trade", reason=f"critic BLOCK: {cdec.reason}")
            self.journal.write("short", {"event": "critic_block", "reason": cdec.reason})
            return
        if cdec.verdict == CriticVerdict.REDUCE and cand.contracts > 1:
            cand.contracts = max(1, cand.contracts // 2)
            self.audit.write("critic_reduce", new_contracts=cand.contracts, reason=cdec.reason)

        self._execute(cand, regime, cdec)

    def _execute(self, cand: CondorCandidate, regime: RegimeDecision, cdec) -> None:
        ex = self.s.strategy["execution"]
        tick = package_tick(cand.legs)
        prices = walk_prices_ticks(cand.credit_mid, cand.credit_natural, tick, [int(x) for x in ex["walk_ticks"]],
                                   bool(ex["final_rung_natural"]))
        r = self.s.risk
        lo = cand.credit_natural - int(r["collar_ticks_beyond_natural"]) * tick - 1e-9
        hi = cand.credit_mid + int(r["collar_ticks_beyond_mid"]) * tick + 1e-9
        pct = float(r["price_collar_pct_of_mid"]) * cand.credit_mid

        def collar_ok(px: float) -> bool:
            return lo <= px <= hi and abs(px - cand.credit_mid) <= pct + 1e-9

        key = self.gates.dedupe_key(cand)
        self.state.recent_order_keys[key] = datetime.now(tz=timezone.utc)
        legs = build_open_legs(cand)
        self.audit.write("execute_start", candidate=cand.summary(), prices=prices, tick=tick,
                         collar=[round(lo, 3), round(hi, 3)], rationale=cand.rationale)
        res = self.walker.run(legs, cand.contracts, prices, tag=f"open-{cand.underlying}", collar_ok=collar_ok,
                              on_order_sent=self._on_order_sent)
        if res["status"] in {"filled", "partial"} and res["filled_qty"] > 0:
            filled_qty = int(res["filled_qty"])
            credit = float(res["avg_price"] or res["last_price"])
            pos = BookPosition(
                position_id=uuid.uuid4().hex[:12], underlying=cand.underlying, expiry=cand.expiry,
                legs=[{"symbol": l.quote.symbol, "strike": l.quote.strike, "right": l.quote.right.value,
                       "side": l.side.value, "ratio": l.ratio} for l in cand.legs],
                contracts=filled_qty, entry_credit=credit,
                max_loss_total=cand.max_loss_per_package * filled_qty,
                opened_ts=datetime.now(tz=timezone.utc), entry_order_id=res["order_ids"][-1] if res["order_ids"] else "",
            )
            self.book.append(pos)
            self.state.fills += 1
            self.state.positions_opened += 1
            self.state.risk_committed += pos.max_loss_total
            slippage = (cand.credit_mid - credit) * 100 * filled_qty
            fill_rung = prices.index(res["last_price"]) if res["last_price"] in prices else None
            self.audit.write("position_opened", position=pos.to_dict(), slippage_vs_mid_usd=round(slippage, 2),
                             fill_rung=fill_rung, rungs=len(prices), expected=cand.summary(),
                             regime=regime.__dict__, critic=cdec.__dict__)
            self.journal.write("mid", {"event": "position_opened", "structure": "iron condor 0DTE", "contracts": filled_qty,
                                       "credit_filled": credit, "credit_mid_at_decision": round(cand.credit_mid, 3),
                                       "slippage_vs_mid_usd": round(slippage, 2), "fill_rung": fill_rung,
                                       "max_loss_usd": pos.max_loss_total, "net_delta": round(cand.net_delta, 3),
                                       "regime": regime.vol_regime.value, "critic": cdec.verdict.value})
            self._persist()
        elif res["status"] == "dry_run":
            self.audit.write("dry_run_would_open", candidate=cand.summary(), prices=prices)
        else:
            self.audit.write("open_not_filled", result={k: v for k, v in res.items()})
            self.journal.write("short", {"event": "open_not_filled", "status": res["status"], "prices_tried": prices})

    def _heartbeat(self, msg: str, now: datetime, kind: str = "heartbeat") -> None:
        if (now - self._last_heartbeat).total_seconds() >= 120:
            self._last_heartbeat = now
            self.audit.write(kind, msg=msg, open_positions=len(self.open_positions()), halted=self.state.halted)
            log.info("%s | %s", to_et(now).strftime("%H:%M:%S ET"), msg)

    # ------------------------------------------------------------------ run
    def run(self, cycle_s: float = 20.0) -> None:
        def _sig(*_):
            self._stop = True
        signal.signal(signal.SIGINT, _sig)
        signal.signal(signal.SIGTERM, _sig)
        log.info("agent running; dry_run=%s; kill file: %s", self.s.dry_run, self.s.risk["kill_switch_file"])
        while not self._stop:
            t0 = time.monotonic()
            try:
                self.cycle()
            except Exception as exc:  # never die silently; log and keep the flatten task alive
                log.exception("cycle error")
                self.audit.write("cycle_error", error=repr(exc)[:800])
            time.sleep(max(1.0, cycle_s - (time.monotonic() - t0)))
        self.audit.write("agent_stop")
        self._persist()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s",
                        handlers=[logging.StreamHandler(sys.stdout)])
    Agent().run()


if __name__ == "__main__":
    main()

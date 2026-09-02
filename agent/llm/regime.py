"""Regime module: the LLM reads anonymised context and returns ENUMS ONLY.

Output schema (gate 18): vol_regime, trend, event_risk, strategy_family, veto, veto_reason,
rationale. Any number in the output is ignored; any invalid enum rejects the whole response.
The LLM can only make the agent trade less (veto, NO_TRADE), never more.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from agent.core.clock import to_et
from agent.core.models import EventRisk, RegimeDecision, RegimeSnapshot, StrategyFamily, Trend, VolRegime
from agent.data.calendar import EventFlags
from agent.llm.anonymize import anonymize, anonymize_headlines
from agent.llm.provider import FeatherlessProvider


class RegimeSchema(BaseModel):
    vol_regime: VolRegime
    trend: Trend
    event_risk: EventRisk
    strategy_family: StrategyFamily
    veto: bool
    veto_reason: str = Field(default="", max_length=400)
    rationale: str = Field(default="", max_length=800)

    @field_validator("veto_reason", "rationale", mode="before")
    @classmethod
    def _str(cls, v):
        return "" if v is None else str(v)


SYSTEM = """You are the regime classifier inside a rule-based options trading system.
You classify; you do not trade. Deterministic code owns every number: prices, strikes,
position size, Greeks, orders, risk limits. Your authority is one-directional: you may
veto or choose NO_TRADE, you can never enlarge a position or override a rejected order.

Answer with ONE JSON object and nothing else, with exactly these keys:
  "vol_regime": one of "low" | "normal" | "elevated" | "stressed"
  "trend": one of "up" | "chop" | "down"
  "event_risk": one of "none" | "scheduled_minor" | "scheduled_major" | "unscheduled"
  "strategy_family": one of "IRON_CONDOR_0DTE" | "PUT_CREDIT_SPREAD" | "CALL_CREDIT_SPREAD" | "LONG_GAMMA_SLEEVE" | "NO_TRADE"
  "veto": true | false
  "veto_reason": short text, empty if veto is false
  "rationale": two or three sentences, no numbers that are not in the input

Guidance grounded in the evidence base of this system:
- Short-dated index premium selling has an expected value near zero after costs; the only
  reason to trade is a calm, contango regime inside a pre-approved time window.
- "stressed" means the term structure is inverted or an unscheduled shock is in the news.
- Set "unscheduled" only for a shock that is NOT on the scheduled calendar you are given
  (geopolitical event, exchange outage, surprise central-bank action, systemic credit news).
- Prefer IRON_CONDOR_0DTE in normal or low regimes with trend "chop"; prefer NO_TRADE in
  "stressed", in "unscheduled" event risk, or when the headlines describe an ongoing crash.
- PUT_CREDIT_SPREAD / CALL_CREDIT_SPREAD are only for a persistent one-directional drift
  with calm volatility; LONG_GAMMA_SLEEVE only when volatility is low and an unpriced
  catalyst is imminent. When unsure, choose IRON_CONDOR_0DTE with veto=false or NO_TRADE;
  do not invent directional views from headlines.
- Names in the input are anonymised on purpose. Do not try to identify them."""


def build_user_prompt(now: datetime, snap: Optional[RegimeSnapshot], flags: EventFlags,
                      upcoming: list[str], headlines: list[dict], spot_change_pct: Optional[float],
                      implied_move_pct: Optional[float], iv_rv_ratio: Optional[float]) -> str:
    et = to_et(now)
    # Dates are masked on purpose (F2: memorised priors keyed on dates); weekday and clock stay.
    lines = [f"Time: {et.strftime('%A %H:%M')} US/Eastern."]
    if snap:
        lines.append(f"Volatility index: {snap.vix:.2f}; 3-month volatility index: {snap.vix3m:.2f}; "
                     f"ratio {snap.slope:.3f} (below 0.95 is contango/calm, above 1.00 inverted). "
                     f"1-day volatility index: {snap.vix1d if snap.vix1d else 'n/a'}.")
        if snap.realized_vol_annualized:
            lines.append(f"Realised intraday volatility today (annualised): {snap.realized_vol_annualized:.1%}.")
    else:
        lines.append("Volatility term structure: UNAVAILABLE (data feed down).")
    if spot_change_pct is not None:
        lines.append(f"INDEX_ETF_A change since previous close: {spot_change_pct:+.2%}.")
    if implied_move_pct is not None:
        lines.append(f"Options-implied expected move to the close: {implied_move_pct:.2%} of spot.")
    if iv_rv_ratio is not None:
        lines.append(f"Implied-to-realised volatility ratio: {iv_rv_ratio:.2f} (below 1.0 means options are cheap vs realised).")
    lines.append("Deterministic calendar flags: " + json.dumps({
        "no_trade_day": flags.no_trade_day, "in_pause_window": flags.in_pause_window,
        "pause_reason": flags.pause_reason, "next_major_event_minutes": flags.next_major_minutes,
        "code_event_risk": flags.deterministic_event_risk.value,
    }))
    lines.append("Scheduled events (anonymised, relative days):")
    lines += ["  - " + anonymize(_relative_day(u, et.date())) for u in upcoming] or ["  - none"]
    lines.append("Recent headlines (anonymised, newest first):")
    hl = anonymize_headlines(headlines)
    lines += ["  - " + h for h in hl[:20]] or ["  - none available"]
    lines.append("Return the JSON object now.")
    return "\n".join(lines)


def _relative_day(line: str, today) -> str:
    """'2026-09-04 08:30 ET: ...' -> 'in 2 days 08:30 ET: ...' (dates masked, ordering kept)."""
    try:
        d = date.fromisoformat(line[:10])
        delta = (d - today).days
        label = "today" if delta == 0 else ("tomorrow" if delta == 1 else f"in {delta} days")
        return label + line[10:]
    except ValueError:
        return line


def decision_hash(dec: RegimeDecision) -> str:
    """Hash of the enums only (not the prose): the determinism metric of Koviazin et al."""
    key = json.dumps({"vol_regime": dec.vol_regime.value, "trend": dec.trend.value, "event_risk": dec.event_risk.value,
                      "strategy_family": dec.strategy_family.value, "veto": dec.veto}, sort_keys=True)
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def entropy_bits(values: list[str]) -> float:
    n = len(values)
    if n == 0:
        return 0.0
    counts = Counter(values)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def classify_regime_votes(provider: FeatherlessProvider, user_prompt: str, k: int
                          ) -> tuple[Optional[RegimeDecision], dict]:
    """k independent calls; unanimity on family and veto required, else NO_TRADE (F2 5.2 fallback).

    The returned decision is the first vote when unanimous; the meta carries the vote
    distribution and per-field entropy in bits for the report.
    """
    votes: list[RegimeDecision] = []
    metas: list[dict] = []
    for i in range(max(1, k)):
        dec, meta = classify_regime(provider, user_prompt)
        metas.append(meta)
        if dec is None:
            return None, {"votes": i, "unanimous": False, "reason": "schema failure", "calls": metas}
        votes.append(dec)
    fields = {
        "vol_regime": [v.vol_regime.value for v in votes],
        "trend": [v.trend.value for v in votes],
        "event_risk": [v.event_risk.value for v in votes],
        "strategy_family": [v.strategy_family.value for v in votes],
        "veto": [str(v.veto) for v in votes],
    }
    entropy = {f: round(entropy_bits(vals), 3) for f, vals in fields.items()}
    unanimous = entropy["strategy_family"] == 0.0 and entropy["veto"] == 0.0
    meta = {"votes": len(votes), "unanimous": unanimous, "entropy_bits": entropy,
            "distribution": {f: dict(Counter(vals)) for f, vals in fields.items()},
            "decision_hashes": [decision_hash(v) for v in votes], "calls": metas,
            "sampling": provider.sampling_params()}
    if not unanimous:
        # disagreement is converted into safety: a NO_TRADE decision with the vote record
        first = votes[0]
        forced = RegimeDecision(first.vol_regime, first.trend, first.event_risk, StrategyFamily.NO_TRADE, True,
                                f"vote disagreement: {meta['distribution']['strategy_family']} / veto {meta['distribution']['veto']}",
                                first.rationale, first.model, first.prompt_hash, first.response_hash,
                                sum(m["latency_ms"] for m in metas), sum(m["tokens_in"] for m in metas),
                                sum(m["tokens_out"] for m in metas))
        return forced, meta
    return votes[0], meta


def classify_regime(provider: FeatherlessProvider, user_prompt: str) -> tuple[Optional[RegimeDecision], dict]:
    res = provider.complete_json(SYSTEM, user_prompt, RegimeSchema, max_tokens=500)
    meta = {"model": res.model, "prompt_hash": res.prompt_hash, "response_hash": res.response_hash,
            "latency_ms": res.latency_ms, "tokens_in": res.tokens_in, "tokens_out": res.tokens_out,
            "error": res.error, "raw": res.raw_text[:1500]}
    if res.parsed is None:
        return None, meta
    p: RegimeSchema = res.parsed  # type: ignore[assignment]
    return RegimeDecision(
        vol_regime=p.vol_regime, trend=p.trend, event_risk=p.event_risk, strategy_family=p.strategy_family,
        veto=bool(p.veto), veto_reason=p.veto_reason, rationale=p.rationale, model=res.model,
        prompt_hash=res.prompt_hash, response_hash=res.response_hash, latency_ms=res.latency_ms,
        tokens_in=res.tokens_in, tokens_out=res.tokens_out,
    ), meta

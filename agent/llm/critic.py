"""Critic module: sees the finished, gate-validated candidate and may say PASS, REDUCE or BLOCK.

It replaces the human approval gate of the Alpaca reference article with an autonomous,
one-directional check (research B, design 6). REDUCE halves the quantity (code applies it,
minimum 1); BLOCK logs the reason and the candidate is dropped. There is no APPROVE_LARGER.
"""
from __future__ import annotations

import json
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from agent.core.models import CondorCandidate, CriticDecision, CriticVerdict, GateResult, RegimeDecision
from agent.llm.provider import FeatherlessProvider


class CriticSchema(BaseModel):
    verdict: CriticVerdict
    reason: str = Field(default="", max_length=500)

    @field_validator("reason", mode="before")
    @classmethod
    def _str(cls, v):
        return "" if v is None else str(v)


SYSTEM = """You are the critic inside a rule-based options trading system. A deterministic
engine has already built a defined-risk iron condor and every hard risk gate has passed.
Your job is a last sanity check for things rules miss: internally inconsistent inputs,
a rationale that contradicts the regime, stale-looking data, or a situation the regime
classifier flagged as risky. You may answer PASS, REDUCE (halve the size) or BLOCK.
You cannot enlarge, re-price or re-strike anything.

Answer with ONE JSON object and nothing else:
  {"verdict": "PASS" | "REDUCE" | "BLOCK", "reason": "one or two sentences"}

Default to PASS when the inputs are consistent. Use REDUCE when the regime is elevated
or the trend is directional against one wing. Use BLOCK only for a concrete inconsistency
or a risk the gates cannot see (e.g. headlines describing an unscheduled shock)."""


def build_user_prompt(cand: CondorCandidate, regime: RegimeDecision, gates: list[GateResult],
                      book_summary: dict) -> str:
    s = cand.summary()
    facts = {
        "candidate": {
            "structure": "iron condor, all wings bought, single package order",
            "distance_short_call_pct": round((s["short_call"] - s["spot"]) / s["spot"] * 100, 2),
            "distance_short_put_pct": round((s["spot"] - s["short_put"]) / s["spot"] * 100, 2),
            "implied_move_pct": round(s["implied_move"] / s["spot"] * 100, 2),
            "credit_to_max_loss_ratio": round(s["credit_mid"] * 100 / s["max_loss_per_package"], 3) if s["max_loss_per_package"] else None,
            "net_delta_per_package": s["net_delta"],
            "contracts": s["contracts"],
            "max_loss_total_usd": s["max_loss_total"],
        },
        "regime": {"vol_regime": regime.vol_regime.value, "trend": regime.trend.value,
                   "event_risk": regime.event_risk.value, "strategy_family": regime.strategy_family.value,
                   "rationale": regime.rationale},
        "gates_passed": [g.name for g in gates if g.passed],
        "gates_failed": [g.name for g in gates if not g.passed],
        "book": book_summary,
    }
    return "Facts (anonymised, numbers are inputs only):\n" + json.dumps(facts, indent=1) + "\nReturn the JSON object now."


def critique(provider: FeatherlessProvider, user_prompt: str) -> tuple[Optional[CriticDecision], dict]:
    res = provider.complete_json(SYSTEM, user_prompt, CriticSchema, max_tokens=300)
    meta = {"model": res.model, "prompt_hash": res.prompt_hash, "response_hash": res.response_hash,
            "latency_ms": res.latency_ms, "tokens_in": res.tokens_in, "tokens_out": res.tokens_out,
            "error": res.error, "raw": res.raw_text[:800]}
    if res.parsed is None:
        # fail-safe: an unreadable critic means BLOCK, never PASS
        return CriticDecision(CriticVerdict.BLOCK, "critic output invalid; fail-safe block", res.model,
                              res.prompt_hash, res.response_hash, res.latency_ms), meta
    p: CriticSchema = res.parsed  # type: ignore[assignment]
    return CriticDecision(p.verdict, p.reason, res.model, res.prompt_hash, res.response_hash, res.latency_ms), meta

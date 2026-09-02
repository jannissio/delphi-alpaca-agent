"""Journal: narrative entries written by the cheap model from structured facts.

Three tiers (research B, design 9): short-term (each decision), mid-term (each closed
trade: expected vs realised Greeks, slippage), long-term (lessons, written only on a
closed trade or a gate breach). The journal is documentation, it never feeds back into
sizing. Facts come from the audit log; the model only phrases them.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from agent.llm.provider import FeatherlessProvider


class JournalSchema(BaseModel):
    entry: str = Field(max_length=1200)
    lesson: str = Field(default="", max_length=400)


SYSTEM = """You write the trading journal of a rule-based options agent. You receive structured
facts and write a short, plain, honest entry in English for a reader who knows options.
Never invent numbers; use only those in the facts. Do not claim an edge: the system's own
evidence says short-dated premium selling has near-zero expected value after costs and the
goal is a risk process that behaves exactly as specified. If a lesson is warranted (a gate
fired, a fill was worse than modelled, a Greek diverged), state it in one sentence.
Answer with ONE JSON object: {"entry": "...", "lesson": "..."} (lesson may be empty)."""


class Journal:
    def __init__(self, path: Path, provider: Optional[FeatherlessProvider]):
        self.path = path
        self.provider = provider
        path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, tier: str, facts: dict) -> dict:
        entry, lesson, model = "", "", "none"
        if self.provider is not None:
            res = self.provider.complete_json(SYSTEM, f"Tier: {tier}\nFacts:\n{json.dumps(facts, indent=1, default=str)}",
                                              JournalSchema, max_tokens=500)
            model = res.model
            if res.parsed is not None:
                entry, lesson = res.parsed.entry, res.parsed.lesson  # type: ignore[attr-defined]
        if not entry:
            entry = f"[auto] {tier}: " + json.dumps(facts, default=str)[:600]
        rec = {"ts": datetime.now(tz=timezone.utc).isoformat(), "tier": tier, "model": model,
               "entry": entry, "lesson": lesson, "facts": facts}
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, default=str, ensure_ascii=False) + "\n")
        return rec

"""LLM provider: Featherless.ai (OpenAI-compatible endpoint, open-weight models).

Every call is: temperature 0, fixed seed, JSON-only output, strict pydantic validation,
prompt and response hashed and logged (determinism replay, gate 18, gate 27). A response
that fails validation after one repair attempt returns None and the caller treats that as
"no new risk". The model never sees a file path, an order endpoint or a number to emit.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Any, Optional, Type, TypeVar

from openai import OpenAI, APIError
from pydantic import BaseModel, ValidationError

log = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

FEATHERLESS_BASE_URL = "https://api.featherless.ai/v1"


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


@dataclass
class LLMResult:
    parsed: Optional[BaseModel]
    raw_text: str
    model: str
    prompt_hash: str
    response_hash: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    error: str = ""


def extract_json(text: str) -> Optional[dict]:
    """Tolerate code fences and leading prose; take the first balanced JSON object."""
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if m:
        text = m.group(1)
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError:
                    return None
    return None


class FeatherlessProvider:
    def __init__(self, api_key: str, model: str, timeout_s: float = 60.0, seed: int = 7):
        if not api_key:
            raise RuntimeError("FEATHERLESS_API_KEY missing")
        self.client = OpenAI(api_key=api_key, base_url=FEATHERLESS_BASE_URL, timeout=timeout_s, max_retries=1)
        self.model = model
        self.seed = seed

    def sampling_params(self) -> dict:
        """All four pinned (Koviazin et al.: T=0 alone leaves 0.98 bits of decision entropy)."""
        return {"temperature": 0.0, "top_p": 1e-6, "top_k": 1, "seed": self.seed, "model": self.model}

    def _call(self, system: str, user: str, max_tokens: int) -> tuple[str, int, int]:
        kwargs: dict[str, Any] = dict(
            model=self.model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.0,
            top_p=1e-6,
            max_tokens=max_tokens,
            seed=self.seed,
            extra_body={"top_k": 1},
        )
        try:
            resp = self.client.chat.completions.create(response_format={"type": "json_object"}, **kwargs)
        except APIError as exc:
            # some models reject response_format; retry without it, JSON is enforced by the prompt
            log.info("response_format rejected by %s (%s); retrying plain", self.model, exc.__class__.__name__)
            resp = self.client.chat.completions.create(**kwargs)
        text = resp.choices[0].message.content or ""
        usage = getattr(resp, "usage", None)
        return text, int(getattr(usage, "prompt_tokens", 0) or 0), int(getattr(usage, "completion_tokens", 0) or 0)

    def complete_json(self, system: str, user: str, schema: Type[T], max_tokens: int = 600) -> LLMResult:
        prompt_hash = sha(self.model + "\n" + system + "\n" + user)
        t0 = time.perf_counter()
        text, tin, tout = "", 0, 0
        error = ""
        parsed: Optional[BaseModel] = None
        try:
            text, tin, tout = self._call(system, user, max_tokens)
            obj = extract_json(text)
            if obj is None:
                raise ValueError("no JSON object in response")
            parsed = schema.model_validate(obj)
        except (ValidationError, ValueError, APIError) as exc:
            error = f"{exc.__class__.__name__}: {str(exc)[:300]}"
            log.warning("LLM output invalid (%s); one repair attempt", error)
            try:
                repair_user = (user + "\n\nYour previous answer was rejected by the schema validator: "
                               + error + "\nReturn ONLY a JSON object with exactly the allowed keys and enum values.")
                text2, tin2, tout2 = self._call(system, repair_user, max_tokens)
                tin += tin2
                tout += tout2
                obj = extract_json(text2)
                if obj is None:
                    raise ValueError("no JSON object in repair response")
                parsed = schema.model_validate(obj)
                text = text2
                error = ""
            except (ValidationError, ValueError, APIError) as exc2:
                error = f"repair failed: {exc2.__class__.__name__}: {str(exc2)[:300]}"
                parsed = None
        latency = int((time.perf_counter() - t0) * 1000)
        return LLMResult(parsed=parsed, raw_text=text, model=self.model, prompt_hash=prompt_hash,
                         response_hash=sha(text), latency_ms=latency, tokens_in=tin, tokens_out=tout, error=error)

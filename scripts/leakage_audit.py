"""Leakage self-audit (research B design 14; Glasserman & Lin 2023; F2 recipe from Chen/Kelly/Xiu).

Two measurements on the most recent logged regime prompt:
  1. De-anonymised control: replace placeholders with the real names and re-classify. If the
     enums change, the model was using identity, not information.
  2. Re-identification probe: ask the model to name the masked entities. The share it gets
     right is the residual leakage of our masking (CKX report 76-96 % re-identification for
     news bodies, so this number is expected to be high for headlines; we report it honestly).

    python scripts/leakage_audit.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pydantic import BaseModel  # noqa: E402

from agent.core.config import STATE_DIR, Settings  # noqa: E402
from agent.llm.provider import FeatherlessProvider  # noqa: E402
from agent.llm.regime import classify_regime, decision_hash  # noqa: E402

REAL = {"INDEX_ETF_A": "SPY", "INDEX_A": "S&P 500", "INDEX_ETF_B": "QQQ", "INDEX_B": "Nasdaq", "INDEX_C": "Dow Jones",
        "COMPANY_1": "Broadcom", "COMPANY_2": "Snowflake", "COMPANY_3": "HPE", "COMPANY_4": "Zscaler",
        "COMPANY_5": "Lululemon", "COMPANY_6": "DocuSign", "COMPANY_7": "Samsara", "COMPANY_8": "Ciena",
        "COMPANY_9": "Nvidia", "COMPANY_10": "Apple", "COMPANY_11": "Microsoft", "COMPANY_12": "Tesla",
        "CENTRAL_BANK": "Federal Reserve"}


class Guess(BaseModel):
    guesses: dict[str, str]


def main() -> None:
    s = Settings()
    recs = [json.loads(l) for l in (STATE_DIR / "audit.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    prompts = [r["prompt"] for r in recs if r["kind"] == "llm_regime" and r.get("prompt")]
    if not prompts:
        print("no logged regime prompts yet")
        return
    prompt = prompts[-1]
    p = FeatherlessProvider(s.featherless_key, s.model_strong)
    masked, _ = classify_regime(p, prompt)
    unmasked_prompt = prompt
    for k, v in REAL.items():
        unmasked_prompt = unmasked_prompt.replace(k, v)
    unmasked, _ = classify_regime(p, unmasked_prompt)
    same = masked is not None and unmasked is not None and decision_hash(masked) == decision_hash(unmasked)

    present = [k for k in REAL if k in prompt]
    probe = ("The following text has entity names replaced by placeholders. For each placeholder listed, "
             "guess the real entity name. Answer with ONE JSON object {\"guesses\": {placeholder: name}}.\n"
             f"Placeholders: {present}\n\nText:\n{prompt}")
    res = p.complete_json("You are a careful analyst. Answer with JSON only.", probe, Guess, max_tokens=400)
    hits, total = 0, len(present)
    guesses = res.parsed.guesses if res.parsed else {}
    for k in present:
        g = str(guesses.get(k, "")).lower()
        if g and (REAL[k].lower() in g or g in REAL[k].lower()):
            hits += 1
    report = {"model": s.model_strong, "masked_decision": decision_hash(masked) if masked else None,
              "unmasked_decision": decision_hash(unmasked) if unmasked else None, "decisions_identical": same,
              "placeholders_in_prompt": total, "reidentified": hits,
              "reidentification_rate": round(hits / total, 2) if total else None, "guesses": guesses}
    print(json.dumps(report, indent=1))
    (STATE_DIR / "leakage_audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

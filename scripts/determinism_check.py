"""Determinism replay (research B design 14; F2 5.2 protocol from Koviazin et al.).

Takes the most recent logged regime prompt (or every prompt with --all), re-sends it k times
with the pinned sampling parameters, and reports per-field decision entropy in bits and a
seed-sensitivity row. Pass criterion: 0.00 bits on strategy_family and veto.

    python scripts/determinism_check.py [--k 5] [--all] [--model deepseek-ai/DeepSeek-V3.2]
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.core.config import STATE_DIR, Settings  # noqa: E402
from agent.llm.provider import FeatherlessProvider  # noqa: E402
from agent.llm.regime import classify_regime, decision_hash, entropy_bits  # noqa: E402

FIELDS = ("vol_regime", "trend", "event_risk", "strategy_family", "veto")


def replay(provider: FeatherlessProvider, prompt: str, k: int) -> dict:
    votes = []
    for _ in range(k):
        dec, meta = classify_regime(provider, prompt)
        votes.append(dec)
    valid = [v for v in votes if v is not None]
    fields = {f: [str(getattr(v, f).value if hasattr(getattr(v, f), "value") else getattr(v, f)) for v in valid] for f in FIELDS}
    return {
        "k": k, "valid": len(valid),
        "entropy_bits": {f: round(entropy_bits(vals), 3) for f, vals in fields.items()},
        "distribution": {f: dict(Counter(vals)) for f, vals in fields.items()},
        "decision_hashes": [decision_hash(v) for v in valid],
        "pass": len(valid) == k and entropy_bits(fields["strategy_family"]) == 0.0 and entropy_bits(fields["veto"]) == 0.0,
    }


def main() -> None:
    s = Settings()
    k = int(sys.argv[sys.argv.index("--k") + 1]) if "--k" in sys.argv else 5
    model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else s.model_strong
    recs = [json.loads(l) for l in (STATE_DIR / "audit.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    prompts = [r["prompt"] for r in recs if r["kind"] == "llm_regime" and r.get("prompt")]
    if not prompts:
        print("no logged regime prompts yet")
        return
    targets = prompts if "--all" in sys.argv else prompts[-1:]
    out = []
    for i, prompt in enumerate(targets):
        base = FeatherlessProvider(s.featherless_key, model, seed=7)
        res = replay(base, prompt, k)
        alt = FeatherlessProvider(s.featherless_key, model, seed=1234)
        res_seed = replay(alt, prompt, max(2, k // 2))
        res["seed_sensitivity"] = {"seed_1234_hashes": res_seed["decision_hashes"],
                                   "same_family_as_seed_7": res_seed["distribution"]["strategy_family"] == res["distribution"]["strategy_family"]}
        res["prompt_index"] = i
        out.append(res)
        print(json.dumps(res, indent=1))
    (STATE_DIR / "determinism_check.json").write_text(json.dumps({"model": model, "sampling": base.sampling_params(),
                                                                   "results": out}, indent=2), encoding="utf-8")
    print("wrote", STATE_DIR / "determinism_check.json")


if __name__ == "__main__":
    main()

"""Conformal Condor: split-conformal arithmetic, ACI, state round trip, the P-vs-Q ledger and gate 31."""
from __future__ import annotations

import json
import random
from datetime import date, timedelta
from statistics import NormalDist

import pytest

from agent.core import conformal as conf
from agent.core.strategy import build_condor
from tests.test_core import NOW, TODAY, _gate_run, settings, synthetic_chain  # noqa: F401


def half_normal_scores(n: int = 250, scale: float = 0.52, seed: int = 0) -> list[float]:
    """Deterministic calibration set: half-normal quantiles, shuffled. scale 0.52 reproduces research/G's
    82 % coverage of the fixed k = 0.70 rule on the 10:30-to-close horizon."""
    nd = NormalDist()
    xs = [scale * nd.inv_cdf(0.5 + 0.5 * (i + 0.5) / n) for i in range(n)]
    random.Random(seed).shuffle(xs)
    return xs


def synthetic_state(alpha: float = 0.20, **kw) -> conf.ConformalState:
    return conf.ConformalState(alpha_t=alpha, scores=half_normal_scores(**kw), source="synthetic half-normal")


def test_conformal_quantile_and_p_value_are_exact():
    scores = [float(i) for i in range(1, 10)]                  # n = 9
    k, level = conf.conformal_quantile(scores, 0.2)             # ceil(10 * 0.8) / 9 = 8/9 -> 8th smallest
    assert (k, level) == (8.0, pytest.approx(8 / 9))
    assert conf.p_outside(scores, 8.0) == pytest.approx(0.2)    # (1 + #{r > 8}) / 10
    assert conf.p_outside(scores, 0.0) == pytest.approx(1.0)
    k_max, level1 = conf.conformal_quantile(scores, 0.01)
    assert (k_max, level1) == (9.0, 1.0)


def test_aci_moves_alpha_toward_target_and_clips():
    a = 0.20
    assert conf.aci_update(a, 1, 0.20, 0.005) == pytest.approx(0.196)     # a miss tightens
    assert conf.aci_update(a, 0, 0.20, 0.005) == pytest.approx(0.201)     # a hit loosens
    assert conf.aci_update(0.021, 1, 0.20, 0.005) == 0.02                 # floor
    assert conf.aci_update(0.399, 0, 0.20, 0.005) == 0.40                 # ceiling


def test_backfill_is_deterministic_and_covers_near_target():
    rows = [((date(2024, 1, 1) + timedelta(days=i)).isoformat(), r) for i, r in enumerate(half_normal_scores(600, seed=3))]
    p = conf.ConformalParams()
    a, b = conf.backfill(rows, p), conf.backfill(rows, p)
    assert json.dumps(a.__dict__) == json.dumps(b.__dict__)
    stats = conf.coverage_stats(a.ledger)
    assert stats["n"] == 600 - p.min_scores
    assert 0.74 <= stats["coverage"] <= 0.86
    assert len(a.scores) <= max(p.window, 400)
    assert a.ledger[-1]["date"] == rows[-1][0] == a.updated_through


def test_state_round_trip_and_eod_update(tmp_path):
    p = conf.ConformalParams()
    st = synthetic_state()
    sess = conf.open_session(st, p, TODAY, NOW, 650.0, 16.0)
    assert sess["impl_ref_pct"] == pytest.approx(conf.impl_move_ref_pct(16.0))
    assert p.k_min <= sess["k"] <= p.k_max and sess["n"] == 250
    st.save(tmp_path / "c.json")
    st2 = conf.ConformalState.load(tmp_path / "c.json")
    assert st2.session == sess and st2.scores == st.scores
    rec = conf.eod_update(st2, p, 650.0 * (1 + 0.02), TODAY)                # a 2 % move: outside
    assert rec["err"] == 1 and rec["alpha_after"] < rec["alpha_before"]
    assert st2.session is None and st2.updated_through == TODAY.isoformat()
    assert st2.scores[-1] == pytest.approx(rec["ratio"]) and len(st2.scores) == 251
    with pytest.raises(ValueError):
        conf.eod_update(st2, p, 650.0, TODAY)                              # no committed interval any more


def test_ledger_reads_q_off_the_quote_and_p_off_the_scores(settings):
    p = conf.ConformalParams()
    st = synthetic_state()
    sess = conf.open_session(st, p, TODAY, NOW, 650.0, 16.0)
    ch = synthetic_chain()
    cand = build_condor(ch, 650.0, "SPY", TODAY, settings.strategy, settings.underlying_cfg("SPY"), NOW,
                        short_distance=sess["k"] * sess["impl_ref_usd"])
    led = conf.ledger_for_candidate(cand, st, p, sess)
    ratio = max(cand.short_call.ratio, cand.short_put.ratio)
    assert led["q_mid"] == pytest.approx(cand.credit_mid / ratio / cand.wing_width)
    assert led["q_call"] > 0 and led["q_put"] > 0
    assert 0 < led["p_mid"] <= led["p_short"] < 1                       # the midpoint lies further out
    assert led["gap"] == pytest.approx(led["q_mid"] - led["p_mid"])
    assert led["strict_gap"] == pytest.approx(led["q_mid"] - led["p_short"])
    assert led["passes"] == (led["gap"] >= p.margin)
    assert led["ev_digital_usd_per_package"] == pytest.approx(100 * ratio * cand.wing_width * led["gap"])
    assert led["kelly"]["f_used"] <= 0.02 and led["kelly"]["binding_constraint"] in {"cap", "kelly"}
    assert "conformal" not in cand.summary() or cand.summary()["conformal"] is None
    cand.extras["conformal"] = led
    assert cand.summary()["conformal"]["gap"] == pytest.approx(led["gap"], abs=1e-4)


def test_short_distance_overrides_the_fixed_rule(settings):
    ch = synthetic_chain()
    fixed = build_condor(ch, 650.0, "SPY", TODAY, settings.strategy, settings.underlying_cfg("SPY"), NOW)
    wide = build_condor(ch, 650.0, "SPY", TODAY, settings.strategy, settings.underlying_cfg("SPY"), NOW, short_distance=6.0)
    assert wide.short_call.quote.strike >= 656 and wide.short_put.quote.strike <= 644
    assert wide.credit_mid < fixed.credit_mid
    assert "conformal distance" in wide.rationale and "conformal" not in fixed.rationale


def test_gate_coverage_passes_fails_and_requires_ledger(settings):
    p = conf.ConformalParams.from_config(settings.strategy.get("conformal"))
    assert p.enabled, "strategy.yaml must enable the conformal block for this test"
    ch = synthetic_chain()
    cand = build_condor(ch, 650.0, "SPY", TODAY, settings.strategy, settings.underlying_cfg("SPY"), NOW)

    def gate(c):
        _, res = _gate_run(settings, c)
        return next(g for g in res if g.name == "gate_coverage")

    assert not gate(cand).passed and "missing" in gate(cand).reason
    cand.extras["conformal"] = {"q_mid": 0.30, "p_mid": 0.10, "gap": 0.20, "margin": p.margin, "passes": True, "warnings": []}
    assert gate(cand).passed and gate(cand).value == pytest.approx(0.2) and gate(cand).limit == p.margin
    cand.extras["conformal"] = {"q_mid": 0.12, "p_mid": 0.10, "gap": 0.02, "margin": p.margin, "passes": False, "warnings": []}
    assert not gate(cand).passed and "does not pay" in gate(cand).reason
    cand.extras["conformal"] = {"q_mid": 0.30, "p_mid": 0.10, "gap": 0.20, "margin": p.margin, "passes": True,
                                "warnings": ["a spread has non-positive mid credit (stale or crossed quote)"]}
    assert not gate(cand).passed

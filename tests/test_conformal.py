"""Conformal Risk Control Condor: conformal arithmetic, risk control, online updates, state round trip,
the P-vs-Q ledger and gate 31."""
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


def synthetic_state(alpha: float = 0.20, beta: float = 0.10, **kw) -> conf.ConformalState:
    return conf.ConformalState(alpha_t=alpha, beta_t=beta, scores=half_normal_scores(**kw), source="synthetic half-normal")


# ------------------------------------------------------------------ coverage arithmetic
def test_conformal_quantile_and_p_value_are_exact():
    scores = [float(i) for i in range(1, 10)]                  # n = 9
    k, level = conf.conformal_quantile(scores, 0.2)             # ceil(10 * 0.8) / 9 = 8/9 -> 8th smallest
    assert (k, level) == (8.0, pytest.approx(8 / 9))
    assert conf.p_outside(scores, 8.0) == pytest.approx(0.2)    # (1 + #{r > 8}) / 10
    assert conf.p_outside(scores, 0.0) == pytest.approx(1.0)
    k_max, level1 = conf.conformal_quantile(scores, 0.01)
    assert (k_max, level1) == (9.0, 1.0)


def test_online_updates_move_toward_target_and_clip():
    assert conf.aci_update(0.20, 1, 0.20, 0.005) == pytest.approx(0.196)     # a miss tightens: 0.20 + 0.005 (0.20 - 1)
    assert conf.aci_update(0.20, 0, 0.20, 0.005) == pytest.approx(0.201)     # a hit loosens
    assert conf.aci_update(0.021, 1, 0.20, 0.005) == 0.02                    # floor
    assert conf.aci_update(0.399, 0, 0.20, 0.005) == 0.40                    # ceiling
    assert conf.online_update(0.10, 1.0, 0.10, 0.005, 0.02, 0.30) == pytest.approx(0.0955)   # full payout tightens
    assert conf.online_update(0.10, 0.0, 0.10, 0.005, 0.02, 0.30) == pytest.approx(0.1005)   # no payout loosens


# ------------------------------------------------------------------ risk-control arithmetic
def test_crc_loss_is_bounded_monotone_and_zero_inside():
    for r in (0.0, 0.3, 0.9, 2.5):
        for k in (0.2, 0.6, 1.0):
            v = conf.crc_loss(r, k, 0.8)
            assert 0.0 <= v <= 1.0
            assert v <= conf.crc_loss(r, k - 0.1, 0.8) + 1e-12          # non-increasing in k
            if r <= k:
                assert v == 0.0
    assert conf.crc_loss(5.0, 0.5, 0.8) == 1.0                            # capped at the wing


def test_crc_radius_certifies_beta_and_is_minimal():
    scores = half_normal_scores()
    omega = 0.8
    for beta in (0.05, 0.10, 0.20):
        k = conf.crc_radius(scores, omega, beta)
        assert conf.crc_certified(scores, k, omega) <= beta + 1e-9
        assert conf.crc_certified(scores, k - 1e-3, omega) > beta         # nothing smaller certifies
    assert conf.crc_radius(scores, omega, 0.05) > conf.crc_radius(scores, omega, 0.20)   # stricter beta, wider interval
    with pytest.raises(ValueError):
        conf.crc_radius(scores, omega, 1e-4)                             # below the 1/(n+1) floor
    n = len(scores)
    assert conf.crc_certified(scores, 0.4, omega) == pytest.approx(n / (n + 1) * conf.crc_risk(scores, 0.4, omega) + 1 / (n + 1))


def test_coverage_is_the_indicator_special_case():
    """With omega -> 0 the CRC loss is the miscoverage indicator, so the risk at k equals the outside frequency."""
    scores = half_normal_scores()
    k = 0.7
    freq = sum(1 for r in scores if r > k) / len(scores)
    assert conf.crc_risk(scores, k, 1e-9) == pytest.approx(freq)


# ------------------------------------------------------------------ backfill and state
def test_backfill_is_deterministic_and_holds_both_targets():
    rows = [((date(2024, 1, 1) + timedelta(days=i)).isoformat(), r, 0.8) for i, r in enumerate(half_normal_scores(700, seed=3))]
    p = conf.ConformalParams()
    a, b = conf.backfill(rows, p), conf.backfill(rows, p)
    assert json.dumps(a.__dict__) == json.dumps(b.__dict__)
    stats = conf.coverage_stats(a.ledger)
    assert stats["n"] == 700 - p.min_scores
    assert 0.74 <= stats["coverage"] <= 0.86                              # coverage track near 1 - alpha
    assert 0.07 <= stats["realized_risk"] <= 0.13                         # risk track near beta
    assert len(a.scores) <= max(p.window, 400)
    assert a.ledger[-1]["date"] == rows[-1][0] == a.updated_through


def test_state_round_trip_and_eod_update(tmp_path):
    p = conf.ConformalParams()
    st = synthetic_state()
    sess = conf.open_session(st, p, TODAY, NOW, 650.0, 16.0, wing_usd=4.0)
    assert sess["impl_ref_pct"] == pytest.approx(conf.impl_move_ref_pct(16.0))
    assert sess["omega"] == pytest.approx(4.0 / sess["impl_ref_usd"])
    assert sess["rule"] == "crc" and sess["k"] == sess["k_crc"]
    assert p.k_min <= sess["k"] <= p.k_max and sess["n"] == 250
    assert sess["k_crc"] >= sess["k_crc_fixed"] - 1e-9 and sess["certified_at_k_crc_fixed"] <= p.beta_target + 1e-9
    assert sess["beta_star"] == p.beta_target
    st.save(tmp_path / "c.json")
    st2 = conf.ConformalState.load(tmp_path / "c.json")
    assert st2.session == sess and st2.scores == st.scores and st2.beta_t == st.beta_t
    rec = conf.eod_update(st2, p, 650.0 * (1 + 0.02), TODAY)                # a 2 % move: outside, full payout
    assert rec["err"] == 1 and rec["alpha_after"] < rec["alpha_before"]
    assert rec["loss"] == 1.0 and rec["beta_after"] < rec["beta_before"]
    assert st2.session is None and st2.updated_through == TODAY.isoformat()
    assert st2.scores[-1] == pytest.approx(rec["ratio"]) and len(st2.scores) == 251
    with pytest.raises(ValueError):
        conf.eod_update(st2, p, 650.0, TODAY)                              # no committed interval any more


def test_legacy_state_without_beta_loads(tmp_path):
    (tmp_path / "old.json").write_text(json.dumps({"alpha_t": 0.2, "scores": half_normal_scores()}), encoding="utf-8")
    st = conf.ConformalState.load(tmp_path / "old.json")
    assert st.beta_t == 0.10 and len(st.scores) == 250


# ------------------------------------------------------------------ ledger and gate
def test_ledger_reads_q_off_the_quote_and_certifies_p(settings):
    p = conf.ConformalParams.from_config(settings.strategy.get("conformal"))
    st = synthetic_state()
    sess = conf.open_session(st, p, TODAY, NOW, 650.0, 16.0, wing_usd=4.0)
    ch = synthetic_chain()
    cand = build_condor(ch, 650.0, "SPY", TODAY, settings.strategy, settings.underlying_cfg("SPY"), NOW,
                        short_distance=sess["k"] * sess["impl_ref_usd"])
    led = conf.ledger_for_candidate(cand, st, p, sess)
    ratio = max(cand.short_call.ratio, cand.short_put.ratio)
    assert led["q_mid"] == pytest.approx(cand.credit_mid / ratio / cand.wing_width)
    assert led["q_call"] > 0 and led["q_put"] > 0
    assert 0 < led["p_mid"] <= led["p_short"] < 1                       # the midpoint lies further out
    assert led["beta_empirical"] >= led["risk_hat"] > 0
    assert led["certified_ok"] and led["beta_certified"] == p.beta_target
    assert led["gap_crc"] == pytest.approx(led["q_mid"] - p.beta_target)
    assert led["gap_empirical"] == pytest.approx(led["q_mid"] - led["beta_empirical"])
    assert led["gap_cov"] == pytest.approx(led["q_mid"] - led["p_mid"])
    assert led["gap"] == pytest.approx(led["gap_crc"] if p.rule == "crc" else led["gap_cov"])
    assert led["passes"] == (led["gap"] >= p.margin)
    assert led["ev_lower_bound_usd_per_package"] == pytest.approx(100 * ratio * (cand.credit_mid / ratio - p.beta_target * cand.wing_width))
    # a strike inside the certified radius voids the certificate and the gate (Theorem 3, remark iii)
    led_in = conf.ledger_for_candidate(cand, st, p, {**sess, "k_crc_fixed": led["k_effective"] + 0.5})
    assert not led_in["certified_ok"] and led_in["beta_certified"] is None and not led_in["passes"]
    assert any("inside the certified radius" in w for w in led_in["warnings"])
    # a session committed with a wider wing (smaller loss per breach) does not certify a narrower package:
    # the radius is re-derived at the traded wing and is the binding one
    sess_wide = conf.open_session(synthetic_state(), p, TODAY, NOW, 650.0, 16.0, wing_usd=4.0 * 3)
    assert sess_wide["k_crc_fixed"] < sess["k_crc_fixed"]
    led_w = conf.ledger_for_candidate(cand, st, p, sess_wide)
    assert led_w["k_crc_fixed_session"] == pytest.approx(sess_wide["k_crc_fixed"])
    assert led_w["k_crc_fixed_at_wing"] == pytest.approx(sess["k_crc_fixed"], abs=1e-4)
    assert led_w["k_crc_fixed"] == pytest.approx(led_w["k_crc_fixed_at_wing"], abs=1e-4)
    assert led_w["certified_ok"] == (led_w["k_effective"] >= led_w["k_crc_fixed"] - 1e-9)
    assert led["kelly"]["f_used"] <= 0.02 and led["kelly"]["binding_constraint"] in {"cap", "kelly"}
    assert cand.summary()["conformal"] is None
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

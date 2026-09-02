"""Anytime-valid evidence (docs/THEORY.md section 9): the two e-processes and the evidence ceiling."""
from __future__ import annotations

import math
import random

import pytest

from agent.core import evidence as ev


def test_evidence_ceiling_and_sessions_for_alpha():
    assert ev.evidence_ceiling(0.20, 3) == pytest.approx(1.953125)       # (1/0.8)^3
    assert 1.0 / ev.evidence_ceiling(0.20, 3) == pytest.approx(0.512, abs=1e-3)
    assert ev.sessions_for_alpha(0.20, 0.05) == 14                          # ln 20 / ln 1.25 = 13.4 -> 14
    assert ev.sessions_for_alpha(0.15, 0.05) == 19
    assert ev.evidence_ceiling(0.20, 6) == pytest.approx(ev.evidence_ceiling(0.20, 3) ** 2)   # per package, not per session


def test_risk_process_is_a_supermartingale_under_the_null():
    """With exchangeable losses whose mean is exactly beta*, the one-step factor has expectation 1 and the wealth
    is non-negative for every admissible bet; the maximal bet 1/beta* is admissible, anything larger is not."""
    rng = random.Random(7)
    beta = 0.10
    losses = [1.0] * 2000 + [0.0] * 18000                                  # exactly E[l] = beta* over the sample
    rng.shuffle(losses)
    for lam in (0.5, 1.0, 1.0 / beta):
        r = ev.risk_wealth(losses, beta, lam)
        assert min(r["path"]) >= -1e-12
        factors = [1.0 + lam * (l - beta) for l in losses]
        assert sum(factors) / len(factors) == pytest.approx(1.0, abs=1e-9)   # one-step expectation is exactly 1
        assert 0.0 < r["p_anytime"] <= 1.0
    with pytest.raises(ValueError):
        ev.risk_wealth(losses, beta, 1.0 / beta + 0.5)
    # a certificate that is violated (mean loss 0.3 against beta* 0.1) accumulates evidence fast
    bad = [1.0 if rng.random() < 0.30 else 0.0 for _ in range(300)]
    assert ev.risk_wealth(bad, beta, 1.0)["p_anytime"] < 0.05


def test_profit_process_bets_and_ceiling():
    g = 0.20
    wins = [(g, 0.0)] * 3
    top = ev.profit_wealth(wins, None)                  # largest admissible bet attains the ceiling
    assert top["W_T"] == pytest.approx(ev.evidence_ceiling(g, 3))
    unit = ev.profit_wealth(wins, 1.0)                  # eta = 1 gives (1+g)^T
    assert unit["W_T"] == pytest.approx((1 + g) ** 3)
    ruin = ev.profit_wealth([(g, 1.0)], None)           # a full-wing loss at the maximal bet: wealth 0, still admissible
    assert ruin["W_T"] == pytest.approx(0.0, abs=1e-12) and ruin["p_anytime"] == 1.0
    mixed = ev.profit_wealth([(g, 0.0), (g, 1.0), (g, 0.0)], 1.0)
    assert mixed["W_T"] == pytest.approx((1 + g) * (1 + g - 1) * (1 + g))
    assert all(w >= -1e-12 for w in mixed["path"])
    with pytest.raises(ValueError):
        ev.profit_wealth([(1.0, 0.0)])

"""The trained regime model can only shrink size, is monotone in its main driver, and loads from config."""
from __future__ import annotations

from datetime import date

import pytest

from agent.core.config import ROOT
from agent.core.regime_model import RegimeModel

PATH = ROOT / "config" / "regime_model.json"
pytestmark = pytest.mark.skipif(not PATH.exists(), reason="config/regime_model.json not trained yet")


def _feats(slope: float = 0.89, gap: float = 0.0, vix: float = 16.3) -> dict:
    spx = [100 * (1 + 0.0005 * i) for i in range(30)]
    f = RegimeModel.market_features(spx, [vix], [vix / slope], 100.0, 100.0 * (1 + gap))
    f.update(RegimeModel.calendar_flags(date(2026, 9, 2)))
    return f


def test_model_loads_and_predicts_in_unit_interval():
    rm = RegimeModel(PATH)
    out = rm.predict(_feats())
    assert 0.0 < out.p_inside < 1.0
    assert out.multiplier in (0.0, 0.5, 1.0)
    assert set(out.features) == set(rm.features)


def test_multiplier_never_exceeds_one_and_is_monotone_in_slope():
    rm = RegimeModel(PATH)
    calm = rm.predict(_feats(slope=0.80))
    inverted = rm.predict(_feats(slope=1.10))
    assert calm.multiplier <= 1.0 and inverted.multiplier <= 1.0
    assert calm.p_inside > inverted.p_inside          # slope coefficient is negative in the fitted model
    assert inverted.multiplier <= calm.multiplier


def test_calendar_flags():
    f = RegimeModel.calendar_flags(date(2026, 9, 4))     # first Friday of September
    assert f["is_first_friday"] == 1 and f["is_third_friday"] == 0 and f["dow_0"] == 0
    f = RegimeModel.calendar_flags(date(2026, 9, 18))
    assert f["is_third_friday"] == 1

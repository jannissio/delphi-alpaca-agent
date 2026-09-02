"""Runtime side of the regime model trained by scripts/train_regime_model.py.

Loads config/regime_model.json (a standardised logistic regression), builds the same features
from live data that the training used (all known at the morning entry), and returns the
probability that the session finishes inside the short strikes plus a size multiplier in
{1.0, 0.5, 0.0}. The multiplier can only shrink the size decided by the deterministic rules.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class RegimeModelOutput:
    p_inside: float
    multiplier: float
    features: dict
    z: float
    thresholds: dict
    name: str
    reason: str


class RegimeModel:
    def __init__(self, path: Path):
        self.path = path
        self.spec = json.loads(path.read_text(encoding="utf-8"))
        self.features: list[str] = self.spec["features"]

    @staticmethod
    def calendar_flags(d: date) -> dict:
        return {
            "is_first_friday": int(d.weekday() == 4 and d.day <= 7),
            "is_third_friday": int(d.weekday() == 4 and 15 <= d.day <= 21),
            "dow_0": int(d.weekday() == 0), "dow_1": int(d.weekday() == 1),
            "dow_2": int(d.weekday() == 2), "dow_3": int(d.weekday() == 3),
        }

    @staticmethod
    def market_features(spx_closes: list[float], vix_closes: list[float], vix3m_closes: list[float],
                        spy_prev_close: Optional[float], spy_open_today: Optional[float]) -> dict:
        """Same definitions as scripts/history_data.py, using PRIOR closes only (plus today's open)."""
        if len(spx_closes) < 22 or len(vix_closes) < 1 or len(vix3m_closes) < 1:
            raise ValueError("insufficient history for regime features")
        rets = [math.log(spx_closes[i] / spx_closes[i - 1]) for i in range(1, len(spx_closes))]

        def sd(x: list[float]) -> float:
            m = sum(x) / len(x)
            return math.sqrt(sum((v - m) ** 2 for v in x) / (len(x) - 1))

        rv5 = sd(rets[-5:]) * math.sqrt(252) * 100
        rv20 = sd(rets[-20:]) * math.sqrt(252) * 100
        vix_prev = vix_closes[-1]
        gap = (spy_open_today / spy_prev_close - 1.0) if (spy_open_today and spy_prev_close) else 0.0
        return {
            "vix_prev": vix_prev,
            "slope_prev": vix_prev / vix3m_closes[-1],
            "rv5_over_vix": rv5 / vix_prev,
            "rv20_over_vix": rv20 / vix_prev,
            "gap": gap,
            "absret_prev": abs(rets[-1]) * 100,
        }

    def predict(self, features: dict) -> RegimeModelOutput:
        z = float(self.spec["intercept"])
        used = {}
        for f in self.features:
            x = float(features[f])
            used[f] = x
            z += float(self.spec["coef"][f]) * (x - float(self.spec["mean"][f])) / float(self.spec["std"][f])
        p = 1.0 / (1.0 + math.exp(-z))
        th = self.spec["thresholds"]
        if not self.spec.get("use_taper", True):
            mult, reason = 1.0, "taper disabled by validation"
        elif p < float(th["p_zero"]):
            mult, reason = 0.0, f"p_inside {p:.3f} below p_zero {th['p_zero']}: bottom decile of history"
        elif p < float(th["p_half"]):
            mult, reason = 0.5, f"p_inside {p:.3f} below p_half {th['p_half']}: bottom tercile of history"
        else:
            mult, reason = 1.0, f"p_inside {p:.3f} at or above p_half {th['p_half']}"
        return RegimeModelOutput(p_inside=p, multiplier=mult, features=used, z=z, thresholds=dict(th),
                                 name=self.spec.get("name", "regime_model"), reason=reason)

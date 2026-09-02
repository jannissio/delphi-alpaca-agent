"""Position sizing from the max-loss budget with a continuous drawdown taper.

Evidence (research C, section 5.2): 2 % of capital per session, 6 % for the campaign,
budget scaled by remaining/total (Grossman & Zhou 1993). Kelly at the measured mean is
zero, so nothing here grows with wins; it only shrinks with losses.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Budget:
    capital: float
    session_budget_nominal: float
    campaign_budget: float
    campaign_loss_so_far: float      # realised + unrealised, positive number = loss
    session_risk_committed: float    # sum of max loss of positions opened this session
    regime_multiplier: float         # 1.0 full, 0.5 half, 0.0 none (VIX/VIX3M slope)

    @property
    def taper(self) -> float:
        remaining = max(self.campaign_budget - self.campaign_loss_so_far, 0.0)
        return min(1.0, remaining / self.campaign_budget) if self.campaign_budget > 0 else 0.0

    @property
    def session_budget(self) -> float:
        return self.session_budget_nominal * self.taper * self.regime_multiplier

    @property
    def session_remaining(self) -> float:
        return max(self.session_budget - self.session_risk_committed, 0.0)


def contracts_for(budget: Budget, max_loss_per_package: float, max_order_max_loss: float,
                  max_contracts: int, pilot_first_order: bool, positions_planned: int = 1) -> int:
    """Largest integer qty whose max loss fits the session remainder, order cap and contract cap."""
    if max_loss_per_package <= 0:
        return 0
    per_position = budget.session_remaining / max(positions_planned, 1)
    cap = min(per_position, max_order_max_loss)
    qty = int(math.floor(cap / max_loss_per_package))
    qty = max(0, min(qty, max_contracts))
    if pilot_first_order and qty > 1:
        qty = 1
    return qty


def regime_multiplier(slope: float, full_below: float, half_below: float) -> float:
    if slope < full_below:
        return 1.0
    if slope < half_below:
        return 0.5
    return 0.0

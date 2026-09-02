"""Anytime-valid evidence at T = 3 (docs/THEORY.md, section 9).

Two test supermartingales built from the per-session ledger, reported and never used to halt:

* the **risk process** for the certificate. Under the conditional null E[l_t | F_{t-1}] <= beta*, where
  l_t in [0, 1] is the realised payout ratio of the interval committed on session t,
      W_t = prod_{s <= t} (1 + lambda_s (l_s - beta*)),   lambda_s in [0, 1/beta*] predictable,
  is a non-negative supermartingale with W_0 = 1, so by Ville's inequality P(sup_t W_t >= 1/alpha) <= alpha at every
  stopping time. Large W is evidence AGAINST the certificate. Non-negativity binds at l = 0, hence the cap 1/beta*.
* the **profit process**, the mirror on the scale-free payoff Y_t = g_t - l_t (g = credit / wing at the fill) under
  the null "no profit" E[Y_t | F_{t-1}] <= 0, with eta_t in [0, 1/(1 - g_t)] (non-negativity binds at l = 1).
  Large W is evidence FOR profitability.

The evidence ceiling is arithmetic: T maximal wins (l = 0) with the largest admissible bet give
(1/(1-g))^T, so three perfect sessions at g = 0.20 cannot push an anytime-valid p-value below 1/1.95 = 0.51.

References: Waudby-Smith & Ramdas (JRSS-B 2023); Ramdas, Grunwald, Vovk & Shafer (Statistical Science 2023);
Han & Qu (2026) on why a firing martingale must not be a kill switch.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence


def risk_wealth(losses: Sequence[float], beta_star: float, lam: float = 1.0) -> dict:
    """Wealth of the risk process with a constant, pre-registered bet lam in [0, 1/beta*]."""
    if not (0.0 < beta_star < 1.0):
        raise ValueError("beta_star must lie in (0, 1)")
    if not (0.0 <= lam <= 1.0 / beta_star + 1e-12):
        raise ValueError(f"lambda must lie in [0, 1/beta*] = [0, {1.0 / beta_star:.3f}]")
    w, w_max, path = 1.0, 1.0, []
    for l in losses:
        if not (-1e-12 <= l <= 1.0 + 1e-12):
            raise ValueError(f"payout ratio outside [0, 1]: {l}")
        w *= 1.0 + lam * (l - beta_star)
        path.append(w)
        w_max = max(w_max, w)
    return {"n": len(path), "lambda": lam, "beta_star": beta_star, "W_T": w, "W_max": w_max,
            "p_anytime": min(1.0, 1.0 / w_max), "path": path}


def profit_wealth(pairs: Sequence[tuple[float, float]], eta: Optional[float] = None) -> dict:
    """Wealth of the profit process over (g_t, l_t) pairs. eta = None uses the largest admissible bet 1/(1-g_t)
    (the ceiling-attaining choice, which goes to zero on a full-wing loss); a constant eta is capped at that."""
    w, w_max, path = 1.0, 1.0, []
    for g, l in pairs:
        if not (0.0 <= g < 1.0):
            raise ValueError(f"credit/wing must lie in [0, 1): {g}")
        if not (-1e-12 <= l <= 1.0 + 1e-12):
            raise ValueError(f"payout ratio outside [0, 1]: {l}")
        cap = 1.0 / (1.0 - g)
        e = cap if eta is None else min(eta, cap)
        w *= 1.0 + e * (g - l)
        path.append(w)
        w_max = max(w_max, w)
    return {"n": len(path), "eta": eta, "W_T": w, "W_max": w_max, "p_anytime": min(1.0, 1.0 / w_max), "path": path}


def evidence_ceiling(g: float, T: int) -> float:
    """Largest wealth T maximal wins can produce at credit/wing g: (1/(1-g))^T."""
    if not (0.0 <= g < 1.0):
        raise ValueError("credit/wing must lie in [0, 1)")
    return (1.0 / (1.0 - g)) ** T


def sessions_for_alpha(g: float, alpha: float) -> int:
    """Smallest T such that T perfect sessions reach an anytime-valid p-value <= alpha."""
    if not (0.0 < alpha < 1.0) or not (0.0 < g < 1.0):
        raise ValueError("need 0 < alpha < 1 and 0 < g < 1")
    return int(math.ceil(math.log(1.0 / alpha) / math.log(1.0 / (1.0 - g)) - 1e-12))

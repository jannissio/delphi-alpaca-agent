# Anytime-valid evidence (docs/THEORY.md section 9)

Source: `conformal.json` ledger (618 calibrated sessions, 2024-03-14..2026-09-01), audit log (0 traded sessions with a closed payout ratio). Bets pre-registered: lambda = 1.0 (admissible [0, 10]), eta = 1.0 (capped at 1/(1-g)). Reported, never used to halt.

## Risk process (evidence against the certificate)

Null: E[l_t | past] <= beta* = 0.1. W_T = 9.189e-12, running maximum 2.659, anytime-valid p-value 0.376 (a value below 0.05 would reject the certificate at level 5 %).

| Year | sessions | mean payout ratio | W_T | max W | anytime p |
|---|---|---|---|---|---|
| 2024 | 202 | 0.070 | 5.55e-05 | 2.66 | 0.376 |
| 2025 | 249 | 0.079 | 3.31e-05 | 6.98 | 0.143 |
| 2026 | 167 | 0.090 | 0.005 | 1 | 1.000 |

## Profit process (evidence for profitability, live sessions only)

No traded session with a closed payout ratio yet (the pilot day ran the fixed rule without a committed interval; the first entries arrive after the 2026-09-03 session).

## Evidence ceiling

T maximal wins at credit/wing g cannot produce more than (1/(1-g))^T; the smallest anytime-valid p-value is its reciprocal.

| g | T=1 | T=2 | T=3 | T=5 | T=10 | T=14 | T=20 | sessions for p <= 0.05 |
|---|---|---|---|---|---|---|---|---|
| 0.15 | 1.18 | 1.38 | 1.63 | 2.25 | 5.08 | 9.73 | 25.80 | 19 |
| 0.20 | 1.25 | 1.56 | 1.95 | 3.05 | 9.31 | 22.74 | 86.74 | 14 |
| 0.25 | 1.33 | 1.78 | 2.37 | 4.21 | 17.76 | 56.12 | 315.34 | 11 |

At g = 0.20 three perfect sessions reach 1.95, i.e. p >= 0.51; p <= 0.05 needs 14 consecutive perfect packages. Evidence accrues per package, so two smaller packages per session raise the three-session ceiling to 3.81 at an unchanged risk budget.

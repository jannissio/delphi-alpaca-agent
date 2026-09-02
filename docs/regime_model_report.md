# Regime model and historical benchmark

Generated 2026-09-02T08:01:07 UTC from `state/history/daily.csv`. Assumptions: short distance 0.7 x VIX-implied full-day E|move| (= 1.10 x the straddle-implied remaining move measured live), wing 0.5 % of spot, credit 17% of wing (live chain 2026-09-02), spot 762. Options history is not available on the basic plan; the credit is an assumption, the moves are data.

## Unconditional back-test of the condor rule

| horizon | n | inside rate | mean P&L % | median P&L % | mean $/contract | P05 $/contract | loss share | worst % |
|---|---|---|---|---|---|---|---|---|
| 10:30->close 2024-2026 | 668 | 0.802 | 0.0323 | 0.085 | 24.61 | -314.87 | 0.151 | -0.415 |
| open->close 2018-2026 | 1533 | 0.676 | -0.0119 | 0.085 | -9.05 | -316.23 | 0.275 | -0.415 |
| close->close 1990-2026 (1.10x, overnight incl.) | 4263 | 0.766 | 0.0086 | 0.085 | 6.57 | -316.23 | 0.203 | -0.415 |

By year (mean P&L % per session), 10:30->close: 2024: 0.0251, 2025: 0.0287, 2026: 0.0486
By year, open->close: 2020: 0.0269, 2021: 0.0224, 2022: -0.0892, 2023: -0.0341, 2024: 0.0074, 2025: -0.0023, 2026: 0.0165

## By regime (open->close, 2018-2026)

| VIX/VIX3M slope | n | mean P&L % | inside rate |
|---|---|---|---|
| <0.85 | 466 | 0.0311 | 0.779 |
| 0.85-0.95 | 789 | -0.0196 | 0.649 |
| 0.95-1.00 | 206 | -0.0513 | 0.612 |
| >=1.00 | 72 | -0.0935 | 0.5 |

| VIX level | n | mean P&L % | inside rate |
|---|---|---|---|
| <15 | 270 | 0.0139 | 0.73 |
| 15-21 | 743 | 0.0056 | 0.704 |
| >21 | 520 | -0.0503 | 0.61 |

## Regime model: expanding-window out-of-sample validation

| dataset | OOS years | n OOS | base rate | logit Brier (base) | logit AUC | GBM Brier | GBM AUC |
|---|---|---|---|---|---|---|---|
| A_1030_close | 2025-2026 | 416 | 0.7778 | 0.15332 (0.15088) | 0.5618 | 0.15058 | 0.6044 |
| B_open_close | 2021-2026 | 1170 | 0.8108 | 0.23112 (0.25416) | 0.5575 | 0.23497 | 0.5515 |
| C_close_close | 2012-2026 | 3687 | 0.7622 | 0.17244 (0.17872) | 0.6257 | 0.17503 | 0.6057 |

## Predicted-probability terciles (out of sample) vs realised

**A_1030_close**

| bucket | n | mean p | inside rate | mean P&L % | median P&L % | mean $/contract | loss share |
|---|---|---|---|---|---|---|---|
| low | 139 | 0.777 | 0.77 | 0.0273 | 0.085 | 20.81 | 0.165 |
| mid | 138 | 0.886 | 0.826 | 0.0365 | 0.085 | 27.81 | 0.13 |
| high | 139 | 0.947 | 0.856 | 0.0462 | 0.085 | 35.2 | 0.115 |

**B_open_close**

| bucket | n | mean p | inside rate | mean P&L % | median P&L % | mean $/contract | loss share |
|---|---|---|---|---|---|---|---|
| low | 390 | 0.491 | 0.592 | -0.0438 | 0.085 | -33.38 | 0.364 |
| mid | 390 | 0.645 | 0.656 | -0.0198 | 0.085 | -15.08 | 0.292 |
| high | 390 | 0.76 | 0.697 | -0.0053 | 0.085 | -4.01 | 0.264 |

**C_close_close**

| bucket | n | mean p | inside rate | mean P&L % | median P&L % | mean $/contract | loss share |
|---|---|---|---|---|---|---|---|
| low | 1229 | 0.684 | 0.676 | -0.0286 | 0.085 | -21.78 | 0.291 |
| mid | 1229 | 0.803 | 0.779 | 0.0164 | 0.085 | 12.53 | 0.184 |
| high | 1229 | 0.866 | 0.845 | 0.042 | 0.085 | 31.97 | 0.129 |

## Random-entry Monte Carlo null (2.5-session campaign, 2 contracts per session)

- A_1030_close: mean 97.27 USD, P05 -502.92, median 259.08, P95 259.08, P(negative) 0.239
- B_open_close: mean -35.13 USD, P05 -684.62, median 194.65, P95 259.08, P(negative) 0.396

## Deployed model

`config/regime_model.json`: B_open_close, logistic regression on vix_prev, slope_prev, rv5_over_vix, rv20_over_vix, gap, absret_prev, is_first_friday, is_third_friday, dow_0, dow_1, dow_2, dow_3; thresholds p_half 0.588, p_zero 0.467; taper enabled: True. Coefficients (standardised): vix_prev -0.095, slope_prev -0.395, rv5_over_vix -0.073, rv20_over_vix +0.012, gap +0.280, absret_prev +0.204, is_first_friday -0.017, is_third_friday +0.079, dow_0 +0.103, dow_1 +0.111, dow_2 +0.053, dow_3 -0.037.

Reading guide: the model is used only to shrink size. If the low-probability tercile has no worse P&L than the others out of sample, the taper is disabled and the report says so. No Sharpe ratios are computed: with 2.5 sessions the Probabilistic Sharpe Ratio cannot reach 95 % (research/F2).
# Conformal Condor - experiment output

Target outside probability alpha = 0.2; wing 0.5 % of spot; baseline k = 0.7; ACI gamma = 0.005.

Calibrated horizon factor theta = 0.556 (sd of the remaining-horizon move / sd of the full VIX day) so that the model credit at the baseline width equals the live 17 % of wing.

Risk-neutral width for alpha = 0.2: k_Q = 0.894 impl_move units (the market's own 80 % interval). Baseline k = 0.7.


## A_1030_close (2024-)

Evaluation sample: 2024-12-30 to 2026-09-01, n = 418 (common to all methods).

| method | n | coverage | mean k | sd k | model credit % | Q(out) | P(out) | Q-P pp | P&L % fixed credit | P&L % model credit | $/contract | loss share | worst % | t |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline k=0.70 | 418 | 0.818 | 0.7 | 0.0 | 0.0868 | 0.174 | 0.182 | -0.8 | 0.0369 | 0.0387 | 29.47 | 0.136 | -0.422 | 6.31 |
| split conformal | 418 | 0.813 | 0.712 | 0.105 | 0.0861 | 0.172 | 0.187 | -1.4 | 0.0363 | 0.0374 | 28.51 | 0.136 | -0.446 | 6.09 |
| split conformal + ACI | 418 | 0.794 | 0.682 | 0.133 | 0.094 | 0.188 | 0.206 | -1.8 | 0.0312 | 0.0402 | 30.64 | 0.141 | -0.447 | 6.28 |
| CQR | 418 | 0.799 | 0.726 | 0.26 | 0.0915 | 0.183 | 0.201 | -1.8 | 0.035 | 0.0415 | 31.65 | 0.132 | -0.496 | 6.54 |
| CQR + ACI | 418 | 0.794 | 0.73 | 0.269 | 0.0914 | 0.183 | 0.206 | -2.3 | 0.0347 | 0.0411 | 31.31 | 0.139 | -0.496 | 6.49 |
| split conformal + ACI, PQ-gated | 366 | 0.779 | 0.645 | 0.097 | 0.1001 | 0.2 | 0.221 | -2.1 | 0.029 | 0.0441 | 33.63 | 0.148 | -0.425 | 6.41 |
| CQR + ACI, PQ-gated | 346 | 0.772 | 0.631 | 0.132 | 0.1044 | 0.209 | 0.228 | -1.9 | 0.0332 | 0.0526 | 40.09 | 0.147 | -0.439 | 7.78 |
| baseline, credit-gated | 47 | 0.681 | 0.7 | 0.0 | 0.1067 | 0.213 | 0.319 | -10.6 | -0.0187 | 0.003 | 2.26 | 0.255 | -0.4 | 0.11 |
| CQR + ACI, credit-gated | 184 | 0.707 | 0.531 | 0.076 | 0.1285 | 0.257 | 0.293 | -3.6 | 0.0246 | 0.0681 | 51.89 | 0.158 | -0.382 | 7.19 |

Gate hit rate (share of sessions traded): split conformal + ACI, PQ-gated 0.876, CQR + ACI, PQ-gated 0.828, baseline, credit-gated 0.112, CQR + ACI, credit-gated 0.44


### A_1030_close (2024-): coverage and P&L (model credit) by year

| year | baseline k=0.70 cov / P&L% | split conformal + ACI cov / P&L% | CQR + ACI cov / P&L% |
|---|---|---|---|
| 2024 | 1.0 / 0.0822 | 0.0 / 0.0529 | 1.0 / 0.0685 |
| 2025 | 0.787 / 0.0306 | 0.799 / 0.0273 | 0.795 / 0.0289 |
| 2026 | 0.862 / 0.0502 | 0.796 / 0.0593 | 0.79 / 0.059 |

### A_1030_close (2024-): empirical coverage vs break-even inside probability (baseline k = 0.7, fixed credit 17% of wing)

| bucket | n | coverage P | Q(inside)=1-c/w | E[loss|outside] % | break-even P* | P - P* pp | mean P&L % |
|---|---|---|---|---|---|---|---|
| slope_prev <0.85 | 132 | 0.879 | 0.83 | 0.225 | 0.726 | 15.3 | 0.0577 |
| slope_prev 0.85-0.95 | 208 | 0.846 | 0.83 | 0.214 | 0.716 | 13.0 | 0.052 |
| slope_prev 0.95-1.00 | 40 | 0.725 | 0.83 | 0.377 | 0.816 | -9.1 | -0.0187 |
| slope_prev >=1.00 | 38 | 0.553 | 0.83 | 0.323 | 0.792 | -23.9 | -0.0596 |
| vix_prev <15 | 35 | 0.971 | 0.83 | 0.04 | 0.32 | 65.2 | 0.0839 |
| vix_prev 15-21 | 302 | 0.844 | 0.83 | 0.242 | 0.74 | 10.5 | 0.0474 |
| vix_prev >21 | 81 | 0.654 | 0.83 | 0.311 | 0.785 | -13.1 | -0.0226 |
| ALL | 418 | 0.818 | 0.83 | 0.265 | 0.757 | 6.1 | 0.0369 |

### A_1030_close (2024-): conditional coverage of the CQR+ACI interval by regime

| bucket | n | conformal coverage | baseline coverage | mean k conformal |
|---|---|---|---|---|
| slope_prev <0.85 | 132 | 0.818 | 0.879 | 0.63 |
| slope_prev 0.85-0.95 | 208 | 0.812 | 0.846 | 0.743 |
| slope_prev 0.95-1.00 | 40 | 0.7 | 0.725 | 0.818 |
| slope_prev >=1.00 | 38 | 0.711 | 0.553 | 0.908 |
| vix_prev <15 | 35 | 0.914 | 0.971 | 0.598 |
| vix_prev 15-21 | 302 | 0.791 | 0.844 | 0.714 |
| vix_prev >21 | 81 | 0.753 | 0.654 | 0.843 |

### A_1030_close (2024-): split conformal on the longest available sample (2024-07-02 to 2026-09-01, n = 543)

| method | n | coverage | mean k | P&L % fixed credit | P&L % model credit | t |
|---|---|---|---|---|---|---|
| baseline k=0.70 | 543 | 0.823 | 0.7 | 0.0375 | 0.0384 | 7.2 |
| split conformal | 543 | 0.823 | 0.738 | 0.0401 | 0.0353 | 6.8 |
| split conformal + ACI | 543 | 0.81 | 0.711 | 0.0359 | 0.0379 | 7.01 |

## B_open_close (2018-)

Evaluation sample: 2022-07-21 to 2026-09-01, n = 1033 (common to all methods).

| method | n | coverage | mean k | sd k | model credit % | Q(out) | P(out) | Q-P pp | P&L % fixed credit | P&L % model credit | $/contract | loss share | worst % | t |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline k=0.70 | 1033 | 0.67 | 0.7 | 0.0 | 0.085 | 0.17 | 0.33 | -16.0 | -0.0125 | -0.0125 | -9.54 | 0.284 | -0.434 | -2.38 |
| split conformal | 1033 | 0.832 | 0.993 | 0.117 | 0.0391 | 0.078 | 0.168 | -9.0 | 0.0383 | -0.0076 | -5.78 | 0.152 | -0.479 | -1.89 |
| split conformal + ACI | 1033 | 0.821 | 0.985 | 0.182 | 0.0422 | 0.084 | 0.179 | -9.5 | 0.0359 | -0.0069 | -5.27 | 0.159 | -0.485 | -1.7 |
| CQR | 1033 | 0.806 | 0.963 | 0.217 | 0.0466 | 0.093 | 0.194 | -10.0 | 0.0322 | -0.0062 | -4.73 | 0.163 | -0.487 | -1.49 |
| CQR + ACI | 1033 | 0.801 | 0.963 | 0.223 | 0.0472 | 0.094 | 0.199 | -10.5 | 0.031 | -0.0068 | -5.17 | 0.165 | -0.489 | -1.61 |
| split conformal + ACI, PQ-gated | 374 | 0.797 | 0.806 | 0.038 | 0.064 | 0.128 | 0.203 | -7.5 | 0.0326 | 0.0116 | 8.83 | 0.166 | -0.45 | 1.72 |
| CQR + ACI, PQ-gated | 420 | 0.726 | 0.752 | 0.097 | 0.0733 | 0.147 | 0.274 | -12.7 | 0.0156 | 0.0038 | 2.93 | 0.21 | -0.459 | 0.53 |
| baseline, credit-gated | 112 | 0.536 | 0.7 | 0.0 | 0.1063 | 0.213 | 0.464 | -25.2 | -0.0931 | -0.0718 | -54.71 | 0.411 | -0.4 | -3.46 |
| CQR + ACI, credit-gated | 43 | 0.628 | 0.56 | 0.058 | 0.1147 | 0.229 | 0.372 | -14.3 | -0.0008 | 0.0289 | 22.02 | 0.256 | -0.389 | 1.3 |

Gate hit rate (share of sessions traded): split conformal + ACI, PQ-gated 0.362, CQR + ACI, PQ-gated 0.407, baseline, credit-gated 0.108, CQR + ACI, credit-gated 0.042


### B_open_close (2018-): coverage and P&L (model credit) by year

| year | baseline k=0.70 cov / P&L% | split conformal + ACI cov / P&L% | CQR + ACI cov / P&L% |
|---|---|---|---|
| 2022 | 0.544 / -0.0582 | 0.877 / -0.0309 | 0.825 / -0.0316 |
| 2023 | 0.612 / -0.0371 | 0.84 / -0.0175 | 0.78 / -0.0211 |
| 2024 | 0.718 / 0.0001 | 0.821 / -0.0048 | 0.825 / 0.0021 |
| 2025 | 0.692 / -0.0003 | 0.8 / -0.0021 | 0.812 / -0.0062 |
| 2026 | 0.737 / 0.0181 | 0.784 / 0.0147 | 0.76 / 0.0174 |

### B_open_close (2018-): empirical coverage vs break-even inside probability (baseline k = 0.7, fixed credit 17% of wing)

| bucket | n | coverage P | Q(inside)=1-c/w | E[loss|outside] % | break-even P* | P - P* pp | mean P&L % |
|---|---|---|---|---|---|---|---|
| slope_prev <0.85 | 246 | 0.748 | 0.83 | 0.244 | 0.742 | 0.6 | 0.0235 |
| slope_prev 0.85-0.95 | 589 | 0.671 | 0.83 | 0.288 | 0.772 | -10.2 | -0.01 |
| slope_prev 0.95-1.00 | 144 | 0.611 | 0.83 | 0.344 | 0.802 | -19.1 | -0.0489 |
| slope_prev >=1.00 | 54 | 0.463 | 0.83 | 0.357 | 0.807 | -34.5 | -0.1065 |
| vix_prev <15 | 270 | 0.73 | 0.83 | 0.263 | 0.756 | -2.6 | 0.0139 |
| vix_prev 15-21 | 543 | 0.681 | 0.83 | 0.282 | 0.768 | -8.7 | -0.0049 |
| vix_prev >21 | 220 | 0.568 | 0.83 | 0.344 | 0.802 | -23.4 | -0.0636 |
| ALL | 1033 | 0.67 | 0.83 | 0.295 | 0.776 | -10.7 | -0.0125 |

### B_open_close (2018-): conditional coverage of the CQR+ACI interval by regime

| bucket | n | conformal coverage | baseline coverage | mean k conformal |
|---|---|---|---|---|
| slope_prev <0.85 | 246 | 0.825 | 0.748 | 0.887 |
| slope_prev 0.85-0.95 | 589 | 0.798 | 0.671 | 0.958 |
| slope_prev 0.95-1.00 | 144 | 0.806 | 0.611 | 1.082 |
| slope_prev >=1.00 | 54 | 0.704 | 0.463 | 1.045 |
| vix_prev <15 | 270 | 0.826 | 0.73 | 0.966 |
| vix_prev 15-21 | 543 | 0.792 | 0.681 | 0.91 |
| vix_prev >21 | 220 | 0.791 | 0.568 | 1.09 |

### B_open_close (2018-): split conformal on the longest available sample (2021-07-23 to 2026-09-01, n = 1283)

| method | n | coverage | mean k | P&L % fixed credit | P&L % model credit | t |
|---|---|---|---|---|---|---|
| baseline k=0.70 | 1283 | 0.656 | 0.7 | -0.0193 | -0.0171 | -3.51 |
| split conformal | 1283 | 0.807 | 0.96 | 0.0274 | -0.0124 | -3.12 |
| split conformal + ACI | 1283 | 0.805 | 0.976 | 0.0293 | -0.0109 | -2.8 |

## Sensitivity of the model-credit P&L to the horizon factor theta

theta is the one free parameter of the modelled risk-neutral measure. It was calibrated to a single live chain. The table shows that the LEVEL of the model-credit P&L is a function of theta; the RANKING of the methods is much less sensitive.

| horizon | theta | k_Q | baseline P&L % | split conf + ACI P&L % | CQR + ACI P&L % |
|---|---|---|---|---|---|
| A_1030_close (2024-) | 0.5 | 0.803 | 0.0181 | 0.0196 | 0.0216 |
| A_1030_close (2024-) | 0.556 | 0.893 | 0.0386 | 0.0401 | 0.041 |
| A_1030_close (2024-) | 0.6 | 0.964 | 0.0546 | 0.056 | 0.056 |
| A_1030_close (2024-) | 0.65 | 1.044 | 0.0722 | 0.0735 | 0.0727 |
| A_1030_close (2024-) | 0.7 | 1.124 | 0.0892 | 0.0903 | 0.0886 |
| B_open_close (2018-) | 0.5 | 0.803 | -0.0328 | -0.0202 | -0.0207 |
| B_open_close (2018-) | 0.556 | 0.893 | -0.0126 | -0.007 | -0.0069 |
| B_open_close (2018-) | 0.6 | 0.964 | 0.0032 | 0.0044 | 0.0049 |
| B_open_close (2018-) | 0.65 | 1.044 | 0.0207 | 0.018 | 0.0187 |
| B_open_close (2018-) | 0.7 | 1.124 | 0.0375 | 0.0318 | 0.0327 |

## Empirical Kelly on the realised P&L distribution (model credit)

f* maximises E[log(1 + f * pnl / maxloss)] over the realised sample. It is an in-sample upper bound, reported to show the order of magnitude only.

| horizon | method | mean P&L % | full Kelly f* | 1/4 Kelly | max loss used |
|---|---|---|---|---|---|
| A_1030_close (2024-) | baseline k=0.70 | 0.0387 | 0.575 | 0.144 | 0.422 % of spot |
| A_1030_close (2024-) | split conformal + ACI | 0.0402 | 0.61 | 0.152 | 0.447 % of spot |
| A_1030_close (2024-) | CQR + ACI | 0.0411 | 0.675 | 0.169 | 0.496 % of spot |
| B_open_close (2018-) | baseline k=0.70 | -0.0125 | 0.0 | 0.0 | 0.434 % of spot |
| B_open_close (2018-) | split conformal + ACI | -0.0069 | 0.0 | 0.0 | 0.485 % of spot |
| B_open_close (2018-) | CQR + ACI | -0.0068 | 0.0 | 0.0 | 0.489 % of spot |

## Kelly fraction for the condor (two-state approximation)

f* = (p*b - (1-p)) / b with b = c/L, c = credit, L = max loss = wing - credit.

| b = c/L | p | full Kelly f* | half Kelly | quarter Kelly |
|---|---|---|---|---|
| 0.15 | 0.75 | -0.917 | -0.458 | -0.229 |
| 0.15 | 0.8 | -0.533 | -0.267 | -0.133 |
| 0.15 | 0.85 | -0.15 | -0.075 | -0.038 |
| 0.2 | 0.75 | -0.5 | -0.25 | -0.125 |
| 0.2 | 0.8 | -0.2 | -0.1 | -0.05 |
| 0.2 | 0.85 | 0.1 | 0.05 | 0.025 |
| 0.25 | 0.75 | -0.25 | -0.125 | -0.062 |
| 0.25 | 0.8 | 0.0 | 0.0 | 0.0 |
| 0.25 | 0.85 | 0.25 | 0.125 | 0.062 |
| 0.3 | 0.75 | -0.083 | -0.042 | -0.021 |
| 0.3 | 0.8 | 0.133 | 0.067 | 0.033 |
| 0.3 | 0.85 | 0.35 | 0.175 | 0.087 |
| 0.41 | 0.75 | 0.14 | 0.07 | 0.035 |
| 0.41 | 0.8 | 0.312 | 0.156 | 0.078 |
| 0.41 | 0.85 | 0.484 | 0.242 | 0.121 |
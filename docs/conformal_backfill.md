# Conformal Condor: back-fill from history

Source: `daily.csv:ratio_1030 2024-01-02..2026-09-01 (668 sessions), replayed 2026-09-02T09:08:02Z`.
Parameters (config/strategy.yaml `conformal`): alpha_target 0.2, gamma 0.005, window 250, clip [0.35, 1.6], margin 0.05, min_scores 50. Score = |close / p_10:30 - 1| / VIX_prev-implied expected absolute daily move (identical unit live and in history).

State written: alpha_t = **0.2180** after 618 calibrated sessions; 250 scores in the window; updated through 2026-09-01.

## Coverage and sharpness (split conformal + ACI, out of sample by construction)

| sample | n | coverage | target | mean k | sd k | alpha at end |
|---|---|---|---|---|---|---|
| all calibrated sessions | 618 | 0.806 | 0.80 | 0.728 | 0.108 | 0.2180 |
| since 2024-12-30 (research/G sample) | 418 | 0.792 | 0.80 | 0.683 | 0.091 | 0.2180 |

## By year: conformal vs the fixed rule (k = 0.7 x VIX-implied move, the live 1.10 x straddle geometry)

| year | n | conformal coverage | mean k | fixed-rule coverage |
|---|---|---|---|---|
| 2024 | 202 | 0.832 | 0.822 | 0.772 |
| 2025 | 249 | 0.799 | 0.731 | 0.787 |
| 2026 | 167 | 0.784 | 0.610 | 0.862 |

Read: the conformal radius moves with the calibration window and alpha_t so that coverage stays near the
target in every year; the fixed rule's coverage is whatever the year's realised-to-implied ratio makes it.
Coverage is the quantity with a guarantee; P&L is not (research/G, sections 5.3 and 5.8). No option prices
exist in this history, so the P-versus-Q gate cannot be back-tested here; it is evaluated live, per session,
from the audit record (`conformal` events: Q_mid, P_mid, gap, decision).

## Alpha path (last 20 calibrated sessions)

| date | k | ratio | err | alpha after |
|---|---|---|---|---|
| 2026-08-05 | 0.628 | 0.654 | 1 | 0.2040 |
| 2026-08-06 | 0.633 | 0.376 | 0 | 0.2050 |
| 2026-08-07 | 0.633 | 0.006 | 0 | 0.2060 |
| 2026-08-10 | 0.633 | 0.268 | 0 | 0.2070 |
| 2026-08-11 | 0.633 | 0.550 | 0 | 0.2080 |
| 2026-08-12 | 0.627 | 0.044 | 0 | 0.2090 |
| 2026-08-13 | 0.627 | 0.234 | 0 | 0.2100 |
| 2026-08-14 | 0.627 | 0.241 | 0 | 0.2110 |
| 2026-08-17 | 0.627 | 0.488 | 0 | 0.2120 |
| 2026-08-18 | 0.627 | 0.210 | 0 | 0.2130 |
| 2026-08-19 | 0.609 | 0.136 | 0 | 0.2140 |
| 2026-08-20 | 0.606 | 0.610 | 1 | 0.2100 |
| 2026-08-21 | 0.610 | 0.148 | 0 | 0.2110 |
| 2026-08-24 | 0.610 | 0.128 | 0 | 0.2120 |
| 2026-08-25 | 0.609 | 0.189 | 0 | 0.2130 |
| 2026-08-26 | 0.609 | 0.222 | 0 | 0.2140 |
| 2026-08-27 | 0.609 | 0.197 | 0 | 0.2150 |
| 2026-08-28 | 0.609 | 0.357 | 0 | 0.2160 |
| 2026-08-31 | 0.605 | 0.350 | 0 | 0.2170 |
| 2026-09-01 | 0.605 | 0.281 | 0 | 0.2180 |

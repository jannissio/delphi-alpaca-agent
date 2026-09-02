# Conformal Risk Control Condor: back-fill from history

Source: `daily.csv:ratio_1030 2024-01-02..2026-09-01 (668 sessions), wing 0.50 % of spot, replayed 2026-09-02T12:54:35Z`.
Parameters (config/strategy.yaml `conformal`): rule crc, beta_target 0.1, alpha_target 0.2, gamma 0.005, window 250, clip [0.35, 1.6], margin 0.05, min_scores 50. Score = |close / p_10:30 - 1| / VIX_prev-implied expected absolute daily move (identical unit live and in history); payout ratio = min((score - k)+, omega) / omega with omega = wing / implied move.

State written: beta_t = **0.1642**, alpha_t = **0.2180** after 618 calibrated sessions; 250 scores in the window; updated through 2026-09-01.

## Risk track (conformal risk control + Rolling RC): realised payout ratio vs the beta target

| sample | n | realised payout ratio | target beta | mean k_crc | fixed rule k=0.70 payout ratio |
|---|---|---|---|---|---|
| all calibrated sessions | 618 | 0.0792 | 0.10 | 0.809 | 0.1039 |
| since 2024-12-30 (research/G sample) | 418 | 0.0831 | 0.10 | 0.730 | 0.0962 |

## Coverage track (split conformal + ACI): coverage vs the 1 - alpha target

| sample | n | coverage | target | mean k_cov | sd k_cov | fixed rule k=0.70 coverage |
|---|---|---|---|---|---|---|
| all calibrated sessions | 618 | 0.806 | 0.80 | 0.728 | 0.108 | 0.803 |
| since 2024-12-30 (research/G sample) | 418 | 0.792 | 0.80 | 0.683 | - | - |

## By year

| year | n | CRC payout ratio | mean k_crc | fixed-rule payout ratio | conformal coverage | mean k_cov | fixed-rule coverage |
|---|---|---|---|---|---|---|---|
| 2024 | 202 | 0.0703 | 0.972 | 0.1188 | 0.832 | 0.822 | 0.772 |
| 2025 | 249 | 0.0791 | 0.795 | 0.1126 | 0.799 | 0.731 | 0.787 |
| 2026 | 167 | 0.0901 | 0.630 | 0.0729 | 0.784 | 0.610 | 0.862 |

Read: the risk track moves the radius so that the realised payout ratio stays near beta in every year, which is
the quantity the gate certifies; the coverage track does the same for the miss frequency; the fixed rule's
payout ratio and coverage are whatever the year's realised-to-implied ratio makes them. Both quantities have
a finite-sample guarantee under exchangeability (docs/THEORY.md); P&L does not (research/G, sections 5.3 and 5.8).
No option prices exist in this history, so the P-versus-Q gate cannot be back-tested here; it is evaluated live,
per session, from the audit record (`conformal` events: credit/wing, certified payout, gap, decision).

## Level paths (last 20 calibrated sessions)

| date | k_crc | k_cov | ratio | payout ratio | beta after | miss | alpha after |
|---|---|---|---|---|---|---|---|
| 2026-08-05 | 0.592 | 0.628 | 0.654 | 0.104 | 0.1551 | 1 | 0.2040 |
| 2026-08-06 | 0.584 | 0.633 | 0.376 | 0.000 | 0.1556 | 0 | 0.2050 |
| 2026-08-07 | 0.576 | 0.633 | 0.006 | 0.000 | 0.1561 | 0 | 0.2060 |
| 2026-08-10 | 0.573 | 0.633 | 0.268 | 0.000 | 0.1566 | 0 | 0.2070 |
| 2026-08-11 | 0.580 | 0.633 | 0.550 | 0.000 | 0.1571 | 0 | 0.2080 |
| 2026-08-12 | 0.577 | 0.627 | 0.044 | 0.000 | 0.1576 | 0 | 0.2090 |
| 2026-08-13 | 0.567 | 0.627 | 0.234 | 0.000 | 0.1581 | 0 | 0.2100 |
| 2026-08-14 | 0.568 | 0.627 | 0.241 | 0.000 | 0.1586 | 0 | 0.2110 |
| 2026-08-17 | 0.563 | 0.627 | 0.488 | 0.000 | 0.1591 | 0 | 0.2120 |
| 2026-08-18 | 0.575 | 0.627 | 0.210 | 0.000 | 0.1596 | 0 | 0.2130 |
| 2026-08-19 | 0.582 | 0.609 | 0.136 | 0.000 | 0.1601 | 0 | 0.2140 |
| 2026-08-20 | 0.566 | 0.606 | 0.610 | 0.066 | 0.1602 | 1 | 0.2100 |
| 2026-08-21 | 0.581 | 0.610 | 0.148 | 0.000 | 0.1607 | 0 | 0.2110 |
| 2026-08-24 | 0.570 | 0.610 | 0.128 | 0.000 | 0.1612 | 0 | 0.2120 |
| 2026-08-25 | 0.579 | 0.609 | 0.189 | 0.000 | 0.1617 | 0 | 0.2130 |
| 2026-08-26 | 0.574 | 0.609 | 0.222 | 0.000 | 0.1622 | 0 | 0.2140 |
| 2026-08-27 | 0.571 | 0.609 | 0.197 | 0.000 | 0.1627 | 0 | 0.2150 |
| 2026-08-28 | 0.561 | 0.609 | 0.357 | 0.000 | 0.1632 | 0 | 0.2160 |
| 2026-08-31 | 0.560 | 0.605 | 0.350 | 0.000 | 0.1637 | 0 | 0.2170 |
| 2026-09-01 | 0.566 | 0.605 | 0.281 | 0.000 | 0.1642 | 0 | 0.2180 |

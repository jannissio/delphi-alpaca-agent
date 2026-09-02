# The Conformal Risk Control Condor: definitions, theorems, proofs

*Delphi, lablab.ai x Alpaca AI Trading Agents Hackathon, 2026-09-02. Everything below is either elementary or a direct
application of a published theorem; the published steps are cited, not re-proved in full. The deterministic lemmas are
additionally machine-checked in Lean 4 where `lean/README.md` says so.*

## 0. Setting and notation

A session starts at the entry price `S_0` (the anchor) and ends at the close `S_T`. Let `m > 0` be the reference implied
move in dollars, `m = S_0 * v / 100 / sqrt(252) * sqrt(2/pi)` with `v` the previous VIX close: the expected absolute daily
move of a normal with the VIX's variance. The **score** of the session is

    r = |S_T - S_0| / m  >= 0.

A symmetric iron condor sold at entry has short strikes at `S_0 +- d` and bought wings at `S_0 +- (d + w)`, `d, w > 0`,
and receives the credit `c` per share for the package. Write `k = d / m` (radius in implied-move units) and
`omega = w / m` (wing in implied-move units).

**Definition (payout ratio).** `loss(r, k) = min((r - k)^+, omega) / omega`, where `x^+ = max(x, 0)`.

*Remarks on the normaliser.* (a) Any constant misspecification of `m` is absorbed exactly: `m -> c m` implies
`r -> r / c` and `k_hat -> k_hat / c`, so the strike distance `k_hat m` is unchanged. The factor `sqrt(2/pi)`, the
calendar-time scaling of a 30-day index and the VIX's own risk premium are therefore not free parameters of the rule.
In the vocabulary of the conformal literature `r` is a normalised nonconformity score with a difficulty estimator.
(b) What is not absorbed is a regime-varying scale. The numerator measures entry-to-close (about 4.75 business hours
from a 10:30 ET anchor) while `v` is a full-day, calendar-time index, and Andersen, Thyrsgaard & Todorov (2019) reject a
time-invariant intraday periodicity for the S&P 500: "when volatility is elevated, the period preceding the market
close constitutes a significantly higher fraction of the total daily integrated volatility than during low volatility
regimes" (their abstract; the average close volatility is about three times the lunchtime level). The ratio
`c = c(v)` then varies with the regime, and conditional coverage degrades on stressed days, with strikes relatively
too narrow. We state this as the one genuine scientific limitation of the score, measure it on our own data where the
history allows (payout ratio by VIX tercile, `docs/conformal_backfill.md`), and do not switch the live normaliser
two days before a deadline, because a mixed-definition calibration window would break exchangeability.

## 1. Lemma 1 (payout structure)

For every realised close, the amount the condor pays to its buyer at expiry is `X = w * loss(r, k)`, and the seller's
payoff is `Pi = c - X`. Moreover `0 <= loss <= 1`, `loss` is non-increasing and continuous in `k`, and `loss = 0`
exactly when `r <= k`.

*Proof.* The call spread pays `min((S_T - S_0 - d)^+, w)` and the put spread pays `min((S_0 - d - S_T)^+, w)`; at most
one of them is positive, and their sum is `min((|S_T - S_0| - d)^+, w) = w * min((r - k)^+, omega) / omega`. The bounds,
monotonicity and continuity follow from those of `x -> min(x^+, omega)`. The zero set is `{r <= k}` because `omega > 0`. QED.

## 2. Lemma 2 (exact P-versus-Q identity)

Let `G` be any probability law of `S_T` and `S_G(x) = G(|S_T - S_0| > x)` its survival function. Then

    E_G[X] = integral_{d}^{d+w} S_G(x) dx.

Under the market's risk-neutral law `Q` (one-day horizon, rates neglected) the mid credit is `c = E_Q[X]`, hence

    E_P[Pi] = integral_{d}^{d+w} [ S_Q(x) - S_P(x) ] dx,

and in particular `c / w` is the average of `S_Q` over the band `[d, d+w]`, which is `Q(|S_T - S_0| > d + w/2)` to
first order in `w` (Breeden & Litzenberger 1978; the digital limit).

*Proof.* Layer-cake: for `Y = |S_T - S_0| >= 0`, `min((Y - d)^+, w) = integral_{d}^{d+w} 1{Y > x} dx`; take expectations
and use Tonelli. Static replication: the condor's short-minus-long legs replicate the payout `X` exactly, so the
no-arbitrage price of the package is `E_Q[X]` (Breeden & Litzenberger 1978 for the density statement; the replication is
Lemma 1). Subtract. The average statement is the identity divided by `w`; the midpoint statement is the mean-value
theorem for the monotone `S_Q`. QED.

*Remark.* Lemma 2 is exact and needs no model. It says what the trade is: a bet that the market's survival function
exceeds the physical one across the wing band. Everything the agent logs (`credit/wing` and its per-side split) is the
left-hand side read off the quote.

## 3. Theorem 3 (finite-sample certificate for the expected payout)

Let `r_1, ..., r_n` be the calibration scores and `r_{n+1}` the score of the coming session, and assume
`(r_1, ..., r_{n+1})` is **exchangeable**. Fix `beta in [1/(n+1), 1]` and today's `omega`. Define the empirical risk
`R_n(k) = (1/n) sum_i loss(r_i, k)` and

    k_hat = inf{ k >= 0 :  n/(n+1) * R_n(k) + 1/(n+1)  <=  beta }.

Then `E[ loss(r_{n+1}, k_hat) ] <= beta`. Consequently, if the nearer short strike is placed at any distance
`d >= k_hat * m` (rounding outward to the strike grid keeps this), then

    E_P[X] <= beta * w      and      E_P[Pi] >= c - beta * w.

**Corollary (gate 31).** If `c / w >= beta + mu`, then `E_P[Pi] >= mu * w`.

*How to read the corollary.* `mu = 0.05` is pre-registered as the modelled round-trip cost of the four legs (about
$20 per contract at a $4 wing against $4-10 of one-tick friction), so `mu w` is a cost budget, not a profit target:
a trade exactly on the gate boundary is certified, in expectation and under exchangeability, not to lose after that
modelled cost, and no more. Decomposing `mu = mu_cost + mu_edge`, the agent ships `mu_edge = 0`. The literature's own
premium for a symmetric one-day band of this width, derived (not measured) in the 2026-09-02 audit from the variance
risk premium, is of the order of 0.05-0.10 of the wing, so the gate asks the market for roughly the average
historical edge rather than more. The credit `c` is read at the expected fill (the natural quote; the mid is logged
alongside), because the certificate must apply to the package that is actually executed.

*Proof.* This is Theorem 1 of Angelopoulos, Bates, Fisch, Lei & Schuster (2024) with `B = 1`: `loss` is non-increasing
and right-continuous in `k` (Lemma 1) and bounded by 1. For completeness, the argument: let
`R_{n+1}(k) = (1/(n+1)) sum_{i<=n+1} loss(r_i, k)` and `k' = inf{k : R_{n+1}(k) <= beta}`. Since `loss <= 1`,
`n/(n+1) R_n(k) + 1/(n+1) >= R_{n+1}(k)` for every `k`, so `{k : n/(n+1) R_n(k) + 1/(n+1) <= beta}` is a subset of
`{k : R_{n+1}(k) <= beta}` and therefore `k' <= k_hat`. By monotonicity `loss(r_{n+1}, k_hat) <= loss(r_{n+1}, k')`.
Now `k'` is a symmetric function of `(r_1, ..., r_{n+1})`, so by exchangeability every `loss(r_i, k')` has the same
expectation, which equals `E[R_{n+1}(k')] <= beta` (right-continuity gives `R_{n+1}(k') <= beta`). The consequences follow
from Lemma 1 (`X = w * loss`, monotone in the distance) and linearity. QED.

*Remarks.* (i) The expectation is marginal over the calibration draw and the new session, not conditional on the
calibration set; this is the same sense in which split conformal prediction guarantees coverage. (ii) `beta` must be
fixed before the data are seen; the agent uses the pre-registered `beta* = 0.10`. (iii) If a delta-band adjustment
moves a short strike inside `k_hat * m`, the certificate is void; the agent logs this and gate 31 rejects. Because
`k_hat` depends on `omega = w / m`, a wing narrowed after the interval was committed gets its radius re-derived at
the traded wing, and the larger of the two radii binds; a radius clip that binds voids the certificate as well.
(iv) The coverage version of research/G is the special case `loss = 1{r > k}` (the limit `omega -> 0`); since
`min((r-k)^+, omega)/omega <= 1{r > k}` pointwise, the risk radius at level `beta` is never wider than the coverage
radius at level `alpha = beta`.
(v) **Selection.** Theorem 3 is marginal over the calibration draw and the test session. Gate 31 conditions on
`c / w`, which is the market's price of the condor placed at `k_hat` and therefore a function of the certified radius
itself: the certificate *conditional on the gate opening* is not implied by Theorem 3. This is the setting of
selection-conditional coverage (Jin & Ren, JRSS-B 2025; Gibbs, Cherian & Candes, JRSS-B 2025), of selective conformal
risk control (Xu, Guo & Wei 2025, whose two-stage select-then-certify design is ours) and of action-conditional
guarantees (Zhu, Kiyani, Pappas & Hassani 2026). The exact repair is a two-cell Mondrian calibration on the gate event
`{c / w >= beta* + mu}` itself; it needs the historical `c / w` of the counterfactual condor of every calibration
session, and that series does not exist on the basic data plan. We therefore state the gap instead of hiding it:
the market tends to pay more for the interval precisely on days it expects a larger move, so the selected days may
carry a payout ratio above `beta*`, and the live ledger (payout ratio on gated sessions versus all sessions) is the
only measurement of that gap we can offer. A proxy-conditional variant (calibration by previous-VIX tercile) is a
pre-registered counterfactual, labelled as such, not a substitute for the gate-conditional bound.
(vi) The theorem applies to each session separately (rolling-window split conformal risk control); nothing joint
across sessions follows from it. The anytime-valid statement across sessions is the e-process monitor of section 9.

## 4. Theorem 4 (online level: one-sided long-run bound without any distributional assumption)

Let the online level evolve as `beta_{t+1} = beta_t + gamma * (beta* - l_t)`, clipped to `[beta_lo, beta_hi]`, where
`l_t in [0, 1]` is the realised payout ratio of the interval actually used on session `t`, and let the radius used be
`max(k_hat(beta*), k_hat(beta_t))` (adaptation may only tighten). Then for every sequence of scores, as long as the
floor `beta_lo` never binds,

    (1/T) sum_{t<=T} l_t  <=  beta* + (beta_hi - beta_lo) / (gamma * T).

*Proof.* Without clipping, telescoping gives `beta_{T+1} - beta_1 = gamma * sum_t (beta* - l_t)`, so
`sum_t l_t = T beta* - (beta_{T+1} - beta_1)/gamma <= T beta* + (beta_hi - beta_lo)/gamma`. Clipping at the ceiling only
lowers `beta_{t+1}` relative to the unclipped value, which preserves the inequality `beta_{t+1} - beta_t <= gamma (beta* - l_t)`
used in the sum; clipping at the floor would break it, hence the hypothesis. QED. (This is the Rolling Risk Control
bound of Feldman, Ringel, Bates & Romano 2023 in its simplest form; it holds for adversarial sequences, i.e. when
exchangeability fails.)

*Remarks.* (i) With `gamma = 0.005`, `beta_hi - beta_lo = 0.28` and `T = 250` sessions the slack term is `0.224`,
larger than `beta*` itself: the bound is vacuous at the one-year horizon and meaningful only over a decade. A tighter
parameterisation (clip range 0.14, `gamma = 0.02`) would give a slack of 0.028 and a one-year bound of 0.128; we report
it as a pre-registered counterfactual and did not adopt it, because a four-times faster valve widens the radius after
every full-wing loss, and the published evidence is that faster-adapting conformal variants cost growth (Ryan 2026).
(ii) With the realised payout ratio below `beta*` throughout the back-fill, `beta_t` drifts upward by about
`gamma beta*` per clean session (0.165 after 619 sessions, against a ceiling of 0.30), so `k_hat(beta_t) < k_hat(beta*)`
and the traded radius is the fixed-level radius: the online layer is currently a one-sided safety valve that binds
only after a run of losses pushes `beta_t` below `beta*`, and it has no effect on today's interval. The
recursion is the integral term of conformal PID control (Angelopoulos, Candes & Tibshirani 2023); the modern
alternatives that remove the choice of `gamma` (DtACI, AgACI) are cited, not shipped.

## 5. Lemma 5 (why a cap, not Kelly)

For the two-outcome approximation of the condor (win `c` with probability `p`, lose `L = w - c` otherwise), with
`b = c / L`, the Kelly fraction is `f* = p - (1 - p)/b` and

    d f* / d p = (1 + b) / b,      so      se(f*) = (1 + b)/b * se(p_hat).

At `b = 0.2` (credit 17 % of the wing) this factor is 6: with `n = 250` sessions, `se(p_hat) ~ 0.025` and `se(f*) ~ 0.15`,
i.e. a two-standard-error move in the estimated probability swings the "optimal" bet by 30 % of capital. Break-even is
`p = 1/(1 + b) = 0.833` in this approximation; the three-outcome version with the observed partial losses
(research/G, section 4.3) has break-even `0.757`. Either way the estimation error dwarfs any prudent bet, which is the
formal reason the 2 % session cap binds and Kelly is logged only as an exhibit. *Proof.* Differentiate. QED.

## 6. What is assumed, what is not proved, what is machine-checked

* **Exchangeability** of the scores over the trailing window is the only probabilistic assumption in Theorem 3. It is
  false across regime changes; Theorem 4 is the fallback, and research/G section 5.4 measures how much the fixed rule
  loses when it fails (coverage 0.46-0.57 in stressed regimes vs 0.70-0.83 for the conformal interval).
* The credit entering gate 31 is read at the **expected fill** (the natural: Alpaca paper fills only marketable
  orders), and the mid is logged alongside; the ladder never sells below the credit floor the gates approved. Mid-quote
  bias in estimated option returns has been measured at over 50 basis points per day (Duarte, Jones & Wang 2024), which
  is why the mid is not the reference.
* The **calibration window is one regime**: the 10:30 anchor series exists from 2024-01, so every calibration score comes
  from 2024-2026. The certificate is exact for that window; how the scores behave in a 2020- or 2022-type regime is not
  in the data, and the back-fill by year (0.070 / 0.079 / 0.090) is the whole out-of-sample record.
* **Two random variables, not one.** The certificate governs the hold-to-expiry payout ratio of the interval; the P&L
  governs the position that is closed at 50 % of the credit or at 15:15 ET. Both are reported; conflating them would be
  the most likely honest mistake in this project.
* The payoff in Lemma 1 is the **hold-to-expiry** payoff. The agent exits at 50 % of the credit or at 15:15 ET; an early
  exit at a profit only raises the realised payoff above the bound's assumption on those paths, an early exit at a loss
  before the close is not covered by the bound. We log the exit reason for every position.
* Paper-simulator fills, strike rounding, and the one-day-VIX-to-intraday scaling are approximations stated in
  `research/G` and `docs/regime_model_report.md`.
* **Machine-checked** in Lean 4 (v4.34.0-rc2) with Mathlib, `lean/Delphi/Condor.lean`, 13 theorems, no `sorry`, only the
  three standard axioms (`propext`, `Classical.choice`, `Quot.sound`; audited with `lake env lean CheckAxioms.lean`):
  Lemma 1 in full (`loss_nonneg`, `loss_le_one`, `loss_mem_Icc`, `loss_antitone`, `loss_eq_zero_of_le`,
  `loss_eq_one_of_ge`); the payoff identity and its monotonicity in the radius (`payoff_eq`, `payoffOfLoss_affine`,
  `payoffOfLoss_antitone`, `payoff_monotone`); the finite-average form of the Corollary of Theorem 3
  (`avg_payoff_ge`, `avg_condor_payoff_ge`: if the average payout ratio over a finite calibration set is at most
  `beta` and `c >= (beta + mu) w`, the average payoff is at least `mu w`); and the discrete layer-cake identity behind
  Lemma 2 (`sum_eq_sum_card_filter`). The probabilistic step of Theorem 3 (exchangeability to expectation) and Theorem 4
  are cited and proved on paper above, not formalised. Rebuild: `lean/README.md`.

## 7. Pre-registration

Fixed on 2026-09-02 before the first live session under the rule, none tuned on live data: `beta* = 0.10`,
`alpha = 0.20` (coverage track, counterfactual), `gamma = 0.005`, window 250 sessions, radius clip `[0.35, 1.60]`,
margin `mu = 0.05` (about $20 per contract at a $4 wing, the modelled round-trip cost of four legs at one tick),
wing `max($3, 0.5 % of spot)` rounded up to the strike grid, entry anchored at the first evaluation inside the entry
window, one update of `alpha_t` and `beta_t` per session including sessions without a trade. Every parameter changed
after the first live cycle is listed, dated and reasoned in `docs/CONFIG_CHANGES.md` (the credit reference moved from
the mid to the expected fill on 2026-09-02 after the pilot's only fill sat below the floor evaluated at the mid).

## 8. What is forgone by construction: the overnight premium

Delphi holds no position overnight: it enters after 10:15 ET and is flat by 15:15 ET, by construction. The
literature's cleanest decomposition of index-option returns says what that costs. Muravyev & Ni (JFE 2020; one-minute
OPRA data 2004-2013, S&P 500 options delta-hedged with index futures) find average delta-hedged SPX returns of about
-0.7 % per day to the buyer, "average close-to-open returns are -1% per day and open-to-close returns are positive,
0.3%" (t-statistics -12.0 overnight and 2.6 intraday), with the intraday gain concentrated in the last two fifths of
the session (0.16 % and 0.19 %, t = 4.3 and 3.7) and the same sign pattern for SPY (intraday +0.17 %, t = 3.1);
their explanation is that "option prices are set as if day and night instantaneous volatilities are equal" while the
day-to-night volatility ratio averages 2.5. Papagelis & Dotsis (JFM 2025; 30-day model-free variance indices
2012-2022, VRP measured as realised minus implied variance, i.e. the long variance swap's P&L) find the US variance
risk premium significantly negative overnight (VIX: -6.149, t = -5.35) and "during the intraday trading period, the
VRP becomes positive and often insignificant" (VIX: +2.894, t = 1.07). Jones & Shemesh (JF 2018; equity options on
S&P 500 members 1996-2014) find the option writer's return concentrated in nontrading periods, "essentially zero on
average on other days", and conclude that "nontrading returns cannot be explained by risk": it is persistent
mispricing of calendar-time variance. Taken together: the half of the index-option premium the literature can
measure is earned while the market is closed, and the half Delphi is exposed to is, on the delta-hedged evidence,
zero to slightly negative for the seller, with the seller's worst intraday hours being the afternoon hours Delphi
holds. Three of the four studies are not 0DTE-specific (Muravyev & Ni cover all maturities and moneyness; Papagelis &
Dotsis use 30-day indices), so the transfer to same-day options is an inference, not a measurement.

We therefore pre-register the give-up rather than argue with it. Delphi forgoes, by construction, the component of the
variance risk premium the literature can measure, in exchange for eliminating overnight gap risk, the non-farm-payrolls
release inside a position, and the pin-risk process Alpaca applies to same-day expiries after 15:30 ET. We expect this
to reduce expected return relative to an overnight variant and we do not claim an intraday premium. The only reason
this agent ever sells is gate 31: the market pays more for the interval than the certificate says it costs, by at least
the modelled cost of trading. If the intraday market never pays that, the agent never trades, and the ledger records a
closed gate as the mechanism working. Roadmap, not shipped: a 1DTE overnight condor entered around 15:00 ET and held to
the next close, calibrated on the close-to-close horizon, which is the horizon on which the regime model already has
fifteen year-blocks of validation; the hackathon window cannot hold it (Thursday to Friday spans the 08:30 ET payrolls
release and the Friday deadline).

## 9. Evidence at T = 3: the e-process monitor and the evidence ceiling

Nothing in sections 3-4 says anything about the sum of three sessions. The instrument that does is a test
supermartingale. Let `l_t in [0, 1]` be the realised payout ratio of the interval committed on session `t` and
`F_{t-1}` everything known before it. Under the **conditional null** `E[l_t | F_{t-1}] <= beta*` (an assumption, not a
corollary of Theorem 3, which is marginal), the wealth process

    W_T = prod_{t <= T} (1 + lambda_t (l_t - beta*)),    lambda_t in [0, 1/beta*] predictable,

is a non-negative supermartingale with `W_0 = 1` (non-negativity binds at `l_t = 0`, hence the cap `1/beta* = 10`), and
Ville's inequality gives `P(exists t: W_t >= 1/alpha) <= alpha` at every stopping time (Waudby-Smith & Ramdas 2023;
Ramdas, Grunwald, Vovk & Shafer 2023). `W_T` is therefore anytime-valid evidence *against* the certificate; it is reported,
never used to halt, because a conformal test martingale on clean data has been observed to fire in 135 of 135 runs at
`alpha = 0.05` (Han & Qu 2026). The mirror process on the scale-free payoff `Y_t = c_t / w - l_t` under the null "no
profit" `E[Y_t | F_{t-1}] <= 0` uses `eta_t in [0, 1/(1 - c_t / w)]` and measures evidence *for* profitability. Its ceiling
is arithmetic: with credit/width `g`, even `T` maximal wins give at most `(1/(1 - g))^T`; at `g = 0.20` and `T = 3` that is
`1.95`, so the smallest anytime-valid p-value three perfect sessions can produce is `0.51`, and `p <= 0.05` would need
fourteen consecutive perfect packages. We publish this ceiling with the ledger. It is why no Sharpe ratio is reported
even in principle: Goetzmann, Ingersoll, Spiegel & Welch (RFS 2007) show that the Sharpe-maximising manipulation is
"selling out-of-the-money calls and selling out-of-the-money puts in an uneven ratio", our exact instrument, that the
expected *sample* Sharpe ratio of that manipulation is infinite and its population maximum finite (1.31 against an
index Sharpe of 1.00). The nearest prior art for the monitor is anytime-valid re-certification of strategy pipelines
(Zhang 2026, arXiv:2608.10410); we found nothing applying an e-process to a live options book.

## References

* Angelopoulos, A. N., Bates, S., Fisch, A., Lei, L., Schuster, T. (2024). Conformal Risk Control. *ICLR 2024*; arXiv:2208.02814.
* Feldman, S., Ringel, L., Bates, S., Romano, Y. (2023). Achieving Risk Control in Online Learning Settings. *TMLR*; arXiv:2205.09095.
* Gibbs, I., Candes, E. (2021). Adaptive Conformal Inference Under Distribution Shift. *NeurIPS 2021*.
* Vovk, V., Gammerman, A., Shafer, G. (2005). *Algorithmic Learning in a Random World.* Springer.
* Lei, J., G'Sell, M., Rinaldo, A., Tibshirani, R. J., Wasserman, L. (2018). Distribution-Free Predictive Inference for Regression. *JASA* 113(523).
* Breeden, D. T., Litzenberger, R. H. (1978). Prices of State-Contingent Claims Implicit in Option Prices. *Journal of Business* 51(4).
* Kelly, J. L. (1956). A New Interpretation of Information Rate. *Bell System Technical Journal* 35(4); Baker, R. D., McHale, I. G. (2013). Optimal Betting Under Parameter Uncertainty. *Decision Analysis* 10(3).
* Bastos, J. A. (2024). Conformal prediction of option prices. *Expert Systems with Applications* 245 (conformal bands around option prices, no trading rule).
* Lekeufack, J., Angelopoulos, A. N., Bajcsy, A., Jordan, M. I., Malik, J. (2024). Conformal Decision Theory: Safe Autonomous Decisions from Imperfect Predictions. *ICRA 2024*, pp. 11668-11675, DOI 10.1109/ICRA57147.2024.10610041 (a buy/short/abstain trade calibrated against a loss budget, in a geometric-Brownian-motion simulation).
* Ryan (2026). Conformal Kelly. arXiv:2608.01494 (position size from a conformal interval; every faster-adapting variant cost growth).
* Xu, Guo, Wei (2025). Selective Conformal Risk Control. arXiv:2512.12844.
* Jin, Y., Ren, Z. (2025). Confidence on the focal: conformal prediction with selection-conditional coverage. *JRSS-B* 87(4), DOI 10.1093/jrsssb/qkaf016.
* Gibbs, I., Cherian, J. J., Candes, E. J. (2025). Conformal prediction with conditional guarantees. *JRSS-B* 87(4), DOI 10.1093/jrsssb/qkaf008.
* Zhu, Kiyani, Pappas, Hassani (2026). Conformal Risk-Averse Decision Making with Action Conditional Guarantee. arXiv:2606.05551.
* Farinhas, A., Zerva, C., Ulmer, D., Martins, A. F. T. (2024). Non-Exchangeable Conformal Risk Control. *ICLR 2024*; arXiv:2310.01262.
* Angelopoulos, A. N., Candes, E. J., Tibshirani, R. J. (2023). Conformal PID Control for Time Series Prediction. *NeurIPS 2023*.
* Canete (2023). Market Implied Conformal Volatility Intervals. *COPA 2023*, PMLR 204:89-99.
* Wisniewski, Lindsay, Lindsay (2020). Application of conformal prediction interval estimations to market makers' net positions. *COPA 2020*.
* Waudby-Smith, I., Ramdas, A. (2023). Estimating means of bounded random variables by betting. *JRSS-B* 86(1), DOI 10.1093/jrsssb/qkad009.
* Ramdas, A., Grunwald, P., Vovk, V., Shafer, G. (2023). Game-theoretic statistics and safe anytime-valid inference. *Statistical Science* 38(4).
* Han, Qu (2026). When the Martingale Never Stops Firing. arXiv:2608.30502.
* Goetzmann, W., Ingersoll, J., Spiegel, M., Welch, I. (2007). Portfolio Performance Manipulation and Manipulation-proof Performance Measures. *RFS* 20(5):1503-1546, DOI 10.1093/rfs/hhm025.
* Andersen, T. G., Thyrsgaard, M., Todorov, V. (2019). Time-Varying Periodicity in Intraday Volatility. *JASA* 114(528):1695-1707, DOI 10.1080/01621459.2018.1512864.
* Duarte, J., Jones, C. S., Wang, J. L. (2024). Very Noisy Option Prices and Inference Regarding the Volatility Risk Premium. *Journal of Finance* 79(5).
* Muravyev, D., Ni, X. (2020). Why do option returns change sign from day to night? *Journal of Financial Economics* 136(1):219-238, DOI 10.1016/j.jfineco.2018.12.006.
* Papagelis, Dotsis (2025). The Variance Risk Premium Over Trading and Nontrading Periods. *Journal of Futures Markets* 45:752-770, DOI 10.1002/fut.22589.
* Jones, C. S., Shemesh, J. (2018). Option Mispricing Around Nontrading Periods. *Journal of Finance* 73(2):861-900, DOI 10.1111/jofi.12603.
* Dew-Becker, I., Giglio, S. (2025). The Decline of the Variance Risk Premium: Evidence from Traded and Synthetic Options. Federal Reserve Bank of Chicago WP 2025-17.
* Ait-Sahalia, Y., Wang, Y., Yared, F. (2001). Do option markets correctly price the probabilities of movement of the underlying asset? *Journal of Econometrics* 102(1).
* Constantinides, G. M., Jackwerth, J. C., Perrakis, S. (2009). Mispricing of S&P 500 index options. *RFS* 22(3).
* Faias, J. A., Santa-Clara, P. (2017). Optimal Option Portfolio Strategies. *JFQA* 52(1).
* Zhang, L. (2026). Objective-oriented quantitative investment. arXiv:2608.10410 (anytime-valid re-certification of strategy pipelines).

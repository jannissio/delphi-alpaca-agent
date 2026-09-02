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
moves a short strike inside `k_hat * m`, the certificate is void; the agent logs this and gate 31 rejects.
(iv) The coverage version of research/G is the special case `loss = 1{r > k}` (the limit `omega -> 0`); since
`min((r-k)^+, omega)/omega <= 1{r > k}` pointwise, the risk radius at level `beta` is never wider than the coverage
radius at level `alpha = beta`.

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

*Remark.* With `gamma = 0.005`, `beta_hi - beta_lo = 0.28` and `T = 250` sessions the slack term is `0.224`, so the bound
is loose over one year and meaningful over a decade; the empirical back-fill (`docs/conformal_backfill.md`) shows the
realised payout ratio close to `beta*` far sooner than the bound requires. We report the number, not a claim.

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
* The credit is the **mid**; fills are at or below it (the ladder walks toward the natural), so the realised `c` is
  smaller than the quoted one by the slippage that the audit log reports per fill.
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
window, one update of `alpha_t` and `beta_t` per session including sessions without a trade.

## References

* Angelopoulos, A. N., Bates, S., Fisch, A., Lei, L., Schuster, T. (2024). Conformal Risk Control. *ICLR 2024*; arXiv:2208.02814.
* Feldman, S., Ringel, L., Bates, S., Romano, Y. (2023). Achieving Risk Control in Online Learning Settings. *TMLR*; arXiv:2205.09095.
* Gibbs, I., Candes, E. (2021). Adaptive Conformal Inference Under Distribution Shift. *NeurIPS 2021*.
* Vovk, V., Gammerman, A., Shafer, G. (2005). *Algorithmic Learning in a Random World.* Springer.
* Lei, J., G'Sell, M., Rinaldo, A., Tibshirani, R. J., Wasserman, L. (2018). Distribution-Free Predictive Inference for Regression. *JASA* 113(523).
* Breeden, D. T., Litzenberger, R. H. (1978). Prices of State-Contingent Claims Implicit in Option Prices. *Journal of Business* 51(4).
* Kelly, J. L. (1956). A New Interpretation of Information Rate. *Bell System Technical Journal* 35(4); Baker, R. D., McHale, I. G. (2013). Optimal Betting Under Parameter Uncertainty. *Decision Analysis* 10(3).
* Bastos, J. A. (2024). Conformal prediction of option prices. *Expert Systems with Applications* 245 (the nearest prior work: conformal bands around option prices, no trading rule).

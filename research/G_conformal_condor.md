# G — The Conformal Condor: validation, sharpening, and one refutation

Report G. Author: Claude (Opus 5) research agent. Date: 2026-09-02. Scope: validate, sharpen or refute
the "Conformal Condor" as the single distinguishing core idea. Literature (RQ1–RQ5) plus a prototype
experiment on `state/history/daily.csv`. Code `research/experiments/conformal_condor.py`, raw output
`research/experiments/conformal_condor_out.md`. Nothing under `agent/` was touched.

---

## 1. Summary — ten bullets, decision-relevant first

1. **Verdict: keep it, but keep the half of it that is a theorem and drop the half that is a hope.**
   The defensible core is a two-line identity plus a distribution-free calibration:
   *(a)* for a vertical spread of width `w`, `credit / w` **is** the risk-neutral probability of
   finishing beyond the short strike (Breeden–Litzenberger 1978, digital limit) — so for a condor
   `Q(outside) = credit / wing`, readable directly from the package quote;
   *(b)* split conformal on the score `r = |move| / implied_move` gives a physical interval whose
   coverage is `1 − α` by construction, with no distributional assumption.
   The trade rule is then **one line with no free parameter**: sell the α-interval iff
   `credit / wing ≥ α + margin`. Everything else in the original proposal (RND estimation,
   smoothing, no-arbitrage cleaning, Kelly sizing off estimated `p`) is either unnecessary or
   actively harmful, and the experiment says so.
2. **Refuted: conformal *widening* does not earn money, because the market charges for the width.**
   This is the single most important experimental result. On horizon B, holding the credit fixed at
   the report's 17 %-of-wing, split conformal lifts mean P&L from **−0.0125 % to +0.0383 %** of spot
   per session. Recompute the credit consistently with the width (Black–Scholes condor at the
   VIX-implied vol, one parameter calibrated to the one live chain we have) and the same rule earns
   **−0.0076 %** — i.e. the entire apparent gain was the fixed-credit assumption. **This invalidates
   any width-changing conclusion drawn from `docs/regime_model_report.md`, which uses a constant
   credit.** Flag it in the write-up; do not quietly fix it.
3. **Confirmed and tradable: the *timing* gate, not the width.** Trading only when the calibrated
   physical interval is narrower than the market's own α-interval (`k_P ≤ k_Q`) turns horizon B from
   −0.0069 % to **+0.0116 %** of spot per session (t = 1.72, 374 of 1,033 sessions, 36 % hit rate).
   That is the "P > Q" rule with real economics behind it: it is a conditional variance risk premium
   filter (Carr–Wu 2009; Bollerslev–Tauchen–Zhou 2009). t = 1.72 is *not* significance; it is a sign
   with the right mechanism.
4. **Conformal buys conditional coverage, which is exactly what a risk process is supposed to buy.**
   Our current fixed `k = 0.70` rule has coverage that collapses with the regime: on horizon B,
   0.748 → 0.671 → 0.611 → **0.463** across VIX/VIX3M slope buckets, and 0.730 → 0.681 → **0.568**
   across VIX levels. The CQR+ACI interval holds **0.825 / 0.798 / 0.806 / 0.704** and
   **0.826 / 0.792 / 0.791** on the same buckets. The fixed rule is a promise the market breaks
   exactly when it matters; the conformal rule is a promise that survives. Sell *that* in the
   write-up, not P&L.
5. **The Kelly number you asked for is negative, and that is the answer.** For a two-state condor
   with `b = c/L = 0.2` and `p = 0.80`, `f* = p − (1−p)/b = −0.20`. Break-even is `p = 1/(1+b) =
   0.833`. Kelly says **do not trade** at 80 % coverage and a 20 % credit-to-loss ratio. The trade is
   only positive because of the partial-loss region between short and wing: the correct break-even
   using `E[loss | outside]` is **0.757** (horizon A) and **0.776** (horizon B), and empirical coverage
   beats it by +6.1 pp on A and misses it by −10.7 pp on B.
6. **And the 2 %-per-session cap dominates for a reason you can put a number on.**
   `∂f*/∂p = (1+b)/b = 6` at `b = 0.2`. With a 250-session conformal calibration set,
   `se(p̂) = √(0.8·0.2/250) = 2.5 pp`, so `se(f*) = 0.15` — the standard error of the Kelly fraction
   is larger than any bet a sane person places. Getting `se(f*)` below 0.02 needs ≈ **14,400 sessions
   (57 years)**. Baker & McHale (2013) is the citation; this arithmetic is the argument. The empirical
   quarter-Kelly on horizon A is 0.14–0.17 of capital; our 2 % max-loss cap is ~7× more conservative,
   and should stay.
7. **Originality claim: true, with one honest neighbour.** OpenAlex and web searches return **no**
   work applying conformal prediction to option strike selection, to option structures as prediction
   intervals, or to trading a calibrated P-interval against its Q-price. The nearest work is Bastos
   (2024, *Expert Systems with Applications*), "Conformal prediction of option prices" — conformal
   intervals around a *machine-learned option price*, not around the underlying's terminal
   distribution, and with no trading rule. Say exactly that: "first application we can find of
   conformal prediction to option **strike selection**; conformal prediction has previously been
   applied to option **price** prediction (Bastos 2024)."
8. **Breeden–Litzenberger in full is not worth building in 2.5 days, and 0DTE is where it breaks.**
   The full RND (second derivative of the call price in strike, smoothed IV surface, arbitrage
   repair) is fragile at one tick of spread and is the exact regime where Bandi/Fusari/Renò (2023)
   show the standard machinery misprices — 0DTE needs local-in-time expansions with skew/kurtosis
   corrections, not Black–Scholes. But we do not need the density. We need one number per side, and
   the **vertical-spread credit divided by its width is that number**, by construction, with the
   bid-ask noise of two quotes instead of a whole surface. Use it; cite Breeden–Litzenberger for
   *why* it is the risk-neutral probability, and Bandi et al. for *why* we refuse to build the rest.
9. **Adaptive Conformal Inference is the right method and the cheapest one.** Financial returns are
   not exchangeable (volatility clustering), which voids the split-conformal guarantee.
   Gibbs & Candès (2021) ACI restores **long-run** coverage with no exchangeability assumption at
   all — it is 3 lines: `α_{t+1} = α_t + γ(α − err_t)`. Conformalising the *ratio* `|move|/implied`
   rather than the raw move handles most volatility clustering before ACI ever fires. CQR
   (Romano–Patterson–Candès 2019) with a quantile GBM adds real conditional adaptivity
   (interval half-width sd 0.22–0.27 vs 0.13–0.18 for plain split conformal) but buys almost nothing
   in P&L and adds a trained model to defend. **Recommendation: ship split conformal on the ratio +
   ACI. Log CQR alongside as a shadow model.**
10. **What to report, and the framing that makes it a submission rather than a backtest.**
    Report the pair (empirical coverage, mean interval half-width) — Gneiting, Balabdaoui & Raftery's
    "maximise sharpness subject to calibration" — plus the realised `credit/wing − α` gap per trade.
    That gives an evaluation whose validity does **not** depend on P&L, which is exactly what
    `STATE_OF_THE_ART.md` §9 says we need for a 2.5-session window: coverage is a per-trade
    verifiable claim; Sharpe is not. Headline: *"We do not claim an edge. We claim a calibrated
    interval, we show its coverage online, and we only sell it when the market pays more than the
    calibration says it is worth."*

---

## 2. Source cards

Citation-worthiness is graded for *our* use: whether we can put it in the write-up and defend it.

### RQ1 — Conformal prediction under distribution shift

**S-G1 — Vovk, Gammerman & Shafer (2005), *Algorithmic Learning in a Random World*, Springer.**
DOI 10.1007/b106715. Founding monograph; finite-sample validity under exchangeability. **High** as
origin, but cite Lei et al. for the split version we use.

**S-G2 — Lei, G'Sell, Rinaldo, Tibshirani & Wasserman (2018), "Distribution-Free Predictive Inference
for Regression", *JASA* 113(523), 1094–1111.** DOI 10.1080/01621459.2017.1307116.
Split (inductive) conformal for regression: with an exchangeable calibration set of size *n*, the
interval built from the `⌈(n+1)(1−α)⌉/n` empirical quantile of the nonconformity scores has coverage
in `[1−α, 1−α+1/(n+1)]`. **This is the exact estimator in our prototype.**
**Citation-worthiness: very high** — peer-reviewed, top statistics journal, the canonical reference.

**S-G3 — Romano, Patterson & Candès (2019), "Conformalized Quantile Regression", *NeurIPS 32*.**
arXiv:1905.03222, DOI 10.48550/arXiv.1905.03222. Fits conditional quantiles `q̂_lo, q̂_hi` by any
quantile regressor, then conformalises the score `E_i = max(q̂_lo − y_i, y_i − q̂_hi)`. Keeps
finite-sample marginal validity *and* gains conditional adaptivity. **Citation-worthiness: high**
(NeurIPS, heavily cited). Used as our shadow model.

**S-G4 — Gibbs & Candès (2021), "Adaptive Conformal Inference Under Distribution Shift", *NeurIPS 34*.**
arXiv:2106.00170. The update `α_{t+1} = α_t + γ(α − err_t)` guarantees
`|(1/T)Σ err_t − α| ≤ (α_1 + γ)/(Tγ)` — long-run coverage **with no exchangeability assumption and no
assumption on the data-generating process at all**, only that α_t stays in a bounded range.
**Citation-worthiness: very high.** This is the theorem that lets us make a coverage claim on
non-exchangeable financial data, which is the whole reason the idea survives.

**S-G5 — Zaffran, Féron, Goude, Josse & Dieuleveut (2022), "Adaptive Conformal Predictions for Time
Series", *ICML*, PMLR 162:25834–25866.** arXiv:2202.07282. ACI's performance is highly sensitive to γ;
proposes AgACI, an online expert-aggregation wrapper removing the choice of γ. Their setting
(electricity prices) has our pathology: heteroskedasticity plus regime breaks. **High.** Cite for the
γ warning; do **not** implement AgACI in 2.5 days.

**S-G6 — Xu & Xie (2021), "Conformal Prediction Interval for Dynamic Time-Series" (EnbPI), *ICML*,
PMLR 139:11559–11569.** arXiv:2010.09107. Bootstrap-ensemble residuals, no data splitting, coverage
under strongly-mixing errors rather than exchangeability. **Medium-high.** Rejected for us: needs an
ensemble refit, and the assumption it buys (stationary strong mixing) we cannot verify on 0DTE.

**S-G7 — Angelopoulos, Candès & Tibshirani (2023), "Conformal PID Control for Time Series
Prediction", *NeurIPS 36*.** arXiv:2307.16895, DOI 10.48550/arXiv.2307.16895. Generalises ACI to a
PID controller on the coverage error (the "I" term is ACI). **High.** Cite as the state of the art we
deliberately simplified away from; a PID controller tuned on 2.5 days would be pure overfitting.

**S-G8 — Bhatnagar, Wang, Xiong & Bai (2023), "Improved Online Conformal Prediction via Strongly
Adaptive Online Learning", *ICML*.** arXiv:2302.07869. Coverage guarantees on *every* sub-interval of
time, not just the long run. **Medium-high**, cite as follow-up work.

**S-G9 — "Adaptive Conformal Inference for Computing Market Risk Measures: An Analysis with Four
Thousand Crypto-Assets", *Journal of Risk and Financial Management* 17(6):248 (2024).**
DOI 10.3390/jrfm17060248. Applies ACI, AgACI, SF-OGD and SAOCP to Value-at-Risk. **Medium** (MDPI;
crypto), but the closest published precedent that ACI-style methods work on a *financial quantile*
problem, which is what an option strike is. Verify the author list before citing — MDPI blocked
automated retrieval.

### RQ2 — Risk-neutral probabilities from option prices

**S-G10 — Breeden & Litzenberger (1978), "Prices of State-Contingent Claims Implicit in Option
Prices", *Journal of Business* 51(4), 621–651.** DOI 10.1086/296025.
`∂C/∂K = −e^{−rT} Q(S_T > K)` and `∂²C/∂K² = e^{−rT} q(K)`. **Citation-worthiness: very high**, and
it is the single citation that turns our trade rule into a theorem. **The form we use is the first
derivative, not the second**: a call (put) vertical of width `w` costs `w · e^{−rT} Q(S_T beyond K)`
to first order, so **credit / wing ≈ Q(outside)** for the condor. At `T ≈ 0` the discount factor is 1.

**S-G11 — Figlewski (2018), "Risk-Neutral Densities: A Review", *Annual Review of Financial Economics*
10, 329–359.** DOI 10.1146/annurev-financial-110217-022944. Survey of how fragile the second-
derivative estimate is: bid-ask noise, strike discreteness, tail extrapolation, monotonicity/convexity
repair. **High.** Cite as the reason we take the first derivative and stop.

**S-G12 — Malz (2014), NY Fed Staff Report 677, "A Simple and Reliable Way to Compute Option-Based
Risk-Neutral Distributions".** Practical smoothing in delta–IV space. **Medium-high** — the reference
implementation if we ever want the full density.

**S-G13 — Bandi, Fusari & Renò (2023), "0DTE Option Pricing", SSRN 4503344.**
DOI 10.2139/ssrn.4503344. Local-in-time pricing expansions specific to `T → 0`, with closed-form
skewness/kurtosis corrections; documents that standard (Black–Scholes / long-dated-calibrated) models
misprice and mis-hedge 0DTE. **Citation-worthiness: medium-high** — working paper, top authors,
directly on-topic and now cited. **This is our stated reason for not modelling Q at all in
production and reading it off the quote instead.**

**S-G14 — Almeida, Freire & Hizmeri (2024), "0DTE Asset Pricing", SSRN 4701401.**
DOI 10.2139/ssrn.4701401. Companion evidence on 0DTE-specific risk premia and pricing anomalies.
**Citation-worthiness: medium** — unread working paper; cite only as "see also", or read it first.

### RQ3 — Trading the P-vs-Q gap

**S-G15 — Carr & Wu (2009), "Variance Risk Premiums", *RFS* 22(3), 1311–1341.** DOI 10.1093/rfs/hhn038.
In `STATE_OF_THE_ART.md` (A-S2) and read in F1: the SPX VRP survives transaction at bid prices
(t = −7.44). **Very high.** The economic reason a `P(inside) > Q(inside)` gap can exist at all rather
than being an arbitrage.

**S-G16 — Bollerslev, Tauchen & Zhou (2009), "Expected Stock Returns and Variance Risk Premia",
*RFS* 22(11), 4463–4492.** DOI 10.1093/rfs/hhp008. The VRP as an explicit **P-minus-Q difference**
`E^Q[RV] − E^P[RV]`, whose time variation predicts returns. **Very high.** Legitimises a
*time-varying* gate: the gap is not constant, so conditioning on it is a known research design.

**S-G17 — Barone-Adesi, Engle & Mancini (2008), "A GARCH Option Pricing Model with Filtered Historical
Simulation", *RFS* 21(3), 1223–1258.** DOI 10.1093/rfs/hhn031. Estimates the physical density by
FHS-GARCH and the risk-neutral density from option prices, and studies the ratio (state price density
per unit probability). **Very high.** The closest ancestor of the Conformal Condor: *same object
(P vs Q), different estimator (parametric GARCH vs distribution-free conformal), no trading rule.*
Our contribution over it: replace the parametric physical density with a distribution-free calibrated
interval, and reduce Q to a single quoted number.

**S-G18 — Beckmeyer, Branger & Gayda (2023), "Retail Traders Love 0DTE Options… But Should They?",
SSRN 4404704.** The retail-loses-in-0DTE evidence already in `STATE_OF_THE_ART.md` §1 bullet 11.
**Medium-high.** For the record: the brief asked for a Beckmeyer & Branger paper on option-implied vs
realised distributions; I could not locate one under that description. Use Bollerslev–Tauchen–Zhou
and Barone-Adesi et al. for that claim instead, and drop the attribution.

**Answer to RQ3's literal question — "is `sell the interval when P(inside) > Q(inside) + margin` a
known rule?"** As a *stated, tested trading rule with conformal calibration on the P side*: **no**,
nothing found. As an *economic idea*: **yes, and it is very old** — it is the variance risk premium
expressed on a digital payoff instead of on variance. Papers that compare an econometric density to
the option-implied density and then trade the difference exist (Barone-Adesi/Engle/Mancini's pricing
performance tests; the "forecasting with option-implied information" line, Christoffersen, Jacobs &
Chang 2013, *Handbook of Economic Forecasting* vol. 2, DOI 10.1016/B978-0-444-53683-9.00010-4), but
they trade *straddles/variance swaps* to harvest the level of the premium, not an interval sized to a
calibrated coverage. **Reported returns are small and mostly vanish after costs** — consistent with
F1's finding that the unconditional 0DTE condor loses (−0.0082 % of spot after half-spread) and with
our own horizon-B result. Frame our claim as *method*, never as *return*.

### RQ4 — Kelly with estimated probabilities

**S-G19 — Kelly (1956), *Bell System Technical Journal* 35(4), 917–926.**
DOI 10.1002/j.1538-7305.1956.tb03809.x. **High** (origin).

**S-G20 — Baker & McHale (2013), "Optimal Betting Under Parameter Uncertainty: Improving the Kelly
Criterion", *Decision Analysis* 10(3), 189–199.** DOI 10.1287/deca.2013.0271. Kelly ignores estimation
error in `p̂`; out-of-sample performance is systematically worse than in-sample; the fix is to shrink
the bet, with shrinkage increasing in `Var(p̂)`, plus a back-of-envelope shrinkage factor.
**High** — peer-reviewed INFORMS journal, exactly our problem.

**S-G21 — MacLean, Thorp & Ziemba (2011), *The Kelly Capital Growth Investment Criterion*, World
Scientific.** DOI 10.1142/7598. **Medium-high**; cite for "half/quarter Kelly gives up little growth
and most of the drawdown".

### RQ5 — Prior work on conformal prediction in options

**S-G22 — Bastos (2024), "Conformal prediction of option prices", *Expert Systems with Applications*
245:123087.** DOI 10.1016/j.eswa.2023.123087. Conformalized quantile regression around a
gradient-boosting **option-price** predictor; simulated data; finds nominal coverage is attained where
non-conformal intervals under-cover, and that OTM/short-maturity options get the widest intervals.
Explicitly describes itself as the first application of conformal prediction in asset pricing.
**Citation-worthiness: high** (peer-reviewed, directly adjacent). **This is the paper we must cite
when we claim novelty, and the distinction is clean: Bastos predicts the price of a contract; we
calibrate an interval on the underlying and then sell it at the price the market quotes for it.**

**Negative search result (this is itself a deliverable).** Searched: OpenAlex full-text and title
searches on conformal prediction × options/strikes/derivatives/trading; web search on conformal
prediction × iron condor / strike selection / prediction interval selling. **No work found** that
(i) sets option strikes from a conformal prediction interval, (ii) frames an option structure as the
sale of a prediction interval, or (iii) compares a conformal physical coverage to a Breeden–
Litzenberger risk-neutral coverage as a trading gate. **Caveat to state honestly:** OpenAlex indexes
SSRN unevenly and practitioner work is often unpublished; the correct claim is *"we found no prior
work"*, not *"none exists"*.

---

## 3. Evidence table

| # | Claim | Evidence | Confidence |
|---|---|---|---|
| G1 | `credit/wing` of a condor = risk-neutral probability of finishing outside the short strikes, to first order in the wing width | Breeden–Litzenberger 1978, first derivative form (S-G10); exact in the `w → 0` limit, error `O(w)` in the RND's local slope | Very high (theorem) |
| G2 | Therefore the condor's two-state break-even inside-probability `1 − c/w` **is** `Q(inside)`; "trade when P > break-even" and "trade when P > Q" are the same rule | Algebra from G1 | Very high |
| G3 | Split conformal on an exchangeable calibration set gives coverage in `[1−α, 1−α+1/(n+1)]` | Lei et al. 2018 (S-G2) | Very high |
| G4 | Daily equity returns are not exchangeable (volatility clustering), so G3's guarantee does not hold as stated | Standard; visible in our data as regime-dependent coverage collapse (§5) | Very high |
| G5 | ACI restores long-run coverage with **no** distributional or exchangeability assumption | Gibbs & Candès 2021 (S-G4), Theorem 1 | Very high |
| G6 | Conformalising the ratio `|move|/implied_move` rather than the raw move absorbs most volatility clustering | Our experiment: plain split conformal on the ratio already achieves 0.805–0.832 coverage at a 0.80 target over 2021–2026 (§5) | High |
| G7 | Our current fixed `k = 0.70` rule has strongly regime-dependent coverage: 0.463–0.748 (slope buckets), 0.568–0.730 (VIX buckets) on horizon B | Experiment §5 | High (in-sample descriptive) |
| G8 | The conformal interval fixes that: 0.704–0.825 and 0.791–0.826 on the same buckets | Experiment §5 | High |
| G9 | Widening the interval does **not** improve P&L once the credit is priced consistently with the width | Experiment §5: horizon B fixed-credit +0.0383 % → width-consistent −0.0076 % | Medium-high (depends on one calibrated parameter θ; sign is stable across θ ∈ [0.50, 0.70]) |
| G10 | The P-vs-Q **timing gate** does improve P&L: horizon B −0.0069 % → +0.0116 %, on 36 % of sessions, t = 1.72 | Experiment §5 | Low-medium (t = 1.72, one gate, one dataset, model Q) |
| G11 | Kelly at `b = c/L = 0.2`, `p = 0.80` is `f* = −0.20`; break-even is `p = 0.833` | Algebra | Very high |
| G12 | The partial-loss region lowers the true break-even to 0.757 (A) / 0.776 (B) | Experiment §5, `E[loss|outside]` = 0.265 % / 0.295 % of spot | High |
| G13 | `se(f*) = ((1+b)/b)·√(p(1−p)/n) = 0.15` at `n = 250`; 57 years of data needed for `se(f*) < 0.02` | Delta method; Baker & McHale 2013 for the prescription | Very high |
| G14 | 0DTE is the regime where full RND extraction is least reliable | Bandi/Fusari/Renò 2023 (S-G13); Figlewski 2018 (S-G11); SEC DERA one-tick spreads (F1 E-F5) | High |
| G15 | No prior work applies conformal prediction to option strike selection | OpenAlex + web searches, §2 negative result; nearest neighbour Bastos 2024 | Medium-high (absence of evidence) |
| G16 | **Our own live chain fails our own credit gate.** The observed 2026-09-02 condor paid 17 % of the wing; the design (F1-derived) requires ≥ 20 % | `docs/regime_model_report.md` header vs `STATE_OF_THE_ART.md` §12 | High — **needs a decision before Wednesday** |

---

## 4. Method recipe for the agent

Deliberately minimal. Everything here is either a closed form or ten lines of Python. No new model
is trained in production.

### 4.1 State kept across sessions (`state/conformal.json`)

```
alpha_t          float   current adaptive miscoverage level, initialised to ALPHA_TARGET = 0.20
scores           list    trailing W = 250 nonconformity scores r_i = |move_i| / implied_move_i
history          list    per-session records (see 4.6)
```

`scores` must be back-filled once from `state/history/daily.csv` (`ratio_1030` for the 10:30→close
horizon, `ratio_oc` for open→close) so the agent starts calibrated, not cold. Log it as a choice.

### 4.2 At entry (10:00–11:00 ET)

1. **Implied remaining move.** `M_t` = ATM straddle mid / spot, from the live chain (this is the live
   analogue of `impl_move_cc`; the historical scores were built on the VIX-implied full-day move, so
   convert with the report's own convention, `short = 1.10 × M_t = 0.70 × impl_move_cc`, i.e. the
   score used live is `r = |move| / (M_t / 0.636)`). **Use one convention and state it once.**
2. **Conformal half-width.**
   ```
   n   = len(scores)                                  # 250
   lvl = ceil((n + 1) * (1 - alpha_t)) / n            # capped at 1.0
   k_t = quantile(scores, lvl, method="higher")       # in units of implied move
   k_t = clip(k_t, 0.35, 1.60)                        # tradability clip, logged when it binds
   ```
3. **Strikes.** Short put at `S(1 − k_t·M̃_t)`, short call at `S(1 + k_t·M̃_t)`, rounded to the
   nearest listed strike; wings `max($3, 0.5 % of spot)` further out (unchanged from §12 of
   `STATE_OF_THE_ART.md`). Log the rounding error in coverage units.
4. **Read Q off the quote — this is the whole idea.**
   ```
   Q_outside = package_credit_mid / wing_width        # Breeden-Litzenberger digital approximation
   Q_inside  = 1 - Q_outside
   ```
   Compute it separately per side as a cross-check: `Q(S_T < K_put_short) ≈ put_spread_credit / wing`,
   `Q(S_T > K_call_short) ≈ call_spread_credit / wing`. If the two sides differ from the delta of the
   short strikes by more than 0.10 in probability, log a warning (this catches a stale or crossed
   quote without needing an arbitrage repair routine).
5. **Decision gate (new Gate 31, "coverage gate").**
   ```
   TRADE  iff  Q_outside >= alpha_t + MARGIN
   ```
   with `MARGIN = 0.05` (5 probability points). Interpretation, one sentence for the journal:
   *"the market pays us as if the close leaves this interval `Q_outside` of the time; our calibration
   says it leaves `alpha_t` of the time; we require a 5-point cushion for costs and estimation
   error."* Rejecting is a logged NO_TRADE with both numbers, which is a better artefact than a fill.
   Note `MARGIN = 0.05` at a 0.5 % wing is 0.025 % of spot ≈ $19 per contract — roughly one
   round-trip of four legs at one tick, so it is a cost margin, not a fudge factor.
6. **Sizing.** Two-state Kelly with the partial-loss correction, then capped:
   ```
   c    = package credit ($), L = wing_width - c (max loss, $)
   p    = 1 - alpha_t                                  # calibrated inside probability
   Lbar = mean(loss | outside) from the trailing scores, in $   # partial-loss region
   f_raw    = (p*c - (1-p)*Lbar) / (c*Lbar/(c+Lbar))   # Kelly for a 3-outcome bet, see 4.3
   f_shrunk = f_raw * max(0, 1 - 2*se_p*(1+b)/b/f_raw) # Baker-McHale style shrinkage, floored at 0
   f_used   = min(f_shrunk/4, 0.02)                    # quarter Kelly, then the 2 % session cap
   contracts = floor(f_used * equity / L)              # then the existing 5/6-contract caps
   ```
   In practice `f_used` will be `0.02` almost always. **That is the point**: the cap binds, and the
   Kelly calculation exists to *demonstrate* that it binds, with the arithmetic of §1 bullet 6 next
   to it in the report.
7. **ACI update, after the close.**
   ```
   err     = 1 if |realised move| > k_t * implied_move else 0
   alpha_t = clip(alpha_t + GAMMA * (ALPHA_TARGET - err), 0.02, 0.40)   # GAMMA = 0.005
   scores.append(realised_ratio); scores = scores[-250:]
   ```
   **Update `alpha_t` on every session, including NO_TRADE sessions.** Calibration is a property of
   the forecast, not of the trade; skipping days breaks the ACI guarantee and is also the honest
   thing to avoid.

### 4.3 The Kelly formula for a condor, derived

Bet fraction `f` of capital, max loss `L` per unit, credit `c` per unit. Three regions:
inside (probability `p`, payoff `+c`), between short and wing (probability `π`, payoff `c − X`,
`0 < X < wing`), beyond the wing (probability `1 − p − π`, payoff `−L`).

Exact: maximise `E[log(1 + f·payoff/L)]`, solved numerically (our prototype does this on the
realised sample).

Two-state approximation (`π = 0`), the textbook result with `b = c/L`:
```
f* = (p·b − (1 − p)) / b = p − (1 − p)/b ,      break-even  p = 1/(1+b)
```
**Requested number: `c/L = 0.2`, `p = 0.80` → `f* = 0.80 − 0.20/0.20 = −0.20`. Kelly says do not
trade.** Break-even is `p = 1/1.2 = 0.8333`.

Three-state approximation replacing the max loss with the expected loss given outside, `L̄`:
```
f* ≈ (p·c − (1 − p)·L̄) / (c·L̄ / (c + L̄))     ,   break-even  p = L̄ / (c + L̄)
```
With horizon A's numbers (`c = 0.085 %`, `L̄ = 0.265 %` of spot): break-even `p = 0.757`, empirical
`p = 0.818` → `f* ≈ (0.818·0.085 − 0.182·0.265) / (0.085·0.265/0.35) = 0.0213/0.0644 = 0.33`.
The prototype's numerical Kelly on the realised distribution gives **0.575–0.695** (the analytic
three-state version is conservative because it ignores that most "outside" days lose far less than
`L̄`). Quarter Kelly is therefore 0.14–0.17 of capital, versus our 2 % cap.

**Sensitivity, the number that justifies the cap:** `∂f*/∂p = (1+b)/b = 6` at `b = 0.2`. With
`n = 250`, `se(p̂) = 0.025`, so `se(f*) = 0.15`. A two-standard-error move in the calibrated
probability swings the "optimal" bet by 30 % of capital. Baker & McHale's prescription (shrink by a
factor increasing in `Var(p̂)`) reduces to: **at our sample size, shrink to a cap.**

### 4.4 What to log per trade (add to the existing journal)

| Field | Why |
|---|---|
| `alpha_target`, `alpha_t`, `gamma`, `n_calibration` | reproduces the interval exactly |
| `implied_move_pct`, `k_conformal`, `k_clipped` (bool) | sharpness, and whether the clip bound |
| `short_put_K`, `short_call_K`, `wing_width`, strike-rounding error in coverage points | strike audit |
| `credit_mid`, `credit_filled`, `Q_outside = credit/wing`, per-side `Q` | the market's price of our interval |
| `Q_outside − alpha_t` (the gap), `MARGIN`, gate decision | the decision, reproducible from two numbers |
| `delta_shortput`, `delta_shortcall` as an independent Q cross-check | catches bad quotes |
| `f_raw`, `f_shrunk`, `f_used`, `binding_constraint` ∈ {kelly, cap, contract_cap} | shows the cap binding |
| after the close: `realised_move_pct`, `inside` (bool), `realised_pnl`, `alpha_{t+1}` | the calibration update |

### 4.5 What to report (this is the evaluation section of the write-up)

1. **Calibration plot.** Running empirical coverage vs the 0.80 target, with the Gibbs–Candès
   long-run bound `(α₁ + γ)/(Tγ)` drawn as an envelope. With T = 3 sessions this envelope is
   enormous — **say so**: "the guarantee is asymptotic; with three sessions we report the number, not
   a claim."
2. **Sharpness.** Mean and sd of `k_t` in implied-move units. Report the pair (coverage, sharpness),
   per Gneiting, Balabdaoui & Raftery (2007), *JRSS-B* 69(2), 243–268,
   DOI 10.1111/j.1467-9868.2007.00587.x: *maximise sharpness subject to calibration*.
3. **The P-vs-Q ledger.** For every session, traded or not: `alpha_t`, `Q_outside`, the gap, the
   decision. This is a *per-session verifiable artefact* that exists even with zero fills — the only
   evaluation object in the whole submission that does not need statistical power.
4. **Counterfactual.** What the fixed `k = 0.70` rule would have done on the same sessions. Two
   configurations only (fixed vs conformal): that is our whole multiple-testing budget per F2 §5.3.
5. **Not reported:** Sharpe, hit rate, annualised return. Unchanged from `STATE_OF_THE_ART.md` §8.3.

### 4.6 What NOT to build

- No RND / density estimation, no IV-surface smoothing, no arbitrage repair. First derivative only.
- No CQR / gradient boosting in the production path (shadow only): it earns nothing and costs a defence.
- No PID controller, no AgACI, no EnbPI. γ = 0.005 fixed and pre-registered.
- No Kelly-driven sizing above the cap, ever. Kelly is an exhibit, not a controller.

---

## 5. Experiment results

Runtime ≈ 40 s. Payoff model as in `docs/regime_model_report.md`: wing 0.5 % of spot, short at
`k × impl_move_cc`, loss linear between short and wing, spot 762. Target `α = 0.20`, ACI γ = 0.005,
rolling calibration 250 sessions (B) / 125 (A), conformal widths clipped to `k ∈ [0.35, 1.60]`.
**Two credit models.** *Fixed credit* = 17 % of the wing, the report's convention. *Model credit* =
Black–Scholes condor under a driftless normal with sd `θ·√(π/2)·impl_move_cc`, the **single** free
parameter `θ = 0.556` calibrated so the model credit at the baseline width reproduces the one
live-observed credit. Under it the risk-neutral 80 % interval sits at `k_Q = 0.894` implied-move
units, versus our baseline `k = 0.70`.

### 5.1 Horizon A — 10:30 → close, common evaluation sample 2024-12-30 to 2026-09-01, n = 418

| method | coverage | mean k | sd k | model credit % | P&L % fixed credit | P&L % model credit | $/contract | loss share | worst % | t |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline k = 0.70 | 0.818 | 0.700 | 0.00 | 0.0868 | 0.0369 | 0.0387 | 29.47 | 0.136 | −0.422 | 6.31 |
| split conformal | 0.813 | 0.712 | 0.105 | 0.0861 | 0.0363 | 0.0374 | 28.51 | 0.136 | −0.446 | 6.09 |
| split conformal + ACI | 0.794 | 0.682 | 0.133 | 0.0940 | 0.0312 | 0.0402 | 30.64 | 0.141 | −0.447 | 6.28 |
| CQR | 0.799 | 0.726 | 0.260 | 0.0915 | 0.0350 | 0.0415 | 31.65 | 0.132 | −0.496 | 6.54 |
| CQR + ACI | 0.794 | 0.730 | 0.269 | 0.0914 | 0.0347 | 0.0411 | 31.31 | 0.139 | −0.496 | 6.49 |
| split conf + ACI, **P-vs-Q gated** (87.6 % of days) | 0.779 | 0.645 | 0.097 | 0.1001 | 0.0290 | 0.0441 | 33.63 | 0.148 | −0.425 | 6.41 |
| CQR + ACI, **P-vs-Q gated** (82.8 %) | 0.772 | 0.631 | 0.132 | 0.1044 | 0.0332 | 0.0526 | 40.09 | 0.147 | −0.439 | 7.78 |
| baseline, **credit ≥ 20 % of wing** (11.2 %) | 0.681 | 0.700 | 0.00 | 0.1067 | −0.0187 | 0.0030 | 2.26 | 0.255 | −0.400 | 0.11 |
| CQR + ACI, **credit ≥ 20 % of wing** (44.0 %) | 0.707 | 0.531 | 0.076 | 0.1285 | 0.0246 | 0.0681 | 51.89 | 0.158 | −0.382 | 7.19 |

Split conformal on the longest sample it allows (2024-07-02 → 2026-09-01, n = 543): baseline coverage
0.823, P&L 0.0384 %; split conformal + ACI coverage 0.810, P&L 0.0379 %.

### 5.2 Horizon B — open → close, common evaluation sample 2022-07-21 to 2026-09-01, n = 1,033

| method | coverage | mean k | sd k | model credit % | P&L % fixed credit | P&L % model credit | $/contract | loss share | t |
|---|---|---|---|---|---|---|---|---|---|
| baseline k = 0.70 | 0.670 | 0.700 | 0.00 | 0.0850 | −0.0125 | −0.0125 | −9.54 | 0.284 | −2.38 |
| split conformal | 0.832 | 0.993 | 0.117 | 0.0391 | **+0.0383** | **−0.0076** | −5.78 | 0.152 | −1.89 |
| split conformal + ACI | 0.821 | 0.985 | 0.182 | 0.0422 | +0.0359 | −0.0069 | −5.27 | 0.159 | −1.70 |
| CQR | 0.806 | 0.963 | 0.217 | 0.0466 | +0.0322 | −0.0062 | −4.73 | 0.163 | −1.49 |
| CQR + ACI | 0.801 | 0.963 | 0.223 | 0.0472 | +0.0310 | −0.0068 | −5.17 | 0.165 | −1.61 |
| split conf + ACI, **P-vs-Q gated** (36.2 % of days) | 0.797 | 0.806 | 0.038 | 0.0640 | +0.0326 | **+0.0116** | **+8.83** | 0.166 | 1.72 |
| CQR + ACI, **P-vs-Q gated** (40.7 %) | 0.726 | 0.752 | 0.097 | 0.0733 | +0.0156 | +0.0038 | +2.93 | 0.210 | 0.53 |
| baseline, credit ≥ 20 % of wing (10.8 %) | 0.536 | 0.700 | 0.00 | 0.1063 | −0.0931 | −0.0718 | −54.71 | 0.411 | −3.46 |
| CQR + ACI, credit ≥ 20 % of wing (4.2 %) | 0.628 | 0.560 | 0.058 | 0.1147 | −0.0008 | +0.0289 | +22.02 | 0.256 | 1.30 |

**The bolded pair in row 2 is the headline negative result.** Same rule, same days; only the credit
assumption changes, and the sign of the P&L flips.

### 5.3 Coverage and P&L by year (model credit)

Horizon B:

| year | baseline cov / P&L % | split conf + ACI cov / P&L % | CQR + ACI cov / P&L % |
|---|---|---|---|
| 2022 | 0.544 / −0.0582 | 0.877 / −0.0309 | 0.825 / −0.0317 |
| 2023 | 0.612 / −0.0371 | 0.840 / −0.0175 | 0.780 / −0.0211 |
| 2024 | 0.718 / +0.0001 | 0.821 / −0.0048 | 0.825 / +0.0020 |
| 2025 | 0.692 / −0.0003 | 0.800 / −0.0021 | 0.812 / −0.0063 |
| 2026 | 0.737 / +0.0181 | 0.784 / +0.0147 | 0.760 / +0.0174 |

Horizon A (2024 row is 1–2 sessions; ignore it):

| year | baseline cov / P&L % | split conf + ACI | CQR + ACI |
|---|---|---|---|
| 2025 | 0.787 / +0.0306 | 0.799 / +0.0273 | 0.795 / +0.0289 |
| 2026 | 0.862 / +0.0502 | 0.796 / +0.0593 | 0.790 / +0.0590 |

Note what conformal does to the *coverage* column in 2022–2023: 0.544 → 0.877 and 0.612 → 0.840,
while the fixed rule was catastrophically miscalibrated. The P&L improves too (−0.058 → −0.031), but
both are still losses. **Conformal made a losing rule honest; it did not make it profitable.**

### 5.4 Conditional coverage by regime (the strongest result in this report)

Horizon B, n = 1,033:

| bucket | n | fixed k = 0.70 coverage | CQR + ACI coverage | mean conformal k |
|---|---|---|---|---|
| VIX/VIX3M slope < 0.85 | 246 | 0.748 | 0.825 | 0.894 |
| slope 0.85–0.95 | 589 | 0.671 | 0.798 | 0.959 |
| slope 0.95–1.00 | 144 | 0.611 | 0.806 | 1.083 |
| slope ≥ 1.00 | 54 | **0.463** | **0.704** | 1.047 |
| VIX < 15 | 270 | 0.730 | 0.826 | 0.971 |
| VIX 15–21 | 543 | 0.681 | 0.792 | 0.912 |
| VIX > 21 | 220 | **0.568** | **0.791** | 1.091 |

Horizon A, n = 418: fixed-rule coverage 0.879 / 0.846 / 0.725 / **0.553** by slope bucket and
0.971 / 0.844 / **0.654** by VIX bucket; conformal 0.818 / 0.812 / 0.700 / 0.711 and
0.914 / 0.791 / 0.753. The fixed rule is *over*-covered in calm regimes (wasting credit) and
*under*-covered in stressed regimes (taking the losses). The conformal rule is roughly flat. That is
conditional calibration, and it is the property a risk process should be judged on.

### 5.5 "P vs break-even" for the current rule — the version testable without option history

Baseline `k = 0.70`, fixed credit 17 % of wing, so `Q(inside) = 1 − c/w = 0.83` exactly (§3, G2).
Break-even `P* = E[loss|outside] / (c + E[loss|outside])` corrects for the partial-loss region.

Horizon A (n = 418):

| bucket | n | coverage P | Q(inside) | E[loss\|outside] % | break-even P* | P − P* pp | mean P&L % |
|---|---|---|---|---|---|---|---|
| slope < 0.85 | 132 | 0.879 | 0.83 | 0.225 | 0.726 | +15.3 | +0.0577 |
| slope 0.85–0.95 | 208 | 0.846 | 0.83 | 0.214 | 0.716 | +13.0 | +0.0520 |
| slope 0.95–1.00 | 40 | 0.725 | 0.83 | 0.377 | 0.816 | −9.1 | −0.0187 |
| slope ≥ 1.00 | 38 | 0.553 | 0.83 | 0.323 | 0.792 | −23.9 | −0.0596 |
| VIX < 15 | 35 | 0.971 | 0.83 | 0.040 | 0.320 | +65.2 | +0.0839 |
| VIX 15–21 | 302 | 0.844 | 0.83 | 0.242 | 0.740 | +10.5 | +0.0474 |
| VIX > 21 | 81 | 0.654 | 0.83 | 0.311 | 0.785 | −13.1 | −0.0226 |
| **ALL** | 418 | 0.818 | 0.83 | 0.265 | 0.757 | **+6.1** | +0.0369 |

Horizon B (n = 1,033):

| bucket | n | coverage P | break-even P* | P − P* pp | mean P&L % |
|---|---|---|---|---|---|
| slope < 0.85 | 246 | 0.748 | 0.742 | +0.6 | +0.0235 |
| slope 0.85–0.95 | 589 | 0.671 | 0.772 | −10.2 | −0.0100 |
| slope 0.95–1.00 | 144 | 0.611 | 0.802 | −19.1 | −0.0489 |
| slope ≥ 1.00 | 54 | 0.463 | 0.807 | −34.5 | −0.1065 |
| VIX < 15 | 270 | 0.730 | 0.756 | −2.6 | +0.0139 |
| VIX 15–21 | 543 | 0.681 | 0.768 | −8.7 | −0.0049 |
| VIX > 21 | 220 | 0.568 | 0.802 | −23.4 | −0.0636 |
| **ALL** | 1,033 | 0.670 | 0.776 | **−10.7** | −0.0125 |

`P − P*` and mean P&L have the same sign in **13 of 15** buckets. The gap is a valid decision
statistic. It also reproduces the existing regime gate exactly (`slope ≥ 0.95` → no new trades)
without any logistic regression — a simpler, more defensible derivation of a rule we already have.

### 5.6 Sensitivity to the one free parameter of the modelled Q

| horizon | θ | k_Q | baseline P&L % | split conf + ACI | CQR + ACI |
|---|---|---|---|---|---|
| A | 0.50 | 0.803 | +0.0181 | +0.0196 | +0.0216 |
| A | **0.556** | 0.893 | +0.0386 | +0.0401 | +0.0410 |
| A | 0.60 | 0.964 | +0.0546 | +0.0560 | +0.0560 |
| A | 0.70 | 1.124 | +0.0892 | +0.0903 | +0.0886 |
| B | 0.50 | 0.803 | −0.0328 | −0.0202 | −0.0207 |
| B | **0.556** | 0.893 | −0.0126 | −0.0070 | −0.0069 |
| B | 0.60 | 0.964 | +0.0032 | +0.0044 | +0.0049 |
| B | 0.70 | 1.124 | +0.0375 | +0.0318 | +0.0327 |

The **level** of every P&L number in this report is a monotone function of θ, a parameter fitted to a
single observed chain. The **ranking** of the methods is nearly θ-invariant, and the ranking of the
*coverage* columns does not involve θ at all. Read the coverage tables as evidence; read the P&L
tables as illustration.

### 5.7 Kelly

Empirical (in-sample, maximising `E[log(1 + f·pnl/maxloss)]` on the realised distribution):

| horizon | method | mean P&L % | full Kelly f* | quarter Kelly |
|---|---|---|---|---|
| A | baseline | +0.0387 | 0.575 | 0.144 |
| A | split conf + ACI | +0.0402 | 0.610 | 0.152 |
| A | CQR + ACI | +0.0411 | 0.675 | 0.169 |
| B | any | ≤ 0 | 0.000 | 0.000 |

Two-state closed form, `f* = p − (1−p)/b`:

| b = c/L | p = 0.75 | p = 0.80 | p = 0.85 |
|---|---|---|---|
| 0.15 | −0.917 | −0.533 | −0.150 |
| **0.20** | −0.500 | **−0.200** | +0.100 |
| 0.25 | −0.250 | 0.000 | +0.250 |
| 0.30 | −0.083 | +0.133 | +0.350 |
| 0.41 (wing 0.5 %, credit 0.145 %) | +0.140 | +0.312 | +0.484 |

### 5.8 What these results do and do not show

**They do show:**
- Coverage of the fixed-`k` rule is regime-dependent and collapses to 0.46–0.57 in stressed regimes;
  conformal calibration removes most of that dependence, out of sample, on 1,033 and 418 sessions.
- The break-even inside-probability is computable without any option data and its sign agrees with
  realised P&L in 13 of 15 regime buckets.
- Once the credit is made consistent with the interval width, widening the interval does not pay.
- The Kelly fraction for our payoff at 80 % coverage and a 20 % credit ratio is negative, and its
  standard error at realistic sample sizes exceeds any prudent bet.

**They do not show:**
- That the Conformal Condor makes money. Horizon B is negative under the width-consistent credit for
  every ungated method; horizon A is positive but covers 2025–2026 only, a period F1 already
  identified as the favourable regime (Vilkov: every condor width profitable 01/2024–02/2026, every
  width unprofitable 01/2022–12/2023). Horizon A is therefore **not** independent evidence.
- That the P-vs-Q gate works. t = 1.72 on one gate, one dataset, with a modelled Q. Under F2's
  best-of-N argument, one gate on one horizon is already most of our testing budget.
- Anything about execution. No spreads, no slippage, no fill probability, no early assignment. F1's
  numbers (four legs at one tick, ≈ $0.021–0.024 net effective cost per leg at the mid) would take a
  further ~0.02–0.03 % of spot off every row in §5.1–5.2 — enough to erase horizon A's edge too.
- Anything about the real risk-neutral measure. Our Q is a normal with one fitted parameter. The real
  0DTE Q is skewed and fat-tailed (Bandi et al.), which means our `Q_outside` understates the put
  side and overstates the call side. **In production we read Q off the quote and this problem
  disappears**; it only contaminates the back-test.

---

## 6. Risks, stated the way they should appear in the write-up

1. **Overfitting.** Configurations tested here: 2 horizons × 5 interval rules × 2 credit models ×
   4 gate variants ≈ 80 cells, plus a 5-point θ sweep. Under F2 §5.3's arithmetic that is far past
   the multiple-testing budget for a 3-session live record. **Mitigation and disclosure:** ship
   exactly one configuration (split conformal on the ratio + ACI, γ = 0.005, α = 0.20, W = 250,
   margin 0.05, clip [0.35, 1.60]), pre-registered in `config/` before the first trade, with this
   report as the timestamped record of everything that was tried. Report the count. Do not tune
   anything after Wednesday's open.
2. **Exchangeability violation.** The split-conformal theorem (S-G2) assumes exchangeable
   calibration data. Daily returns are not exchangeable — volatility clusters, and our own §5.4 table
   is the proof. Two honest defences, both stated: (i) conformalising the **ratio** to implied vol
   removes most of the heteroskedasticity before calibration; (ii) ACI's guarantee (S-G4) requires
   **no** exchangeability, only bounded α — so the claim we make is the ACI long-run claim, not the
   split-conformal finite-sample claim. **Do not state the finite-sample interval as if it held.**
3. **The guarantee is asymptotic and we have three sessions.** Gibbs–Candès bound the *time-averaged*
   miscoverage by `(α₁ + γ)/(Tγ)`; at T = 3 and γ = 0.005 that bound is vacuous. The correct
   statement in the video is: *"the method is calibrated by construction over long horizons; over
   three sessions we can only show you the numbers, and we show you all of them."*
4. **Fixed-credit bias in our own existing back-test.** `docs/regime_model_report.md` prices every
   condor at 17 % of the wing regardless of the strike distance. That is fine for a fixed-`k` rule
   and **wrong for any rule that varies `k`**, in the optimistic direction — §5.2 quantifies it at
   +0.046 % of spot per session, four times the effect being measured. Correct the report or add the
   caveat; do not let it stand as a validation of a variable-width rule.
5. **0DTE pricing biases on the Q side.** Bandi/Fusari/Renò (S-G13) show standard models misprice at
   `T → 0`. Our production estimator sidesteps model risk (`credit/wing` is a price, not a model) but
   inherits **discretisation bias** — `credit/w = Q(outside)` is exact only as `w → 0`, and at a
   0.5 %-of-spot wing on a 0DTE distribution the error is second-order in the local RND slope,
   biasing `Q_outside` *upward* (the vertical spread is worth slightly less than `w·Q` when the
   density is decreasing across the wing). Direction: **it makes the gate look more attractive than
   it is.** Mitigation: the 5-point margin, and log the per-side delta cross-check.
6. **Bid-ask on the Q side.** `Q_outside` computed at the mid is not achievable; at the fill it is
   lower. Log both `credit_mid` and `credit_filled` and report the gate decision under both. If the
   gate flips sign between mid and fill, that is a finding worth a slide.
7. **Regime dependence, not edge.** F1 E-V5/E-V6 already established that every result in
   2024–2026 flips sign in 2022–2023 and that the structural-break test is insignificant (t = 1.18).
   Our §5.3 reproduces exactly that. **Any claim built on horizon A alone is a claim about a
   two-year regime.** Say it in the same sentence as the number.
8. **Back-fill of the calibration window.** Starting `alpha_t` and `scores` from historical data is a
   modelling choice that makes the agent look calibrated on day 1. It is defensible (the alternative
   is 250 sessions of no trading) but it must be logged as an assumption, and the coverage plot must
   mark where the back-filled scores end and live scores begin.
9. **The credit gate conflict (action required).** The design adopted "credit ≥ 20 % of wing" from
   F1; the live chain on 2026-09-02 paid 17 % at `k = 0.70` and a 0.5 % wing. Under the coverage-gate
   formulation these are the same constraint expressed twice: `credit/wing ≥ 0.20` is
   `Q_outside ≥ 0.20`, i.e. exactly `α + margin` at `α = 0.20, margin = 0`. **Recommendation: delete
   the separate 20 % credit gate and replace it with the coverage gate `Q_outside ≥ α_t + 0.05`,
   which is the same object with an explicit, defensible derivation.** This removes a rule, adds a
   theorem, and resolves the conflict.

---

## 7. Follow-up sources

Ordered by value to us; none is required to ship.

1. **Angelopoulos & Bates (2023), "Conformal Prediction: A Gentle Introduction", *Foundations and
   Trends in Machine Learning* 16(4), 494–591.** DOI 10.1561/2200000101. The reference to put in the
   write-up's bibliography for a reader who has never seen conformal prediction.
2. **Almeida, Freire & Hizmeri (2024), "0DTE Asset Pricing", SSRN 4701401.** Unread; likely contains
   the P-vs-Q gap measured directly on 0DTE options, which is exactly the number our modelled Q is
   standing in for. Highest-value single read if there is time.
3. **Bandi, Fusari & Renò (2023), SSRN 4503344, full text.** Needed only if we ever want to price Q
   ourselves. Read the section on the size of the Black–Scholes error at `T → 0` to quote a number
   for risk 5.
4. **Zaffran et al. (2022), PMLR 162, γ-sensitivity figure.** Pre-register our γ against it rather
   than against nothing.
5. **Gneiting, Balabdaoui & Raftery (2007), *JRSS-B* 69(2), 243–268.**
   DOI 10.1111/j.1467-9868.2007.00587.x. The (calibration, sharpness) reporting frame; one paragraph
   suffices.
6. **Christoffersen, Jacobs & Chang (2013), "Forecasting with Option-Implied Information",
   *Handbook of Economic Forecasting* vol. 2A, 581–656.** DOI 10.1016/B978-0-444-53683-9.00010-4.
   Why Q ≠ P is expected rather than an anomaly.
7. **Bastos (2024), *ESWA* 245:123087, full text.** Read before making the novelty claim in public.

---

## 8. One-paragraph version, for the write-up

> An iron condor is the sale of a prediction interval on today's close. We build the interval with
> split conformal prediction on the ratio of the realised move to the implied move, and we adapt the
> confidence level online with Adaptive Conformal Inference, so the interval is calibrated without
> assuming any distribution and without assuming the market is stationary. We then read the market's
> own probability for that same interval directly off the option chain: for a vertical spread of
> width *w*, the credit divided by *w* is the risk-neutral probability of finishing beyond the short
> strike — that is Breeden and Litzenberger (1978) in its simplest form, one subtraction instead of a
> density estimate. We sell the interval only when the market pays more for it than our calibration
> says it is worth, by a margin that covers the round trip. We size it with a capped fractional
> Kelly, and we report what almost nobody reports: the empirical coverage of our own intervals,
> session by session, against the level we promised. We do not claim an edge. We claim a calibrated
> interval and a price we were willing to sell it at.

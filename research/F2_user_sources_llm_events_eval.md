# F2 — Four paywalled sources: LLM return signals, earnings-event option pricing, LLM reproducibility, deflated Sharpe

Report F2. Author: Claude (Opus 5) research agent. Date: 2026-09-02.
Scope: full read of four user-supplied papers, checked against the design decisions in `STATE_OF_THE_ART.md` §4, §5, §6, §8.
All arithmetic in §5 was recomputed from scratch; the reconstruction of Bailey & López de Prado's own worked example reproduces their published DSR values to four decimals, which validates the formulas used.

---

## 1. Summary (decision-relevant first)

1. **Chen/Kelly/Xiu does not support giving the LLM any numeric or directional role in our design, and it is the strongest available citation for *why*.** Every result is cross-sectional (long top quintile / short bottom quintile of single stocks), one day ahead, executed open-to-open, with a ridge head trained on six years of labelled returns. There is **no index-level, market-timing, volatility or option result anywhere in the paper**. For large caps executed close-to-close — the closest analogue to what an SPY agent could act on — the annualized long-short Sharpe collapses to **0.14** (Table IA9). Our "LLM emits categories only" split is confirmed.
2. **Model size barely matters; open-weight is fine.** LLaMA 7B/13B/70B and LLaMA2/LLaMA3 are within noise of each other and of ChatGPT embeddings (Diebold-Mariano statistics among them 0.03–0.49, insignificant). LLaMA3-70B is *worse* than LLaMA3-8B on articles (3.98 vs 4.59). Chen et al.: "no monotonic relationship between model scale and Sharpe ratios" (IA D.4, p. 7 of the appendix). A Featherless 8B–70B instruct model is defensible; paying for the largest is not.
3. **Koviazin et al. give us the exact determinism recipe and the number that justifies it.** Temperature 0 alone leaves decision entropy at 0.98 bits and return SD at 5.5 pp; fixing the seed as well leaves 0.73 bits / 4.3 pp; **only T=0 + fixed seed + top_k=1 + top_p=0 reaches entropy 0.0 and SD 0.0.** With defaults (T=1) the same agent on the same stock over the same 3 months produced final returns from **≈5% to ≈28%** across 10 identical runs — SD ≈ 50% of the mean.
4. **Our "no single-name earnings trades" rule survives, but our justification in `STATE_OF_THE_ART.md` §6 V15 is factually wrong and must be replaced.** Dubinsky et al. show earnings straddles are, on average, a *losing long / profitable short*: mean 1-day EAD straddle return **−7.96%**, median **−10.24%**, t = **−13.25**, negative in all 16 sample years. The correct reason to abstain is dispersion, not sign: SD **27.47%**, short-side skew **−1.44**, kurtosis **8.93**, giving a per-trade Sharpe of 0.29 and a **Minimum Track Record Length of ~52 trades** to establish the edge at 95%. We could take at most 5. One draw can consume the whole 2%/6% budget.
5. **The earnings premium has been shrinking and reverses on the mean in the last third of the sample.** Pooled Q-vol 8.22% vs P-vol 7.42% (80 bp premium), but 2011–2015: Q-vol **6.78%** vs P-vol **7.35%** — the mean-based premium is *negative*. Only the standardized-return statistic (SD of standardized EAD returns 0.91–0.94, χ² rejects 1.0 at 1%) is stable across subperiods. This is an additional, decisive argument for the abstention.
6. **Dubinsky gives us a free, novel, cheap feature for the event gate: price the macro event out of the SPY term structure.** Their term-structure estimator, verified here on their own Brexit example to 3 decimals, turns two ATM implied vols into the *event-only* move: σ_j = sqrt((IV₁² − IV₂²) / (1/T₁ − 1/T₂)). Applied to SPY expiries that do and do not span Thursday's ISM or Friday's NFP, this produces a logged number ("the market prices a 0.9% NFP jump") instead of a hard-coded clock rule. No other hackathon team will have this.
7. **Their vol-of-vol replication is a direct code warning for our IV-vs-RV veto.** Sorting on a short-dated IV statistic computed across an earnings window destroys the signal: high-minus-low CAPM alpha is −1.20%/month (t = −4.56) for non-announcing firms but +0.04% (t = 0.10) for announcing firms. Any short-dated IV feature that spans a scheduled event is mechanically contaminated. Our `IV-vs-RV` veto (D-R14) must strip the event component, or use a longer maturity, or it will misfire on exactly the days it exists for.
8. **Bailey & López de Prado give the four numbers that should headline our evaluation section.** With daily returns, skew −1.5, kurtosis 6: certifying an annualized Sharpe of 0.5 / 1.0 / 2.0 at 95% needs **2,860 / 751 / 207 trading days**. A hypothetical +$400 over 3 trades has an apparent annualized Sharpe of **8.27** and a Probabilistic Sharpe Ratio of only **0.69–0.76**. And with T = 3 observations and kurtosis 6, **PSR can never exceed 0.897** no matter how good the record looks. Nothing is inferable from our horizon — provably, not rhetorically.
9. **Two configurations already exhaust the multiple-testing budget on our horizon.** Under the null, a strategy's estimated annualized Sharpe over 3 daily observations has SD sqrt(252/3) = 9.17. The expected maximum over N = 2 independent trials is **4.76**; over N = 5 it is **10.93**. The "how many configurations until E[max Sharpe] = 1.0" question has the answer **N ≈ 2** for us (and N ≈ 4–26 for a normal one-year backtest depending on trial dispersion). Recommendation: make the random-entry Monte Carlo benchmark a *best-of-N* null, and pre-register the 37% secretary stopping rule.
10. **Two cheap upgrades to the plan, both citation-backed.** (a) Feed the LLM *model-generated one-sentence summaries*, not raw headlines: Chen et al. find summaries beat both headlines and full text for every LLM (LLaMA3 EW Sharpe 3.59 headline → 4.59 article → 5.42 summary) — this gives our existing two-model-tier plan a citation. (b) Measure our anonymization the way they do: re-feed the masked text to the same model and ask it to name the entity; report the failure rate (they get 86.4% on bodies, 95.7% on alerts, and only 76.4% under a stricter evaluation prompt).

---

## 2. Source cards

### S-F2-1 — Chen, Kelly & Xiu, "Expected Returns and Large Language Models"

| | |
|---|---|
| Authors | Yifei Chen (Chicago Booth), Bryan Kelly (Yale, AQR, NBER), Dacheng Xiu (Chicago Booth, NBER) |
| Status | SSRN working paper 4416687, unpublished |
| Version | No date printed in the extracted PDF. Internal evidence dates this version to **late 2025 or later**: it cites Aït-Sahalia, Jacod & Xiu 2025 *RFS* 38:3542–3579, He/Lv/Manela/Wu 2025 (ChronoBERT), Shen & Xiu 2025 NBER w33421, Jha/Liu/Manela 2025 *RFS*, Breitung & Müller 2025 *JFE*. First draft circulated 2022 (fn. 3, fn. 8). Not in OpenAlex (checked). |
| Citation-worthiness | **High.** Top-tier authors, enormous sample, explicit look-ahead controls. But: working paper, not peer-reviewed; Sharpe ratios of 4–5 on daily equal-weighted small-cap long-short portfolios should be read as an upper bound. Cite the *design* implications, not the Sharpes. |

**Data and method.** Refinitiv news (RTRS + third-party), Jan 1996 – Jun 2019 (US extended to May 2022 for robustness), 3.04 m US articles and 2.94 m alerts after filters, plus 15 non-US markets / 12 additional languages. Step 1: mean-pool the last-hidden-layer token embeddings of each document with a frozen pre-trained LLM (BERT-large, RoBERTa-large, LLaMA-13B, LLaMA2-13B, LLaMA3-8B, OpenAI `text-embedding-3-large`), first 512 tokens. Step 2: ridge panel regression of next-period return on the embedding, trained on a rolling 8-year window (6 train / 2 validate), tested on the following year; OOS 2004–2019. Portfolios: daily quintile long-short, open-to-open, news between 09:00 and 09:30 ET pushed to the next day. Benchmarks: Loughran-McDonald, SESTM (Ke/Kelly/Xiu), Word2Vec/fastText.

### S-F2-2 — Dubinsky, Johannes, Kaeck & Seeger, "Option Pricing of Earnings Announcement Risks"

| | |
|---|---|
| Authors | Andrew Dubinsky (Goldman Sachs), Michael Johannes (Columbia), Andreas Kaeck (Sussex), Norman J. Seeger (VU Amsterdam) |
| Venue | *The Review of Financial Studies* 32(2), 2019, pp. 646–687 |
| DOI / dates | 10.1093/rfs/hhy060; received 2017-04-13, accepted 2018-02-05, advance access 2018-05-22. Subsumes Dubinsky & Johannes (2006). |
| Citation-worthiness | **Very high.** Peer-reviewed top-3 finance journal, editor Van Nieuwerburgh, closed-form estimators, 15-year sample. The single best citable source for scheduled-event option pricing. |

**Data and method.** OptionMetrics IvyDB, Jan 2000 – Aug 2015; the 50 most liquid firms by dollar volume each year (196 firms total), dividend yield < 2%, price > $5, CRSP share code 10/11. Announcement dates and *times* reconciled across Thomson Reuters, IBES and Compustat with LexisNexis tie-breaking. ATM implied vols are the average of the closest-to-the-money call and put IV per maturity (mitigates stale-quote / put-call-parity bias); options with < 3 DTE excluded. 3,008 usable EAD observations for the term-structure estimator. Theory: Black-Scholes and Heston-type SV augmented with a *predictably timed* jump on the announcement date; structural SV models estimated by unscented Kalman filter on six firms (AMZN, GE, IBM, INTC, MSFT, QCOM).

### S-F2-3 — Koviazin, Mudarisov, Polyachenko & State, "Reproducibility in the TradingAgents Framework"

| | |
|---|---|
| Authors | Aleksandr Koviazin, Timur Mudarisov, Evgeny Polyachenko, Radu State — all University of Luxembourg |
| Venue | IC-AIF 2026 (Int. Conf. on AI and Fintech), Guangzhou, 9–11 Jan 2026, ACM, pp. 365–370, 6 pages, CC BY-NC-ND |
| DOI | 10.1145/3800973.3801029 — **verified via OpenAlex**, publication date 2026-01-09 |
| Citation-worthiness | **Medium-high for the reproducibility numbers, low for the performance claim.** Peer-reviewed conference paper, but one asset, one 3-month window, and the returns are statistically indistinguishable from everything. Cite it for the entropy/variance figures and the parameter recipe, which are the parts that are properly measured. |

**Data and method.** Re-run of the TradingAgents multi-agent framework (Xiao et al., arXiv 2412.20138) on GOOGL, May–Jul 2025, research-debate depth 1. Backends: GPT-4o (5 runs, temperature 0 and 1 only — API cost was prohibitive) and locally hosted Qwen3-30B (10 independent runs per configuration, Ollama). Sampling parameters varied: temperature {0,1}, seed {random, 42}, top_k {40, 1}, top_p {0.9, 0}. Metrics: daily Shannon entropy over the {Buy, Hold, Sell} signal (max log₂3 = 1.58) and cumulative return of a fully-invested long/short/flat simulator, benchmarked against GOOGL buy-and-hold, QQQ buy-and-hold, and a perfect-foresight lookahead upper bound.

### S-F2-4 — Bailey & López de Prado, "The Deflated Sharpe Ratio"

| | |
|---|---|
| Authors | David H. Bailey (LBNL ret., UC Davis), Marcos López de Prado (Guggenheim Partners, LBNL) |
| Venue | *Journal of Portfolio Management*, forthcoming 2014 (as printed) |
| Versions / SSRN | First version 2014-04-15, this version **2014-07-31**; SSRN 2460551 |
| Citation-worthiness | **High**, and it is already the standard citation for this argument. Caveat: **the paper does not contain the MinTRL formula.** "Minimum Track Record Length" appears only in the keyword list; the formula lives in the companion Bailey & López de Prado (2012a), *The Sharpe Ratio Efficient Frontier*, J. Risk 15(2). Cite MinTRL to the 2012 paper, not this one. |

**Content.** Argues that the number of trials is the single most important missing datum in published backtests; that holdout does not protect against it (apply holdout 20 times at 95% and false positives are *expected*); that overfitting in the presence of memory effects maximizes out-of-sample *losses*, not merely zero. Derives, via extreme value theory, the expected maximum Sharpe over N independent trials; defines the Deflated Sharpe Ratio as a Probabilistic Sharpe Ratio whose threshold is that expected maximum; supplies Python (Snippet 1) and a numerical accuracy study (Exhibits 3.1/3.2); supplies a method to convert M dependent trials into N implied independent trials via average correlation (Appendix 3); recommends the 1/e secretary rule as a stopping rule for the number of configurations to test.

---

## 3. Evidence table

Confidence: H = directly stated + numerically checkable; M = stated once or reconstructed from a garbled table; L = inference.

| ID | Finding | Number | Page / table | Source | Conf. |
|---|---|---|---|---|---|
| **CKX — what the signal is** ||||||
| X1 | Signal = mean-pooled document embedding of a news item, mapped to expected return by ridge on a rolling 6y-train/2y-validate window | 512 tokens baseline; P = 1,024–5,120 dims | §2.1–2.2, pp. 7–9 | CKX | H |
| X2 | Horizon is **one day**, cross-sectional quintile long-short, open-to-open; news 09:00–09:30 ET deferred to next day | 1 day | §2.2–2.3, pp. 9–10 | CKX | H |
| X3 | **No time-series / market-timing / index-level test exists in the paper.** Every table is a cross-sectional stock sort | — | whole paper | CKX | H |
| X4 | Equal-weighted L-S annualized Sharpe: ChatGPT 4.78, LLaMA3 4.59, LLaMA2 4.36, LLaMA 4.04, RoBERTa 3.69, BERT 3.00, Word2Vec 2.74, SESTM 2.57, LMMD 2.33 | see left | Table 5, p. 23 | CKX | H |
| X5 | **Value-weighted (large-cap) L-S Sharpe is 3–4× lower**: ChatGPT 1.34, LLaMA3 1.10, LLaMA2 1.02, LLaMA 0.89, RoBERTa 0.92, BERT 0.70, SESTM 0.74, Word2Vec 0.60, LMMD 0.40 | see left | Table 5, p. 23 | CKX | H |
| X6 | Mean daily cross-sectional correlation between prediction and realized return: ChatGPT 2.68%, LLaMA3 2.45%, LMMD 0.98% — i.e. R² ≈ 0.07% | 0.0268 | Table 3, p. 20 | CKX | H |
| X7 | **Execution timing destroys it for large caps**: LLaMA3 VW L-S Sharpe = 1.10 open-to-open, 0.50 at VWAP, **0.14 close-to-close** | 0.14 | Table IA9 | CKX | H |
| X8 | **Decay**: EW L-S Sharpe by delay day 1→6: 4.58, 1.35, 0.98, 0.91, 0.54, 0.25. VW: 1.10, −0.22, −0.05, 0.31, 0.27, 0.73 | see left | Table 18, p. 43 | CKX | H |
| X9 | Predictability persists 3–4 days for small firms, "absorbed within one to two trading days" for large firms | — | §4.3, p. 44 | CKX | H |
| X10 | **Transaction costs kill the article strategy at high turnover.** LLaMA3 EW net Sharpe by turnover parameter λ: 0.77 (λ=0.1, 16.7% daily turnover), 0.72, 0.53, 0.29, 0.04, **−0.21** (λ=0.6, 107% turnover), … −0.87 (λ=0.9). Cost model: 10 bp (large) / 20 bp (small) per 100% turnover | net Sharpe turns negative above ~107% daily turnover | Table 8 Panel A, p. 28 | CKX | H |
| X11 | Alert-based (headline-only) strategies survive costs: net Sharpe 1.26 → peak **1.68** at λ=0.4 → 1.33 at λ=0.9 | 1.68 | Table 8 Panel B, p. 28 | CKX | H |
| X12 | **Model scale is non-monotonic**: LLaMA 7B 3.99 vs 13B 4.04; LLaMA2 7B 4.25 / 13B 4.36 / 70B 4.89; LLaMA3 8B 4.59 vs **70B 3.98** (article, EW) | see left | Table IA8, IA p. 7 | CKX | H |
| X13 | Diebold-Mariano statistics among LLaMA, LLaMA2, LLaMA3 and ChatGPT are 0.03–0.49 — **insignificant**; all four decisively beat LMMD (~2.1) and BERT/Word2Vec | 0.03–0.49 | Table 4, p. 20 | CKX | H |
| X14 | Context length is nearly irrelevant: EW Sharpe 4.59 (512 tok) vs 4.38 (1k) vs 4.39 (4k) vs 4.39 (8k). 60.5% of articles are under 512 tokens | ±0.2 | Table IA10, IA D.5 | CKX | H |
| X15 | **AI-generated summaries beat both headlines and full text**: LLaMA3 EW 3.59 (headline) → 4.59 (article) → **5.42** (summary); LLaMA2 4.04 → 4.36 → 5.63; ChatGPT 4.57 → 4.78 → 5.01 | see left | Table 16, p. 39 | CKX | H |
| X16 | **Post-knowledge-cutoff performance is not lower**: BERT EW L-S Sharpe 2.90 pre-cutoff vs 4.97 post (Oct 2018→Jun 2022); RoBERTa 3.72 pre vs 4.91 post (Jul 2019→Jun 2022) | 4.9–5.0 | Table 13, p. 36 | CKX | H |
| X17 | **Anonymization costs little**: LLaMA3 articles EW 4.59 → 4.38 masked → 3.99 filtered → 3.71 masked+filtered. Alerts: 4.79 → **4.96** masked (improves) | −0.2 to +0.2 | Table 15, p. 38 | CKX | H |
| X18 | Masking success rate (evaluator = LLaMA3.1-8B-Instruct): 95.73% alerts, 86.38% articles, 90.53% both. Under the stricter "act like a skilled analyst" prompt: 95.13% / 76.43% | 76–96% | Tables 14, IA4, IA5 | CKX | H |
| X19 | Non-English works: LLaMA3 mean cross-sectional correlation 1.93% overall, **1.92% in non-English markets**; Word2Vec 0.79% English / 0.36% non-English. Non-US pooled portfolio EW L-S Sharpe: LLaMA2 1.69, LLaMA 1.56, LLaMA3 1.35, RoBERTa 1.23, BERT 0.87, **Word2Vec 0.10** | see left | Tables 11–12, pp. 32–34 | CKX | H |
| X20 | **Topic heterogeneity**: sell-side recommendation / target-price revisions is the strongest and most stable channel; qualitative corporate narrative contributes almost nothing. Removing the whole earnings cluster: EW Sharpe 5.42 → 4.55. Excluding the ±1-day earnings window: 4.59 → 4.30 | see left | §4.5, pp. 51–52; Table 6, p. 25 | CKX | H |
| X21 | Verbatim, on prompt-based (as opposed to embedding-based) use of LLMs: "LLM responses can be highly sensitive to small changes in the prompt and typically incorporate randomness even in controlled settings (which can hinder replicability)" | — | §1.4, p. 6 | CKX | H |
| **Dubinsky — event pricing** ||||||
| D1 | Model: annualized implied variance across N events = σ² + T⁻¹ Σ (σ_j^Q)². IV rises non-linearly into the event, drops discontinuously after, term structure slopes down before | Eq. (1), (3) | pp. 648, 654 | DJKS | H |
| D2 | **Term-structure estimator (ex ante):** (σ_j^Q)² = (IV²_{t,T1} − IV²_{t,T2}) / (T₁⁻¹ − T₂⁻¹) | Eq. (4) | p. 654 | DJKS | H |
| D3 | **Time-series estimator (ex post):** (σ_j^Q)² = Δ·(IV²_before − IV²_after), Δ = 1/252 | Eq. (5) | p. 654 | DJKS | H |
| D4 | Brexit worked example: 1M and 2M USD/GBP IV of 28.21% and 21.51% → implied event move **7.45%**; GBP actually fell 7.6% the next day. **Reproduced here as 7.451%** | 7.45% vs 7.6% | p. 650 / 291 | DJKS | H |
| D5 | AMZN 2014-10-23 example: term estimator 10.26%, time-series estimator 9.87% from the same day. (The printed IVs 75.28%@8d / 54.37%@15d reproduce as 11.28% at act/365 — a likely OCR digit error in the extraction; the two-estimator agreement is the point) | 10.26% / 9.87% | p. 654 | DJKS | M |
| D6 | Pooled anticipated announcement volatility across 3,008 EADs: **mean 6.87%, median 5.55%, IQR 3.48–9.06%**. Time-series estimator mean 6.04%; rank correlation between the two 93% across firms, 82% pooled within firm | 6.87% | Tables 4–6, pp. 663–666 | DJKS | H |
| D7 | Cross-firm range is enormous: NFLX 14.92%, FSLR 14.13%, AMZN 12.06%, YHOO 9.96%, AAPL 8.83%, CSCO 8.13%, GOOGL 7.94%, INTC 7.04%, IBM 5.68%, MSFT 5.35% vs JNJ 2.56%, XOM 2.50%, CVX 2.53%, MO 2.71% | 2.5–15% | Table 4, pp. 662–663 | DJKS | H |
| D8 | Strong business-cycle variation: 2000 10.51%, 2001 10.91%, 2008 10.05% vs 2003 4.90%, 2010 5.05%. Cross-sectional dispersion more than doubles in recessions (<3% → >6%) | 2× | Table 5, p. 665 | DJKS | H |
| D9 | **Implied predicts realized well**: cross-firm correlation of average Q-vol with average realized EAD vol = **85%**; pooled time-series correlation of σ_j^Q with |EAD return| = **54.9%** (rank 53.5%) — "close to what could maximally be expected given normal sampling errors" | 85% / 55% | pp. 649, 667; Table 7 | DJKS | H |
| D10 | Regression of |EAD return| on σ_j^Q: slope 0.58, **t = 11.42, R² = 28.47%**. Analyst-forecast dispersion: R² = 0.17%, insignificant. All three predictors: R² = 29.68% | 28.5% | Table 8 Panel A, p. 668 | DJKS | H |
| D11 | For the *following month's* volatility: σ_j^Q alone R² = 45.99%, diffusive IV alone 65.80%, both 73.46% | see left | Table 8 Panel B, p. 669 | DJKS | H |
| D12 | **Earnings variance carries a premium — but a shrinking one.** Pooled Q-vol 8.22% vs realized close-to-close P-vol 7.42% (**+80 bp**); close-to-open comparison 6.87% vs 6.31% (**+56 bp**). Subperiods (Q vs P, close-to-close): 2000–05 **9.92 vs 7.63**; 2006–10 **7.74 vs 7.22**; 2011–15 **6.78 vs 7.35 — reversed** | +80 bp pooled, −57 bp in 2011–15 | Table 9, p. 670 | DJKS | H |
| D13 | The robust statistic is the SD of standardized EAD returns: **0.92 pooled** (0.94/0.92/0.91 by subperiod), where 1.0 = no premium; χ² rejects 1.0 at the 1% level in every subperiod | 0.92 | Table 9, p. 670 | DJKS | H |
| D14 | **Long ATM straddle held across the announcement: mean −7.96%, median −10.24%, SD 27.47%, skewness +1.44, kurtosis 8.93, t = −13.25.** Negative in all 16 years; best firm-level average merely +1%. Bootstrap of matched non-EAD days: mean −1.51%, 1st percentile −2.17% — EADs are far more negative than normal days, but normal days are negative too | −7.96% ± 27.47% | Table 10, p. 672 | DJKS | H |
| D15 | Straddle returns of −8.5% are what a 1-percentage-point wedge between P- and Q- jump vol produces in their calibrated model — the observed −7.96% implies a wedge of roughly 1 vol point | ~1 pt | p. 672 | DJKS | H |
| D16 | **The vol crush, quantified.** With diffusive σ = 40% and σ_j = 10%, a 1-week ATM option's IV is ≈92% before the release and 40% after. Their worked straddle example loses ≈50% of its value from the vol drop alone with the stock unchanged | 92% → 40% | fn. 15 p. 664; p. 671 | DJKS | H |
| D17 | Realized EAD volatility vs normal days: pooled variance ratio **5.71** (EAD vol 7.32% vs 3.06%); by year up to 19.15 (2013); by firm up to 47.32 (NFLX), down to 1.00 (CVX). In 2015 EADs produced **19.4% of the year's total variance in 4 days** (uniform would be 1.6%) | 5.71× | Tables 2–3, pp. 660–661 | DJKS | H |
| D18 | Close-to-open volatility on EADs is **more than 3× normal**, open-to-close is only slightly higher → the move is a jump, fully digested by the open (Martineau 2017: 80% of the response in the first few trades) | 3× | §3.1 / Online App. A.3, p. 660 | DJKS | H |
| D19 | **Short-dated IV features are contaminated by events.** Replicating the vol-of-vol anomaly: high-minus-low CAPM alpha is −0.73%/mo (t = −2.76) for all stocks, **+0.04% (t = 0.10) for firms announcing in the formation month**, and **−1.20% (t = −4.56) for firms not announcing**. With 1-year options the contamination vanishes (−0.81% vs −0.79%) | see left | Table 11, p. 675 | DJKS | H |
| D20 | Code note: "the most reasonable interpolation is linear in variances", **not** OptionMetrics' log-maturity interpolation | — | p. 675 | DJKS | H |
| D21 | The earnings jump has a **systematic** component: ex-ante earnings vol correlates ~60% across firms with historical equity beta | 60% | p. 650 | DJKS | H |
| D22 | Trading costs caveat: ATM bid-ask spreads are 6.17% of mid on EAD+1 vs 6.05% on normal days (small), but the authors state naive strategies at closing quotes "may consume a substantial portion of these short straddle returns" | ~6% of mid | Table 1B p. 659; p. 673 | DJKS | H |
| D23 | The framework explicitly generalizes to macro announcements, elections, referendums, summits, OPEC meetings | — | p. 650 | DJKS | H |
| **Koviazin — reproducibility** ||||||
| K1 | Decision entropy over {Buy, Hold, Sell} (max 1.58 bits): GPT-4o T=1 **0.76**; Qwen3-30B T=1 **1.10**; Qwen T=0 **0.98**; Qwen T=0 + seed 42 **0.73**; Qwen T=0 + seed 42 + top_k=1 + top_p=0 **0.00** | see left | Table 1, p. 366 | KMPS | H |
| K2 | Cumulative return over 3 months, mean ± SD (SEM): GPT-4o T=1 15.8 ± 9.4 (4.2); Qwen T=1 **18.1 ± 9.0** (2.8); Qwen T=0 21.3 ± 5.5 (1.7); Qwen T=0+seed 16.8 ± 4.3 (1.5); fully deterministic **28.2 ± 0.0** | see left | Table 1, p. 366 | KMPS | M (table garbled; cross-checked against abstract and §3.2 text) |
| K3 | Benchmarks: GOOGL buy-and-hold **19.1%**, QQQ **17.4%**, perfect foresight **97.3%** (lookahead converges at N=3 days: 83.51% → 94.18% → 97.25%) | see left | Table 1 / §2 | KMPS | H |
| K4 | Across 10 identical runs at T=1, final returns spanned **≈5% to ≈28%**; SD ≈ 50% of the expected return | 23 pp spread | Fig. 3, §3.2 | KMPS | H |
| K5 | t-tests: agent vs buy-and-hold **p > 0.26** (not significant); agent vs perfect foresight p < 0.001. Confidence intervals for both stochastic configurations contain both benchmarks | p > 0.26 | §3.2, p. 368 | KMPS | H |
| K6 | Transaction costs: 17 trades per quarter at 0.05% round-trip ≈ **0.85%** drag — an order of magnitude below the return SD | 0.85% | §3.2, p. 368 | KMPS | H |
| K7 | **Fixing the seed introduces seed dependence.** The authors explicitly label the deterministic 28.2% "a form of cherry-picking" because it is a single seed realization, and say the means of seeded configs cannot fairly be compared with seed-averaged ones | — | §3.2, §4, pp. 368–369 | KMPS | H |
| K8 | **Look-ahead was avoided by construction, not audited.** They chose May–Jul 2025, past both cutoffs (GPT-4o May 2024, Qwen3-30B Apr 2025), and assert this "eliminat[es] the risk of data leakage". No leakage test was run inside TradingAgents | — | §2, p. 366 | KMPS | H |
| K9 | Limitations they state: single asset, single 3-month window; they call for multi-asset, longer-horizon validation and cite Dodge et al. 2019 ("Show Your Work") as the reporting standard | — | §4 | KMPS | H |
| **Bailey & López de Prado** ||||||
| B1 | Expected maximum Sharpe over N independent trials: E[max SR] ≈ E[SR] + sqrt(V[SR]) · ((1−γ)·Z⁻¹[1−1/N] + γ·Z⁻¹[1−1/(N·e)]), γ = 0.5772156649 | Eq. (1)/(6) | pp. 7, 12 | BLdP | H (verified against Snippet 1, p. 13) |
| B2 | DSR = Z[ (SR̂ − SR₀)·sqrt(T−1) / sqrt(1 − γ₃·SR̂ + ((γ₄−1)/4)·SR̂²) ], with SR₀ = E[max SR] from B1 | Eq. (2) | p. 8 | BLdP | H (structure reconstructed; **verified by exactly reproducing the paper's own example**, see §5.3) |
| B3 | PSR is the same expression with a user-chosen threshold SR* in place of SR₀ | — | p. 8 | BLdP | H |
| B4 | Worked example (reconstructed): SR̂ = 2.5 annualized, T = 1250 daily, γ₃ = −3, γ₄ = 10, V[{SR_n}] = 0.5, N = 100 → SR₀ ≈ 1.79 annualized, **DSR = 0.9004**. At N = 46, DSR = **0.9505**. With Normal returns, DSR = 0.9505 at N = 88 | see left | pp. 9–10 | BLdP | H (all four values reproduced to 4 dp) |
| B5 | M dependent trials → N implied independent trials via average correlation ρ̄; N → M as ρ̄ → 0 and N → 1 as ρ̄ → 1; entropy/multi-information is the better estimator when M > T | Eqs. (7)–(9), Exhibit 4 | pp. 14–15 | BLdP | H |
| B6 | Accuracy of B1: analytic overestimates the empirical maximum by < 0.05 for N < 50 at V = 1, falling to 0.006 by N = 1000 | < 0.05 | Exhibit 3.1, p. 18 | BLdP | H |
| B7 | **Holdout is no defence**: apply it 20 times at 95% confidence and false positives are expected, then published as a single-trial result | 20 | p. 6 | BLdP | H |
| B8 | Stopping rule: sample ⌊M/e⌋ ≈ **37%** of the theoretically justified configurations at random, then take the first that beats all of them (1/e-law of optimal choice, Bruss 1984) | 37% | pp. 10–11 | BLdP | H |
| B9 | Under memory effects, overfitting selects the rules that profited from the most extreme in-sample patterns — which must be *undone* → overfitting **maximizes** out-of-sample loss | — | p. 6 | BLdP | H |
| B10 | **MinTRL is not in this paper.** It appears only as a keyword; the formula is in Bailey & López de Prado (2012a), J. Risk 15(2) | — | keyword list p. 2 | BLdP | H |

---

## 4. Design check

| # | Decision | What the papers say | Verdict | Recommended change |
|---|---|---|---|---|
| 1 | **LLM emits only categories** (vol regime, trend, event flag, strategy family, veto, journal) | CKX's entire demonstrated value is a cross-sectional single-name next-day ridge signal (X2, X3); it never touches indices, options or timing. CKX itself flags prompt-based LLM use as prompt-sensitive and non-replicable (X21). KMPS quantify the price of letting the LLM own the decision: 0.76–1.10 bits of decision entropy, return SD ≈ 50% of the mean, a 23-point spread across identical runs (K1, K2, K4) | **Supports** | No change. Add one refinement: **measure and report per-field decision entropy in bits**, using KMPS's own metric, for each enum the LLM emits. This makes our claim auditable instead of asserted, and it directly borrows a peer-reviewed metric |
| 2 | **Featherless open-weight model at runtime** (Llama / Qwen / DeepSeek / Mistral) | Model scale is non-monotonic and the frontier models are statistically tied (X12, X13); context beyond 512–1k tokens adds nothing (X14); multilingual capability matters only for non-English news (X19), which we do not have. But KMPS found the open-weight Qwen3-30B *noisier at the decision layer* than GPT-4o (1.10 vs 0.76 bits, K1) | **Refines** | Choose an **8B–70B instruct model with documented `seed`, `top_k` and `top_p` support** (Llama-3.x-70B-Instruct or Qwen-2.5/3 Instruct are both defensible). Do **not** pay for the largest available; cite X12/X13 in the write-up as the reason. Pin the exact model id string and log it with every call. Budget the extra determinism work implied by K1 |
| 3 | **LLM reads news + macro calendar; produces no directional forecast that sizes positions** | Decisive support. For large caps at close-to-close execution the LLM news signal Sharpe is **0.14** (X7); by day+2 the value-weighted signal is **negative** (X8); large-firm predictability is "absorbed within one to two trading days" (X9); net of realistic costs the article strategy is negative above ~107% daily turnover (X10); mean predictive correlation is 2.7%, i.e. R² ≈ 0.07% (X6) | **Supports, strongly** | No change to the design. **Change the write-up:** replace the current generic claim ("LLMs can read text but not own numbers") with the specific, citable one — "the best-documented LLM news signal in the literature is a cross-sectional single-name overnight signal whose large-cap, close-to-close Sharpe is 0.14 (Chen, Kelly & Xiu, Table IA9); there is no published evidence that it times an index." That is a much stronger sentence for the judges |
| 4 | **Tickers anonymized in text prompts** | Anonymization costs little and sometimes helps (X17: articles 4.59 → 4.38 masked; alerts 4.79 → **4.96** masked). Pattern-based masking succeeds 86.4% on bodies / 95.7% on alerts, but only **76.4%** on bodies under a stricter re-identification prompt (X18). CKX also mask **years, person names, products and abbreviations**, not just tickers (Table IA3) | **Refines** | Three concrete changes. (a) Mask **dates and absolute index levels** too, not only tickers — CKX mask "The company expects growth in 2022" → "in SOME_YEAR". Present the LLM relative quantities (% moves, VIX/VIX3M ratio) rather than absolute levels wherever possible. (b) Turn our leakage self-audit into CKX's **measurable** version: feed the masked text back to the same model, ask it to name the underlying, report the failure rate as a percentage. (c) Use their stricter prompt ("use contextual and domain knowledge like a skilled analyst"), not the lenient "return Unknown if unsure", so we do not overstate our own masking |
| 5 | **LLM authority monotone-decreasing in risk** (block or shrink, never enlarge) | KMPS is the empirical case for it: stochasticity propagates one-to-one from decision entropy into return dispersion (K1 vs K2), and the framework they tested has no bounded-loss structure to absorb it | **Supports** | Add a concrete mechanism that uses the residual stochasticity *in the safe direction*: run the regime/critic call **k = 5 times on the frozen snapshot** and require unanimity on the strategy-family enum; any disagreement escalates to `NO_TRADE`. This makes non-determinism a conservative force rather than a risk, and it is exactly what "monotone-decreasing in risk" means operationally. Log the disagreement rate as a reported metric |
| 6 | **No single-name earnings trades in either direction** (AVGO, ZS, LULU, DOCU, S, CIEN) | **Our stated reason is wrong.** DJKS show the *short* side has positive expected value: mean straddle return −7.96%, median −10.24%, t = −13.25, negative in all 16 years (D14), consistent with a ~1 vol-point P/Q wedge (D15) and with an 8% mean-based premium (D12) and SD of standardized returns 0.92 (D13). **But**: per-trade SD 27.47% with short-side skew −1.44 and kurtosis 8.93 (D14); the mean-based premium **reverses in 2011–2015** (Q 6.78% vs P 7.35%, D12); quoted spreads run ~6% of the option mid (D22) | **Contradicts the stated reason; supports the rule for a different reason** | **Rewrite `STATE_OF_THE_ART.md` §6 V15 and §8.1 "Earnings".** New text: selling earnings premium has a small positive expected value (mean +7.96% per short straddle, Dubinsky et al. 2019 RFS, Table 10), but the per-trade Sharpe is **0.29** and the payoff has skew −1.44 / kurtosis 8.93, which by the Bailey/López de Prado MinTRL requires **≈52 trades** to certify at 95%. We can take at most 5 in the window. We abstain because a 1–5 trade sample of a fat-left-tailed lottery is uninformative and one draw can consume the 2% session budget — not because the trade loses money. This is more honest, more sophisticated and fully citable |
| 7 | **Event gate blocks SPY/QQQ new entries around scheduled macro releases; Friday = NO_TRADE** | DJKS explicitly generalize their framework to macro announcements, elections, referendums and summits (D23), and their Brexit example is exactly this pattern executed on a scheduled macro event (D4). Their vol-of-vol replication (D19) shows that not accounting for a scheduled event destroys a short-dated IV signal (t goes from −4.56 to +0.10) | **Supports and extends** | Add a **quantitative** layer to the currently clock-based gate: compute the implied event move for Thursday ISM and Friday NFP from two SPY ATM implied vols via D2, and log it (recipe in §5.1). Gate on the number, not only on the clock: if the term-structure-implied event move exceeds a pre-set threshold, block. This is a genuine differentiator and costs ~30 lines of code |
| 8 | **Implied move computed by code from the ATM straddle** | Partly wrong as specified. The straddle price gives the **total** implied move = diffusive + event (D1: IV² = σ² + σ_j²/T). That is correct for *strike placement* but wrong for any *comparison* with a realized diffusive move | **Refines** | (a) Keep the ATM-straddle implied move for strike anchoring — it is the right quantity there. (b) **The `IV vs RV` veto (D-R14/R15) must strip the event component first**, or use the post-event quote: comparing an event-inflated implied move to a realized non-event move will fire the veto on precisely the days it exists for. Implement D2 to split σ into diffusive and event parts. (c) If we ever build a constant-maturity IV, **interpolate linearly in variance × time, not in log-maturity** (D20). (d) On Thursday, take the straddle quote *after* 10:15 ET (post-ISM), not before |
| 9 | **Evaluation: process metrics; no Sharpe or alpha claim; disclose configurations tried** | Fully supported and now quantified. MinTRL to certify a Sharpe of 0.5 / 1.0 / 2.0 = 2,860 / 751 / 207 days (§5.3a). PSR of +$400 over 3 trades = 0.69–0.76 (§5.3b). With T = 3 and kurtosis 6 the **PSR ceiling is 0.897** — 95% is unreachable at any performance level (§5.3b). Expected max Sharpe over 2 configurations on 3 daily observations = **4.76** (§5.3c). Holdout is no defence (B7); M dependent trials must be converted to N independent ones (B5) | **Supports; makes it quantitative** | Put a **"Deflated Sharpe box"** in the write-up with those four numbers and the one-line arithmetic. Add: "We disclose M = ⟨count⟩ configurations tried. Because they are highly correlated variants of one structure, the implied number of independent trials N̂ is far smaller than M (Bailey & López de Prado 2014, App. 3); even N̂ = 2 gives an expected maximum annualized Sharpe of 4.8 under a true edge of zero on a 3-day sample. This is why we report no Sharpe ratio." Cite MinTRL to **Bailey & López de Prado 2012a**, not the DSR paper (B10) |
| 10 | **Determinism replay: same inputs → identical decisions** | KMPS give the exact recipe and prove the intermediate steps are insufficient: T=0 alone leaves 0.98 bits / 5.5 pp SD; +seed leaves 0.73 bits / 4.3 pp; only T=0 + seed + top_k=1 + top_p=0 reaches zero (K1, K2). And fixing the seed introduces seed dependence, which they call cherry-picking (K7) | **Supports; sharpens materially** | Adopt the full recipe and the two extra tests in §5.2. Key upgrades over our current plan: (i) set **all four** sampling parameters, not just temperature; (ii) hash the **parsed decision object**, not the raw text, because a hosted provider can be token-non-deterministic even at greedy decoding; (iii) also run a **seed-sensitivity check** with 3 different seeds and report whether the decision changes — KMPS's own critique of their best result makes this the honest thing to do; (iv) report **decision entropy in bits per field**, their metric |
| 11 | **Benchmarks: SPY, Cboe PUT, Cboe CNDR, random-entry Monte Carlo percentile** | The random-entry Monte Carlo is a single-trial null. B1/B5/B8 say a single-trial null understates the threshold whenever more than one configuration was tried | **Refines** | Make the Monte Carlo a **best-of-N̂ null**: draw N̂ random-entry paths per replication, take the maximum, and report our realized P&L against the distribution of *that* maximum. It is one extra loop and it is the non-parametric analogue of the DSR — a much stronger claim. Also **pre-register the 37% secretary stopping rule** (B8): from the list of theoretically justified configurations, evaluate ⌊M/e⌋ at random, then take the first that beats all of them, and say so in the write-up |
| 12 | **Core strategy: 0DTE SPY iron condor, delta-neutral, 2%/session, 6% cumulative, flat by 15:15 ET** | Largely **silent** — none of the four papers studies index condors, 0DTE, or intraday sizing. Two indirect touch points: DJKS's measured short-premium moments (skew −1.44, kurtosis 8.93, D14) are the closest empirical anchor for the return shape we are underwriting; DJKS D17 (EAD variance ratio 5.71) and D21 (earnings vol correlates 60% with beta) bear on the AVGO-into-SPY question but do not answer it | **Silent** | No change to the strategy. One documentation change: our risk arithmetic assumes skew −1.5 / kurtosis 6; DJKS measure **−1.44 / 8.93** on a structurally similar short-premium payoff. Our skew is right, **our kurtosis is optimistic** — state that, and note that fatter tails make every statistical claim weaker, not stronger, which reinforces the "we claim no edge" framing |

---

## 5. Concrete recipes

### 5.1 Computing the implied event move from two expiries (Dubinsky et al., Eq. 4)

**In words.** An option spanning a scheduled event prices two things: ordinary day-to-day diffusive volatility, which contributes variance proportional to time, and a one-off jump on the event date, which contributes a *fixed* amount of variance regardless of maturity. Because the jump's variance is spread over a longer window in a longer-dated option, the annualized implied variance of the short option exceeds that of the long one by exactly the jump variance times the difference in the reciprocals of the two maturities. Invert that and you get the jump volatility.

```
IV(t,T)^2  =  sigma_diffusive^2  +  (1/T) * sum_over_events_in_(t, t+T] sigma_j^2      # Eq. (3)

sigma_event = sqrt( (IV_1^2 - IV_2^2) / (1/T_1 - 1/T_2) )                              # Eq. (4)
```

with `T_1 < T_2` in **years**, both expiries spanning **exactly the same single event**, `IV` = average of the closest-to-the-money call and put implied vol for that expiry.

```python
def implied_event_move(iv_short, T_short, iv_long, T_long):
    """Dubinsky/Johannes/Kaeck/Seeger (2019 RFS) Eq. (4).
    iv_*  : annualized ATM implied vol, decimal (avg of call and put IV)
    T_*   : time to expiry in YEARS; T_short < T_long; both span the SAME single event
    returns: sigma_j, the risk-neutral one-off event move, decimal (e.g. 0.0075 = 0.75%)
    """
    num = iv_short**2 - iv_long**2
    if num <= 0:                     # "Err1" case in their Tables 4-5: term structure not
        return None                  # downward sloping -> microstructure noise or no event
    return (num / (1.0/T_short - 1.0/T_long)) ** 0.5
```

**Validation (both run here).**
- Brexit, 23 Jun 2016: 1-month USD/GBP IV 28.21%, 2-month 21.51%, T = 1/12 and 2/12 → **7.451%**. Paper reports 7.45%; GBP fell 7.6% the next day. Exact match.
- AMZN, 23 Oct 2014: paper reports 10.26% (term) and 9.87% (time-series). Recomputing from the printed IVs (75.28% @ 8d, 54.37% @ 15d, act/365) gives 11.28% — the printed short IV is probably an OCR digit error. The *agreement of two independent estimators* is the reusable point.

**Implementation notes for our code.**
- Use the **average of the ATM call and put IV** per expiry, as they do — this cancels most stale-quote and put-call-parity noise. Drop the pair if call and put IV differ extremely.
- Exclude expiries with **< 3 DTE** (they do; microstructure noise explodes).
- Handle the `Err1` case explicitly: 245 of 3,008 firm-EADs (8.1%) had a non-downward-sloping term structure, concentrated in low-event-volatility names. Return `None`, log it, do not clamp to zero.
- Bias: with strongly mean-reverting spot variance far from its long-run mean, the estimator is biased by roughly ±0.5 vol points on a true 8% — "small in absolute terms, but also relative to microstructure noise" (p. 655). Do not over-interpret one reading.
- **Applied to SPY for our gate.** Take the expiry that spans Friday 08:30 ET NFP (`T_1`) and the next weekly that also spans it (`T_2`); the difference in annualized ATM variance gives the market's priced NFP jump. Illustrative arithmetic: IV(1d) = 22%, IV(8d) = 15% → σ_event = **0.90%**; IV(1d) = 18%, IV(8d) = 14% → **0.63%**. Log the number every session and show the drop after the release. This gives the Friday NO_TRADE decision a measured justification instead of a rule.
- **Do not** feed an event-inflated implied move into the IV-vs-RV veto. Split it: `sigma_diffusive^2 = IV_1^2 - sigma_event^2 / T_1`, and compare *that* to realized intraday volatility.
- If we ever need a constant-maturity IV: interpolate **linearly in variance**, not in log-maturity (DJKS p. 675).

### 5.2 Determinism / replay test design (from Koviazin et al.)

**Sampling parameters — all four, not just temperature.** KMPS prove the partial settings are insufficient (entropy 0.98 with T=0 alone; 0.73 with T=0 + seed; 0.00 only with all four):

```
temperature = 0
top_k       = 1
top_p       = 0            # or 1.0 with top_k = 1, depending on the provider's semantics
seed        = <fixed int>
max_tokens  = <fixed>
model       = "<exact provider model id>"   # pinned string, logged, never "latest"
stream      = false
```

**Test protocol.**

1. **Freeze a snapshot.** Serialize every input to the decision — chain, quotes, VIX/VIX3M, headline set, macro calendar, clock — to canonical JSON (sorted keys, fixed float formatting). `input_hash = sha256(canonical_json)`.
2. **Replay k = 5 times** against the same frozen snapshot, same parameters. (KMPS used 10; 5 is enough for a hackathon and still gives a reportable entropy.)
3. **Hash the decision, not the text.** `decision_hash = sha256(canonical_json({vol_regime, trend, event_risk, strategy_family, veto, veto_reason_code}))`. Journal prose is explicitly excluded — a hosted provider can vary tokens even under greedy decoding (batching, kv-cache, GPU non-associativity), and we should not fail our own test on prose. Downstream, also hash the deterministic code outputs (strikes, contract counts, max loss) and require **exact** equality there — that half must be bitwise reproducible.
4. **Metric = per-field Shannon entropy in bits**, their Eq. (1), plus a disagreement rate. Report a table shaped like their Table 1:

   | field | cardinality | max bits | observed bits over k=5 | unanimous? |
   |---|---|---|---|---|
   | `vol_regime` | 4 | 2.00 | — | — |
   | `trend` | 3 | 1.58 | — | — |
   | `event_risk` | 4 | 2.00 | — | — |
   | `strategy_family` | 5 | 2.32 | — | — |
   | `veto` | 2 | 1.00 | — | — |

   **Pass criterion:** 0.00 bits on `strategy_family` and `veto`. `vol_regime` and `trend` are advisory and may be allowed a small non-zero entropy, provided it does not change the family.

5. **Seed-sensitivity check.** Repeat step 2 with 3 different seeds. If the decision changes across seeds, **say so** — KMPS's own strongest result (28.2%) is one seed realization, which they themselves label cherry-picking (K7). Reporting seed sensitivity is what distinguishes an honest determinism claim from a decorative one.
6. **Fallback that turns residual noise into safety.** If the provider will not be deterministic, require **unanimity across k = 5 calls** on `strategy_family`; any disagreement → `NO_TRADE`, logged with the vote distribution. This is the operational meaning of "LLM authority is monotone-decreasing in risk", and it converts a weakness into a demonstrable control.
7. **Log per call:** model id, all sampling parameters, seed, full prompt, full response, latency, prompt/completion tokens, `input_hash`, `decision_hash`, git commit hash.

**What to say in the write-up about why our architecture avoids their failure modes.**

> Koviazin et al. (IC-AIF 2026) re-ran the TradingAgents framework ten times per configuration on one stock over three months. With default sampling the same agent on the same data produced final returns from about 5% to about 28% — a standard deviation of roughly half the mean return — and its performance was statistically indistinguishable from buy-and-hold (p > 0.26). Three properties of their setup produced that: the LLM emitted the trading decision itself, so decision entropy mapped one-to-one into return variance; positions had unbounded loss, so that variance was unbounded too; and full determinism required all four sampling parameters to be pinned, which is easy to get wrong.
> Our architecture removes all three. The LLM emits a five-valued enum and a veto; every number — strikes, contract counts, max loss, orders — comes from deterministic code, so the *support* of the decision distribution is small and enumerable. Every position is defined-risk with a max loss capped at 2% of capital per session, so decision variance cannot produce a 23-point return spread. And we pin temperature, top_k, top_p and seed, replay each decision five times against a frozen input hash, and report the measured per-field decision entropy in bits — the same metric they used — rather than asserting reproducibility.

### 5.3 The DSR / PSR / MinTRL numbers, with the arithmetic

**Formulas.** γ = 0.5772156649 (Euler-Mascheroni); Z = standard normal CDF; SR̂, SR₀, SR* all in **per-observation** units; γ₃ = skewness, γ₄ = kurtosis (not excess).

```
E[max SR over N trials] = E[SR] + sd(SR) * [ (1-γ)·Z^-1(1 - 1/N) + γ·Z^-1(1 - 1/(N·e)) ]     (B&LdP Eq. 1)

PSR(SR*) = Z[ (SR̂ - SR*)·sqrt(T-1) / sqrt(1 - γ3·SR̂ + ((γ4-1)/4)·SR̂²) ]                     (B&LdP Eq. 2 form)

DSR      = PSR(SR₀)  with  SR₀ = E[max SR over N trials]                                      (B&LdP Eq. 2)

MinTRL   = 1 + [1 - γ3·SR̂ + ((γ4-1)/4)·SR̂²] · ( Z_α / (SR̂ - SR*) )²        (B&LdP 2012a, NOT the DSR paper)
```

**Verification.** The DSR paper's own worked example prints only its conclusions, because pdftotext dropped the numerals from the parameter sentence. Reconstructing from the printed conclusions gives SR̂ = 2.5 annualized, T = 1250 daily, γ₃ = −3, γ₄ = 10, V[{SR_n}] = 0.5, N = 100. Recomputing with the formulas above:

| N | SR₀ (annualized) | DSR | Paper says |
|---|---|---|---|
| 46 | 1.5869 | **0.9505** | "DSR would have been 0.9505" ✓ |
| 88 (Normal returns, γ₃=0, γ₄=3) | 1.7574 | **0.9505** | "DSR > 0.95 after N = 88" ✓ |
| 100 | 1.7894 | **0.9004** | "only a 90% chance" ✓ |

Three independent matches to four decimals. The formulas as written above are correct.

#### (a) MinTRL in daily observations, skew −1.5, kurtosis 6, SR* = 0, 95% confidence (Z = 1.6449), 252 days/year

| Annualized SR | SR̂ per day = SR/√252 | bracket = 1 + 1.5·SR̂ + 1.25·SR̂² | (Z/SR̂)² | **MinTRL (days)** | in years |
|---|---|---|---|---|---|
| 0.5 | 0.0314970 | 1 + 0.0472455 + 0.0012401 = 1.0484856 | 2,727.19 | **2,860.4** | 11.35 |
| 1.0 | 0.0629941 | 1 + 0.0944911 + 0.0049603 = 1.0994514 | 681.80 | **750.6** | 2.98 |
| 2.0 | 0.1259882 | 1 + 0.1889823 + 0.0198412 = 1.2088235 | 170.45 | **207.0** | 0.82 |

Same under Normality (γ₃ = 0, γ₄ = 3) for comparison: 2,729.5 / 684.2 / 172.8 days. **Negative skew and fat tails add 5% / 10% / 20% to the requirement** — the penalty grows with the Sharpe, because the SR̂² term dominates.

**Our horizon is 2.5 sessions, i.e. T ≈ 3 daily observations.** Even in the most flattering case — a true annualized Sharpe of 2.0 — we are short by a factor of **207 / 3 ≈ 69**. For a plausible short-premium Sharpe of 0.5 we are short by a factor of **≈ 950**.

**Same calculation for a short earnings straddle** (from Dubinsky Table 10: mean +7.96%, SD 27.47%, skew −1.44, kurtosis 8.93 for the short side): SR̂ = 0.2898 per trade, bracket = 1 + 1.44·0.2898 + 1.9825·0.2898² = 1.5837, (Z/SR̂)² = 32.22, **MinTRL = 52.0 trades**. There are 5 single-name earnings events in our window. This is the number to put in the write-up next to the event gate.

#### (b) PSR of a strategy showing +$400 over 3 trades

Take three trade P&Ls summing to +$400 on $100,000: **+$250, +$310, −$160**.

```
daily returns r = {0.00250, 0.00310, -0.00160}
mean   = 0.00133333                                   (13.33 bp/day)
sd     = 0.00255799   (sample, n-1 = 2)               (25.58 bp)
SR̂     = 0.00133333 / 0.00255799 = 0.521242 per obs
       = 0.521242 * sqrt(252)    = 8.2745 annualized      <-- looks spectacular
T      = 3,  sqrt(T-1) = 1.414214
numerator = 0.521242 * 1.414214 = 0.737147
```

| Moment assumption | bracket | z | **PSR(0)** |
|---|---|---|---|
| Normal (γ₃=0, γ₄=3) | 1.135846 | 0.691663 | **0.7554** |
| Short-premium (γ₃=−1.5, γ₄=6) | 2.121479 | 0.506098 | **0.6936** |
| Measured earnings-straddle moments (γ₃=−1.44, γ₄=8.93) | 2.653 | 0.4526 | **0.6746** |

An apparent annualized Sharpe of **8.27** yields only a **69–76% probability that the true Sharpe exceeds zero**. To *certify* even that ludicrous Sharpe at 95% would need MinTRL = 1 + 1.1358 × (1.6449/0.5212)² = **12.3 observations** under Normality, or **22.1** with skew −1.5 / kurtosis 6. We have 3.

**And the result is worse than "we happened to pick a weak example."** With T = 3, as SR̂ → ∞ the z-score converges to sqrt(T−1) / sqrt((γ₄−1)/4):

| kurtosis γ₄ | supremum of z at T=3 | **supremum of PSR** |
|---|---|---|
| 3 (Normal) | 2.0000 | 0.9772 |
| 6 | 1.2649 | **0.8970** |
| 8.93 (measured) | 1.0044 | **0.8424** |

**With three observations and any realistic fat-tailed short-premium return distribution, the Probabilistic Sharpe Ratio can never reach 95% — at any performance level whatsoever.** Under Normality it is reachable but requires a per-observation Sharpe of 2.04, i.e. a mean daily return more than twice the daily standard deviation across all three days. This is the single most decisive sentence available for our evaluation section, and it is arithmetic, not opinion.

#### (c) How many configurations before E[max Sharpe] under the null reaches 1.0

`E[max SR] = sd(SR) · maxZ(N)` with `maxZ(N) = (1−γ)·Z⁻¹(1−1/N) + γ·Z⁻¹(1−1/(N·e))`.

| N | 2 | 3 | 4 | 5 | 8 | 10 | 25 | 50 | 100 | 1000 |
|---|---|---|---|---|---|---|---|---|---|---|
| maxZ(N) | 0.520 | 0.853 | 1.052 | 1.193 | 1.459 | 1.575 | 1.997 | 2.276 | 2.531 | 3.255 |

**Answer depends entirely on the dispersion of Sharpe estimates across trials:**

| sd of trial Sharpes (annualized) | N such that E[max SR] ≈ 1.0 |
|---|---|
| 0.25 | ≈ 17,850 |
| 0.30 | ≈ 1,340 |
| 0.50 | ≈ **26** |
| 0.707 (= V[SR] 0.5, the value in the paper's own example) | ≈ **8** |
| 1.00 | ≈ **4** |

**For our situation the answer is N ≈ 2.** Under the null (true Sharpe = 0), the estimated annualized Sharpe from T = 3 daily observations has standard deviation sqrt(252/3) = **9.17**. Hence:

| N configurations tried | E[max annualized Sharpe] under a true edge of exactly zero |
|---|---|
| 1 | 0.00 (a single trial is the mean) |
| **2** | **4.76** |
| 3 | 7.82 |
| 5 | 10.93 |
| 10 | 14.43 |
| 20 | 17.42 |

The threshold of 1.0 is crossed between the first and second configuration. **Trying two variants of the condor and reporting the better one has an expected best annualized Sharpe of 4.8 with no edge at all.** This is the number to print next to our disclosed configuration count.

Two operational consequences:
- The disclosed count must be converted from M *dependent* trials to N̂ *independent* ones. Our configurations (strike multiplier, entry window, wing width) are heavily correlated, so N̂ ≪ M — Bailey & López de Prado's Eq. (9) interpolates between N̂ = M at ρ̄ = 0 and N̂ = 1 at ρ̄ = 1. Report both M and a reasoned N̂.
- Pre-register the **37% stopping rule** (B8): list the theoretically justified configurations *before* trading, evaluate ⌊M/e⌋ of them at random, then take the first that beats all of those. It is a one-line commitment that pre-empts the entire overfitting objection.

### 5.4 LLM model-choice guidance for Featherless

| Question | Evidence | Guidance |
|---|---|---|
| Does bigger help? | X12: LLaMA3-8B (4.59) beats LLaMA3-70B (3.98) on articles; LLaMA2-70B is best on some cells and not others. X13: DM statistics among the four frontier models are 0.03–0.49, insignificant | **No.** Pick an **8B–70B instruct** model. The claim "we chose the smallest model that saturates the task, per Chen/Kelly/Xiu IA D.4" is a better write-up line than "we used the biggest" |
| Does newer help? | X4: BERT 3.00 < RoBERTa 3.69 < LLaMA family ≈ ChatGPT 4.0–4.8. The generational gap is real up to ~2023, then flat | **Yes up to a point.** Do not use a pre-LLaMA-era encoder. Any modern instruct model is on the plateau |
| Which family? | KMPS K1: Qwen3-30B showed higher decision entropy (1.10) than GPT-4o (0.76) at T = 1. CKX has no Qwen/Mistral/DeepSeek results | **Weak preference for Llama-3.x-Instruct**, which is the family CKX actually tested and which KMPS did not find noisier. Whatever you choose, verify empirically with the §5.2 replay before trusting it |
| Context window? | X14: 512 vs 1k vs 4k vs 8k tokens changes the Sharpe by ≤ 0.2; 60.5% of news items are under 512 tokens | **Irrelevant.** A short context is fine. Do not pay for long-context variants |
| Provider parameters that matter | K1: only T=0 **and** seed **and** top_k=1 **and** top_p=0 gives determinism | **Hard requirement:** the model must expose `seed`, `top_k` and `top_p` through the OpenAI-compatible endpoint. Check this before committing to a model id |
| What text to feed it? | X15: summaries > full articles > headlines for every LLM (LLaMA3: 5.42 / 4.59 / 3.59). X11: headline-only alerts survive costs best because they are *timely*, and the LLM-vs-word-model gap narrows there | **Two-tier, as already planned, now with a citation.** Cheap model condenses each news item to one sentence; strong model classifies the summary set. For pure event *flagging*, headlines/alerts are sufficient — timeliness beats richness (§4.3) |
| Multilingual? | X19: matters only for non-English news | **Irrelevant** for us |

---

## 6. Follow-up sources cited in these papers worth reading

Ordered by expected value for this project.

1. **Barth, M. & So, E. (2014)** — uses Dubinsky's estimators to study whether earnings announcements contribute to *market-wide, non-diversifiable* volatility risk and command a premium (DJKS p. 656). **This is the paper that answers the open question "does SPY price Broadcom's earnings day?"** — the one thing Dubinsky et al. do not test. Highest priority.
2. **Kelly, B., Pástor, Ľ. & Veronesi, P. (2016), "The Price of Political Uncertainty", *Journal of Finance*** — option pricing of *scheduled political* events (elections, summits, referendums). The direct analogue of our NFP/ISM gate, at index level rather than single name. Cited by DJKS p. 650, 656.
3. **Bailey, D. & López de Prado, M. (2012a), "The Sharpe Ratio Efficient Frontier", *Journal of Risk* 15(2)** — the actual home of the PSR and MinTRL formulas we use in §5.3. **We must cite this, not the DSR paper, for MinTRL.**
4. **Bailey, Borwein, López de Prado & Zhu (2013), "The Probability of Backtest Overfitting", SSRN 2326253** — non-parametric PBO via combinatorial cross-validation; complements the parametric DSR and works with any performance statistic.
5. **He, S., Lv, L., Manela, A. & Wu, J. (2025), "Chronologically Consistent Large Language Models"** — models trained only on text available up to each date. CKX cite it as showing that look-ahead-free models match LLaMA3 performance. The cleanest citation for "leakage is not driving the result".
6. **Glasserman, P. & Lin, C. (2023), arXiv 2309.17322** — look-ahead bias in GPT sentiment analysis; the pattern-based masking algorithm CKX extend. Directly reusable for our anonymization self-audit.
7. **Muravyev, D. & Pearson, N. (2016)** — actual option execution costs are far below quoted bid-ask spreads. Cited twice by DJKS as the reason their straddle result may still be tradable. Relevant to our "reject if round-trip cost > 25% of credit" gate, which currently uses quoted spreads.
8. **Frazzini, A., Israel, R. & Moskowitz, T. (2018), "Trading Costs", SSRN 3229719** — the 10 bp (large) / 20 bp (small) per 100% turnover model CKX use. A citable default if we need a cost model for the Monte Carlo benchmark.
9. **Wang, J. J. & Wang, V. X. (2025), arXiv 2503.16974**, "Assessing Consistency and Reproducibility in the Outputs of Large Language Models: Evidence Across Diverse Finance and Accounting Tasks" — cited by Koviazin [9]. Broader base rate for LLM output consistency in finance than a single trading framework.
10. **Xiao, Y., Sun, E., Luo, D. & Wang, W. (2025), "TradingAgents", arXiv 2412.20138** — the framework Koviazin reproduce, and the source of the Sharpe 8.21 claim already flagged in `STATE_OF_THE_ART.md` L5. Worth skimming so we can name it precisely.
11. **Harvey, C. & Liu, Y. (2014), "Backtesting", SSRN 2345489** — a Benjamini-Hochberg-based multiple-testing threshold; B&LdP explicitly recommend computing DSR against *both* thresholds.
12. **Shen, Z. & Xiu, D. (2025), "Can Machines Learn Weak Signals?", NBER w33421** — why dense (ridge) beats sparse (Lasso) when signal-to-noise is low. CKX rely on it; relevant if we ever fit anything.
13. **Martineau, C. (2017)** — 80% of the price response to after-hours news occurs in the first few trades. Supports the jump assumption and our "no overnight short options" rule.
14. **Baltussen, Van Bekkum & Van der Grient (vol-of-vol)** — the paper DJKS replicate in §3.6; the cautionary example for short-dated IV features.
15. **Dodge, J. et al. (2019), "Show Your Work", arXiv 1909.03004** — Koviazin's cited reporting standard for experimental results. Useful template for our configuration-disclosure section.

---

## 7. Method log

**Files read (all with `sed -n` chunking through the whole file; nothing skipped):**
- `Expected Returns and Large Language Models.txt` — 3,567 lines / ~28,700 words, read in six chunks (1–300, 300–700, 700–1100, 1100–1520, 1520–1980, 1980–2450, 2450–2900) plus targeted appendix reads (2900–3300) for model-scale, execution-timing and truncation tables.
- `Option_Pricing_of_Earnings_Announcement_Risks.txt` — 2,618 lines / ~21,200 words, read in six chunks (1–290, 290–650, 650–1080, 1080–1560, 1560–2050, 2050–2400).
- `Reproducibility in the TradingAgents Framework.txt` — 387 lines, read in full (two chunks).
- `The Deflated Sharpe Ratio…txt` — 1,004 lines, read in full (three chunks, including all appendices, the Python snippet and all exhibits).
- `STATE_OF_THE_ART.md` — lines 1–33, 95–274, 329–400 as instructed.

**Extraction problems and how they were handled.**
- Every mathematical display in the DSR paper lost its symbols; the formulas in §5.3 were reconstructed from surrounding prose plus the verbatim Python in Snippet 1 (which survived intact and pins Eq. 1 exactly), then **validated by reproducing all three of the paper's own published DSR conclusions to four decimals**. This is the strongest available check short of the original PDF.
- The numerals in the DSR paper's numerical-example parameter sentence were dropped by pdftotext. They were **solved for** from the three printed conclusions (DSR = 0.9505 at N=46; DSR > 0.95 at N=88 under Normality; "only a 90% chance" at the analyst's N) and are reported as reconstructed: SR̂ = 2.5, T = 1250, γ₃ = −3, γ₄ = 10, V[{SR_n}] = 0.5, N = 100.
- Koviazin Table 1 is badly interleaved. Values were cross-checked against the abstract (which independently states 18.1 ± 2.8 and 15.8 ± 4.2, and the three benchmarks) and against §3.1/§3.2 prose (which independently states every entropy value and the standard deviations). Marked confidence M in the evidence table.
- Chen/Kelly/Xiu Tables 3, 19 and IA8 are column-shifted. Table 19's alert numbers were disambiguated by matching rows against Table IA8, where the same LLaMA variants appear with the same four columns. Where the mapping remained ambiguous (LMMD, SESTM rows of Table 19) no numbers are reported. Table 5, Table 8, Table 13, Table 15, Table 16, Table 18 and Table IA9/IA10 extracted cleanly and are the basis of most X-IDs.
- The Dubinsky AMZN worked example does not reproduce from its printed implied vols (11.28% computed vs 10.26% printed); the Brexit example reproduces exactly (7.451% vs 7.45%). Flagged in D5 as a probable OCR digit error rather than a formula problem.

**Computations performed** (pure-Python, normal CDF via `math.erfc`, inverse by bisection to 1e-12; script at `…/scratchpad/calc.py`):
MinTRL at three Sharpe levels under two moment assumptions; PSR of the +$400/3-trade record under three moment assumptions; the analytic PSR supremum at T = 3; the Sharpe required for PSR = 0.95 at T = 3 under Normality; `maxZ(N)` table and the inverse solve for E[max SR] = 1.0 at five dispersion levels; expected max annualized Sharpe under the null at T = 3 for N = 2…20; full reconstruction and verification of the DSR paper's numerical example at N = 46, 88, 100; MinTRL for the short earnings straddle from Dubinsky's Table 10 moments; verification of the Dubinsky term-structure estimator on the Brexit and AMZN examples; three illustrative SPY event-move calculations.

**Bibliographic verification.** OpenAlex queried for both non-journal papers. Koviazin et al. confirmed: publication date 2026-01-09, DOI 10.1145/3800973.3801029, exact title match. Chen/Kelly/Xiu not indexed (expected for an SSRN working paper); version dated by internal citation evidence instead. Dubinsky et al. and Bailey/López de Prado carry full bibliographic data in the documents themselves and needed no lookup. No other web access was used.

**Scope note.** The `sources_txt` directory also contains four papers not assigned to F2 (`0DTE Trading Rules`, `DTEs Trading, Gamma Risk and Volatility Propagation`, `Variance Risk Premiums`, `hope-reasonable-prc-2503`). They were not read; if they have not been covered by another agent, they represent an open gap — the first two in particular bear directly on §8.1's core structure, which these four sources are silent on.

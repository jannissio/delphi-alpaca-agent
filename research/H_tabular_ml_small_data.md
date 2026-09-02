# H — Modern tabular ML for the regime model: gradient boosting, tabular foundation models, and what is honest on 1,500 sessions

Research agent H, 2026-09-02. Deliverables: literature review with source cards, a controlled experiment on our own data
(`research/experiments/model_comparison.py`, results in `research/experiments/model_comparison_results.md`), and a verdict.
Everything below is reproducible with the repo venv; no file under `agent/` or `config/` was touched.

---

## 1. Summary — ten bullets, decision-relevant first

1. **Verdict: keep the logistic regression for the size multiplier. Do not deploy a tabular foundation model.**
   A TFM wins only on the horizon that has two independent year-blocks (A), loses significantly on the horizon that has
   fifteen (C), and ties on the horizon in between (B). That is the signature of a sample-size artefact, not of skill.
   The scientifically defensible upgrade, if any change is made at all, is the **50/50 average of logit + XGBoost**,
   which is the only candidate that never loses on any horizon — but its edge over the logit alone is
   −0.0005 Brier on horizon C with a 90 % block-bootstrap CI of [−0.0013, +0.0003], i.e. indistinguishable from zero.
2. **License-eligible shortlist for deployment (2026-09-02):** TabICL / TabICLv2 (BSD-3-Clause, code *and* weights, ungated),
   Mitra (Apache-2.0), TabDPT (Apache-2.0), XGBoost (Apache-2.0), LightGBM (MIT), scikit-learn (BSD-3).
   **TabPFN v2** weights are usable commercially but under the *Prior Labs License* (Apache-2.0 **plus** a mandatory
   "Built with PriorLabs-TabPFN" display clause) — not MIT/Apache-plain, so it does not fit an MIT repo without carrying
   that extra license file and badge. **TabPFN-2.5 / 2.6 / 3 are non-commercial and gated** behind an account and API key;
   we hit that gate live. Correction to the coordinator's brief: TabPFN **v2** is *not* research-only; the 2.5+ line is.
3. **State of the art as of 2026-09:** the open, permissively licensed frontier is **TabICLv2** (checkpoint
   `tabicl-classifier-v2-20260212.ckpt`, BSD-3, classification *and* regression, pretrained on 300–48 000 rows × 2–100 columns,
   scales to million-row data on GPU). The overall frontier is RealTabPFN-2.5 / TabPFN-3, which are non-commercial.
   TabArena (NeurIPS 2025) puts a 4-hour AutoGluon ensemble first, TFMs strong on *small* data, GBDTs still competitive
   everywhere, and cross-model ensembles ahead of any single model. Our experiment reproduces exactly that ordering.
4. **On our live horizon (10:30 → close, 416 OOS sessions) the currently deployed logit is worse than a constant.**
   Brier 0.15333 vs 0.15088 for the training base rate — a Brier skill score of **−1.6 %** — and a calibration slope of
   **0.14**, i.e. its probabilities carry almost no usable information after recalibration. Its P&L tercile spread is
   +14.7 $/contract with t = 1.27 (p = 0.21). The taper it drives is, on horizon A, not statistically supported.
5. **On the same horizon every non-linear model does clearly better** — XGBoost Brier 0.14531 / AUC 0.639,
   TabICLv2 0.14681 / AUC 0.660, TabPFN v2 0.14465 / AUC 0.653 — with tercile P&L spreads of 57 / 45 / 53 $/contract
   (naive t = 4.5 / 4.0 / 4.5). **But horizon A contains only two calendar years.** A block bootstrap over two blocks is
   arithmetically incapable of supporting an inference, and Harvey–Liu–Zhu's t > 3 hurdle is meaningless when the
   effective number of independent observations is ~2. This is the single most important caveat in the report.
6. **On the horizon with real statistical power (C, 3 687 OOS sessions, 15 year-blocks) the logit is the best single model**
   (Brier 0.17244) and both foundation models are **significantly worse** (TabPFN +0.00586 [+0.0011, +0.0131],
   TabICL +0.00516 [+0.0011, +0.0109] — CIs exclude zero). Part of that gap is our 1 200-row training cap on CPU, which we
   disclose; but the direction agrees with Grinsztajn 2022, McElfresh 2023 and Cheng et al. 2025 (TFMs degrade as n grows
   and under distribution shift).
7. **Leakage from autocorrelated volatility is not our problem.** Purging the 5 sessions before every test year moves the
   Brier by at most 0.0011 in absolute value on any model or horizon, and usually *improves* out-of-sample scores slightly.
   Our labels are one-session, non-overlapping, so López de Prado's purge/embargo machinery is cheap insurance rather than
   a fix. The real problems are (a) 1 170–3 687 observations, (b) regime drift, (c) 21 configurations tried.
8. **Regime drift dominates everything on horizon B.** The training base rate is 0.8108 while the realised OOS inside rate
   is 0.6487. Every model's calibration slope on B is ≈ 0.35, i.e. two thirds of the nominal probability spread is noise.
   Most of what any model "earns" on B is the level shift, not the ranking. Also flagged: `docs/regime_model_report.md`
   labels horizon B as "open→close 2018–2026" and its OOS window as "2021–2026"; the data actually begin **2020-07-27**
   and the first usable test year is **2022** (the 2021 fold is skipped for having < 200 training rows). Fix the labels.
9. **Multiple testing is now the binding constraint, and we must disclose it.** This report evaluated 7 model families
   × 3 horizons = **21 configurations** on top of the 2 already in the write-up. Bailey & López de Prado's arithmetic
   (F2 §5.3) already showed that with T ≈ 3 live sessions the Probabilistic Sharpe Ratio ceiling is 0.897 and 2 trials give
   an expected maximum annualized Sharpe of 4.76 under a *true edge of zero*. Picking the horizon-A winner after seeing
   21 results is the textbook path to a high Probability of Backtest Overfitting. The correct response is to pre-commit to
   the horizon with the most blocks (C), and there the incumbent wins.
10. **Is a tabular foundation model scientifically justified here, or decoration? Decoration — but a *falsifiable* one,**
    and that is worth writing up. Deploying TabICLv2 would add a 200 MB torch dependency, **4.0 s of CPU for one
    prediction** on our 1 200-row context (TabPFN v2: 2.4 s; the logit: 0.1 ms), a third-party checkpoint downloaded at
    runtime, and a model whose advantage exists only on the sample where we cannot measure it.
    Reporting that we *tested* two 2025/2026 tabular foundation models under an identical protocol and that they did not
    beat a twelve-coefficient logistic regression is a stronger and more honest claim than shipping one.

---

## 2. Source cards

### Tabular foundation models

**H-S1 — Hollmann, Müller, Purucker, Krishnakumar, Körfer, Hoo, Schirrmeister & Hutter (2025), "Accurate predictions on
small data with a tabular foundation model", *Nature* 637(8045), 319–326, DOI 10.1038/s41586-024-08328-6.**
TabPFN v2: a transformer pre-trained on millions of synthetic tabular tasks that performs Bayesian-style in-context
inference — no gradient training on the target dataset. Claim: outperforms all previous methods on datasets **up to
10 000 samples and ~500 features** by a wide margin, in a fraction of the time a tuned baseline needs (their headline
comparison is against a 4-hour AutoGluon budget). Relevance: our datasets are 416–3 687 rows × 12 features, squarely inside
the design regime. Confidence: high (peer-reviewed, Nature).

**H-S2 — Qu, Holzmüller, Varoquaux & Le Morvan (2025), "TabICL: A Tabular Foundation Model for In-Context Learning on
Large Data", ICML 2025, arXiv:2502.05564.** Two-stage column-then-row attention producing fixed-dimension row embeddings,
then a transformer for ICL. Pretrained on synthetic sets up to 60 K rows; handles 500 K rows on affordable hardware.
On the 200-dataset TALENT suite it is **on par with TabPFN v2 while up to 10× faster**; on the 53 datasets with > 10 K rows
it beats both TabPFN v2 and CatBoost. Confidence: high.

**H-S3 — TabICLv2 (2026), arXiv:2602.11139, "TabICLv2: A better, faster, scalable, and open tabular foundation model";
code and weights github.com/soda-inria/tabicl, BSD-3-Clause.** New synthetic-data engine, scalable softmax attention,
Muon optimizer. Claims to surpass **RealTabPFN-2.5** (tuned, ensembled, real-data fine-tuned) on TabArena and TALENT
*without tuning*, and to beat current GBDTs. Supports classification **and regression**. Documented pretraining range:
**300–48 000 rows, 2–100 columns**. This is the checkpoint our experiment actually ran
(`tabicl-classifier-v2-20260212.ckpt`). Confidence: high for the licence and limits (verified from the repo);
medium-high for the benchmark claims (preprint, authors' own evaluation).

**H-S4 — Erickson, Purucker, Tschalzev, Holzmüller, Mutalik Desai, Salinas & Hutter (2025), "TabArena: A Living Benchmark
for Machine Learning on Tabular Data", NeurIPS 2025 Datasets & Benchmarks, arXiv:2506.16791.** 51 manually curated
datasets, nested CV, Elo leaderboard, continuously maintained. Four findings, all directly relevant: gradient-boosted
trees remain strong contenders; deep learning catches up only with large time budgets **and ensembling**;
**foundation models excel on smaller datasets**; **cross-model ensembles advance the state of the art**.
Confidence: high.

**H-S5 — Grinsztajn, Oyallon & Varoquaux (2022), "Why do tree-based models still outperform deep learning on typical
tabular data?", NeurIPS 2022 D&B.** 45 curated datasets. Tree ensembles remain state of the art on medium-sized
(~10 K row) tabular data even ignoring their speed advantage; the causes are inductive biases (robustness to
uninformative features, non-smooth target functions, non-rotation-invariance). Confidence: high.

**H-S6 — McElfresh et al. (2023), "When Do Neural Nets Outperform Boosted Trees on Tabular Data?", NeurIPS 2023 D&B,
arXiv:2305.02997.** 19 algorithms × 176 datasets, the largest such study. Findings: the NN-vs-GBDT debate is
overemphasised — on most datasets either the gap is negligible or light GBDT tuning matters more than the model class;
GBDTs are favoured on **larger datasets, high row-to-feature ratios and "irregular" datasets**. Confidence: high.

**H-S7 — Cheng, Jia, Zhou, Li & Guo (2025), "Realistic Evaluation of TabPFN v2 in Open Environments", arXiv:2505.16226.**
First systematic stress test of TabPFN v2 outside curated benchmarks. TabPFN v2 "shows significant limitations in open
environments"; it is suitable for **small-scale, covariate-shifted, class-balanced** tasks, and
"**tree-based models remain the optimal choice for general tabular tasks in open environments**". Our horizon B is
label-shifted (base rate 0.81 → 0.65), which is exactly the case they flag. Confidence: medium-high (preprint).

**H-S8 — Zhang, Tan, Tian & Li (2025), "TabPFN: One Model to Rule Them All?", arXiv:2505.20003.** Statistical reading of
TabPFN as approximate Bayesian inference under its synthetic prior; documents cases where it beats LASSO even when the
LASSO assumptions hold, and cases of covariate-shift failure. Useful for the write-up's framing: a TFM is a *prior*, and
if the prior does not match financial regime data, in-context learning cannot rescue it. Confidence: medium.

**H-S9 — Adjacent open models, 2024–2026.** TabDPT (Layer6 AI, arXiv:2410.18164, Apache-2.0) — ICL + retrieval + real-data
self-supervision, power-law scaling. Mitra (AWS/AutoGluon, arXiv:2510.21204, NeurIPS 2025, **Apache-2.0** weights on HF)
— mixed synthetic priors, claims to beat both TabPFN v2 and TabICL on classification and regression.
CARTE (arXiv:2402.16785) — graph representation of table entries, enables transfer across tables with unmatched columns;
irrelevant to us (we have one fixed schema). ConTextTab (SAP), TabSTAR, LimiX (code Apache-2.0, **weights academic-only,
commercial by authorisation**), TabFlex, MotherNet. Confidence: medium (vendor/preprint claims, not independently
replicated here); licences verified on Hugging Face where stated.

### Machine learning in finance and the overfitting problem

**H-S10 — Gu, Kelly & Xiu (2020), "Empirical Asset Pricing via Machine Learning", *RFS* 33(5), 2223–2273.**
~30 000 stocks, 60 years (1957–2016), 94 characteristics × 8 macro interactions ≈ 900+ signals — millions of
observations. Monthly out-of-sample R²: OLS-3 benchmark **0.16 %**; unrestricted OLS **deeply negative**; elastic net
**0.11 %**; PCR / PLS **0.26 % / 0.27 %**; trees and neural nets **0.33 %–0.40 %**. The nonlinear gain over a
three-variable linear benchmark is **~0.2 percentage points of monthly R²** on a dataset roughly a thousand times larger
than ours. Read the right way, this is the strongest argument *against* expecting a large ML gain on 1 533 sessions.
Confidence: high.

**H-S11 — López de Prado (2018), *Advances in Financial Machine Learning*, Wiley, ch. 7 (purged/embargoed k-fold) and
ch. 12 (Combinatorial Purged CV).** Standard k-fold assumes i.i.d. rows; overlapping labels leak information into the
training set and inflate backtested Sharpe. Purging removes training samples whose label windows overlap the test set;
the embargo removes a further buffer for serial correlation; CPCV generates many train/test paths to give a *distribution*
of backtest outcomes rather than one number. Confidence: high (textbook).

**H-S12 — Bailey, Borwein, López de Prado & Zhu (2014), "The Probability of Backtest Overfitting" (JCF / SSRN 2326253);
Bailey & López de Prado (2014), "The Deflated Sharpe Ratio", *JPM* 40(5); Bailey & López de Prado (2012a),
"The Sharpe Ratio Efficient Frontier", *Journal of Risk* 15(2).** PBO is estimated by Combinatorially Symmetric CV: the
share of splits in which the in-sample best configuration ranks below median out of sample. MinBTL / MinTRL give the
number of observations needed before a claimed Sharpe is credible. Already reproduced in-house to four decimals in
`research/F2_user_sources_llm_events_eval.md` §5.3 (MinTRL 2 860 / 751 / 207 days for annualized SR 0.5 / 1.0 / 2.0 at
skew −1.5, kurtosis 6; PSR ceiling 0.897 at T = 3; E[max SR] over 2 trials = 4.76). Confidence: high.

**H-S13 — Harvey, Liu & Zhu (2016), "…and the Cross-Section of Expected Returns", *RFS* 29(1), 5–68.** After multiple-testing
adjustment a new factor needs **t > 3.0**; only 9 of 313 candidate variables survive. Directly applicable: our
horizon-A tercile-spread t-statistics of 4.0–4.5 are naive (i.i.d., 2 year-blocks, 21 configurations searched) and would
not survive an honest adjustment. Confidence: high.

**H-S14 — White (2000), "A Reality Check for Data Snooping", *Econometrica* 68(5); Hansen (2005), "A Test for Superior
Predictive Ability", *JBES* 23(4).** Bootstrap tests for "is the best of M models better than the benchmark", correcting
for the search over M. Hansen's SPA studentizes the statistic and re-centres the null, restoring power that White's
least-favourable configuration destroys when many poor models are included. This is the textbook-correct test for exactly
what section 4 does (7 models against one benchmark); with 2–15 independent blocks we do not have enough data to run it
credibly, which is itself the finding. Confidence: high.

**H-S15 — Arnott, Harvey & Markowitz (2019), "A Backtesting Protocol in the Era of Machine Learning", *JFDS* 1(1), 64–74.**
Research protocol for ML in investing: require an ex-ante economic rationale, keep the model simple relative to the data,
document every specification tried, do not iterate on the holdout, and report the full search. Confidence: high.

**H-S16 — "Spurious Predictability in Financial Machine Learning" (2026), arXiv:2604.15531.** Adaptive specification
search produces statistically significant walk-forward backtests **even under martingale-difference nulls**. Proposes a
"falsification audit": run the *complete* workflow on synthetic zero-predictability and microstructure-placebo data; if it
still shows significant walk-forward evidence, it is spurious. Directly implementable for us and cheap. Confidence:
medium-high (preprint, 2026).

**H-S17 — Kelly, Malamud & Zhou (2024), "The Virtue of Complexity in Return Prediction", *Journal of Finance* 79(1),
459–503.** The dissenting view: ridgeless/heavily-parameterised models can beat simple ones even when parameters far
exceed observations, with benign overfitting. Cited here for balance — but their mechanism is *shrinkage in the
overparameterised limit with random features*, not a 200-tree boosted model on 12 hand-built features, and their
evaluation is a monthly market-timing Sharpe over decades. It does not license a TFM on 1 500 daily sessions.
Confidence: high for the paper, low for its transferability to our setting.

### Volatility as the underlying target

**H-S18 — Corsi (2009), "A Simple Approximate Long-Memory Model of Realized Volatility", *Journal of Financial
Econometrics* 7(2), 174–196.** HAR-RV: a constrained AR(22) regressing realised variance on its 1-day, 5-day and 22-day
averages. Estimated by OLS, >2 100 citations, and still the workhorse benchmark. Relevance: our `rv5_over_vix` /
`rv20_over_vix` / `absret_prev` features are a HAR in disguise, and the literature says a *linear* combination of them is
already close to the achievable frontier. Confidence: high.

**H-S19 — Bollerslev, Patton & Quaedvlieg (2016), "Exploiting the errors: A simple approach for improved volatility
forecasting", *Journal of Econometrics* 192(1), 1–18.** HARQ: let the HAR coefficients vary with the *estimated
measurement error* of realised variance, so persistence rises when RV is measured precisely. Significant forecast gains
for the S&P 500 and DJIA constituents. The lesson for us: the productive direction on this data is a better-specified
*linear* volatility model, not a bigger classifier. Confidence: high.

**H-S20 — ML-vs-HAR evidence, 2023–2025 (mixed).** Panel-data ML for RV (Journal of Empirical Finance 2023) finds linear
ML ≈ HAR, gradient-boosted trees a modest improvement, neural nets mixed, and models on granular predictor sets
typically *worse*; other studies (e.g. JFEC 2024, intraday commonality) do find significant RF/NN gains. The consistent
meta-finding is that training-window length, window type and window size drive the result as much as the model class.
Confidence: medium (heterogeneous literature); the defensible summary is "HAR is hard to beat and ML gains, where real,
are small".

### Calibration and scoring

**H-S21 — Niculescu-Mizil & Caruana (2005), "Predicting Good Probabilities With Supervised Learning", ICML '05;
and "Obtaining Calibrated Probabilities from Boosting", UAI '05.** Boosted trees and boosted stumps push probability mass
away from 0 and 1, producing a characteristic sigmoid distortion; Platt scaling (a 1-D logistic on the scores) and
isotonic regression fix it. After calibration, boosted trees predict the best probabilities of the methods compared.
Isotonic needs more data than Platt and overfits on small validation sets. Confidence: high.

**H-S22 — Guo, Pleiss, Sun & Weinberger (2017), "On Calibration of Modern Neural Networks", ICML, arXiv:1706.04599.**
Temperature scaling — one parameter on the logits, fitted on held-out data — is remarkably effective; its virtue on small
data is precisely that it has one parameter and therefore cannot overfit the validation set the way a many-parameter
calibrator would. It explicitly fails when the validation set is small or noisily labelled. Confidence: high.

**H-S23 — Murphy (1973), Brier-score decomposition; Brier (1950).** Brier = **reliability − resolution + uncertainty**.
Reliability = calibration (do 70 % forecasts verify 70 % of the time), resolution = how far the conditional rates depart
from the climatology, uncertainty = the base-rate variance, which no forecaster can influence. Reporting the three
components separately is the correct way to show that our small Brier differences are almost entirely *uncertainty* and
that resolution is what the taper actually monetises. Confidence: high.

### Online / sequential updating

**H-S24 — Recursive and Bayesian online updating.** Exponentially-weighted recursive least squares gives closed-form
per-observation updates with a forgetting factor; Bayesian logistic regression with a Laplace approximation gives a
recursive posterior without storing the history. In the forecasting literature, drift-triggered retraining achieves
accuracy comparable to periodic retraining at lower cost, and periodic retraining still wins when the data change
quickly; the practical gain of *online* over *periodic* updating is small, and it is further limited because the label
arrives only after the forecast horizon. Confidence: medium (no finance-specific, daily-frequency regime-classification
study found that isolates the online-updating effect).

---

## 3. Evidence table

| # | Question | What the evidence says | Strength | What we do |
|---|---|---|---|---|
| 1 | Do TFMs beat GBDT on 1–10 k rows? | Yes on curated benchmarks with weak drift (H-S1, H-S2, H-S3, H-S4: "foundation models excel on smaller datasets") | High | Test them; do not assume it transfers |
| 2 | Do they hold up under drift / open environments? | No — TabPFN v2 is for "small-scale, covariate-shifted, class-balanced" tasks; "tree-based models remain the optimal choice for general tabular tasks in open environments" (H-S7) | Medium-high | Treat our label shift (0.81 → 0.65) as disqualifying |
| 3 | Do trees beat deep learning on tabular data generally? | Yes at ~10 k rows (H-S5); gap often negligible and tuning matters more (H-S6) | High | Use XGBoost as the non-linear reference, not a NN |
| 4 | How much does ML add in asset pricing? | 0.16 % → 0.40 % monthly R² on ~3 M observations (H-S10) | High | Expect a *tiny* gain here; size the claim accordingly |
| 5 | Minimum honest protocol on ~1 500 sessions? | Expanding-window OOS + purge/embargo (H-S11); disclose M configurations; PBO/CSCV; DSR/MinTRL; t > 3 (H-S12, H-S13); SPA/Reality Check for the best-of-M (H-S14); ex-ante rationale, no holdout iteration (H-S15); falsification audit on synthetic nulls (H-S16) | High | Section 5 |
| 6 | Is a linear volatility model hard to beat? | Yes — HAR is the standing benchmark (H-S18); HARQ improves it *linearly* (H-S19); ML-vs-HAR evidence is mixed and window-dependent (H-S20) | High / medium | Prefer better linear features over a bigger classifier |
| 7 | Calibration method for small data? | Platt / temperature (1–2 parameters) over isotonic; boosted trees need it most (H-S21, H-S22) | High | Report calibration slope+intercept; use Platt if we ever calibrate |
| 8 | What to report for a probabilistic classifier? | Brier decomposed into reliability/resolution/uncertainty, log loss, AUC, calibration curve (H-S23) | High | Section 5 checklist |
| 9 | Does online/sequential updating help at daily frequency? | No specific evidence; drift-triggered ≈ periodic retraining; gains small and label-delayed (H-S24) | Medium | Decoration. Retrain nightly at most; do not build an online learner |
| 10 | Does the "virtue of complexity" license a big model here? | Their mechanism is ridgeless random features for market timing over decades, not 12 features on 1 500 days (H-S17) | High for paper, low for transfer | Do not cite it as support |

---

## 4. Experiment

### 4.1 Design

`research/experiments/model_comparison.py` reuses the **exact** feature list, target definitions, payoff model and CV
protocol of `scripts/train_regime_model.py`:

* Geometry: short distance = 0.70 × VIX-implied full-day E|move| (1.10 × straddle-implied), wing 0.50 % of spot,
  credit 17 % of wing, spot 762. P&L% = credit − clip(|move| − short, 0, wing).
* Targets: `inside = |move| ≤ short`. Horizon **A** = 10:30 → close (first test year 2025), **B** = open → close
  (2021), **C** = close → close at 1.10 × (2012).
* Features: `vix_prev, slope_prev, rv5_over_vix, rv20_over_vix, gap, absret_prev, is_first_friday, is_third_friday,
  dow_0..dow_3` (C drops `gap`).
* CV: expanding window, train on all years < y, test on year y, pooled OOS predictions. Folds with < 200 training rows
  are skipped (unchanged from the incumbent script).
* Models: constant base rate; logistic regression C=1 standardised (incumbent); XGBoost (depth 3, 200 trees, lr 0.03,
  subsample/colsample 0.8, min_child_weight 20, λ=5, α=0.5); LightGBM (8 leaves, depth 3, 200 trees, lr 0.03,
  min_child_samples 40, λ=5); sklearn HistGradientBoosting (the repo's existing cross-check); **TabPFN v2** (CPU,
  n_estimators 2); **TabICLv2** (CPU, `tabicl-classifier-v2-20260212.ckpt`); and the 50/50 logit+XGB average.
* Foundation models are given the **most recent 1 200 training rows** per fold (CPU budget; TabPFN's own CPU guard trips
  above 1 000 rows and its pretraining regime is ≤ 10 000 rows, TabICLv2's is 300–48 000). **This caps the TFMs on
  horizon C, where the other models see up to 5 500 rows — part of the TFM deficit on C is this cap, not the model.**
* Uncertainty: paired **block bootstrap by calendar year** of the per-observation Brier difference against the logit
  (2 000 resamples, 90 % interval). Blocks available: **A = 2, B = 5, C = 15**.
* Robustness: a *purged* variant dropping the 5 sessions before each test year; a 5-seed stability check for the tree
  models.

Environment: repo venv, CPU only, `torch.set_num_threads(8)`. Full run wall-clock ≈ 6 minutes.
Raw tables: `research/experiments/model_comparison_results.md`.

### 4.2 Headline metrics

**Horizon A — 10:30 → close, 416 OOS sessions (2025–2026), 2 year-blocks. Training base rate 0.7778, realised 0.8173.**

| model | Brier | log loss | AUC | cal. int. | cal. slope | ΔBrier vs logit [90 % block CI] | s |
|---|---|---|---|---|---|---|---|
| base rate | 0.15088 | 0.48018 | 0.500 | – | – | −0.00245 [−0.01059, +0.00970] | 0.0 |
| **logit (deployed)** | 0.15333 | 0.51771 | 0.562 | 1.204 | **0.140** | – | 0.0 |
| xgb | 0.14531 | 0.46122 | 0.639 | −0.807 | 1.723 | −0.00802 [−0.01062, −0.00415] | 0.2 |
| lgbm | 0.15025 | 0.47846 | 0.573 | 0.789 | 0.443 | −0.00308 [−0.00453, −0.00210] | 0.0 |
| hgb | 0.15013 | 0.48410 | 0.609 | 0.615 | 0.463 | −0.00319 [−0.00431, −0.00152] | 0.1 |
| **tabpfn v2** | **0.14465** | 0.45971 | 0.653 | −0.665 | 1.287 | −0.00868 [−0.01332, −0.00175] | 2.8 |
| **tabicl v2** | 0.14681 | 0.46708 | **0.660** | −0.048 | **0.808** | −0.00651 [−0.00833, −0.00381] | 4.0 |
| logit+xgb | 0.14605 | 0.46437 | 0.620 | −0.304 | 1.123 | −0.00728 [−0.00979, −0.00354] | 0.2 |

**Horizon B — open → close, 1 170 OOS sessions (2022–2026), 5 blocks. Training base rate 0.8108, realised 0.6487.**

| model | Brier | log loss | AUC | cal. int. | cal. slope | ΔBrier vs logit [90 % block CI] | s |
|---|---|---|---|---|---|---|---|
| base rate | 0.25416 | 0.72094 | 0.500 | – | – | +0.02304 [+0.00252, +0.04020] | 0.0 |
| **logit (deployed)** | 0.23112 | 0.65757 | 0.558 | 0.407 | 0.367 | – | 0.0 |
| xgb | 0.23010 | 0.65479 | 0.560 | 0.330 | 0.401 | −0.00102 [−0.00566, +0.00362] | 0.2 |
| lgbm | 0.23107 | 0.65896 | 0.555 | 0.350 | 0.360 | −0.00004 [−0.00660, +0.00606] | 0.1 |
| hgb | 0.23671 | 0.67921 | 0.548 | 0.433 | 0.232 | +0.00559 [−0.00240, +0.01222] | 0.3 |
| tabpfn v2 | 0.23157 | 0.65833 | 0.534 | 0.381 | 0.309 | +0.00045 [−0.00946, +0.01024] | 10.5 |
| tabicl v2 | 0.23170 | 0.66029 | 0.551 | 0.336 | 0.344 | +0.00058 [−0.00951, +0.00905] | 19.2 |
| **logit+xgb** | **0.22800** | **0.64953** | **0.563** | 0.318 | **0.471** | **−0.00312 [−0.00549, −0.00062]** | 0.2 |

**Horizon C — close → close at 1.10×, 3 687 OOS sessions (2012–2026), 15 blocks. Base rate 0.7622, realised 0.7670.**

| model | Brier | log loss | AUC | cal. int. | cal. slope | ΔBrier vs logit [90 % block CI] | s |
|---|---|---|---|---|---|---|---|
| base rate | 0.17872 | 0.54292 | 0.500 | – | – | +0.00628 [+0.00410, +0.00860] | 0.0 |
| **logit (deployed)** | 0.17244 | 0.52607 | 0.626 | 0.075 | **0.857** | – | 0.1 |
| xgb | 0.17323 | 0.52869 | 0.618 | 0.144 | 0.818 | +0.00079 [−0.00088, +0.00262] | 0.7 |
| lgbm | 0.17354 | 0.52955 | 0.616 | 0.204 | 0.767 | +0.00110 [−0.00061, +0.00299] | 0.4 |
| hgb | 0.17488 | 0.53393 | 0.610 | 0.368 | 0.631 | +0.00244 [+0.00031, +0.00479] | 0.9 |
| tabpfn v2 † | 0.17830 | 0.54138 | 0.604 | 0.456 | 0.538 | **+0.00586 [+0.00109, +0.01308]** | 36.1 |
| tabicl v2 † | 0.17760 | 0.54034 | 0.609 | 0.434 | 0.548 | **+0.00516 [+0.00106, +0.01089]** | 72.8 |
| **logit+xgb** | **0.17190** | **0.52463** | **0.630** | −0.027 | **0.949** | −0.00054 [−0.00133, +0.00026] | 0.8 |

† capped at 1 200 training rows per fold; the other models see the full expanding window (up to ~5 500 rows).

### 4.3 Economics: Brier skill and the P&L tercile spread

Terciles of the pooled OOS probability; `high − low` is the difference in mean condor P&L per contract. The
t-statistics are **naive Welch t-tests that assume i.i.d. sessions and ignore both within-year clustering and the
21-configuration search**; read them as effect-size indicators, not as evidence.

| horizon | model | Brier skill vs base rate | high − low, % of spot | high − low, $/contract | naive t | naive p | n/bucket |
|---|---|---|---|---|---|---|---|
| A | **logit (deployed)** | **−0.0162** | 0.0193 | **+14.71** | 1.27 | 0.207 | 139 |
| A | xgb | +0.0369 | 0.0752 | +57.31 | 4.52 | <0.001 | 139 |
| A | tabicl v2 | +0.0269 | 0.0588 | +44.79 | 3.96 | <0.001 | 139 |
| A | tabpfn v2 | +0.0413 | 0.0695 | +52.94 | 4.49 | <0.001 | 139 |
| B | **logit** | +0.0907 | 0.0385 | **+29.37** | 3.01 | 0.003 | 390 |
| B | xgb | +0.0947 | 0.0296 | +22.57 | 2.36 | 0.019 | 390 |
| B | tabicl v2 | +0.0884 | 0.0291 | +22.16 | 2.27 | 0.023 | 390 |
| B | tabpfn v2 | +0.0889 | 0.0046 | **+3.51** | 0.35 | 0.725 | 390 |
| C | **logit** | +0.0352 | 0.0705 | **+53.75** | 10.93 | <0.001 | 1229 |
| C | xgb | +0.0307 | 0.0686 | +52.28 | 10.58 | <0.001 | 1229 |
| C | tabicl v2 | +0.0063 | 0.0623 | +47.45 | 9.59 | <0.001 | 1229 |
| C | tabpfn v2 | +0.0024 | 0.0629 | +47.95 | 9.70 | <0.001 | 1229 |

Two things stand out. First, **the ranking of models flips with the horizon**: TFM > GBDT > logit on A (2 blocks),
GBDT ≈ logit > TFM on B (5 blocks), logit > GBDT > TFM on C (15 blocks). Second, **TabPFN's tercile ordering breaks on
B** — its "high" bucket earns −21.3 $/contract while its "mid" bucket earns −6.3, i.e. non-monotone, which is
disqualifying for a monotone size taper regardless of its Brier.

### 4.4 Robustness

**Purged variant** (drop the 5 sessions before each test year from training). Largest absolute Brier change across all
models and horizons: **0.0011** (LightGBM on A, and it *improves*). On B and C every change is ≤ 0.0006, and signs are
mixed. Conclusion: with one-session, non-overlapping labels there is no measurable leakage through volatility
autocorrelation at a 5-day scale. We should still keep a purge in the protocol, but it is not what is limiting us.

| horizon | logit | xgb | lgbm | tabpfn | tabicl |
|---|---|---|---|---|---|
| A ΔBrier (purged − plain) | −0.00059 | +0.00004 | −0.00110 | −0.00043 | −0.00079 |
| B ΔBrier | +0.00026 | +0.00046 | +0.00060 | −0.00004 | −0.00008 |
| C ΔBrier | +0.00001 | −0.00012 | −0.00028 | – | – |

**Seed stability** (5 seeds, tree models). XGBoost Brier sd = 0.00006 (A), 0.00043 (B), 0.00019 (C); LightGBM
0.00088 / 0.00020 / 0.00010; HistGB is deterministic. Seed noise is therefore **one order of magnitude smaller** than the
model-to-model Brier differences on A (~0.008) and the same order as the differences on B and C (~0.001) — another way of
saying that the B and C rankings among logit / xgb / lgbm are not resolvable.

**Wall-clock** (full expanding-window CV, CPU): logit 0.0–0.1 s, LightGBM 0.0–0.4 s, XGBoost 0.2–0.7 s,
HistGB 0.1–0.9 s, TabPFN v2 2.8–36.1 s, TabICLv2 4.0–72.8 s. Per-call latency for the live agent is in section 6.

### 4.5 Honest interpretation

* **Only horizon C supports an inference.** A block bootstrap over 2 blocks (A) reproduces the same two years in every
  resample; its "CI excludes zero" is an artefact of resampling 416 correlated observations, not evidence. B has 5
  blocks — marginal. C has 15 — usable. On C the incumbent logit wins among single models and both TFMs are worse with
  CIs that exclude zero, though the 1 200-row cap confounds part of that.
* **The one consistent, direction-stable result is the ensemble.** logit+XGB is better than logit alone on all three
  horizons (−0.0073 / −0.0031 / −0.0005 Brier) and is the best model overall on B and C. This is exactly TabArena's
  finding (H-S4) that cross-model ensembles advance the state of the art. But on the only horizon with power its
  advantage is **−0.0005 Brier with a CI spanning zero**. Under Bailey–López de Prado that is not a discovery.
* **Multiple testing:** 7 model families × 3 horizons = 21 configurations, plus a purged variant and 5 seeds for three of
  them. If we picked the horizon-A winner we would be selecting the maximum of 7 correlated statistics on the sample with
  the least power — the canonical PBO failure mode (H-S12). We do not.
* **MinTRL framing:** even taking the horizon-A tercile spread at face value (+57 $/contract for XGBoost, ~2 contracts,
  ~$114/session on $100 k = 11 bp/session), F2 §5.3's arithmetic says that certifying an annualized Sharpe of 1.0 at
  skew −1.5 / kurtosis 6 needs **751 sessions**. Our live window is 2.5. No model choice changes that, which is precisely
  why the model is confined to shrinking size.
* **What would change the verdict:** more data on the true horizon. Horizon A has 668 sessions total and starts
  2024-01-02; horizon B starts 2020-07-27 (not 2018 as the report claims). If the 10:30 series were extended backwards to
  2018 and the TFM advantage on A survived 6–8 year-blocks, a TabICLv2 deployment would become defensible. That is a
  post-hackathon project.

---

## 5. Recommended protocol and reporting checklist

**Protocol for model selection on ~1 500 sessions.**

1. **Ex-ante rationale first** (H-S15). Every feature must have a stated economic reason before it is fitted. Ours do
   (VIX level, term slope, RV/IV ratio, gap, calendar).
2. **Expanding-window, year-by-year OOS only.** No random k-fold, no shuffling. Report the number of *independent
   blocks*, not just n — it is the block count that bounds the inference.
3. **Purge and embargo** (H-S11). Our labels are one-session and non-overlapping, so a 5-session purge suffices; we
   measured its effect (≤ 0.0011 Brier) and report it rather than assuming it away.
4. **Fix the candidate list before looking at results, and count it.** M = 7 families × 3 horizons = 21 here. Disclose M.
5. **Pre-commit to the decision horizon** — the one with the most independent blocks that shares the geometry. We
   pre-commit to C for inference and use A only to describe the live horizon.
6. **Paired block bootstrap by year** for every score difference against the incumbent; report the interval, not a
   p-value. Where a proper best-of-M test is wanted, Hansen's SPA (H-S14) is the right one — it needs more blocks than we
   have, and saying so is part of the result.
7. **Seed stability** for any stochastic learner: if seed sd is the same order as the model gap, the gap is not real.
8. **Falsification audit** (H-S16): re-run the entire pipeline with the target shuffled within each year and with a
   synthetic martingale-difference series. Any surviving "skill" is search bias. *(Not yet run — listed as follow-up.)*
9. **Never iterate on the deployment decision after seeing the OOS table.** The incumbent stays unless a challenger wins
   on the pre-committed horizon by more than the bootstrap interval.
10. **Calibration**: if a model is ever recalibrated, use Platt/temperature (1–2 parameters), never isotonic, on this
    sample size (H-S21, H-S22).

**Reporting checklist for the write-up** (what must be disclosed):

- [ ] Number of model families and configurations tried: **21** (7 × 3 horizons), plus the 2 live configurations from F2.
- [ ] CV design: expanding-window yearly, first test year per horizon, folds skipped for < 200 training rows,
      **independent blocks: A = 2, B = 5, C = 15**.
- [ ] Purge/embargo used and its measured effect (≤ 0.0011 Brier).
- [ ] Metrics: Brier **with its base-rate reference and skill score**, log loss, AUC, calibration intercept **and slope**;
      ideally the Murphy reliability/resolution/uncertainty split (H-S23).
- [ ] The economic metric that the model actually drives: mean condor P&L per predicted-probability tercile, with n.
- [ ] Seed sd for stochastic models.
- [ ] Wall-clock per model and per-call latency.
- [ ] The statement that **no Sharpe ratio is claimed** and the MinTRL/PSR arithmetic from F2 §5.3.
- [ ] The negative results: the logit is worse than a constant on horizon A; TabPFN's terciles are non-monotone on B;
      the TFMs lose on C.
- [ ] The two label errors found in `docs/regime_model_report.md` (horizon B starts 2020-07-27, OOS is 2022–2026).
- [ ] Licence and provenance of every third-party model weight used (section 6).

---

## 6. Licences and practical constraints

**Verified 2026-09-02 from the primary sources.**

| component | code licence | weights licence | gated? | commercial use | MIT-repo friendly |
|---|---|---|---|---|---|
| **TabICL / TabICLv2** | BSD-3-Clause (`github.com/soda-inria/tabicl/LICENSE`, "Copyright (c) 2025, Soda team @ Inria"); the `src/tabicl/forecast` subdirectory is Apache-2.0 derived from TabPFN-TS | **BSD-3-Clause** (HF `jingang/TabICL`, `license: bsd-3-clause`, `gated: false`) | **No** | Yes | **Yes** |
| **TabPFN v2** | Prior Labs License v1.2 (Apache-2.0 + Paragraph 10) | **Prior Labs License v1.1** (HF `Prior-Labs/TabPFN-v2-clf` / `-reg`, `license: other`, `license_name: priorlabs-1-1`, `gated: false`) | No | **Yes**, with the attribution obligation | **No** (adds a non-standard clause) |
| **TabPFN-2.5 / 2.6 / 3** | as above | **non-commercial**, licence acceptance + API key required | **Yes** | **No** (Enterprise Licence required) | **No** |
| Mitra (AutoGluon) | Apache-2.0 | Apache-2.0 (HF `autogluon/mitra-classifier`, `gated: false`) | No | Yes | Yes |
| TabDPT | Apache-2.0 | Apache-2.0 | No | Yes | Yes |
| LimiX | Apache-2.0 | academic-open; commercial by authorisation | – | No | No |
| XGBoost | Apache-2.0 | – | – | Yes | Yes |
| LightGBM | MIT | – | – | Yes | Yes |
| scikit-learn | BSD-3-Clause | – | – | Yes | Yes |

**Prior Labs License, Paragraph 10 (verbatim, from `github.com/PriorLabs/TabPFN/blob/main/LICENSE`, v1.2 Dec 2025;
identical text in v1.1 May 2025, the version the v2 weights point to):**

> 10. Additional attribution.
> If You distribute or make available the Work or any Derivative Work thereof relating to any part of the source or model
> weights, or a product or service (including another AI model) that contains any source or model weights, You shall
> (A) provide a copy of this License with any such materials; and (B) prominently display "Built with PriorLabs-TabPFN"
> on each related website, user interface, blogpost, about page, or product documentation. If You use the source or model
> weights or model outputs to create, train, fine tune, distil, or otherwise improve an AI model, which is distributed or
> made available, you shall also include "TabPFN" at the beginning of any such AI model name.
> **To clarify, internal benchmarking and testing without external communication shall not qualify as distribution or
> making available pursuant to this Section 10 and no attribution under this Section 10 shall be required.**

The final sentence is why the *research comparison* in section 4 is unencumbered: it is internal benchmarking. The header
line of the same file states: *"Prior Labs License (Apache 2.0 with ADDITIONAL PROVISION) … a derivative of the Apache 2.0
license … The added Paragraph 10 introduces an enhanced attribution requirement inspired by the Llama 3 license."*

**Prior Labs docs, `docs.priorlabs.ai/how-to-access-gated-models` (verbatim):**
> "TabPFN-2.5, TabPFN-2.6, and TabPFN-3 are released under a non-commercial license, which you need to accept before the
> model files can be downloaded."

We hit this live: `pip install tabpfn` (v8.5.0) opened a browser login to `ux.priorlabs.ai` and blocked on an API-key
prompt. We therefore pinned **`tabpfn<3` → 2.2.1**, which downloads the ungated v2 weights, for the benchmark only.

**TabICL, `github.com/soda-inria/tabicl/LICENSE` (verbatim opening):**
> "BSD 3-Clause License / Copyright (c) 2025, Soda team @ Inria"

Weights: `huggingface.co/jingang/TabICL`, `license: bsd-3-clause`, `gated: false`, auto-downloaded on first use. This is
the only tabular foundation model in the current frontier that is unambiguously MIT-repo compatible for both code and
weights, so it is the tested candidate.

**Practical constraints for a live deployment (measured, CPU only, 8 torch threads, this machine):**

| model | `fit` on 1 200 × 12 | **one single-row prediction** | extra dependency | runtime download |
|---|---|---|---|---|
| logistic regression | 3 ms | **0.1 ms** | – (already in the repo) | – |
| XGBoost | 138 ms | **0.2 ms** | xgboost wheel (~5 MB) | – |
| TabPFN v2 | 691 ms | **2 412 ms** | torch CPU (~200 MB) | checkpoint from Hugging Face |
| TabICLv2 | 264 ms | **4 041 ms** | torch CPU (~200 MB) | checkpoint from Hugging Face |

Both foundation models are *in-context* learners: `fit` merely stores the context and the transformer forward pass over
the whole 1 200-row context happens inside `predict_proba`, which is why a **single** prediction costs 2.4 s (TabPFN v2)
to 4.0 s (TabICLv2) on CPU — four orders of magnitude more than the logit. At one decision per hour that is affordable in
absolute terms. At one decision per hour this is affordable; it is nevertheless a torch dependency,
a third-party checkpoint download at runtime, and a new failure mode (HF unreachable at 10:30 ET) added to an agent whose
strongest selling point is determinism. Both models also introduce non-determinism unless `random_state` is pinned and
threads are fixed; our runs pin the seed.

---

## 7. Follow-up sources and open gaps

1. **Run the falsification audit of H-S16** (arXiv:2604.15531) on this exact pipeline: shuffle `inside` within each
   calendar year and re-run all 21 configurations. Expected result: the horizon-A TFM advantage largely survives, which
   would prove it is search bias. Cheap (≈ 6 min) and the single most valuable remaining experiment.
2. **Hansen (2005) SPA test** with the stationary bootstrap over the 15 horizon-C year-blocks — the formally correct
   best-of-7 test. Worth doing if a model change is ever contemplated.
3. **Murphy decomposition** of the Brier scores in section 4.2 into reliability / resolution / uncertainty, to show
   numerically that the differences live in resolution and that uncertainty dominates.
4. **Bollerslev–Patton–Quaedvlieg HARQ features** (H-S19): add a measurement-error-scaled RV term instead of a bigger
   classifier. This is the highest-expected-value modelling change on this dataset and it stays linear.
5. **Mitra (arXiv:2510.21204, Apache-2.0)** — not benchmarked here because it ships inside AutoGluon (a large install)
   and the time budget was spent on TabICLv2. If a TFM is ever revisited, Mitra is the second license-eligible candidate.
6. **TabArena leaderboard** (`github.com/autogluon/tabarena`, live) — check whether TabICLv2 still leads the
   permissively-licensed field before any future deployment decision.
7. **Bailey & López de Prado (2012a), "The Sharpe Ratio Efficient Frontier", *Journal of Risk* 15(2)** — the correct
   citation for MinTRL (F2 already flags that the DSR paper is the wrong home for it).
8. **Extend the 10:30 bar series back to 2018** so horizon A gains 6–8 independent year-blocks. Without that, no
   statement about the live horizon can be made with confidence, and this whole comparison would have to be redone.
9. **Open gap:** we found no study that isolates the benefit of *online/sequential* updating for daily-frequency regime
   classification in finance. Treat any such claim in the write-up as unsupported; nightly refit of a 12-coefficient
   logit is both simpler and defensible.

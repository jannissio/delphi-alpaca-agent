# Delphi: an evidence-based 0DTE options agent for Alpaca paper trading

*lablab.ai x Alpaca AI Trading Agents Hackathon, 28 Aug - 4 Sep 2026. Solo entry.*

**We do not claim a statistically detectable edge. We claim a risk process that behaved exactly as specified.**

Delphi sells defined-risk, same-day-expiry iron condors on SPY inside pre-approved time windows, sized
so that the worst case of a session is 2 % of capital and the worst case of the whole hackathon is 6 %.
The short strikes are a conformal prediction interval for the close, calibrated on history and adapted
after every session; the agent sells that interval only when the option market pays more for it than the
calibration says it is worth (the Conformal Condor, below). A large language model classifies the regime
and may veto; deterministic code owns every number. Every decision, gate evaluation, order and fill is
written to an append-only audit log from which the post-session report, the determinism replay and the
leakage audit are computed.

## Why this design (short version of `research/STATE_OF_THE_ART.md`)

| Finding | Evidence | Consequence |
|---|---|---|
| The volatility risk premium is real but ~2-3 % a year; 0DTE premium selling has ~zero expected value after costs | Carr & Wu 2009 RFS; Bakshi & Kapadia 2003; Almeida, Freire & Hizmeri 2025; Beckmeyer, Branger & Gayda 2023; Vilkov 2026 | No edge is claimed. Positions are small, defined-risk, and the P&L is reported against benchmarks, not as alpha |
| Defined risk cuts the max drawdown by ~60 % vs naked premium | Cboe CNDR vs PUT 2006-2019; Augustin et al. 2021 | Every short leg has a bought wing in the same package order; no price stops: the wing is the stop |
| A condor is a short prediction interval; conformal prediction gives intervals with guaranteed coverage and adapts online under distribution shift | Vovk et al. 2005; Lei et al. 2018 JASA; Gibbs & Candes 2021 NeurIPS; Barber et al. 2023 AoS | Short strikes = split-conformal interval on the ratio realised move / implied move, alpha adapted after every session (`research/G`) |
| For a vertical spread, credit / width is the risk-neutral probability of finishing beyond the spread (digital limit) | Breeden & Litzenberger 1978 J. Business | The market's price of our interval is read off the quote: trade only when it exceeds the calibrated probability by a cost margin (gate 31) |
| Condor Sharpe rises with short-strike distance; the put side was the richer 0DTE sale 2016-2026 | Vilkov 2026 (SPXW, n = 1,319) | Symmetric shorts, wings max($3, 0.5 % of spot); the fixed 1.10x-implied-move rule ran on the pilot day and stays as the logged counterfactual |
| 0DTE quoted spreads are 1-2 ticks; a mid-price limit fills within a second 58-71 % of the time; percent-of-mid collars veto everything | Fu, Li & Musto (SEC DERA) | Order walking and price collars in ticks, on the package, never market orders |
| LLM agents change behaviour when tickers are visible; the same agent on the same data produced returns from 5 % to 28 % across runs | Glasserman & Lin 2023; Koviazin et al. 2026 | Tickers and dates masked; LLM emits enums only; temperature, top_p, top_k and seed pinned; k = 3 votes must agree or the answer is NO_TRADE |
| Gradient boosting and tabular foundation models do not beat a small logit on ~1,500 sessions where inference is possible | TabArena 2025; Grinsztajn et al. 2022; our `research/H` (21 configurations) | The regime model stays a twelve-coefficient logistic regression that can only shrink size; the negative result is reported |
| With 3 observations the Probabilistic Sharpe Ratio cannot reach 95 % at any performance level for fat-tailed returns | Bailey & Lopez de Prado 2014 | No Sharpe, win rate or annualised return is reported. Process metrics are |
| Non-farm payrolls on Fri 2026-09-04 08:30 ET; ISM services Thu 10:00 ET; Broadcom earnings Wed after close | BLS, ISM, company IR | Friday is a logged NO_TRADE day; Thursday entries after 10:15 ET; no single-name earnings trades |

## The Conformal Condor (live from 2026-09-03)

1. **Score.** For every past session, `r = |close / price_10:30 - 1| / (VIX-implied expected absolute daily move)`.
   The unit is the same in history and live, so the calibration set and the live decision never disagree
   about what "one implied move" means.
2. **Interval.** With the trailing 250 scores and the current miscoverage level `alpha_t` (target 0.20), the
   split-conformal radius `k_t` is the `ceil((n+1)(1-alpha_t))/n` empirical quantile. Short strikes go at
   `spot +- k_t x implied move`, wings `max($3, 0.5 % of spot)` further out, always bought. Coverage 1 - alpha
   is a theorem under exchangeability; after every session, traded or not, `alpha_t` moves by
   `gamma (alpha_target - err_t)` with `gamma = 0.005` (adaptive conformal inference), which keeps long-run
   coverage at the target even when the distribution drifts.
3. **The market's price of the interval.** `Q_mid = credit / wing`, read off the quote. To first order in the
   wing width this is the risk-neutral probability of finishing beyond the midpoint of the spread.
   `P_mid` is the conformal p-value of the same distance in the scores. The expected payoff of one package is,
   to the same order, `wing x (Q_mid - P_mid)`.
4. **Gate 31 (coverage gate).** Trade iff `Q_mid - P_mid >= 0.05`. Five probability points at a $4 wing are
   about $20 per contract, the modelled round-trip cost of four legs at one tick: a cost margin, not a knob.
5. **Kelly is an exhibit, not a controller.** The audit record carries the two- and three-state Kelly
   fractions with their standard error; at these odds Kelly is negative or its error exceeds any prudent bet,
   so the 2 % cap binds, and the record shows that it binds.
6. **What is logged, every session, even with zero fills:** `alpha_t`, `n`, `k_t`, the strikes, `Q_mid` and
   the per-side `Q`, `P_mid`, the gap, the decision, and what the fixed rule would have done. After the close:
   the realised ratio, inside or outside, and the alpha update. This ledger is the evaluation object of the
   write-up; it needs no statistical power to be verified.

Back-fill from history (`docs/conformal_backfill.md`): coverage 0.806 over 618 calibrated sessions against the
0.80 target, by year 0.83 / 0.80 / 0.78, while the fixed rule's coverage drifts 0.77 / 0.79 / 0.86. What the
history cannot show is whether the gate makes money: there is no option-price history on the basic plan, so
`Q` exists only live. Evidence, sharpening and the refutation of the width-changing variant: `research/G_conformal_condor.md`.

## What was trained on history, and what it is allowed to do

`scripts/history_data.py` assembles 9,230 sessions (S&P 500 since 1975 and VIX since 1990 from Cboe;
SPY open/close from 2020-07 and 30-minute bars from 2024-01 from Alpaca IEX). `scripts/train_regime_model.py`
fits a standardised logistic regression that maps regime features known at the morning entry (VIX level,
VIX/VIX3M slope, realised-vs-implied volatility, overnight gap, calendar flags) to the probability that the
session ends inside the condor's short strikes. Validation is expanding-window, year by year, against the
unconditional base rate. The deployed model (`config/regime_model.json`) can only shrink the position size:
full at or above the historical tercile threshold, half below it, zero in the bottom decile. The same dataset
gives the random-entry Monte Carlo null against which the campaign P&L is reported as a percentile.

Disclosed, not hidden (`docs/regime_model_report.md`, `research/H_tabular_ml_small_data.md`): on the exact
10:30-to-close horizon the logit is worse than a constant (two year-blocks, no inference possible); on the
close-to-close horizon with fifteen blocks it is the best single model. XGBoost, LightGBM, a logit+XGBoost
average, TabPFN v2 and TabICL v2 were run under the identical protocol (7 families x 3 horizons = 21
configurations): the foundation models win only where nothing can be measured and lose where it can. The
constant-credit assumption of the back-test (17 % of the wing) invalidates any conclusion that changes the
interval width; the live agent reads the credit off the quote instead. No third-party model weights ship
with the agent (TabICL v2 is BSD-3, TabPFN v2 carries an attribution clause, TabPFN 2.5+ is non-commercial).

## Architecture

```
Alpaca data (alpaca-py) + Cboe VIX/VIX3M/VIX1D + Alpaca news
        |
        v
Regime module (LLM, Featherless)  -->  enums only: VOL_REGIME, TREND, EVENT_RISK, FAMILY, VETO
        |
        v
Strategy module (code): conformal interval on |move|/implied move (ACI) -> symmetric condor -> Q from the quote
        |
        v
Sizing (code): 2 % / 6 % max-loss budget, Grossman-Zhou taper, VIX/VIX3M, VIX1D and regime-model multipliers
        |
        v
Gate engine (code): 30 gates from SEC 15c3-5, MiFID II RTS 6, FINRA 15-09, Knight Capital + gate 31 (Q_mid - P_mid >= margin)
        |
        v
Critic (LLM): PASS / REDUCE / BLOCK, never enlarge
        |
        v
Execution (code): mleg limit-order ladder in ticks -> book -> reconciliation -> flatten by 15:15 ET -> alpha update after the close
        |
        v
Audit log (JSONL) -> journal (LLM prose from facts) -> post-session report -> determinism + leakage audits
```

* **Alpaca Trading API** (alpaca-py): account, clock, option chain snapshots, multi-leg orders, positions; IEX bars for the conformal scores.
* **Alpaca CLI**: `scripts/status.sh` is the independent monitoring and reconciliation path (JSON output to `logs/`).
* **Alpaca MCP server**: used by the operator (Claude Code) to inspect the account and chains during development and in the demo.
* **Featherless.ai**: open-weight models (`deepseek-ai/DeepSeek-V3.2` for regime and critic, `Qwen/Qwen3-30B-A3B-Instruct-2507` for the journal) through the OpenAI-compatible endpoint.

## Run

```bash
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt   # Windows; use bin/ on Unix
cp .env.example .env        # fill in paper keys and the Featherless key; never commit .env
.venv/Scripts/python -m pytest -q             # 28 tests incl. a fake end-to-end cycle and the conformal arithmetic
python scripts/history_data.py                # assemble state/history/daily.csv (Cboe + Alpaca IEX)
python scripts/conformal_backfill.py --force  # replay ACI through history -> state/conformal.json, docs/conformal_backfill.md
python scripts/preflight.py --at 10:20        # live pre-flight: interval, P vs Q, sizing, every gate; sends nothing
AGENT_DRY_RUN=true .venv/Scripts/python -m agent.main   # logs would-be orders without sending
.venv/Scripts/python -m agent.main            # live paper loop (updates alpha after the close by itself)
python scripts/conformal_update.py            # end-of-session alpha update if the agent was not running at 16:10 ET
python scripts/kill.py --flatten              # kill switch: cancel all, flag, flatten with limit orders
python scripts/report.py --session 2026-09-03 --out docs/report_2026-09-03.md
python scripts/dashboard.py                   # docs/dashboard.html incl. the P-vs-Q ledger
python scripts/determinism_check.py --k 5     # replay the last regime prompt, entropy in bits
python scripts/leakage_audit.py               # masked vs unmasked decision, re-identification rate
```

Paper trading is enforced: the agent refuses to start unless `ALPACA_PAPER_TRADE=true`.

## Repository map

* `config/` risk limits (immutable at runtime), strategy parameters incl. the pre-registered `conformal` block, event calendar, trained regime model
* `agent/core` models, clock, config, strategy, sizing, conformal (interval, ACI, P-vs-Q ledger), regime model, Black-Scholes fallback; `agent/gates` the gate engine; `agent/llm` provider, anonymiser, regime, critic, journal; `agent/execution` orders, flatten, reconciliation; `agent/reporting` audit log
* `scripts/` history assembly, model training, conformal back-fill and update, pre-flight, kill, flatten, status (CLI), report, dashboard, determinism check, leakage audit
* `research/` five literature reports, two source-reading reports, the conformal-condor study (G), the tabular-ML study (H) with their experiments, and the synthesis with a 50-entry bibliography
* `docs/` incident runbook, regime model report, conformal back-fill, session reports, write-up, slides

## License

MIT.

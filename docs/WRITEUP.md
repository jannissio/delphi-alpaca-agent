# Delphi: a risk process first, a trading agent second

*One-page write-up for the lablab.ai x Alpaca AI Trading Agents Hackathon. Paper account ID: see submission form. Public repo: MIT.*

**We do not claim a statistically detectable edge. We claim a risk process that behaved exactly as specified.**

## What the evidence allowed us to build

Over 2.5 trading sessions no options strategy has a measurable expected return: the index variance risk premium is real but worth about 2-3 % a year (Carr & Wu 2009; Bakshi & Kapadia 2003), and same-day-expiry premium selling is roughly zero after costs (Almeida, Freire & Hizmeri 2025; Beckmeyer, Branger & Gayda 2023; Vilkov 2026: unconditional 0DTE condor -0.008 % of spot per day after entry frictions, 45 % losing sessions). With three daily observations the Probabilistic Sharpe Ratio cannot reach 95 % at any performance level once returns are fat-tailed (Bailey & Lopez de Prado 2014; our arithmetic in `research/F2`). So the deliverable is a small, defined-risk, fully explained book plus a control system that a regulator would recognise.

## AI logic: the model decides categories, code decides numbers

The LLM (open-weight models on Featherless.ai) reads anonymised headlines, the macro calendar and the volatility term structure and returns **enums only**: VOL_REGIME, TREND, EVENT_RISK, a strategy family from a fixed menu, and a veto with a reason. Three independent calls must agree; disagreement is converted into NO_TRADE. A second LLM pass, the critic, sees the finished, gate-validated order and may say PASS, REDUCE or BLOCK, never "larger". Tickers and dates are masked (Glasserman & Lin 2023; Chen, Kelly & Xiu); sampling is pinned on temperature, top_p, top_k and seed (Koviazin et al. 2026 show temperature alone leaves 0.98 bits of decision entropy); every prompt and response is hashed and logged, and a replay script reports per-field decision entropy in bits.

Deterministic code computes the implied remaining-day move from the ATM straddle, places symmetric short strikes at 1.10x that move with wings of max($3, 0.5 % of spot) (Vilkov 2026: condor Sharpe rises with short distance; the put side, not the call side, was the richer sale), sizes from the max-loss budget, prices the package in ticks (Fu, Li & Musto, SEC: 0DTE spreads are 1-2 ticks; percent collars veto everything) and manages the exit.

**Trained on history, allowed only to brake.** A logistic regression fitted on 1,533 SPY sessions (2018-2026; decades of S&P 500 and VIX data for the regime features) estimates, from what is known at 10:00 ET, the probability that the day ends inside the condor's short strikes. Out of sample (expanding window, 2021-2026) its probability terciles separate condor P&L monotonically: -33, -15 and -4 dollars per contract from low to high on the open-to-close proxy, +21, +28 and +35 on the exact 10:30-to-close horizon. The model sets the size multiplier to 1, 0.5 or 0 and can never increase it. The same history gives the random-entry Monte Carlo null (2.5 sessions, two contracts per session: median +259, P05 -503 dollars) against which our P&L is reported as a percentile, not as alpha.

## Risk gates

Thirty controls derived from SEC Rule 15c3-5, MiFID II RTS 6, FINRA Notice 15-09 and the Knight Capital order (`research/C`, `config/risk_limits.yaml`, `agent/gates/engine.py`). The ones that fired or mattered: session max loss 2 % of capital ($2,000) with a continuous Grossman-Zhou taper toward a 6 % campaign cap; defined risk only (every short has a bought wing in the same package order); per-order caps of $1,000 max loss and 5 contracts; message-rate and fill throttles; duplicate-order window; stale, crossed or drifted quotes rejected; Greek budgets on the whole book; buying-power check at 1.25x; entry windows by day (Wed 10:00-11:00 and 12:30-13:30 ET, Thu after ISM at 10:15, **Friday NO_TRADE because of non-farm payrolls at 08:30 ET**), pause windows around scheduled releases, no entry after 14:00; flatten by 15:15 ET with escalating limit orders (Alpaca stops 0DTE opens at 15:30); kill switch file checked every cycle, cancel-all under 5 s; daily loss kill on an independent code path; order-echo and position reconciliation every cycle, any mismatch halts new risk; append-only audit log with git and config hashes; immutable risk config outside the agent's writable scope; incident runbook written before the first cycle.

## Alpaca infrastructure

Trading API through alpaca-py for account, clock, option chain snapshots with Greeks, multi-leg (mleg) limit orders and positions; the Alpaca CLI as the independent monitoring and reconciliation path (`scripts/status.sh`, JSON to disk); the Alpaca MCP server for operator inspection during development and the demo. Cboe delayed indices supply VIX, VIX3M and VIX1D. Paper trading is enforced at start-up.

## What we report

Gate evaluations and rejections per gate, NO_TRADE reasons, fill rung (mid, -1 tick, -2 ticks, natural) and slippage versus the decision mid, ex-ante versus ex-post Greeks, time-to-flat, LLM latency, tokens, vote unanimity and decision entropy, the leakage audit (masked versus unmasked decision, re-identification rate), P&L per package against SPY over the same hours, and the term-structure-implied event variance for the NFP day (Dubinsky et al. 2019). Not reported, on purpose: Sharpe, win rate, annualised return. Number of configurations tried: **{N_CONFIGS}**.

## Results

*(filled in after the Friday cutoff; see `docs/report_<date>.md`)*

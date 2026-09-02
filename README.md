# Delphi: an evidence-based 0DTE options agent for Alpaca paper trading

*lablab.ai x Alpaca AI Trading Agents Hackathon, 28 Aug - 4 Sep 2026. Solo entry.*

**We do not claim a statistically detectable edge. We claim a risk process that behaved exactly as specified.**

Delphi sells defined-risk, same-day-expiry iron condors on SPY inside pre-approved time windows, sized
so that the worst case of a session is 2 % of capital and the worst case of the whole hackathon is 6 %.
A large language model classifies the regime and may veto; deterministic code owns every number.
Every decision, gate evaluation, order and fill is written to an append-only audit log from which the
post-session report, the determinism replay and the leakage audit are computed.

## Why this design (short version of `research/STATE_OF_THE_ART.md`)

| Finding | Evidence | Consequence |
|---|---|---|
| The volatility risk premium is real but ~2-3 % a year; 0DTE premium selling has ~zero expected value after costs | Carr & Wu 2009 RFS; Bakshi & Kapadia 2003; Almeida, Freire & Hizmeri 2025; Beckmeyer, Branger & Gayda 2023; Vilkov 2026 | No edge is claimed. Positions are small, defined-risk, and the P&L is reported against benchmarks, not as alpha |
| Defined risk cuts the max drawdown by ~60 % vs naked premium | Cboe CNDR vs PUT 2006-2019; Augustin et al. 2021 | Every short leg has a bought wing in the same package order; no price stops: the wing is the stop |
| Condor Sharpe rises with short-strike distance; the put side was the richer 0DTE sale 2016-2026 | Vilkov 2026 (SPXW, n = 1,319) | Symmetric shorts at 1.10x the implied move, wings max($3, 0.5 % of spot) |
| 0DTE quoted spreads are 1-2 ticks; a mid-price limit fills within a second 58-71 % of the time; percent-of-mid collars veto everything | Fu, Li & Musto (SEC DERA) | Order walking and price collars in ticks, on the package, never market orders |
| LLM agents change behaviour when tickers are visible; the same agent on the same data produced returns from 5 % to 28 % across runs | Glasserman & Lin 2023; Koviazin et al. 2026 | Tickers and dates masked; LLM emits enums only; temperature, top_p, top_k and seed pinned; k = 3 votes must agree or the answer is NO_TRADE |
| With 3 observations the Probabilistic Sharpe Ratio cannot reach 95 % at any performance level for fat-tailed returns | Bailey & Lopez de Prado 2014 | No Sharpe, win rate or annualised return is reported. Process metrics are |
| Non-farm payrolls on Fri 2026-09-04 08:30 ET; ISM services Thu 10:00 ET; Broadcom earnings Wed after close | BLS, ISM, company IR | Friday is a logged NO_TRADE day; Thursday entries after 10:15 ET; no single-name earnings trades |

## Architecture

```
Alpaca data (alpaca-py) + Cboe VIX/VIX3M/VIX1D + Alpaca news
        |
        v
Regime module (LLM, Featherless)  -->  enums only: VOL_REGIME, TREND, EVENT_RISK, FAMILY, VETO
        |
        v
Strategy module (code): implied move from the ATM straddle -> symmetric condor -> Greeks -> cost model
        |
        v
Sizing (code): 2 % / 6 % max-loss budget, Grossman-Zhou taper, VIX/VIX3M and VIX1D multipliers
        |
        v
Gate engine (code): 30 gates from SEC 15c3-5, MiFID II RTS 6, FINRA 15-09, Knight Capital
        |
        v
Critic (LLM): PASS / REDUCE / BLOCK, never enlarge
        |
        v
Execution (code): mleg limit-order ladder in ticks -> book -> reconciliation -> flatten by 15:15 ET
        |
        v
Audit log (JSONL) -> journal (LLM prose from facts) -> post-session report -> determinism + leakage audits
```

* **Alpaca Trading API** (alpaca-py): account, clock, option chain snapshots with Greeks, multi-leg orders, positions.
* **Alpaca CLI**: `scripts/status.sh` is the independent monitoring and reconciliation path (JSON output to `logs/`).
* **Alpaca MCP server**: used by the operator (Claude Code) to inspect the account and chains during development and in the demo.
* **Featherless.ai**: open-weight models (`deepseek-ai/DeepSeek-V3.2` for regime and critic, `Qwen/Qwen3-30B-A3B-Instruct-2507` for the journal) through the OpenAI-compatible endpoint.

## Run

```bash
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt   # Windows; use bin/ on Unix
cp .env.example .env        # fill in paper keys and the Featherless key; never commit .env
.venv/Scripts/python -m pytest -q             # 17 tests incl. a fake end-to-end cycle
AGENT_DRY_RUN=true .venv/Scripts/python -m agent.main   # logs would-be orders without sending
.venv/Scripts/python -m agent.main            # live paper loop
python scripts/kill.py --flatten              # kill switch: cancel all, flag, flatten with limit orders
python scripts/report.py --session 2026-09-02 --out docs/report_2026-09-02.md
python scripts/determinism_check.py --k 5     # replay the last regime prompt, entropy in bits
python scripts/leakage_audit.py               # masked vs unmasked decision, re-identification rate
```

Paper trading is enforced: the agent refuses to start unless `ALPACA_PAPER_TRADE=true`.

## Repository map

* `config/` risk limits (immutable at runtime), strategy parameters, event calendar
* `agent/core` models, clock, config, strategy, sizing; `agent/gates` the gate engine; `agent/llm` provider, anonymiser, regime, critic, journal; `agent/execution` orders, flatten, reconciliation; `agent/reporting` audit log
* `scripts/` kill, flatten, status (CLI), report, determinism check, leakage audit
* `research/` five literature reports, two source-reading reports, and the synthesis with a 50-entry bibliography
* `docs/` incident runbook, session reports, write-up

## License

MIT.

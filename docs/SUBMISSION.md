# Submission text (lablab.ai form)

**Title:** Delphi: the Conformal Risk Control Condor on Alpaca

**Short description (one line):** An options agent whose every trade carries a finite-sample lower bound on its expected
payoff, from two numbers you can check: the market's price of the interval and its certified cost.

**Description:**

An iron condor is a bet that the close stays inside an interval. Delphi builds that interval with conformal risk
control (Angelopoulos et al., ICLR 2024): from the last 250 sessions of SPY moves in implied-volatility units it
computes the smallest radius at which the expected payout to the buyer is certified, in finite samples, to be at most
10 % of the wing. It then reads the market's price of the same interval off the quote (credit / wing, the risk-neutral
probability of finishing outside, Breeden-Litzenberger 1978) and sells only if the market pays at least 5 points more than
the certified cost. That gate is one line with no free parameter, and by a three-line theorem it implies an expected
payoff of at least 5 % of the wing per package under exchangeability of the scores (docs/THEORY.md). After every session,
traded or not, the level adapts online (Rolling Risk Control, TMLR 2023) and may only tighten; a deterministic bound
holds even if the distribution drifts. On 618 historical sessions the realised payout ratio is 0.079 against the 0.10
certificate in every year (0.070 / 0.079 / 0.090), while the fixed strike rule most agents use drifts 0.119 / 0.113 / 0.073.
Nothing in the 66 submissions we read, and to our knowledge nothing in the literature, sets option strikes by conformal
risk control or trades a calibrated interval against its market price; the nearest work (Bastos 2024) puts conformal bands
around option prices without a trading rule.

Around that core sits the part every serious entry has, done thoroughly: open-weight LLMs on Featherless.ai return enums
only (regime, event risk, veto) from anonymised headlines, three votes must agree, a critic may PASS, REDUCE or BLOCK and
never enlarge; a test proves the order is byte-identical across different LLM outputs. Thirty-one gates derived from
SEC 15c3-5, MiFID II RTS 6, FINRA 15-09 and the Knight Capital order; mleg limit orders walked in ticks, never market
orders; flat by 15:15 ET; kill switch, daily loss kill, reconciliation each cycle, append-only audit log with git and
config hashes. A logistic regime model trained on 9,230 sessions can only shrink size, and its negative results are
disclosed: worse than a constant on the live horizon, and neither XGBoost nor two 2025/26 tabular foundation models
(TabPFN v2, TabICL v2) beat it where inference is possible (21 configurations reported).

What we report, per session and even with zero fills: the P-versus-Q ledger (credit/wing, certified payout, gap,
decision, and what the fixed rule would have done), gate rejections, fill rung and slippage, LLM entropy and latency,
and the alpha/beta updates after the close. `python scripts/reproduce.py` regenerates every number in the write-up and
prints MATCH or MISMATCH. Not reported, on purpose: Sharpe, win rate, annualised return; with 2.5 sessions the
Probabilistic Sharpe Ratio cannot reach 95 %. We do not claim a statistically detectable edge. We claim a certified
bound, a risk process that behaved exactly as specified, and a ledger anyone can check.

**Alpaca infrastructure:** Trading API via alpaca-py (chains, mleg orders, positions, IEX bars for the calibration
scores); Alpaca CLI as the independent monitoring and reconciliation path; Alpaca MCP server for operator inspection.
Paper trading enforced at start-up. Paper account ID: PA314NYH4H7G.

**Tags:** Alpaca, Featherless, Options Alpha Agents, Claude Code, DeepSeek, Qwen.

**Links:** GitHub (MIT), one-page write-up (docs/WRITEUP.md), theory note (docs/THEORY.md), dashboard and ledger
(docs/index.html, docs/ledger.json), video.

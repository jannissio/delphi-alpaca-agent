# Delphi: slide outline (10 slides, 3-minute video)

Cover image: team_cover/Delphi_*.jpg. Tone: calm, evidence first, no hype. Every number on a slide
has a source in `research/` or in `state/audit.jsonl`.

1. **Title.** Delphi: an evidence-based 0DTE options agent on Alpaca. One line: "We do not claim a
   statistically detectable edge. We claim a risk process that behaved exactly as specified, and one idea
   we can defend line by line."
2. **The honest premise.** Over 2.5 sessions, options P&L is noise: variance risk premium ~2-3 % a year
   (Carr & Wu 2009); 0DTE condor mean ~0 after costs, 45 % losing days (Vilkov 2026); with three
   observations the Probabilistic Sharpe Ratio cannot reach 95 % for fat tails (Bailey & Lopez de Prado).
   So we optimise what the judges can actually verify: process, technology, explanation.
3. **What we trade and why: the Conformal Condor.** A condor's short strikes are a prediction interval for the
   close. We build it by split conformal prediction on |move| / implied move (coverage 80 % by construction,
   adaptive alpha after every session, Gibbs & Candes 2021), read the market's price of the same interval off
   the quote (credit / wing = risk-neutral probability of finishing outside, Breeden & Litzenberger 1978), and
   sell only when the market pays more than the calibration says it is worth, by a 5-point cost margin. One
   line, no free parameter. Wings max($3, 0.5 % of spot), always bought. Windows Wed/Thu mornings; Friday
   NO_TRADE (NFP 08:30 ET). Flat by 15:15 ET. The pilot day (Wed) ran the fixed 1.10x rule; it stays as the
   logged counterfactual.
4. **Trained on history, allowed only to brake, and honest about it.** 9,230 sessions (S&P 500 since 1975,
   VIX since 1990, SPY open/close from 2020-07, 30-minute bars from 2024). Logistic regime model,
   expanding-window validation; multiplier 1 / 0.5 / 0. Negative results on the slide: on the live 10:30
   horizon the logit is worse than a constant (two year-blocks, no inference); XGBoost, LightGBM and two
   2025/26 tabular foundation models (TabPFN v2, TabICL v2) tested under the same protocol, none beats twelve
   coefficients where there is power; 21 configurations disclosed. Conformal back-fill: coverage 0.806 over
   618 sessions vs the 0.80 target, by year 0.83 / 0.80 / 0.78 while the fixed rule drifts 0.77 / 0.79 / 0.86.
   Random-entry Monte Carlo null for the campaign: median +259, P05 -503 dollars.
5. **The LLM decides categories, code decides numbers.** Regime enums, veto, critic PASS/REDUCE/BLOCK,
   journal. Tickers and dates masked (Glasserman & Lin). Three votes must agree, otherwise NO_TRADE.
   Live example from 2026-09-02: 11-hour-old geopolitical headlines produced a 2:1 split, the unanimity
   rule turned it into NO_TRADE; with headline ages in the prompt the vote became 3:0 for the condor.
   Sampling pinned on four parameters; measured decision entropy in bits (Koviazin et al. 2026).
6. **Thirty-one risk gates.** From SEC Rule 15c3-5, MiFID II RTS 6, FINRA 15-09, Knight Capital, plus the
   coverage gate. Show the gate ledger from the dashboard: every candidate, every gate, pass/reject counts.
   Kill switch under five seconds, daily loss kill on an independent path, reconciliation each cycle.
7. **Execution in ticks.** SEC data (Fu, Li & Musto): 0DTE spreads are one or two ticks; percent collars
   veto everything. Ladder mid, -1, -2 ticks, natural; fill rung reported. Alpaca mleg sign convention
   (negative limit = credit) verified against the API reference, not the tutorial.
8. **Alpaca infrastructure.** Trading API (alpaca-py): chains, mleg orders, positions, IEX bars for the
   conformal scores. CLI: independent monitoring and reconciliation path. MCP server: operator inspection
   in Claude Code. Paper trading enforced at start-up. Screenshot of `scripts/status.sh` and the MCP tool list.
9. **What happened.** The P-versus-Q ledger per session (alpha_t, k, strikes, Q_mid, P_mid, gap, decision,
   and what the fixed rule would have done): the one evaluation object that needs no statistical power.
   Then positions, fills, slippage vs mid, gate rejections and NO_TRADE reasons, P&L vs SPY over the same
   hours, percentile in the Monte Carlo null, determinism replay and leakage audit numbers. (Filled Friday.)
10. **What we would do with a month.** Options history so that Q can be back-tested against P; the
    10:30 series extended to 2018 so the foundation-model comparison gets six year-blocks; term-structure
    event variance as a gate input; k=5 votes; a second underlying only if the VRP survives bid prices.

## Video script (3 minutes)

0:00 Title + premise (slides 1-2, 30 s).
0:30 The Conformal Condor in one picture: interval, market price, gate (slide 3, 40 s).
1:10 History model and the negative results (slide 4, 30 s) with the back-fill table on screen.
1:40 Live demo: dashboard with the P-vs-Q ledger, an audit-log excerpt with a full cycle (interval, regime
     votes, gates incl. gate 31, critic, ladder, fill), then `scripts/status.sh` and one MCP call (55 s).
2:35 Results slide with the honest framing (15 s).
2:50 Close: repo, write-up, "risk process that behaved exactly as specified" (10 s).

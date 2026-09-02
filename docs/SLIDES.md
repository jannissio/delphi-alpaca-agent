# Delphi: slide outline (10 slides, 3-minute video)

Cover image: team_cover/Delphi_*.jpg. Tone: calm, evidence first, no hype. Every number on a slide
has a source in `research/` or in `state/audit.jsonl`.

1. **Title.** Delphi: an evidence-based 0DTE options agent on Alpaca. One line: "We do not claim a
   statistically detectable edge. We claim a risk process that behaved exactly as specified."
2. **The honest premise.** Over 2.5 sessions, options P&L is noise: variance risk premium ~2-3 % a year
   (Carr & Wu 2009); 0DTE condor mean ~0 after costs, 45 % losing days (Vilkov 2026); with three
   observations the Probabilistic Sharpe Ratio cannot reach 95 % for fat tails (Bailey & Lopez de Prado).
   So we optimise what the judges can actually verify: process, technology, explanation.
3. **What we trade and why.** Symmetric 0DTE SPY iron condor, shorts at 1.10x the straddle-implied
   remaining move, wings max($3, 0.5 % of spot), always bought. Sourced strike geometry (Vilkov: Sharpe
   rises with distance; put side was the richer sale). Windows Wed/Thu mornings; Friday NO_TRADE because
   of non-farm payrolls at 08:30 ET. Flat by 15:15 ET.
4. **Trained on history, allowed only to brake.** 9,230 sessions (S&P 500 since 1975, VIX since 1990,
   SPY intraday since 2018/2024). Logistic regime model, expanding-window validation, out-of-sample
   terciles monotone in condor P&L (-33 / -15 / -4 $ per contract on the proxy horizon; +21 / +28 / +35 on
   the exact 10:30-to-close horizon). Multiplier 1 / 0.5 / 0. Random-entry Monte Carlo null for the
   campaign: median +259, P05 -503 dollars.
5. **The LLM decides categories, code decides numbers.** Regime enums, veto, critic PASS/REDUCE/BLOCK,
   journal. Tickers and dates masked (Glasserman & Lin). Three votes must agree, otherwise NO_TRADE.
   Live example from 2026-09-02: 11-hour-old geopolitical headlines produced a 2:1 split, the unanimity
   rule turned it into NO_TRADE; with headline ages in the prompt the vote became 3:0 for the condor.
   Sampling pinned on four parameters; measured decision entropy in bits (Koviazin et al. 2026).
6. **Thirty risk gates.** From SEC Rule 15c3-5, MiFID II RTS 6, FINRA 15-09, Knight Capital. Show the
   gate ledger from the dashboard: every candidate, every gate, pass/reject counts. Kill switch under
   five seconds, daily loss kill on an independent path, reconciliation each cycle.
7. **Execution in ticks.** SEC data (Fu, Li & Musto): 0DTE spreads are one or two ticks; percent collars
   veto everything. Ladder mid, -1, -2 ticks, natural; fill rung reported. Alpaca mleg sign convention
   (negative limit = credit) verified against the API reference, not the tutorial.
8. **Alpaca infrastructure.** Trading API (alpaca-py): chains with Greeks, mleg orders, positions.
   CLI: independent monitoring and reconciliation path. MCP server: operator inspection in Claude Code.
   Paper trading enforced at start-up. Screenshot of `scripts/status.sh` and the MCP tool list.
9. **What happened.** Sessions, positions, fills, slippage vs mid, gate rejections and NO_TRADE reasons,
   P&L vs SPY over the same hours, percentile in the Monte Carlo null. Determinism replay and leakage
   audit numbers. (Filled Friday morning.)
10. **What we would do with a month.** Options history for a real credit model; term-structure event
    variance as a gate input; k=5 votes; second underlying only if the VRP survives bid prices.

## Video script (3 minutes)

0:00 Title + premise (slides 1-2, 35 s).
0:35 Strategy and history model (slides 3-4, 45 s) with the regime report table on screen.
1:20 Live demo: dashboard, an audit-log excerpt with a full cycle (regime votes, gates, critic, ladder,
     fill), then `scripts/status.sh` and one MCP call in Claude Code (60 s).
2:20 Results slide with the honest framing (25 s).
2:45 Close: repo, write-up, "risk process that behaved exactly as specified" (15 s).

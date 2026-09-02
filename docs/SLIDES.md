# Delphi: slide outline (10 slides, 3-minute video)

Cover image: team_cover/Delphi_*.jpg. Tone: calm, evidence first, no hype. Every number on a slide
has a source in `research/` or in `state/audit.jsonl`.

1. **Title.** Delphi: an evidence-based 0DTE options agent on Alpaca. One line: "We do not claim a
   statistically detectable edge. We claim a risk process that behaved exactly as specified, and one idea
   we can defend line by line."
2. **The honest premise.** Over 2.5 sessions, options P&L is noise: the index variance risk premium is ~2-3 % a
   year and "over the past 15 years, option alphas have become indistinguishable from zero" (Dew-Becker & Giglio
   2025); Vilkov's 0DTE study, after the author's own 2026-08 cost correction, finds no structure with a materially
   positive net Sharpe (condor bucket -2.67); the measurable premium is overnight and we never hold overnight
   (Muravyev & Ni 2020); three perfect sessions cannot push an anytime-valid p-value below 0.51. So we optimise
   what the judges can actually verify: a certificate per trade, process, technology, explanation.
3. **What we trade and why: the Conformal Risk Control Condor.** A condor's payout to its buyer is a bounded loss
   that falls with the interval's radius. Conformal risk control (ICLR 2024) gives the smallest radius at which
   the expected payout is certified, in finite samples, to be at most 10 % of the wing. The market's price of the
   same interval is credit / wing (Breeden & Litzenberger 1978). Sell only if the market pays 0.10 + 0.05, and
   the theorem says: certified, in expectation, not to lose after the modelled cost. One line, no free parameter;
   the online level (TMLR 2023) may only tighten. Wings max($3, 0.5 % of spot), always bought. Windows Wed/Thu
   mornings; Friday NO_TRADE (NFP 08:30 ET). Flat by 15:15 ET. The pilot day (Wed) ran the fixed 1.10x rule;
   it stays as the logged counterfactual. Show the three-line proof on the slide.
4. **Trained on history, allowed only to brake, and honest about it.** 9,230 sessions (S&P 500 since 1975,
   VIX since 1990, SPY open/close from 2020-07, 30-minute bars from 2024). Logistic regime model,
   expanding-window validation; multiplier 1 / 0.5 / 0. Negative results on the slide: on the live 10:30
   horizon the logit is worse than a constant (two year-blocks, no inference); XGBoost, LightGBM and two
   2025/26 tabular foundation models (TabPFN v2, TabICL v2) tested under the same protocol, none beats twelve
   coefficients where there is power; 21 configurations disclosed. Back-fill of the certified radius: realised payout ratio 0.079
   over 618 sessions vs the 0.10 certificate, by year 0.070 / 0.079 / 0.090, while the fixed rule drifts
   0.119 / 0.113 / 0.073.
   Random-entry Monte Carlo null for the campaign: median +259, P05 -503 dollars.
5. **The LLM decides categories, code decides numbers.** Regime enums, veto, critic PASS/REDUCE/BLOCK,
   journal. Tickers and dates masked (Glasserman & Lin). Three votes must agree, otherwise NO_TRADE: an
   abstention filter, not an ensemble (majority voting beats the best member in under 10 % of size-3 sets).
   Live example from 2026-09-02: 11-hour-old geopolitical headlines produced a 2:1 split, the unanimity
   rule turned it into NO_TRADE; with headline ages in the prompt the vote became 3:0 for the condor.
   Sampling pinned on four parameters; measured decision entropy in bits (Koviazin et al. 2026).
6. **Thirty-one risk gates.** From SEC Rule 15c3-5, MiFID II RTS 6, FINRA 15-09, Knight Capital, plus the
   coverage gate. Show the gate ledger from the dashboard: every candidate, every gate, pass/reject counts.
   Kill switch under five seconds, daily loss kill on an independent path, reconciliation each cycle.
7. **Execution in ticks, and what the pilot taught.** SEC data (Fu, Li & Musto): 0DTE spreads are one or two
   ticks; percent collars veto everything. Alpaca paper fills only marketable orders: on the pilot day a ladder
   fixed at the decision chased a credit that fell 0.47 -> 0.39 in 60 s and missed; now every rung is re-quoted
   and reaches the live natural inside 60 s, and no rung sells below the gated floor. Alpaca mleg sign convention
   (negative limit = credit) verified against the API reference, not the tutorial. A dated table of every
   parameter changed after the first live cycle is in the repo.
8. **Alpaca infrastructure.** Trading API (alpaca-py): chains, mleg orders, positions, IEX bars for the
   conformal scores. CLI: independent monitoring and reconciliation path. MCP server: operator inspection
   in Claude Code. Paper trading enforced at start-up. Screenshot of `scripts/status.sh` and the MCP tool list.
9. **What happened.** The P-versus-Q ledger per session (beta*, k, strikes, credit/wing at the fill, empirical
   payout, gap, decision, and what the fixed rule would have done): the one evaluation object that needs no
   statistical power. Next to it the two e-processes and the evidence ceiling: "three perfect sessions cannot
   push p below 0.51; here is the arithmetic, so here is why we show no Sharpe ratio".
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

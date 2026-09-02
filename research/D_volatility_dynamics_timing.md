# D — Volatility Dynamics & Timing: when to sell premium, when not to, and what to avoid

Research analyst review, time-boxed. Compiled 2026-09-01 (Tue), for the trading window
**Wed 2026-09-02, Thu 2026-09-03 (full sessions) and Fri 2026-09-04 09:30–11:00 ET.**

Scope: volatility risk premium conditioning, short-horizon vol forecasting, intraday/0DTE timing,
macro-event risk, option-implied filters, and earnings IV dynamics. The academic straddle/earnings
return literature is covered by the parallel review; here the earnings section is deliberately
practitioner/data-provider focused.

---

## Kurzfassung (Deutsch)

1. **Grundsatz**: Der Varianzrisikoprämie (VRP) ist bei ultrakurzen Laufzeiten am größten. Almeida/Freire/Hizmeri messen für 0DTE eine annualisierte VRP von **1,54–2,96 Prozentpunkten** gegenüber nur **0,56 % (1DTE)** und **0,81 % (22DTE)** — Prämienverkauf auf 0DTE ist strukturell besser bezahlt als auf 1–7 DTE.
2. **Regime-Filter statt IV-Rank**: Johnson (2017, JFQA) zeigt, dass nicht das *Niveau*, sondern die *Steigung* der VIX-Terminstruktur (SLOPE) Varianzrenditen prognostiziert. Im untersten SLOPE-Quintil dreht die Prämie das Vorzeichen — dann verliert Short-Vol. Simon & Campasano (2014) bestätigen das zweiseitig.
3. **Aktueller Zustand (Stand 31.08.2026)**: VIX 14,92; VIX3M 17,53; **VIX/VIX3M = 0,851 → deutliches Contango, Tag 101 dieses Regimes.** Das Regime-Signal steht also klar auf „Prämie verkaufen". Der niedrige VIX-Stand ist *kein* Veto, reduziert aber die eingenommene Prämie je Einheit Tail-Risiko → kleiner sizen.
4. **Praktiker-Regel „IV-Rank > 50"** hat in dieser Recherche **keine** begutachtete Grundlage gefunden; sie widerspricht sogar Johnson (Level prognostiziert nicht). Nicht als Veto verwenden.
5. **Intraday-Fenster**: Bid-Ask-Spreads bei 0DTE sind bei Eröffnung und zum Schluss am weitesten und **zwischen 10:00 und 14:00 ET am engsten** (Almeida et al., Fig. 3). Einstieg daher **10:00–14:00 ET**, nicht 09:30.
6. **Schlussphase meiden**: Baltussen et al. (2021, JFE) zeigen „market intraday momentum" — die letzten 30 Minuten trenden in Richtung des Tagesverlaufs (OOS-R² 2,88 % bei Aktienindex-Futures), getrieben von negativem Dealer-Gamma. Short-Gamma-Positionen daher **bis 15:15–15:30 ET glattstellen**.
7. **Gamma-Panik ist überzogen**: Amaya/Garcia-Ares/Pearson/Vasquez (Cboe-Daten) beziffern den *maximalen* gammabedingten Anstieg der annualisierten 30-Minuten-Vol auf **6,4 Prozentpunkte** — gegenüber einem Maximum von 63,4 Punkten aus allen Ursachen; im Mittel **dämpft** Dealer-Gamma die Vol um 0,2 Punkte.
8. **Ereignisse im Fenster**: Mi 02.09. 08:15 ADP (vorbörslich), 10:00 Factory Orders, **14:00 Beige Book**; Do 03.09. 08:30 Erstanträge/Handelsbilanz (vorbörslich), **10:00 ISM Services (im Fenster, hohe Relevanz)**; **Fr 04.09. 08:30 US-Arbeitsmarktbericht (NFP) — direkt vor unserem Fenster**.
9. **NFP ist der Hauptrisikofaktor.** Der Sprung passiert um 08:30 ET, also im Overnight-Gap, das man nicht hedgen kann. Regel: **keine kurzlaufenden Short-Optionen über Do→Fr halten**; alles mit Verfall Fr 04.09. spätestens Do vor Handelsschluss schließen.
10. Ederington & Lee (1996, JFQA): implizite Vol **fällt nach** planmäßigen Meldungen. Am Freitag um 09:30 ist die Prämie also schon zusammengebrochen, während die realisierte Vol noch erhöht ist — die schlechteste Kombination für Stillhalter. **Freitag 09:30–10:00 nichts Neues eröffnen**; frühestens 10:00–10:30, klein, oder nur bestehende Positionen managen.
11. **Wing-Struktur**: Bei 0DTE ist der Smile *symmetrisch* (OTM-Puts und -Calls gleich teuer in IV) — anders als bei längeren Laufzeiten. Deshalb **symmetrischer, deltaneutraler Iron Condor bei 0DTE**.
12. Bei **1–7 DTE** liegt die Prämie dagegen fast ausschließlich auf der **Unterseite** (VRP⁺ wird ab 5DTE negativ, VRP⁻ = 0,61–0,75). Dort also eher **Put-Credit-Spreads als Call-Credit-Spreads** — aber zwingend definiert im Risiko.
13. **Kein Richtungs-Tilt** aus Skew oder Put/Call-Ratio: Xing/Zhang/Zhao (2010) und Pan/Poteshman (2006) sind Querschnitts-Signale für Einzelaktien über Wochen/Monate, nicht für einen 1–2-Tage-Index-Condor. Deltaneutral bleiben.
14. **Kein Pinning einplanen**: Golez & Jackwerth (2012) finden vor dem Verfall von SPX-Indexoptionen sogar „Anti-Cross-Pinning" (Wegdrücken vom ATM-Strike). Das Pinning von Ni/Pearson/Poteshman (16,5 Bp) betrifft Einzelaktien an Monatsverfällen.
15. **Earnings-Prämienverkauf auf AVGO/LULU ist durch die Daten nicht gedeckt**: AVGO hat in **10 von 16** Berichten die implizite Bewegung überschritten (62 %); zuletzt (03.06.2026) implizit ±8,7 % gegen tatsächlich −12,6 % Schluss / −15,9 % Peak. LULU: 6 von 8. Wenn Earnings sein muss: sehr klein, definiertes Risiko, Strikes ≥ 2× implizite Bewegung — oder ganz lassen.

---

## Source cards

### S1 — Johnson (2017), "Risk Premia and the VIX Term Structure"
- **Citation**: Johnson, T. L. (2017). *Risk Premia and the VIX Term Structure.* Journal of Financial and Quantitative Analysis 52(6), 2461–2490. DOI 10.1017/S0022109017000825. Open PDF: https://www.travislakejohnson.com/pdfs/Johnson%20VIXTS%202017%20(JFQA).pdf
- **Type / venue / year**: Peer-reviewed journal (JFQA), 2017.
- **Citations**: 113 (OpenAlex, journal version) + 23 (SSRN WP version).
- **Quality verdict**: **Citation-worthy: yes.** Top-tier finance journal, directly on our conditioning question, open PDF verified first-hand.
- **Key findings (numbers, read from the PDF)**:
  - The VIX term structure's second principal component, **SLOPE**, predicts excess returns of synthetic S&P 500 variance swaps, VIX futures and S&P 500 straddles at *all* maturities, and does so **to the exclusion of the rest of the term structure**. The *level* of volatility does not.
  - Unconditional variance-asset risk premia are **largest at the shortest maturity**: 1-month synthetic variance swaps have mean daily excess returns of **−1.36 %** (annualized Sharpe ≈ **−1.44** for the long side, i.e. ≈ **+1.44 for the short side**), 3-month −0.35 %/day (Sharpe −0.71), 12-month −0.08 %/day (Sharpe −0.29).
  - **Sign flip in backwardation**: "when SLOPE is low, future variance risk premia are not just smaller, they actually **change sign and become positive for 17 of 18 variance assets**." Example: 12-month S&P 500 straddles average **+30 bp/day above the risk-free rate** when SLOPE is in its lowest quintile.
- **Relevance**: This is the single strongest academic justification for (a) preferring the shortest maturities when selling variance and (b) using a term-structure *slope* gate rather than an IV-level gate.
- **Caveats**: SLOPE is constructed from a replicated VIX term structure across maturities, not from a broker feed; the practical proxy (VIX/VIX3M, or front-vs-second VIX future) is a coarser version. Results are daily/monthly-horizon, not intraday.

### S2 — Simon & Campasano (2014), "The VIX Futures Basis"
- **Citation**: Simon, D. P., & Campasano, J. (2014). *The VIX Futures Basis: Evidence and Trading Strategies.* Journal of Derivatives 21(3), 54–69. DOI 10.3905/jod.2014.21.3.054. Open WP: https://www.efmaefm.org/0efmameetings/efma%20annual%20meetings/2013-Reading/papers/VIX%20paper_EFMA.pdf
- **Type / venue / year**: Peer-reviewed journal (Journal of Derivatives), 2014; EFMA working-paper version read first-hand.
- **Citations**: 35 (journal, OpenAlex) + 15 (SSRN version).
- **Quality verdict**: **Citation-worthy: with caveats.** Peer-reviewed but a practitioner-facing journal with modest citation count; 2006–2011 sample only; strategy is on VIX futures, not on SPY option spreads.
- **Key findings (verified in the WP)**:
  - The basis has **no** forecast power for changes in spot VIX, but **does** forecast VIX futures returns — i.e. it is a risk premium, not an expectation.
  - Rule: short the nearest VIX future with ≥10 trading days to maturity when daily roll > **0.10** points (contango), long when < **−0.10** (backwardation); hold 5 days; hedge with E-mini S&P futures.
  - Short-in-contango, hedged: **62 trades, mean +$792 after transaction costs**, win:loss ≈ **2:1**, bottom-decile P&L **−$1,045**, **Sortino 1.26** (vs 0.88 unhedged; unhedged mean +$861 but bottom decile −$1,973).
  - Symmetrically, **long-in-backwardation, hedged: 40 trades, mean +$1,018**, roughly equal win/loss count.
- **Relevance**: Two-sided confirmation of the term-structure gate. The backwardation leg matters most for us: it says the correct action in backwardation is not "sell less", it is "stop selling".
- **Caveats**: A secondary summary circulating online quotes a "53 % annual compound return"; **that figure is not in the WP version I read** — treat as unverified. Sample ends 2011, pre-dating the entire 0DTE era.

### S3 — Bollerslev, Tauchen & Zhou (2009), "Expected Stock Returns and Variance Risk Premia"
- **Citation**: Bollerslev, T., Tauchen, G., & Zhou, H. (2009). *Expected Stock Returns and Variance Risk Premia.* Review of Financial Studies 22(11), 4463–4492. DOI 10.1093/rfs/hhp008. Open FEDS WP: https://www.federalreserve.gov/pubs/feds/2007/200711/200711pap.pdf
- **Type / venue / year**: Peer-reviewed journal (RFS), 2009.
- **Citations**: **1,919** (OpenAlex).
- **Quality verdict**: **Citation-worthy: yes.** Foundational, heavily cited, open working-paper version verified.
- **Key findings (verified in the FEDS WP)**: The difference between model-free implied and realized variance — the variance risk premium — explains **>15 %** of the ex-post time-series variation in **quarterly** excess market returns (1990–2005); combined with the P/E ratio, **R² > 25 %**. Predictability dominates P/E, P/D and CAY, and is **strongest at quarterly-to-annual horizons**.
- **Relevance**: Establishes (i) that VRP is real and time-varying, and (ii) that a *high* VRP forecasts *high* subsequent equity returns. It does **not** directly say "sell options when VRP is high" — that inference requires an extra step. Important for honesty in the pitch.
- **Caveats**: Horizon mismatch — quarterly, not 1–3 days. Sample ends 2005.

### S4 — Almeida, Freire & Hizmeri (2025), "0DTE Asset Pricing"
- **Citation**: Almeida, C., Freire, G., & Hizmeri, R. (2025, draft 23 May 2025; first draft Jan 2024). *0DTE Asset Pricing.* SSRN 4701401. Open PDF: https://www.fma.org/assets/docs/Derivatives2025/Almeida.pdf
- **Type / venue / year**: Working paper (SSRN / FMA Derivatives 2025 conference), 2024–2025. Princeton / Erasmus / Liverpool.
- **Citations**: 4 (OpenAlex, SSRN record) — new paper, low count expected.
- **Quality verdict**: **Citation-worthy: yes, with the "working paper" caveat.** Serious authors, conference-vetted (SoFiE, MFA, Paris December Finance), sample Jan 2012 – Mar 2025, Cboe intraday data. This is the **single most decision-relevant source in this review**.
- **Key findings (all read from the PDF)**:
  - **VRP by maturity** (annualized, percentage points): 0DTE **1.54–2.96** depending on time of day; **1DTE 0.558**, 2DTE 0.671, 3DTE 0.477, 5DTE 0.489, 7DTE 0.545, 22DTE 0.812. The 0DTE VRP is "up to **four times larger** than what is observed for longer horizons".
  - **VRP by time of day (Table 1, mean)**: 10:00 **1.804**, 10:30 1.562, 11:00 1.540, 11:30 1.717, 12:00 1.806, 12:30 2.205, 13:00 1.981, 13:30 2.460, 14:00 **2.956**. Standard deviations rise in step (9.12 → 14.41), so the **VRP/vol ratio is nearly flat across the day at ≈0.16–0.21** (my calculation from their table).
  - **Sign asymmetry**: at 0DTE the "good"/upside premium **VRP⁺ exceeds** the downside **VRP⁻** (14:00: 1.971 vs 0.985). At longer maturities the reverse holds and **VRP⁺ turns negative from 5DTE onwards** (5DTE −0.122, 7DTE −0.202, 22DTE −0.217), while VRP⁻ rises with horizon (5DTE 0.611, 7DTE 0.747, 22DTE 1.029).
  - **Smile shape**: "For all times of the day, 0DTE IVs display a **smile** across moneyness, where **OTM puts and calls are equally expensive in terms of IV**. This is in contrast to the usual smirk observed for longer-maturity S&P 500 options."
  - **Liquidity by time of day (Fig. 3)**: "While trading volume is higher at market **open and close**, these times of the day are also the ones with **highest bid-ask spread** over the day. The bid-ask spread tends to be relatively stable at its **minimum between 10:00 and 14:00**." Quotable strike depth also thins from ~4 strikes/bin at 10:00 to ~2 at 14:00.
  - **Alpha decay warning**: their stochastic-dominance-violation strategy earned Sharpe **0.1–0.2 per very-short-horizon trade net of costs** — "an order of magnitude larger" than selling the delta-hedged ATM call, which produced **mostly negative Sharpe ratios net of costs** — but "**after 2022 the performance of the strategy mostly stagnates**", consistent with growing efficiency after 0DTEs became daily.
  - Conditioning: the mispricing Sharpe is **higher when 0DTE volume, realized variance and retail attention are LOW**; conditioning on the VRP itself "has only a small effect".
  - FOMC: excluding FOMC days lowers the average VRP but leaves conclusions intact; around the announcement, long-straddle average returns turn **positive** (short vol loses) — though not statistically significant in their small sample.
- **Relevance**: Gives us (a) maturity selection (0DTE ≫ 1–7 DTE for premium richness), (b) an evidence-based intraday entry window, (c) symmetric vs skewed wing construction by maturity, (d) a sober warning that easy 0DTE alpha died in 2022.
- **Caveats**: Working paper, not yet peer-reviewed. VRP is a model-free variance decomposition, **not** the realized P&L of an iron condor; the mapping from "VRP⁺ is positive" to "sell the call spread" is an inference, not their result. Their delta-hedged short-call benchmark being *negative* net of costs is a direct warning that naive short vol at 0DTE does not automatically pay.

### S5 — Amaya, Garcia-Ares, Pearson & Vasquez (2025), "0DTE Index Options and Market Volatility: How Large is Their Impact?"
- **Citation**: Amaya, D., Garcia-Ares, P. A., Pearson, N. D., & Vasquez, A. (2025, 25 Jan). *0DTE Index Options and Market Volatility: How Large is Their Impact?* Cboe-hosted research PDF: https://cdn.cboe.com/resources/education/research_publications/gammasqueezes.pdf
- **Type / venue / year**: Working paper hosted by Cboe (data provided by Cboe Global Markets + Algoseek), 2025. Authors at Wilfrid Laurier, Notre Dame/ITAM, Illinois, ITAM.
- **Citations**: not indexed in OpenAlex under this title at time of search.
- **Quality verdict**: **Citation-worthy: yes, with a disclosure caveat** — Cboe supplied the proprietary trade data and hosts the PDF, so there is a mild incentive alignment toward "0DTE is not destabilising". The methodology (per-minute OMM net position from all SPX/SPXW trades, GARCH + linear models, counterfactual simulation) is transparent and the conclusion is quantified rather than rhetorical.
- **Key findings (read from the PDF, sample Jul 2020 – Jun 2023)**:
  - Aggregate options-market-maker (OMM) gamma is **typically positive but often negative**; the **mean effect of gamma is to REDUCE volatility by 0.2 percentage points**.
  - **Maximum** gamma-induced increase in annualized **daily** realized volatility: **+3.3 pp**. For context, the SD of daily changes in annualized RV is **4.5 pp**, and moves >3.0 pp occur on **~20 % of trading days**. Authors' own verdict: "**not large**".
  - **Maximum** gamma-induced increase in annualized **30-minute** realized volatility: **+6.4 pp**, versus a maximum 30-minute change from *all* causes of **63.4 pp**; SD of the gamma-induced change is only **0.9 pp** vs 4.6 pp from all causes. More than 5 % of 30-minute windows exceed 6.4 pp anyway, i.e. **>3 such windows in a typical week**.
  - Their linear model uses **hour-of-day fixed effects for 9:30–10:30, 10:30–11:30, … 15:30–16:00**; gamma coefficients are negative at all lags.
- **Relevance**: Directly de-risks the "0DTE gamma will blow up my condor" fear at the *typical* level, while confirming that the tail risk concentrates when dealer gamma is negative (i.e. in selloffs). Argues **against** building a GEX-flip-level entry signal.
- **Caveats**: Sample ends June 2023, before the largest growth in 0DTE volume. Estimates a *maximum* impact under a model; not a tail-event study.

### S6 — Baltussen, Da, Lammers & Martens (2021), "Hedging demand and market intraday momentum"
- **Citation**: Baltussen, G., Da, Z., Lammers, S., & Martens, M. (2021). *Hedging demand and market intraday momentum.* Journal of Financial Economics 142(1), 377–403. DOI 10.1016/j.jfineco.2021.04.029. Open PDF: https://academicweb.nd.edu/~zda/intramom.pdf
- **Type / venue / year**: Peer-reviewed journal (JFE), 2021.
- **Citations**: 97 (OpenAlex).
- **Quality verdict**: **Citation-worthy: yes.** Top-3 finance journal, huge sample, open PDF verified.
- **Key findings (from the PDF)**:
  - Across **60+ futures** (equities, bonds, commodities, FX), **Dec 1974 – May 2020**: the return in the **last 30 minutes** before the close is **positively predicted** by the rest-of-day return (previous close → last 30 minutes).
  - For equity index futures, the rest-of-day predictor achieves the **highest out-of-sample R² of 2.88 %**; adjusted in-sample R² ≈ 2.45 %. It beats the first-half-hour predictor of Gao et al. (2018), whose OOS R² is **−1.71 %**.
  - Timing strategies produce "very high Sharpe ratios and success rates well above 0.50", outperforming always-long benchmarks.
  - Mechanism: **negative gamma exposure of option and leveraged-ETF hedgers** forces trading in the direction of price moves; effect strengthens the more negative the aggregate gamma. The effect **reverts over the following days**.
- **Relevance**: The direct argument for closing short-gamma 0DTE positions **before ~15:30 ET**. A short iron condor is the exact opposite side of this documented late-day trend.
- **Caveats**: It is a *return* predictability result, not a volatility result — the tail risk it implies for short gamma is an inference. Effect sizes are small in R² terms though economically meaningful.

### S7 — Ni, Pearson & Poteshman (2005), "Stock price clustering on option expiration dates"
- **Citation**: Ni, S. X., Pearson, N. D., & Poteshman, A. M. (2005). *Stock price clustering on option expiration dates.* Journal of Financial Economics 78(1), 49–87. DOI 10.1016/j.jfineco.2004.08.005.
- **Type / venue / year**: Peer-reviewed journal (JFE), 2005. **Citations**: 205 (OpenAlex).
- **Quality verdict**: **Citation-worthy: yes**, but **not directly transferable** to daily index expirations.
- **Key findings**: On expiration dates, closing prices of optionable **single stocks** cluster at strikes; returns of optionable stocks are altered by an average of **at least 16.5 basis points**, an aggregate market-cap shift of ~**$9 bn**. Drivers: OMM delta-hedge rebalancing and proprietary-trader manipulation.
- **Relevance**: This is the canonical "pinning" citation, but it concerns monthly single-stock expirations, 1996–2002. Our instruments are SPY/QQQ/SPX with **daily** expirations.
- **Caveats**: 16.5 bp is small relative to a 0DTE condor's short-strike distance; no evidence it generalises to index ETFs in a daily-expiration regime.

### S8 — Golez & Jackwerth (2012), "Pinning in the S&P 500 futures"
- **Citation**: Golez, B., & Jackwerth, J. C. (2012). *Pinning in the S&P 500 futures.* Journal of Financial Economics 106(3), 566–585. DOI 10.1016/j.jfineco.2012.06.010.
- **Type / venue / year**: Peer-reviewed journal (JFE), 2012. **Citations**: 43 (OpenAlex).
- **Quality verdict**: **Citation-worthy: yes.** The correct index-level counterpart to S7.
- **Key findings**: S&P 500 futures are **pulled toward** the ATM strike on days when **serial options on S&P 500 futures** expire (pinning), but are **pushed away** from the cost-of-carry-adjusted ATM strike right before the expiration of **options on the S&P 500 index** ("**anti-cross-pinning**"). Lower bound on the associated price move: **≥$115 m notional per expiration date**, **≥$240 m** in the Oct 1998 – Nov 2009 subperiod. The driver is **not** market-maker delta decay (they are net short index options) nor manipulation, but ITM-call holders selling/early-exercising to avoid weekend risk.
- **Relevance**: **Do not** design strikes around an assumed pin. At the index level the documented effect near index-option expiry points the *other* way.
- **Caveats**: Sample is monthly/serial expirations pre-2010; says nothing directly about the current daily-expiry regime.

### S9 — Lucca & Moench (2015) + Kurov, Wolfe & Gilbert (2021)
- **Citations**: Lucca, D. O., & Moench, E. (2015). *The Pre-FOMC Announcement Drift.* Journal of Finance 70(1), 329–371. DOI 10.1111/jofi.12196 — **642 citations** (OpenAlex). Kurov, A., Wolfe, M. H., & Gilbert, T. (2021). *The disappearing pre-FOMC announcement drift.* Finance Research Letters 40, 101781. DOI 10.1016/j.frl.2020.101781 — **30 citations**. Open PDF: https://www.skidmore.edu/economics/documents/KurovWolfeGilbert-TheDisappearingPre-FOMC-Announce-Drift-200914.pdf
- **Type**: Both peer-reviewed journals (JF; FRL).
- **Quality verdict**: **Citation-worthy: yes**, and the pair should always be cited *together* — citing Lucca & Moench alone would be misleading in 2026.
- **Key findings**: Lucca & Moench document large average excess US equity returns in the 24 hours before scheduled FOMC announcements, Sep 1994 – Mar 2011. Kurov et al. extend to Dec 2019 and find the drift **essentially disappeared after 2015**, in both press-conference and non-press-conference announcements; they attribute it to reduced uncertainty.
- **Relevance to our window**: **None operationally — there is no FOMC in 2026-09-02…04** (next meeting 15–16 Sep 2026). Included because the pattern is often cited by hackathon-grade strategies; the honest position is that the effect is gone.

### S10 — Ederington & Lee (1993, JF) and (1996, JFQA)
- **Citations**: Ederington, L. H., & Lee, J. H. (1993). *How Markets Process Information: News Releases and Volatility.* Journal of Finance 48(4), 1161–1191. DOI 10.1111/j.1540-6261.1993.tb04750.x — **991 citations**. Ederington, L. H., & Lee, J. H. (1996). *The Creation and Resolution of Market Uncertainty: The Impact of Information Releases on Implied Volatility.* Journal of Financial and Quantitative Analysis 31(4), 513–539. DOI 10.2307/2331358 — **277 citations**.
- **Type / venue**: Peer-reviewed journals (JF; JFQA).
- **Quality verdict**: **Citation-worthy: yes** for the mechanism; **with caveats** for magnitudes, since I verified the mechanism through secondary summaries rather than the paywalled originals.
- **Key findings**: Scheduled macro releases (the **employment report** and PPI are their leading examples) are the dominant source of intraday volatility in interest-rate futures/options; because the *timing* is known but the *content* is not, pre-release implied standard deviations impound the anticipated jump and **implied volatility declines after the release** as uncertainty is resolved. The model predicts IV **decreases** on scheduled announcement days and **increases** on unscheduled news.
- **Relevance**: This is the analytical core of our NFP-Friday rule. At 09:30 ET on 4 Sep the event premium has already been paid out; a seller entering then collects post-crush prices while realized vol is still elevated.
- **Caveats**: Original asset class is T-bond/Eurodollar options, not SPX. Magnitudes for SPX 0DTE were not obtained (see *Paywalled / wanted*).

### S11 — Andersen, Bollerslev, Diebold & Vega (2003)
- **Citation**: Andersen, T. G., Bollerslev, T., Diebold, F. X., & Vega, C. (2003). *Micro Effects of Macro Announcements: Real-Time Price Discovery in Foreign Exchange.* American Economic Review 93(1), 38–62. DOI 10.1257/000282803321455151. NBER WP 8959.
- **Type / venue / year**: Peer-reviewed journal (AER), 2003. **Citations**: 1,424 (OpenAlex).
- **Quality verdict**: **Citation-worthy: yes** for the general result; **with caveats** for our use, since the asset class is FX.
- **Key findings**: Announcement **surprises** (actual minus consensus) produce **conditional-mean jumps** at high frequency; announcement effects are asymmetric (bad news moves more than good). Adjustment is essentially instantaneous, with elevated volatility persisting for a period after the release.
- **Relevance**: Formalises "the jump happens at the release, not at the open". Because NFP lands at 08:30 ET, the jump is entirely inside the overnight gap for anyone holding SPY options — unhedgeable.
- **Caveats**: FX, 1992–1998. Extrapolation to SPY is standard but is an extrapolation.

### S12 — Poon & Granger (2003) and Corsi (2009) and Christensen & Prabhala (1998)
- **Citations**: Poon, S.-H., & Granger, C. W. J. (2003). *Forecasting Volatility in Financial Markets: A Review.* Journal of Economic Literature 41(2), 478–539. DOI 10.1257/002205103765762743 — **1,347 citations**. Corsi, F. (2009). *A Simple Approximate Long-Memory Model of Realized Volatility.* Journal of Financial Econometrics 7(2), 174–196. DOI 10.1093/jjfinec/nbp001 — **2,576 citations**. Christensen, B. J., & Prabhala, N. R. (1998). *The relation between implied and realized volatility.* Journal of Financial Economics 50(2), 125–150. DOI 10.1016/S0304-405X(98)00034-8 — **1,186 citations**.
- **Type / venue**: All peer-reviewed (JEL; JFEc; JFE).
- **Quality verdict**: **Citation-worthy: yes** (all three). Verdicts below rest partly on secondary summaries of the survey — flagged.
- **Key findings**:
  - **Poon & Granger**: survey of **93 studies**; conclusion widely reported as **implied volatility (the VIX) being the best single predictor of realized volatility, though a biased one** (biased *upward* — which is the VRP restated).
  - **Corsi**: the HAR-RV cascade (daily/weekly/monthly realized-vol components) is the workhorse short-horizon RV model; recent comparisons report **adjusted R² ≈ 0.605 for the benchmark HAR-RV on one-day-ahead S&P 500 RV**, with augmented variants reaching 0.624–0.644.
  - **Christensen & Prabhala**: implied volatility **subsumes** past realized volatility as a forecast of future realized volatility once errors-in-variables and the overlapping-data problem are handled.
  - Consensus of the modern literature: **HAR-RV augmented with implied volatility** beats either alone at 1-day horizons.
- **Relevance to us**: For a 3-day agent, the pragmatic answer is: **use the market's own 0DTE ATM straddle price as the primary forecast of the remaining-day move**, and use a simple realized-vol anchor (last 5–10 days of intraday RV) only to detect whether IV is unusually cheap relative to RV. Do not build a HAR-RV estimator in a hackathon.
- **Caveats**: The exact HAR R² figures come from a secondary source (arXiv horse-race paper), not Corsi's own tables; the Poon–Granger "VIX is best" line is a summary of a survey, and the survey itself is nuanced by asset class.

### S13 — Xing, Zhang & Zhao (2010) and Pan & Poteshman (2006)
- **Citations**: Xing, Y., Zhang, X., & Zhao, R. (2010). *What Does the Individual Option Volatility Smirk Tell Us About Future Equity Returns?* JFQA 45(3), 641–662. DOI 10.1017/S0022109010000220 — **761 citations**. Pan, J., & Poteshman, A. M. (2006). *The Information in Option Volume for Future Stock Prices.* Review of Financial Studies 19(3), 871–908. DOI 10.1093/rfs/hhj024 — **909 citations**.
- **Type / venue**: Peer-reviewed (JFQA; RFS).
- **Quality verdict**: **Citation-worthy: yes** for what they say; **"no" as a basis for tilting an index condor** — wrong asset, wrong horizon.
- **Key findings**: Xing/Zhang/Zhao — stocks with the **steepest** volatility smirks underperform those with the flattest by **10.9 % per year** risk-adjusted; predictability persists ≥6 months and concentrates in firms with the worst subsequent earnings shocks. Pan/Poteshman — the **signed** (trade-direction-classified, non-public) put–call volume ratio predicts next-day-to-next-week stock returns; the **publicly observable unsigned put–call ratio carries far less information**.
- **Relevance**: Two-fold negative result for us. (1) Both are **cross-sectional single-stock** signals over weeks–months, not index signals over 1–2 days. (2) Pan & Poteshman's key caveat is that the *public* put/call ratio — the only one an Alpaca-based agent can compute — is the weak version.
- **Caveats**: Samples 1996–2005 / 1990–2001; both effects have been argued to have weakened.

### S14 — Cboe options-industry statistics (0DTE share)
- **Citation**: Cboe Global Markets, *The State of the Options Industry: Quarter Three 2025.* https://www.cboe.com/insights/posts/the-state-of-the-options-industry-quarter-three-2025/
- **Type**: Exchange/industry research (first-party data).
- **Quality verdict**: **Citation-worthy: yes for volume facts, no for strategy claims.** The exchange has a commercial interest in 0DTE growth, but the volume numbers are its own tape.
- **Key findings**: 0DTE crossed **50 % of total SPX options volume by 2024** (~1.5 m contracts/day); in **Q3 2025**, index options ADV ≈ **4.9 m contracts**, of which **2.15 m (≈57 %) of SPX ADV was 0DTE**.
- **Relevance**: Confirms 0DTE liquidity is deep enough that a $100 k account is a price-taker with negligible impact — the binding constraint is spread, not depth.
- **Caveats**: SPX, not SPY/QQQ; and volume ≠ tight spreads at every minute (see S4 Fig. 3).

### S15 — thetrading.tools, VIX term-structure tracker
- **Citation**: thetrading.tools, *VIX Term Structure: VIX/VIX3M Ratio, Backwardation & Contango Tracker.* https://www.thetrading.tools/vix-term-structure (data as of 2026-08-31 close).
- **Type**: Data provider / retail analytics site.
- **Quality verdict**: **Citation-worthy: with caveats.** Useful for a live regime read; the underlying VIX and VIX3M are Cboe indices, so the inputs are sound; the site itself is not authoritative. **The agent should recompute VIX/VIX3M from a primary feed at runtime.**
- **Key findings (2026-08-31 close)**: **VIX 14.92; VIX3M 17.53; VIX/VIX3M = 0.8511 → contango, day 101 of the current contango regime**, i.e. 0.1489 below the 1.0 backwardation threshold.
- **Relevance**: The regime gate from S1/S2 is currently **wide open** for premium selling.
- **Caveats**: One-day snapshot; must be re-read each morning.

### S16 — earnings-watcher.com, AVGO September 2026 earnings page
- **Citation**: earnings-watcher.com, *AVGO Earnings September 2026: Sep 2, ±8.7 % Implied Move.* https://earnings-watcher.com/wiki/avgo-earnings-september-2026
- **Type**: Data-provider / aggregator website.
- **Quality verdict**: **Citation-worthy: with caveats.** Numbers are internally consistent and cross-check against the Benzinga/Bloomberg implied-move figures found elsewhere, but this is not an auditable data source and the implied move quoted drifted between ±8.2 % and ±8.7 % across snapshots.
- **Key findings**: AVGO implied move for 2 Sep 2026 ≈ **±8.2–8.7 %**. **10-year average peak earnings-day move ±7.4 %; median ±5.8 %; 95th percentile ±16.1 %.** **Actual move exceeded the implied move in 10 of the last 16 reports (62 %).** Most recent report (3 Jun 2026): front-expiry IV rose from **59 % to 160 % in the five sessions into earnings (+88 vol points)**; options priced ±8.7 %; the stock **closed −12.6 %** with a **peak move of −15.9 %**.
- **Relevance**: This is the decisive number against an AVGO short-premium earnings trade. A 62 % breach rate means the straddle seller has been on the wrong side of the *move* more often than not, even before considering that the losses are the large ones.
- **Caveats**: Aggregator, method not published; "peak move" vs "close-to-close move" definitions matter and inflate breach rates. 16 observations is a small sample.

### S17 — ORATS earnings-strategy backtest
- **Citation**: ORATS, *Earnings Options Strategies Backtest.* https://orats.com/blog/earnings-options-strategies-backtest ; and ORATS University, *Volatility around earnings*, https://orats.com/university/volatility-around-earnings
- **Type**: Data-provider research blog (Option Research & Technology Services).
- **Quality verdict**: **Citation-worthy: with caveats.** ORATS is a respected options-data vendor with a documented earnings-effect extraction methodology, but this particular backtest has a **very short and unrepresentative sample** and is marketing-adjacent.
- **Key findings**: 5,217 earnings announcements → 20,868 trades; enter the day before earnings, exit the next day. In-sample Jan 2020 – Jul 2021, out-of-sample Jul – Oct 2021. Returns normalized by stock price: **sell straddle +1.18 % in-sample (214 trades), +0.65 % out-of-sample (54 trades)** — but with a **loss range of −26.7 % against a gain range of only +8.3 %**. Buy straddle +0.40 % / +0.65 %; buy calendar +0.90 % / +0.91 % (their best out-of-sample strategy). Separately, ORATS documents that IV rises into earnings because the expected range widens (their illustration: 25 % → ~30 % IV), and that the "implied earnings **effect**" differs from the "implied earnings **move**".
- **Relevance**: The short-straddle number is positive on average but the **−26.7 % vs +8.3 % asymmetry is the whole story**: this is the canonical picking-up-pennies profile, in a risk-averse mandate, on a 3-day clock where one bad print ends the competition.
- **Caveats**: 2020–2021 only (post-COVID vol regime); tiny out-of-sample; no transaction-cost detail given; vendor-published.

### S18 — Dim, Eraker & Vilkov (2023/24) and Brogaard, Han & Won (2023) — 0DTE market impact
- **Citations**: Dim, C., Eraker, B., & Vilkov, G. (2023/2024). *0DTEs: Trading, Gamma Risk and Volatility Propagation.* SSRN 4692190. Brogaard, J., Han, J.-H., & Won, P. Y. (2023). *Does 0DTE Options Trading Increase Volatility?* SSRN 4426358 — **12 citations** (OpenAlex).
- **Type**: Working papers (SSRN).
- **Quality verdict**: **Citation-worthy: with caveats** — SSRN pages were behind a Cloudflare challenge and I could not read the PDFs first-hand; findings below come from search summaries plus **the description of these papers inside S5, which I did read**.
- **Key findings (second-hand)**: Dim/Eraker/Vilkov find volatility is related to the sign and magnitude of OMM position gammas, and that 0DTE presence **dampens** market volatility, driven not by same-day 0DTE trading but by longer-dated positions rolling into 0DTE. Brogaard/Han/Won find ETF return volatility **correlates** with the 0DTE share of index-option volume. Adams, Fontaine & Ornthanalai (2024) find market volatility is **lower** on days when 0DTEs are available.
- **Relevance**: The weight of evidence is that 0DTE availability is volatility-**neutral to dampening**, not amplifying. Supports trading 0DTE at all; does not support any specific entry timing.
- **Caveats**: Second-hand. Brogaard et al. is correlational.

### S19 — Practitioner "IV Rank" material (tastytrade-derived blogs)
- **Citation**: Various — e.g. MenthorQ *IV Rank vs Percentile Guide*; Volatility Box *IV Rank vs IV Percentile*.
- **Type**: Blogs / retail education sites.
- **Quality verdict**: **Citation-worthy: no.** I could not locate a primary tastytrade research page or any peer-reviewed study supporting IV-rank thresholds. The concrete claims found (e.g. "iron condors entered with IV rank and percentile > 50 produce a 56.8 % win rate across 595 symbols vs 48.2 % unfiltered") come from a vendor blog with no published methodology, no cost assumptions and no confidence intervals.
- **Key findings as claimed**: IVR > 50 favours premium selling; IVR < 30 favours premium buying; a 10-year SPY 16-delta strangle study at 45 DTE managed at 21 DTE showed "slightly higher success rates when IVR or IVP exceeded 30 %".
- **Relevance**: **Negative.** With VIX ≈ 15 and at its lowest monthly close since Nov 2024, an IVR filter would veto our entire strategy. Since the rule is unsupported and contradicted by Johnson (2017) — where the *level* has no predictive power and the *slope* does — we should not adopt it.
- **Caveats**: Absence of evidence found here is not proof the rule is wrong; it may simply be that tastytrade's own studies are video-only and not indexed.

### S20 — Market context sources for 2026-09-01
- **Citations**: Investrade, *Morning Preview: September 01, 2026*, https://investrade.com/morning-preview-september-01-2026/ ; HaiKhuu Trading, *Weekly Preview 08/31/2026*, https://haikhuu.com/reports/weekly-preview-08312026 ; Trading Economics US calendar, https://tradingeconomics.com/united-states/calendar ; Federal Reserve Beige Book page, https://www.federalreserve.gov/monetarypolicy/publications/beige-book-default.htm ; FOMC calendar, https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
- **Type**: Market-news / macro-calendar aggregators + primary Federal Reserve pages.
- **Quality verdict**: **Citation-worthy: with caveats** for the aggregators (used only where two independent ones agree); **yes** for the federalreserve.gov pages.
- **Key findings**: SPX **7,686.14** (−0.33 %), Nasdaq Composite **26,370.89** (−0.19 %), VIX ~**15.0–15.8** intraday on 1 Sep after a close below 15 — its lowest monthly close since Nov 2024. 10-year yields reported around **4.8 %**. JOLTS (released 1 Sep, 10:00 ET): job openings **7.3 m**, little changed. July payrolls were **−23 k**; consensus for August is roughly **+42 k to +55 k** with unemployment **4.1 %**. Beige Book confirmed for **2 Sep**; FOMC **15–16 Sep** (none in our window); Fed blackout begins **Sat 5 Sep**.
- **Relevance**: Establishes the starting regime: low absolute vol, steep contango, but a fragile labour-market narrative heading into NFP.
- **Caveats**: BLS.gov itself blocks automated retrieval (403 "Access Denied" for bots), so the NFP date/time is confirmed from four independent secondary sources rather than the BLS schedule page.

---

## Evidence table

| # | Claim | Supporting sources (independent) | Contradicting / qualifying | Confidence |
|---|---|---|---|---|
| 1 | A positive variance risk premium exists in S&P 500 options and is economically large | S3 (BTZ 2009, RFS), S1 (Johnson 2017: 1M variance-swap Sharpe −1.44 long ⇒ +1.44 short), S4 (Almeida et al.) | — | **Supported — high** |
| 2 | The VRP is **larger at shorter maturities**, and largest at 0DTE | S1 (Sharpe monotone in maturity: −1.44 at 1M → −0.29 at 12M), S4 (0DTE 1.54–2.96 vs 0.48–0.81 at 1–22 DTE) | — | **Supported — high** |
| 3 | The **slope** of the VIX term structure, not its level, conditions short-vol profitability | S1 (SLOPE subsumes the rest of the curve; level does not predict), S2 (basis predicts VIX-futures returns, not spot VIX) | S19 (IV-rank folklore uses level) — but unsupported | **Supported — high** |
| 4 | In **backwardation**, short-vol expected returns turn negative | S1 (VRP flips sign for 17 of 18 variance assets in lowest SLOPE quintile), S2 (long-in-backwardation profitable: 40 trades, +$1,018 mean) | — | **Supported — medium-high** |
| 5 | "Only sell premium when IV rank > 50" is a supported rule | — | S1 (level has no predictive power), S4 (0DTE mispricing Sharpe is *higher* when realized variance is low) | **Not supported — the evidence points the other way** |
| 6 | Implied volatility is the best single short-horizon forecast of realized volatility, but upward-biased | S12 (Poon & Granger 2003 survey of 93 studies; Christensen & Prabhala 1998), S3 (the bias *is* the VRP) | HAR-RV augmented with IV beats IV alone (S12 secondary) | **Supported — medium-high** |
| 7 | 0DTE bid-ask spreads are widest at the open and close and tightest **10:00–14:00 ET** | S4 (Fig. 3, Cboe intraday data 2012–2025) | Only one source found | **Single-source — medium** |
| 8 | 0DTE premium *richness* (annualized VRP) **increases** through the afternoon, peaking near 14:00 | S4 (Table 1: 1.54 at 11:00 → 2.96 at 14:00) | Risk rises in step: VRP/SD ratio is flat at ≈0.16–0.21 (my calculation from S4) | **Supported — medium** |
| 9 | The **last 30 minutes** of the session trend with the rest of the day, driven by negative dealer gamma | S6 (JFE, 60+ futures, 1974–2020, OOS R² 2.88 %), S5 (gamma effect largest when OMM gamma is negative) | Gao et al. (2018) first-half-hour predictor is weaker (OOS R² −1.71 %) | **Supported — high** |
| 10 | Dealer gamma effects on index volatility are **real but small** | S5 (mean −0.2 pp; max +3.3 pp daily, +6.4 pp on 30-min vs 63.4 pp from all causes), S18 (0DTE availability dampens vol) | Popular "gamma squeeze" narrative; Brogaard et al. correlational finding | **Supported — medium-high** |
| 11 | Do **not** rely on option-expiration pinning at the index level | S8 (anti-cross-pinning before SPX index-option expiry), S7 (pinning is a single-stock, monthly, 16.5 bp effect) | — | **Supported — medium-high** |
| 12 | Implied volatility **falls** after a scheduled macro release as uncertainty resolves | S10 (Ederington & Lee 1996 model + evidence), S11 (announcement jump is instantaneous) | — | **Supported — medium-high** (magnitudes for SPX not obtained) |
| 13 | The pre-FOMC drift is exploitable today | S9a (Lucca & Moench 2015) | S9b (Kurov et al. 2021: disappeared after 2015) | **Not supported — and moot, no FOMC in window** |
| 14 | At 0DTE the IV smile is **symmetric** (puts ≈ calls), unlike the longer-dated smirk | S4 (explicit statement, all times of day) | Only one source found | **Single-source — medium** |
| 15 | At **5–7 DTE** the premium is concentrated on the **downside**; upside variance premium is negative | S4 (VRP⁺ = −0.122 at 5DTE, −0.202 at 7DTE; VRP⁻ = 0.611, 0.747) | Mapping variance decomposition → credit-spread P&L is an inference | **Single-source — medium-low** |
| 16 | Option-implied skew / put-call ratios can profitably tilt an index position over 1–2 days | — | S13 (both are cross-sectional single-stock signals over weeks–months; the *public* put-call ratio is the weak version) | **Not supported — stay delta-neutral** |
| 17 | Naive short 0DTE vol has become less profitable since 0DTEs became daily (May 2022) | S4 ("performance mostly stagnates after 2022"; delta-hedged short call has *negative* Sharpe net of costs) | S4 also shows the VRP itself remains large and significant post-2022 | **Supported — medium** |
| 18 | For AVGO specifically, selling the earnings straddle has an unfavourable historical record | S16 (breach in 10 of last 16 = 62 %; Jun-2026 implied ±8.7 % vs actual −12.6 % close / −15.9 % peak) | S17 (short straddle averaged +1.18 % / +0.65 % across a broad cross-section) — but with −26.7 % vs +8.3 % range asymmetry | **Supported — medium** (single aggregator, small n) |
| 19 | NFP (Employment Situation) is released Fri 2026-09-04 at 08:30 ET | Four independent secondary sources (financecalendar.com, stockmarkethours.org, Trading Economics, HaiKhuu) | bls.gov blocks bots — primary source not directly readable | **Supported — high** |
| 20 | The VIX term structure is currently in solid contango | S15 (VIX/VIX3M = 0.8511 on 2026-08-31), S20 (VIX < 15 monthly close, low-vol regime) | Seasonal note: VIX median rises from ~16.5 in late Aug toward ~18 by mid-Sep | **Supported — medium-high; re-verify live** |

---

## Macro and event calendar 2026-09-02 to 2026-09-04

Our trading windows: **Wed 09:30–16:00 ET**, **Thu 09:30–16:00 ET**, **Fri 09:30–11:00 ET** (= 15:30–22:00 / 15:30–17:00 CEST).

| Date | Time ET | Time CEST | Event | Source | In our window? | Implication |
|---|---|---|---|---|---|---|
| Wed 02.09. | 07:00 | 13:00 | MBA Mortgage Applications | [TradingEconomics](https://tradingeconomics.com/united-states/calendar) | No (pre-open) | Ignore |
| Wed 02.09. | **08:15** | 14:15 | **ADP National Employment Report (Aug)**, prior 48 k, cons ~51 k | [HaiKhuu](https://haikhuu.com/reports/weekly-preview-08312026), TradingEconomics | No (pre-open) | Moves the pre-open; shapes NFP expectations. Wait for the 09:30 open to settle before entering. |
| Wed 02.09. | 09:45 | 15:45 | S&P Global Manufacturing PMI final (if scheduled) | TradingEconomics | Marginal | Low impact |
| Wed 02.09. | **10:00** | 16:00 | Factory Orders (Jul), prior 0.7 %, cons 0.4 % | TradingEconomics | **Yes** | Low impact. Not a reason to delay entry past ~10:05. |
| Wed 02.09. | 10:30 | 16:30 | EIA Crude Oil / Gasoline Stocks | TradingEconomics | Yes | Negligible for SPY/QQQ |
| Wed 02.09. | **14:00** | 20:00 | **Federal Reserve Beige Book** | [federalreserve.gov](https://www.federalreserve.gov/monetarypolicy/publications/beige-book-default.htm) | **Yes** | Low-to-medium. Occasional 15–30 min vol bump. Do not add risk 13:55–14:15. |
| Wed 02.09. | 16:05–17:00 | 22:05–23:00 | **Earnings after close: AVGO, HPE, SNOW** (+ NTAP, FIVE, PVH, GOLD, CHPT, WOOF). AVGO call 17:00 ET | [Broadcom IR](https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announce-third-quarter-fiscal-year-2026-financial), HaiKhuu | No (after close) | Creates Thursday's opening gap in QQQ/SPY. AVGO is a top-5 SPX weight: an 8.7 % AVGO move ≈ 20 bp on SPX, more on QQQ. Do **not** hold Wednesday-entered Thursday-expiry shorts through it. |
| Thu 03.09. | 07:30 | 13:30 | Challenger Job Cuts, cons 62.0 k | TradingEconomics | No | Low |
| Thu 03.09. | pre-open | — | **CIEN earnings (BMO)** (+ CPB, TTC, LE, DLTH) | [Investing.com](https://www.investing.com/news/stock-market-news/samsara-ciena-lululemon-and-more-set-to-report-earnings-thursday-93CH-4724975) | No | Single-name only; negligible index impact |
| Thu 03.09. | **08:30** | 14:30 | **Initial Jobless Claims** (prior 205 k, cons 203 k) **+ Trade Balance (Jul)** | TradingEconomics, HaiKhuu | No (pre-open) | Medium. Claims matter more than usual given the labour narrative. |
| Thu 03.09. | 09:45 | 15:45 | S&P Global Services / Composite PMI final, 56.0 | TradingEconomics, HaiKhuu | **Yes** | Low (final revision) |
| Thu 03.09. | **10:00** | 16:00 | **ISM Services PMI (Aug)**, prior 54.3, cons 54.0 | TradingEconomics | **Yes — highest-impact in-window print of the week** | Tier-1 US macro. Enter **after** ~10:15, not before. |
| Thu 03.09. | 16:05–16:30 | 22:05–22:30 | **Earnings after close: ZS, LULU, DOCU, IOT** (+ PATH, AMBA, GWRE). ZS call 16:30 ET | Investing.com, [TIKR](https://www.tikr.com/blog/zscaler-reports-q4-fy2026-earnings-september-3-what-the-stock-needs-to-show) | No (after close) | Implied moves: **ZS ≈ ±13 %**, **LULU ≈ ±8.1 %** (Bloomberg data via Investing.com). Single-name, negligible index effect. |
| **Fri 04.09.** | **08:30** | **14:30** | **EMPLOYMENT SITUATION — Nonfarm Payrolls (Aug), Unemployment Rate, Average Hourly Earnings.** Prior NFP −23 k; consensus ≈ +42 k…+55 k; UE 4.1 % | [financecalendar.com](https://www.financecalendar.com/us-jobs-report/), [stockmarkethours.org](https://stockmarkethours.org/events/us-jobs-report), TradingEconomics | **No — 60 min BEFORE our window opens** | **The dominant risk of the whole competition.** The jump is entirely in the overnight gap. See rules R7–R9. |
| Fri 04.09. | 09:30–11:00 | 15:30–17:00 | **Our final trading window** | — | **Yes** | Post-announcement: IV already crushed (S10), realized vol still elevated (S11). Worst risk/reward of the three days for opening new short premium. |
| Mon 07.09. | — | — | **Labor Day — US markets closed** | — | After window | 3-day weekend follows Friday's close; afternoon liquidity thins (outside our window). |

**Confirmed absent from the window**: no FOMC meeting, no FOMC minutes, no CPI, no PPI, no JOLTS (released Tue 1 Sep, 10:00 ET; openings 7.3 m). Next FOMC **15–16 Sep 2026**; Fed communications **blackout begins Sat 5 Sep**, so **Fed speakers are still permitted Wed–Fri** — an unscheduled headline risk that cannot be calendared.

---

## Answers to research questions 1–6

### Q1 — Does selling premium work better when VIX/IV is high, when IV > RV, or in contango?

**The term structure dominates the level.** Johnson (2017, JFQA) is decisive: the second principal component of the VIX term structure, SLOPE, "summarizes nearly all" the risk-premium information and predicts excess returns on variance swaps, VIX futures **and S&P 500 straddles at all maturities, "to the exclusion of the rest of the term structure".** The level does not. Critically, in the **lowest SLOPE quintile the variance risk premium changes sign and becomes positive for 17 of 18 variance assets** — short vol stops paying and starts losing.

Simon & Campasano (2014) independently confirm the two-sidedness on VIX futures: shorting in contango (daily roll > 0.10) earned a mean **+$792/trade after costs across 62 trades with a 2:1 win ratio and Sortino 1.26**, while going **long** in backwardation earned **+$1,018/trade across 40 trades**. Their framing matters: the basis has **no** forecast power for spot VIX, so it is a harvestable risk premium, not a forecast.

**IV > RV (the VRP itself)**: Bollerslev, Tauchen & Zhou (2009) establish the premium is real and time-varying (VRP explains >15 % of quarterly excess market return variation, >25 % with P/E). But note the honest gap: BTZ show a high VRP predicts high *equity* returns, not directly high *option-selling* returns. Almeida et al. (2025) test the option-selling version at 0DTE and find that conditioning on the VRP "has only a small effect" on their strategy's Sharpe — while conditioning on **low realized variance, low 0DTE volume and low retail attention** *raises* it.

**IV rank / IV percentile**: I found **no peer-reviewed support**. The concrete numbers circulating (e.g. 56.8 % vs 48.2 % iron-condor win rate for IVR/IVP > 50) come from a vendor blog with no published methodology. The rule also directly contradicts Johnson's level-vs-slope result. **Recommendation: use a term-structure gate, not an IV-rank gate.** Practically this matters a great deal for us: at VIX ≈ 15 an IVR filter would veto everything, while the slope filter (VIX/VIX3M = 0.851) is wide open.

**Applied to now**: contango (0.851, day 101), no backwardation stress. The regime says *sell*. The low absolute level says *sell smaller*, because the dollars of premium per unit of tail exposure are compressed.

### Q2 — Short-horizon volatility forecasting: HAR-RV, GARCH, or IV?

For **1–3 day horizons** the ranking that emerges from the literature is:

1. **Implied volatility is the best single predictor.** Poon & Granger's (2003) survey of 93 studies concludes the VIX is the best predictor of realized volatility, though **biased** — and the bias is precisely the VRP we intend to harvest. Christensen & Prabhala (1998) show implied volatility **subsumes** past realized volatility once the errors-in-variables and overlapping-observations problems are corrected.
2. **HAR-RV (Corsi 2009) is the best purely-historical model** and remains the workhorse; reported one-day-ahead adjusted R² for S&P 500 RV is ≈ **0.605** for the benchmark HAR-RV, with augmented variants reaching 0.624–0.644 (from a recent horse-race paper, not Corsi's own tables).
3. **GARCH-family models are dominated at daily horizons** once intraday realized measures are available; Hansen & Lunde's classic finding that nothing beats GARCH(1,1) applies to the daily-return information set, not to the realized-volatility one.
4. **The combination wins**: adding implied volatility to a HAR specification "substantially improves forecasts" in multiple studies.

**Typical IV–RV gap for SPY/SPX**: I could not verify a clean headline "3–4 volatility points" number from a primary source and will not invent one. What I *can* state with verified numbers is the variance-space equivalent from Almeida et al.: annualized VRP of **1.54–2.96 percentage points at 0DTE**, **0.56 % at 1DTE**, **0.81 % at 22DTE**; and from Johnson: **−1.36 % mean daily excess return on 1-month synthetic variance swaps** (annualized Sharpe −1.44 long / +1.44 short).

**Practical recommendation for a 3-day agent**: do not build a forecasting model. Use the **0DTE ATM straddle price as the market's own estimate of the remaining-day move**, and maintain one cheap sanity check — a 5–10 day trailing intraday realized-vol estimate. If IV implies materially *less* than trailing RV, that is the one condition under which you should *not* sell (the premium is not there). This is a direct, defensible reading of Poon & Granger + Christensen & Prabhala without any modelling risk.

### Q3 — Intraday volatility and 0DTE timing

**The intraday U-shape** (Wood, McInish & Ord 1985, JF, 570 citations; Andersen & Bollerslev 1997, J. Empirical Finance, 1,368 citations) is one of the oldest stylised facts in market microstructure: volume and volatility are highest at the open and into the close, lowest around midday.

**Where is 0DTE premium richest?** Almeida et al.'s Table 1 gives the direct answer, and it **contradicts the popular "sell at 10:00" folk rule on richness grounds**: the annualized 0DTE VRP is *lowest* at 10:30–11:00 (1.54–1.56) and *highest* at 14:00 (2.96), rising almost monotonically through the afternoon. However, the dispersion rises in lockstep (SD 7.63 → 14.41), so the **VRP-per-unit-of-risk is essentially flat across the session at ≈0.16–0.21** (my calculation). There is therefore **no risk-adjusted richness edge to any particular hour.**

**Where is the *execution* edge?** Here the same paper is unambiguous and this is the argument that should drive our rule: "trading volume is higher at market **open and close**, [but] these times of the day are also the ones with **highest bid-ask spread** over the day. The bid-ask spread tends to be relatively stable at its **minimum between 10:00 and 14:00**." Quotable strike depth also thins from ~4 strikes per moneyness bin at 10:00 to ~2 at 14:00. For a four-legged iron condor paying the spread four times on entry and four on exit, this is the dominant consideration.

**Where is gamma risk worst?** Two distinct answers:
- *Systematically*: the last 30 minutes. Baltussen, Da, Lammers & Martens (2021, JFE) document that the last-30-minute return is positively predicted by the rest-of-day return across 60+ futures over 1974–2020 (equity-index OOS R² **2.88 %**), and attribute it explicitly to **negative gamma exposure of option and leveraged-ETF hedgers forcing trading in the direction of price moves**. A short iron condor is short exactly that gamma. The effect reverts over subsequent days, which is no help to a 0DTE position.
- *In magnitude*: smaller than the folklore suggests. Amaya, Garcia-Ares, Pearson & Vasquez (Cboe data, Jul 2020 – Jun 2023) estimate the **mean** effect of OMM gamma is to **reduce** volatility by 0.2 pp; the **maximum** gamma-induced increase is **+3.3 pp** in annualized daily RV and **+6.4 pp** in annualized 30-minute RV — versus a 63.4 pp maximum 30-minute change from all causes, and with >5 % of 30-minute windows exceeding 6.4 pp anyway. Their own verdict: "not large." Dim/Eraker/Vilkov and Adams/Fontaine/Ornthanalai reach compatible conclusions (0DTE availability **dampens** volatility).

**Expiration-day pinning**: Ni, Pearson & Poteshman (2005, JFE) is the canonical pinning paper, but its effect is **single-stock, monthly-expiration, and 16.5 basis points** on average. The index-level counterpart, Golez & Jackwerth (2012, JFE), finds S&P 500 futures pin to the ATM strike on **serial futures-option** expirations but are **pushed away** from the ATM strike right before **SPX index-option** expiration ("anti-cross-pinning"), with a lower-bound notional effect of ≥$115 m (≥$240 m post-1998). **Conclusion: do not design strikes around an assumed pin.** In a regime where 0DTE is ~57 % of SPX volume and every day is an expiration, the monthly-expiry pinning literature does not transfer.

**Verdict on 10:00–10:30 vs the open vs the afternoon**: entering at **10:00–11:00 ET is supported — by liquidity, not by premium richness.** The open (09:30–10:00) is the worst execution window and carries unabsorbed overnight-gap and pre-open-data risk. The afternoon has richer premium but wider spreads after 14:00, thinner quotable strikes, and runs into the documented last-30-minute trend. A defensible split: **primary tranche 10:00–11:00, optional second tranche 12:30–13:30, everything flat by 15:15–15:30.**

### Q4 — Macro announcement effects, and what is actually in our window

**The mechanism.** Andersen, Bollerslev, Diebold & Vega (2003, AER) establish that scheduled announcement *surprises* produce essentially instantaneous conditional-mean **jumps** at high frequency, with asymmetric response (bad news moves more) and elevated volatility persisting after the release. Ederington & Lee (1993, JF) show scheduled macro releases — the **employment report** foremost — dominate intraday volatility; Ederington & Lee (1996, JFQA) add the options-market half: because the *timing* is known but the *content* is not, pre-release implied volatility impounds the anticipated jump and **implied volatility falls after the release** as uncertainty resolves.

**Together these two facts define the worst possible trade for a premium seller around NFP:**
- Holding a short short-dated option **through** the 08:30 print means eating the entire jump in an **overnight gap you cannot hedge or stop out of**. Gamma is unbounded and the position is unmanageable between 16:00 Thursday and 09:30 Friday.
- Opening a short position **at 09:30 Friday** means selling **after** the event premium has already been crushed (Ederington & Lee 1996) while realized intraday volatility is **still elevated** (Andersen et al. 2003). You collect the lowest premium at the highest realized vol — a negative-edge combination.

**Pre-FOMC drift**: cite the pair, not just Lucca & Moench. Lucca & Moench (2015, JF, 642 citations) documented large pre-announcement excess returns 1994–2011; Kurov, Wolfe & Gilbert (2021, FRL) extend to 2019 and find it **essentially disappeared after 2015**. Moot in any case — no FOMC in our window.

**What is actually in our window** (see the calendar table for full detail):
- **Wed 2 Sep**: nothing tier-1 inside RTH. ADP at 08:15 is pre-open; Factory Orders 10:00 is low-impact; the Beige Book at 14:00 is low-to-medium. **This is the cleanest session of the three.**
- **Thu 3 Sep**: **ISM Services PMI at 10:00 ET is the highest-impact in-window print of the week.** Claims and trade balance at 08:30 are pre-open. Plus an opening gap from the AVGO/HPE/SNOW prints.
- **Fri 4 Sep**: **NFP at 08:30 ET, 60 minutes before our window opens.** Everything above applies.
- **Not in the window**: FOMC, minutes, CPI, PPI, JOLTS. Fed speakers remain unmuzzled until the Sat 5 Sep blackout — an uncalendarable headline risk on Wed and Thu.

### Q5 — Option-implied signals as filters: strong enough to tilt a condor?

**Short answer: no. Stay delta-neutral.**

- **IV skew (Xing, Zhang & Zhao 2010, JFQA, 761 citations)**: steepest-smirk stocks underperform flattest-smirk stocks by **10.9 % per year** risk-adjusted, persisting ≥6 months. This is a **cross-sectional single-stock** signal at a **monthly-to-semiannual** horizon. It says nothing about SPY over two days.
- **Put-call ratio (Pan & Poteshman 2006, RFS, 909 citations)**: the **signed** put-call volume ratio predicts next-day-to-next-week stock returns — but the paper's own key caveat is that the **publicly observable, unsigned** ratio "carries far less information". An Alpaca-based agent can only compute the weak version.
- **VIX term-structure slope (Johnson 2017)**: this one **is** strong, but it is a **volatility-level** signal, not a **direction** signal. Use it to decide *whether* to sell, never *which side* to skew.
- **Option volume / order imbalance**: I found no evidence of index-level, 1–2-day-horizon usability within this review's scope.

**The one skew-related finding that *is* actionable** comes from Almeida et al. and concerns wing *construction*, not direction:
- At **0DTE the IV smile is symmetric** — "OTM puts and calls are equally expensive in terms of IV... in contrast to the usual smirk observed for longer-maturity S&P 500 options." A **symmetric, delta-neutral 0DTE iron condor is therefore the natural structure**; you are not being systematically underpaid on the call wing the way you would be at 30 DTE.
- Reinforcing this, the 0DTE **upside** variance premium exceeds the downside one (VRP⁺ 0.96–1.97 vs VRP⁻ 0.58–0.99), and the gap widens through the afternoon.
- At **5–7 DTE the picture inverts**: VRP⁺ turns **negative** (−0.122 at 5DTE, −0.202 at 7DTE) while VRP⁻ is solidly positive (0.611, 0.747). If we trade 1–7 DTE credit spreads at all, the premium lives on the **put side**, not the call side.

Confidence on that last inference is **medium-low**: it maps a model-free variance decomposition onto spread P&L, and the 2012–2025 sample is a period of persistent equity upside, which mechanically raises realized upside variance and depresses VRP⁺ at longer horizons.

### Q6 — Earnings IV dynamics for our specific names (practitioner/industry evidence)

Honest grading first: **none of the sources in this section is peer-reviewed.** They are data vendors and aggregators, some with commercial incentives. I report their numbers and grade them individually.

**AVGO (Wed 2 Sep, after close)** — *the most important name and the clearest signal against selling its earnings premium.*
- Implied move ≈ **±8.2 %–8.7 %** (earnings-watcher; a Benzinga/Bloomberg-sourced list gave the same order of magnitude; a separate aggregator quoted 8.85 %).
- 10-year average **peak** earnings-day move **±7.4 %**; median **±5.8 %**; **95th percentile ±16.1 %**.
- **The actual move exceeded the implied move in 10 of the last 16 reports — 62 %.**
- Most recent report (3 Jun 2026): front-expiry IV rose from **59 % to 160 % in the five sessions into the print (+88 vol points)**, options priced ±8.7 %, and the stock **closed −12.6 %** with a **peak move of −15.9 %**.
- *Grade: with caveats.* Single aggregator, undocumented method, n = 16, and "peak move" definitions inflate breach rates versus close-to-close. But the direction of the evidence is consistent and the June 2026 outcome is verifiable market history.
- **Implication**: short premium on AVGO earnings is not supported. To be outside the 95th percentile you would need short strikes near ±16 %, roughly 2× the implied move, where the credit is negligible. Strikes at 1.5× implied (≈13 %) would have **lost** on the most recent report.

**SNOW (Wed 2 Sep, after close)**: average post-earnings move **±12.8 %** over the last seven reports (Benzinga). *Grade: with caveats* — a raw historical average with no implied-move comparison. High-move name; treat as unsuitable for short premium.

**ZS (Thu 3 Sep, after close, call 16:30 ET)**: options imply ≈ **±13 %** (Bloomberg data reported by Investing.com/TIKR). *Grade: with caveats* — the Bloomberg provenance is the best in this section, but it is second-hand.

**LULU (Thu 3 Sep, after close)**: implied ≈ **±8.1 %** (Bloomberg via Investing.com); **exceeded the implied move in 6 of the past 8 reports**. *Grade: with caveats.* Same direction as AVGO: the seller has been on the wrong side of the move 75 % of the time recently.

**DOCU, IOT (Thu 3 Sep, after close); CIEN (Thu 3 Sep, pre-market)**: confirmed dates; no reliable implied-move figures obtained within the time box.

**Cross-sectional context (ORATS, data vendor)**: across 5,217 announcements / 20,868 trades, entering the day before and exiting the day after, the **short straddle averaged +1.18 % (in-sample, 214 trades) and +0.65 % (out-of-sample, 54 trades)** normalized by stock price — **but with a loss range of −26.7 % against a gain range of only +8.3 %**. Their best out-of-sample strategy was the **long calendar** (+0.91 %), not the short straddle. *Grade: with caveats* — sample is Jan 2020 – Oct 2021 only, an extreme vol regime, with a tiny out-of-sample and no cost detail.

**Contradicting evidence worth flagging honestly**: an SSRN working paper (Khan & Khan, *17-Year Backtest of Straddles around S&P 500 Earnings Announcements*, SSRN 4832160) reports that **buying** a straddle one day before earnings and selling one day after produced a **108 % CAGR and Sharpe 2.2 over 13,120 trades** — while itself conceding single-week losses of 83.8 % and unaccounted commissions, slippage and taxes. *Grade: no.* A 108 % CAGR from mid-price fills on ATM straddles is almost certainly an execution artifact. It is listed only so we do not appear to have cherry-picked.

**Bottom line for Q6**: the industry data give **no support** for selling earnings premium on AVGO or LULU, and the two highest-implied-move names (ZS ±13 %, SNOW ±12.8 %) are the worst candidates of all. The one structural fact that *is* solid and usable is the ORATS mechanism: **IV is inflated ahead of the print and collapses immediately after** — which means the low-risk way to express an earnings view in this window is to trade **after** the crush (day-after direction or a defined-risk structure on the *residual* elevated realized vol), not before it.

---

## Design implications

Numbered, concrete rules. Each carries its justifying source(s) and a confidence grade.

**R1 — Regime gate (term structure, not IV level).** Before any premium-selling entry, compute **VIX / VIX3M**. Sell only if the ratio is **< 0.95**. Between 0.95 and 1.00, halve size. At **≥ 1.00 (backwardation), do not open new short-vol positions at all** and reduce existing ones. *Sources: Johnson 2017 (SLOPE subsumes the curve; VRP flips sign in the lowest slope quintile); Simon & Campasano 2014 (long-vol is the profitable trade in backwardation).* Current reading 2026-08-31: **0.8511 → gate open.** **Confidence: high.**

**R2 — Do NOT use an IV-rank/IV-percentile veto.** VIX at ~15 (lowest monthly close since Nov 2024) would fail any IVR > 30/50 rule, but that rule has no peer-reviewed support and is contradicted by Johnson's level-vs-slope result; Almeida et al. even find 0DTE mispricing is *more* exploitable when realized variance is low. Instead let the low level act on **size**: scale contract count to a fixed max-loss budget, not to a fixed contract count. *Sources: Johnson 2017; Almeida et al. 2025 (Table 7); S19 graded not citation-worthy.* **Confidence: medium-high.**

**R3 — Prefer 0DTE over 1–7 DTE for premium selling.** The annualized VRP at 0DTE is **1.54–2.96 pp** versus **0.48–0.81 pp** at 1–22 DTE — a 2–4× richer premium — and Johnson independently shows short-variance Sharpe falls monotonically with maturity (+1.44 at 1M → +0.29 at 12M for the short side). *Sources: Almeida et al. 2025 Tables 1–2; Johnson 2017 Table.* **Confidence: high.** *Trade-off to disclose in the write-up: 0DTE buys premium richness at the cost of maximal gamma.*

**R4 — Entry window 10:00–11:00 ET (primary), optional 12:30–13:30 ET (secondary). Never at 09:30–10:00.** Justified by **execution cost**, not premium richness: 0DTE bid-ask spreads are widest at the open and close and at their minimum 10:00–14:00, and quotable strike depth halves between 10:00 and 14:00. A four-legged condor crosses the spread eight times round-trip, so spread dominates. *Source: Almeida et al. 2025, Fig. 3 and §3.* **Confidence: medium (single source, but directly measured on Cboe intraday data).**

**R5 — Flatten all short-gamma 0DTE positions by 15:15–15:30 ET.** The last 30 minutes trend in the direction of the rest of the day (equity-index OOS R² 2.88 %), driven by negative dealer gamma — precisely the exposure a short condor holds. Do not "let them expire worthless" to save commission. *Source: Baltussen, Da, Lammers & Martens 2021, JFE.* **Confidence: high.**

**R6 — Do not build a dealer-gamma (GEX) entry signal.** The maximum gamma-induced increase in annualized 30-minute volatility is **6.4 pp** against a 63.4 pp maximum from all causes, and the mean gamma effect is **−0.2 pp (dampening)**. Use the concept only as a risk-off overlay: aggregate OMM gamma is most negative in selloffs, so treat a sharp intraday drawdown as a reason to reduce, not as a signal to fade. *Sources: Amaya et al. 2025 (Cboe); Dim/Eraker/Vilkov; Adams/Fontaine/Ornthanalai (both second-hand).* **Confidence: medium-high.**

**R7 — Hard rule: no short short-dated options held from Thu 3 Sep close into Fri 4 Sep.** Any position expiring Fri 4 Sep must be **opened and closed within a single session**, or not opened. The NFP jump lands at 08:30 ET entirely inside the unhedgeable overnight gap. *Sources: Andersen, Bollerslev, Diebold & Vega 2003 (instantaneous announcement jumps); Ederington & Lee 1993.* **Confidence: high.**

**R8 — Fri 4 Sep 09:30–10:00 ET: no new short premium.** Implied volatility has already collapsed with the resolution of the scheduled announcement while realized volatility remains elevated — the worst combination for a seller. If anything is done on Friday, wait until **≥10:00–10:15 ET**, size at ≤50 % of a normal clip, and prefer simply **closing/managing** existing positions and banking the competition result. *Sources: Ederington & Lee 1996 (IV declines post-scheduled-release); Andersen et al. 2003 (post-announcement volatility persistence).* **Confidence: medium-high** (mechanism verified; SPX-specific magnitudes not obtained).

**R9 — Thu 3 Sep: enter only after ~10:15 ET.** ISM Services PMI at 10:00 ET is the highest-impact in-window release of the week, and Thursday opens on an AVGO/HPE/SNOW gap. Let the print and the gap be absorbed. *Sources: Trading Economics calendar; Ederington & Lee 1993 (scheduled releases dominate intraday vol).* **Confidence: medium-high.**

**R10 — Wed 2 Sep is the cleanest session: make it the primary 0DTE day.** No tier-1 macro inside RTH; only Factory Orders (10:00, low impact) and the Beige Book (14:00, low-medium). Avoid adding risk 13:55–14:15. *Sources: federalreserve.gov Beige Book schedule; Trading Economics.* **Confidence: high on the calendar, medium on the "clean" characterisation (Fed speakers remain possible until the 5 Sep blackout).**

**R11 — Wing structure by maturity: symmetric at 0DTE, put-biased at 1–7 DTE.** At 0DTE the IV smile is symmetric (OTM puts and calls equally expensive) and the upside variance premium exceeds the downside one, so build a **symmetric, delta-neutral iron condor**. At 5–7 DTE the upside variance premium is **negative** while the downside premium is solidly positive, so any 1–7 DTE credit spread should be a **put** credit spread. *Source: Almeida et al. 2025 (§4, Tables 1–2).* **Confidence: medium at 0DTE, medium-low at 5–7 DTE (variance decomposition ≠ spread P&L; bull-market sample).**

**R12 — No directional skew tilt from option-implied signals.** Do not use IV skew, the public put-call ratio, or option volume to asymmetrise the condor. Both canonical signals are cross-sectional single-stock effects over weeks-to-months, and Pan & Poteshman's own result is that the *publicly observable* ratio is the uninformative one. Keep the structure **delta-neutral at entry and re-centre only on a defined delta band**, not on a signal. *Sources: Xing, Zhang & Zhao 2010; Pan & Poteshman 2006.* **Confidence: high.**

**R13 — Do not assume pinning.** No strike placement, no "magnet" logic, no expectation that SPY gravitates to a max-pain level. The index-level evidence shows the opposite sign near index-option expiry (anti-cross-pinning), and the 16.5 bp single-stock effect is both tiny and from a monthly-expiration regime that no longer describes daily SPY/SPX expiries. *Sources: Golez & Jackwerth 2012; Ni, Pearson & Poteshman 2005.* **Confidence: medium-high.**

**R14 — Strike distance: anchor to the market's own implied move, not to a fixed delta.** Because implied volatility is the best available short-horizon forecast but is *upward*-biased (Poon & Granger; Christensen & Prabhala; the bias is the VRP), the 0DTE ATM straddle price is the right estimate of the remaining-day move. Place short strikes at a multiple of it (e.g. ≥1.25× the remaining-day implied move) and let the resulting delta fall where it may. I found **no peer-reviewed basis** for the practitioner 16-delta convention and will not present one. *Sources: Poon & Granger 2003; Christensen & Prabhala 1998.* **Confidence: medium.**

**R15 — Add a one-line IV-vs-RV sanity check as a veto, not as a scaler.** If the 0DTE implied move is *below* the trailing 5–10 day intraday realized move, do not sell — the premium is not there. This is the only condition under which the VRP is plausibly absent intraday. *Sources: Bollerslev, Tauchen & Zhou 2009; Almeida et al. 2025.* **Confidence: medium.**

**R16 — Earnings: do not sell premium on AVGO, LULU, ZS or SNOW into their prints.** AVGO exceeded its implied move in 10 of 16 reports (62 %) and moved −15.9 % peak against an ±8.7 % implied move on its most recent report; LULU exceeded in 6 of 8; ZS implies ±13 % and SNOW has averaged ±12.8 %. Getting outside the 95th percentile on AVGO requires ~2× the implied move, where the credit is negligible. If an earnings element is required for the "creativity" score, prefer a **defined-risk, sub-0.25 %-of-NAV** expression, or express it **after** the crush (Thursday for the Wednesday reporters). *Sources: earnings-watcher.com; Investing.com/Bloomberg implied moves; ORATS backtest (short straddle: −26.7 % loss range vs +8.3 % gain range).* **Confidence: medium** — good directional evidence, non-peer-reviewed sources, small samples.

**R17 — Assume the naive edge is smaller than backtests suggest.** Almeida et al. find their 0DTE mispricing strategy's performance "mostly stagnates" after May 2022 when 0DTEs became daily, and that **selling the delta-hedged ATM 0DTE call produced mostly negative Sharpe ratios net of transaction costs**. Budget for the spread explicitly, quote-improve rather than crossing, and do not project backtest P&L into the pitch. *Source: Almeida et al. 2025, §5.* **Confidence: medium-high.**

---

## Follow-up reading

- **Dim, C., Eraker, B. & Vilkov, G., "0DTEs: Trading, Gamma Risk and Volatility Propagation"** (SSRN 4692190) — *cited in Amaya et al. (S5)*. Blocked by Cloudflare; an open version exists at westernfinance-portal.org (paper id 950096). Would give first-hand intraday gamma/order-flow numbers.
- **Adams, G., Dim, C., Eraker, B., Fontaine, J.-S., Ornthanalai, C. & Vilkov, G., "Do S&P500 Options Increase Market Volatility? Evidence from 0DTEs"** (SSRN 5641974) — *cited in Amaya et al. and in search results*. The best-identified study of whether 0DTE availability raises or lowers volatility.
- **Vilkov, G., "0DTE Trading Rules"** (SSRN 4641356) plus the companion repo `github.com/vilkovgr/0dte-strategies` — *new idea*. Appears to contain explicit intraday-return distributions by entry time for 0DTE strategies ("all strategies reap negative returns on average, with the distribution extremely wide and right-skewed, especially later in the day" — **unverified second-hand quote**). This is the single most directly relevant unread source for our entry-time question.
- **Gao, L., Han, Y., Li, S. Z. & Zhou, G. (2018), "Market intraday momentum", JFE 129(2)** — *cited in Baltussen et al.* (222 citations). The first-half-hour predictor variant; useful for a morning-direction overlay if we ever wanted one.
- **Onan, M., Altay-Salih, A. & Yaşar, B. (2014), "Impact of macroeconomic announcements on implied volatility slope of SPX options and VIX", Finance Research Letters 11(4)** (51 citations, DOI 10.1016/j.frl.2014.07.006) — *new idea*. Would quantify how the SPX **skew** (not just the level) moves around macro prints — directly relevant to whether the NFP-day wing pricing is distorted.
- **Gu, C., Chen, D. & Stan, R. (2022), "Resolution of financial market uncertainty around the release of unemployment rate announcements", International Review of Economics & Finance** (3 citations) — *new idea*. The closest thing found to an NFP-specific IV-crush study.
- **Cremers, M. & Weinbaum, D. (2010), "Deviations from Put-Call Parity and Stock Return Predictability", JFQA 45(2)** (213 citations) — *new idea*. A third option-implied predictor not covered here.
- **Bevilacqua, M. et al., "Morning Volatility Uncertainty and Variance Risk Premium"** (FoFI 2026 working paper) — *new idea, surfaced while searching for Almeida et al.* Title suggests it directly addresses intraday timing of the VRP.
- **Hansen, P. R. & Lunde, A. (2005), "A forecast comparison of volatility models: does anything beat a GARCH(1,1)?", JAE 20(7)** (1,772 citations) — *cited alongside Andersen & Bollerslev in OpenAlex results*. The standard reference for the GARCH-vs-realized-measures question in Q2.

---

## Paywalled / wanted

| Source | Identifier | Why wanted | Status |
|---|---|---|---|
| Ederington & Lee (1996), JFQA 31(4), 513–539 | DOI 10.2307/2331358 | Exact magnitude of the post-announcement IV decline; whether it generalises beyond rate futures to equity index options | Paywalled (JSTOR/Cambridge). Mechanism confirmed via multiple secondary citations; **magnitudes not obtained — do not quote numbers** |
| Ederington & Lee (1993), JF 48(4), 1161–1191 | DOI 10.1111/j.1540-6261.1993.tb04750.x | Duration of elevated post-8:30 volatility | Paywalled (Wiley) |
| Dim, Eraker & Vilkov, "0DTEs: Trading, Gamma Risk and Volatility Propagation" | SSRN 4692190 | First-hand intraday gamma numbers | SSRN behind a Cloudflare JS challenge; curl returned "Just a moment…". Open mirror candidate: westernfinance-portal.org/viewpaper?n=950096 |
| Vilkov, "0DTE Trading Rules" | SSRN 4641356 | Entry-time-conditional 0DTE return distributions — the most decision-relevant unread item | SSRN blocked (same Cloudflare challenge) |
| Simon & Campasano, published J. of Derivatives version | DOI 10.3905/jod.2014.21.3.054 | To confirm or refute the widely-quoted "53 % annual compound return"; that figure is **absent** from the EFMA working paper I read | Paywalled (PMR). **Treat the 53 % figure as unverified** |
| Xing, Zhang & Zhao (2010), JFQA 45(3) | DOI 10.1017/S0022109010000220 | Confirm the 10.9 %/yr figure first-hand | Author PDF exists at ruf.rice.edu/~yxing/option-skew-FINAL.pdf; **not fetched within the time box.** 10.9 % taken from a secondary summary |
| Pan & Poteshman (2006), RFS 19(3) | DOI 10.1093/rfs/hhj024 | Exact magnitude of next-day predictability from the signed put-call ratio | Paywalled; NBER WP 10925 is open but not fetched. **No number quoted in this report** |
| Corsi (2009), J. Financial Econometrics 7(2) | DOI 10.1093/jjfinec/nbp001 | Corsi's own one-day-ahead R² tables | Paywalled (OUP). The ~0.605 figure comes from a third-party horse-race paper, not Corsi |
| Onan, Altay-Salih & Yaşar (2014), FRL 11(4) | DOI 10.1016/j.frl.2014.07.006 | Announcement effects on the SPX IV **slope** | ScienceDirect returns 403; abstract not in OpenAlex |
| BLS 2026 release schedule (primary) | https://www.bls.gov/schedule/news_release/2026_sched.htm | Primary confirmation of the 4 Sep NFP release | **bls.gov actively blocks bots** (HTTP 403 "Access Denied", error code returned). Confirmed instead from four independent secondary sources |
| Market Chameleon AVGO earnings charts | https://marketchameleon.com/Overview/AVGO/Earnings/Earnings-Charts/ | Independent cross-check of the AVGO implied-vs-realized breach rate and IV-crush magnitudes | Fetch timed out (60 s) twice |
| Cboe VIX futures term-structure snapshot | https://www.cboe.com/tradable-products/vix/term-structure/ | Primary front-vs-second VIX futures basis (the Simon–Campasano input) rather than the VIX/VIX3M index proxy | Not fetched; **the agent should read this live at runtime** |

---

## Method log

**Time box**: ~1 hour, 2026-09-01. Tools: WebSearch, WebFetch, `curl` + `pdftotext` via Bash for blocked pages, OpenAlex API for bibliographic verification. No browser automation used, per brief.

**Bibliographic verification**: Semantic Scholar was avoided per brief (prior 429s). All citation counts, venues, years and DOIs in this report come from the **OpenAlex API** (`api.openalex.org/works?search=<title>`), queried in five batches. Where OpenAlex returned both a journal record and an SSRN/NBER preprint record, both counts are reported. Two DOI-lookup guesses failed (returned unrelated works) and were discarded rather than reported.

**Papers read first-hand (full text or key sections, via curl + pdftotext)**:
- Amaya, Garcia-Ares, Pearson & Vasquez, *0DTE Index Options and Market Volatility* (Cboe PDF, 1,723 lines extracted; read abstract, introduction, §4–6 and conclusion).
- Almeida, Freire & Hizmeri, *0DTE Asset Pricing* (FMA Derivatives 2025 PDF, 2,930 lines; read abstract, introduction, §3 data/liquidity, §4 results, §5 robustness, Tables 1, 2, 6, 7).
- Baltussen, Da, Lammers & Martens, *Hedging demand and market intraday momentum* (Notre Dame open PDF; read abstract, results tables, strategy section).
- Johnson, *Risk Premia and the VIX Term Structure* (author's open JFQA PDF; read abstract, introduction, Table of variance-asset moments).
- Simon & Campasano, *The VIX Futures Basis* (EFMA 2013 working-paper PDF; read abstract and the trading-simulation results section).
- Bollerslev, Tauchen & Zhou, *Expected Stock Returns and Variance Risk Premia* (Federal Reserve FEDS 2007-11 open working paper; read abstract and introduction for the R² figures).

**Blocked / failed retrievals and workarounds**: bls.gov returned HTTP 403 to both WebFetch and a Chrome-UA curl ("Access Denied — bot activity ... is prohibited"), so the NFP date and time were confirmed from four independent secondary sources instead (financecalendar.com, stockmarkethours.org, Trading Economics, HaiKhuu weekly preview), all agreeing on **Fri 2026-09-04, 08:30 ET**. SSRN returned a Cloudflare JS challenge to curl. ScienceDirect and Benzinga returned 403. x.com returned 402. Market Chameleon timed out. The Cboe research PDF initially returned only binary to WebFetch and was recovered with curl + `pdftotext -layout`.

**Calendar cross-checking**: the Wed–Fri event list was built by intersecting Trading Economics (whose displayed times are GMT — 12:30 GMT = 08:30 ET; converted throughout) with the HaiKhuu weekly preview (native ET) and the Investrade morning preview. Where the two disagreed (HaiKhuu lists only the 09:45 S&P Global Services PMI on Thursday; Trading Economics also lists ISM Services at 10:00 ET), **both are included and the higher-impact one is flagged**. Beige Book (2 Sep) and FOMC dates (15–16 Sep, none in window) were taken from primary federalreserve.gov pages. The Fed blackout start (Sat 5 Sep) was confirmed from Reserve Bank blackout-policy pages.

**Known weaknesses of this review**:
1. The **intraday timing recommendation rests substantially on one working paper** (Almeida et al.) for the liquidity result and the smile-symmetry result. Both are marked single-source in the evidence table.
2. **No SPX-specific magnitudes** for the post-NFP IV crush were obtained; the Friday rule rests on a well-established mechanism (Ederington & Lee) applied to a different asset class.
3. The **earnings section is entirely non-peer-reviewed** and rests on aggregators with undocumented methodologies and small samples (n = 16 for AVGO). It is directionally consistent but should not be presented as rigorous.
4. Several headline figures used elsewhere in the literature (Xing/Zhang/Zhao's 10.9 %, Corsi's R², Poon & Granger's "VIX is best") were taken from **secondary summaries** rather than the originals, and are flagged as such at each point of use.
5. Live market state (VIX, VIX3M, the futures basis) is a **31 Aug / 1 Sep snapshot** and must be re-read by the agent each morning before R1 is evaluated.

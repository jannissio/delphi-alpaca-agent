# A — Options Strategy Evidence Review

**Scope:** literature evidence for an options-trading AI agent that will be evaluated on P&L
realised on a fresh $100,000 Alpaca **paper** account over ~2.5 US trading sessions
(Wed 2 Sep, Thu 3 Sep, and 09:30–11:00 ET on Fri 4 Sep 2026).
**Author:** research pass, 2026-09-01. **Method:** WebSearch / WebFetch / curl+pdftotext on open versions.
**Not covered here:** Alpaca API mechanics (covered elsewhere).

---

## Kurzfassung (Deutsch)

1. Die **Varianzrisikoprämie (VRP)** ist eines der robustesten Phänomene der Optionsliteratur: Delta-gehedgte
   Long-Optionen verlieren im Mittel Geld (Bakshi/Kapadia 2003: ATM-Calls −0,10 % des Indexniveaus, −12,2 % des
   Optionspreises pro Trade), Zero-Beta-Straddles verlieren ca. **3 % pro Woche** (Coval/Shumway 2001).
2. Die Prämie ist aber **klein pro Tag** und wird von Transaktionskosten leicht aufgefressen. Israelov/Nielsen (2014):
   von der Gesamtrendite eines Covered Call sind nur **~2,0–2,8 % p. a.** VRP, der Rest ist Aktien-Beta.
3. **Für ein 2-Tage-Fenster ist das faktisch null:** 2,5 % p. a. VRP ≈ **0,025 % über 2,5 Tage ≈ 25 USD auf 100 000 USD**.
   „Langfristig konservativ" ist als Lebensstrategie richtig, als 2-Tage-Ziel aber wirkungslos.
4. Nur **ultrakurze Laufzeiten (0–7 DTE)** erzeugen nennenswerten Theta-Zufluss: ein 0DTE-ATM-Straddle verfällt an
   einem Tag um ~0,76 % des Spot, ein 30-DTE-Straddle nur um ~0,07 % pro Tag — Faktor ~11.
5. Aber: **Almeida/Freire/Hizmeri (2025)** zeigen, dass das naive Verkaufen delta-gehedgter 0DTE-ATM-Optionen
   **nach Transaktionskosten negative Sharpe-Ratios** liefert (−0,010 bis −0,042 pro Trade), und dass der frühere
   0DTE-Vorteil **nach Mai 2022 weitgehend verschwunden** ist.
6. **Beckmeyer/Branger/Gayda (2023)** liefern die beste empirische Verteilung: 0DTE-Iron-Condors von Privatanlegern
   haben Median **+5,5 %** der Margin, aber Mittelwert **−1,1 %**, P25 = −24 %, P5 = **−100 %**. Hohe Trefferquote,
   negativer Erwartungswert nach Kosten.
7. **Definiertes Risiko schlägt undefiniertes Risiko klar**: Cboe-Drawdowns 2006–2019: CNDR (Iron Condor) −13,7 % vs.
   PUT (Cash-Secured Put) −32,7 %, BXM −35,8 %, S&P 500 −51,0 %. Volmageddon 5.2.2018: Short-Vol-ETPs −90 % an einem Tag.
8. **Earnings:** Gao/Xing/Zhang (2018) finden, dass Straddles **vor** der Ankündigung **+3,34 %** verdienen — man sollte
   also **kaufen, nicht verkaufen**. Der IV-Crush ist nur nach der Ankündigung und nur bei liquiden Titeln signifikant
   (−1,37 % für Long-Straddles am Tag danach). Anfang September ist zudem kaum Earnings-Saison.
9. **Ausführungskosten sind der Killer**: effektive Spreads bei 0DTE-SPX liegen bei **5–6 %** (mit Price Improvement)
   bzw. **9,6–12,5 %** des Mittelkurses — pro Bein. Ein 4-beiniger Condor, der den Spread überquert, verliert leicht
   10–25 % der Prämie. Muravyev/Pearson (2020): geduldige Limit-Orders senken die effektiven Kosten auf
   **1,3 statt 6,2 Cent** (16 % des Quoted Spread).
10. **Signal-Rausch-Verhältnis:** selbst bei optimistischer täglicher Sharpe von 0,1 ergibt 2,5 Tage einen t-Wert von
    ~0,16. Das Ergebnis ist **zu ~100 % Rauschen**. Kein Backtest der Welt macht 2 Tage statistisch aussagekräftig.
11. **Empfohlene Risikohaltung:** defensiv-defined-risk. Pro Tag **2–4 % des Kapitals** als maximales definiertes
    Risiko in 0–2 DTE Credit Spreads / Iron Condors auf SPY/QQQ (ggf. IWM), Short-Strikes bei **10–16 Delta**,
    Wings immer gekauft, kein Short-Strangle, keine ungedeckten Legs.
12. **Erwartung:** Median-P&L über 2,5 Tage ≈ **+0,3 % bis +1,0 %** (300–1 000 USD), Erwartungswert ≈ 0,
    5 %-Tail ≈ **−2 % bis −4 %** (2 000–4 000 USD). Bei 20–30 % Kapitaleinsatz vervielfachen sich beide Seiten.
13. Da drei von vier Bewertungskriterien (Technologie, Kreativität, Präsentation) **nicht** P&L sind, ist die
    dominante Strategie: **kleines, sauber begründetes, verlustbegrenztes Buch + exzellente Dokumentation** der
    Evidenz und der Risikologik. Ein großer negativer P&L-Ausreißer schadet mehr, als ein großer positiver nützt.
14. Ein **Barbell** ist vertretbar: ~80 % des Risikobudgets in definierte Prämienverkäufe, ~20 % in eine kleine
    Long-Gamma-/Tail-Position (weit OTM Put-Debit-Spread), die den 5 %-Tail kappt und in der Präsentation zeigt,
    dass die Agentin die Tail-Literatur verstanden hat.
15. Ehrliche Kernaussage für den Nutzer: **Die Literatur sagt nicht „konservativ ist besser" oder „aggressiv ist besser",
    sondern: in 2 Tagen ist keine Options-Alpha-Erwartung statistisch realisierbar. Optimiere daher auf Varianz-
    kontrolle und Nachvollziehbarkeit, nicht auf Renditemaximierung.**

---

## Source cards

### S1 — Carr & Wu (2009), "Variance Risk Premiums"
- **Citation:** Carr, P. and L. Wu (2009). "Variance Risk Premiums." *Review of Financial Studies* 22(3), 1311–1341. DOI 10.1093/rfs/hhn038.
- **Type / venue / year:** peer-reviewed journal, RFS, 2009. **Citations:** 435 (RePEc/IDEAS count, 2026-09-01).
- **Quality verdict:** citation-worthy — **yes**. Top-3 finance journal, model-free methodology, large OptionMetrics sample, foundational and heavily replicated.
- **Key findings:** Introduces the model-free synthetic variance swap rate from a portfolio of options and defines the VRP as `realized variance − variance swap rate`. Applied to **5 stock indexes and 35 individual stocks**. Result: variance swap rates systematically **exceed** subsequent realized variance for the indexes (i.e. a large, significantly **negative** variance risk premium to the buyer of variance / positive to the seller); the premium is much weaker and often insignificant for individual stocks. The premium is not explained by a linear market-return beta — it is a separate priced risk factor.
- **Relevance:** This is the theoretical licence for premium selling *in index options*, and the reason to prefer **SPY/QQQ/IWM over single names**: the index VRP is the robust one.
- **Caveats:** The full magnitude tables are behind the OUP paywall; I could verify the abstract and the citation count but not reproduce the per-index numbers here. Sample ends 2000s — pre-0DTE regime.

### S2 — Bakshi & Kapadia (2003), "Delta-Hedged Gains and the Negative Market Volatility Risk Premium"
- **Citation:** Bakshi, G. and N. Kapadia (2003). *Review of Financial Studies* 16(2), 527–566.
- **Type / venue / year:** peer-reviewed journal, RFS, 2003. Open PDF at people.umass.edu. **Citations:** not verified (S2 API rate-limited); widely regarded as >1,500.
- **Quality verdict:** citation-worthy — **yes**. Peer-reviewed, clean identification (delta-hedged portfolios isolate volatility exposure from direction), standard errors reported per cell.
- **Key findings** (S&P 500 index calls, **1988–1995**, 14–60 day maturities):
  - Averaged over all moneyness/maturities the delta-hedged long position loses **≈0.05 % of the index level**; for ATM calls (moneyness ±2.5 %) **≈0.10 %**.
  - Mean delta-hedged gain scaled by the call price over the 8-year sample: **−12.18 %**.
  - Average ATM dollar loss **−$0.43** per call vs. a mean bid-ask spread of **$0.375** — i.e. the premium is roughly the size of the spread.
  - Frequency of negative delta-hedged gains: **68–72 %** for ATM and OTM-put-side strikes.
  - **Important asymmetry:** for calls **5–10 % OTM** the delta-hedged gains are *positive* (+0.74 % to +1.33 % of the call price; negative only 26–41 % of the time). In their sample, **selling far-OTM calls lost money.**
  - Underperformance is *greater* when volatility is high.
- **Relevance:** Quantifies the per-trade edge as ~10 % of an ATM option's price over a month — small. The OTM-call result is a direct warning against assuming both wings of an iron condor carry premium.
- **Caveats:** 1988–1995 only; pre-decimalisation, wide spreads; index calls only (the put side is inferred by put-call parity, not measured directly).

### S3 — Coval & Shumway (2001), "Expected Option Returns"
- **Citation:** Coval, J. D. and T. Shumway (2001). *Journal of Finance* 56(3), 983–1009.
- **Type / venue / year:** peer-reviewed journal, JF, 2001. **Citations:** not verified; canonical (>2,000).
- **Quality verdict:** citation-worthy — **yes**. Top journal, simple and endlessly replicated result.
- **Key findings:** Beta-neutralised (**zero-beta**) at-the-money S&P 500 straddles earn **≈ −3 % per week** on average. Expected call returns exceed the underlying's and increase with strike, consistent with theory; but the straddle loss cannot be explained by market beta, implying an additional priced factor (systematic stochastic volatility).
- **Relevance:** The single cleanest number for sizing the premium-selling edge. −3 %/week for the buyer ⇒ **≈ +0.6 % of straddle value per trading day** for the seller, gross of costs. Note this is % of the *option premium*, not of capital.
- **Caveats:** 1986–1995 SPX futures options; gross of transaction costs; ignores the extreme left tail (the sample contains Oct 1987 only partially).

### S4 — Bollen & Whaley (2004), "Does Net Buying Pressure Affect the Shape of Implied Volatility Functions?"
- **Citation:** Bollen, N. P. B. and R. E. Whaley (2004). *Journal of Finance* 59(2), 711–753.
- **Type / venue / year:** peer-reviewed journal, JF, 2004. **Citations:** not verified; canonical.
- **Quality verdict:** citation-worthy — **yes**.
- **Key findings:** Changes in implied volatility are driven by *net public order flow*. For **S&P 500 options**, implied-vol changes are dominated by **buying pressure for index puts**; for **individual stock options**, by **call demand**. Demand for OTM index puts is what bends the smile upward on the downside.
- **Relevance:** Explains *why* the index VRP exists (limits to arbitrage + one-sided hedging demand) and predicts where the richness sits: the **index put skew** and the **single-name call side**. It also implies the premium is a *demand* phenomenon and can therefore change when demand changes — which is exactly what the 0DTE papers document post-2022.
- **Caveats:** 1995–2000 sample; descriptive, not a trading study.

### S5 — Beckmeyer, Branger & Gayda (2023/2024), "Retail Traders Love 0DTE Options… But Should They?"
- **Citation:** Beckmeyer, H., N. Branger and L. Gayda. "Retail Traders Love 0DTE Options... But Should They?" Working paper, University of Münster; version of **15 Dec 2023**, first version 30 Mar 2023. SSRN 4404704. Open copy: FoFI 2024 conference PDF.
- **Type / venue / year:** **working paper** (conference-refereed: FoFI 2024, German Finance Association 2023, IFABS 2023). Not yet peer-reviewed at the version read.
- **Citations:** not verified (S2 API rate-limited); heavily discussed in trade press.
- **Quality verdict:** citation-worthy — **with caveats**. Excellent data (Cboe SLAN/MLAT retail identification + Open/Close data, Feb 2021 – Sep 2023), transparent methodology, but a working paper and it measures *retail behaviour*, not an optimised strategy.
- **Key findings (all with numbers):**
  - >75 % of retail S&P 500 option volume is 0DTE; retail share of 0DTE volume >6 %; >40 % of all SPX contracts traded now expire same-day.
  - **Aggregate retail loss >$125 million** over ~3 years; **>$90 million of it is transaction costs**. Average daily loss **$241k** full sample, **$350k** after the May-2022 daily-expiry launch. ~**60 % of daily losses are transaction costs**.
  - **Debit vs credit:** retail lost **$364k/day on debit orders** after costs and **made $122k/day on credit orders**. The authors explicitly attribute the credit-side profit to harvesting the variance risk premium (citing Coval & Shumway).
  - **Effective spreads (0DTE SPX):** retail **6.0 % (calls) / 5.0 % (puts)** of mid; non-retail **12.5 % / 9.6 %**. Spreads *widen* into expiry. Sell orders get better spreads than buy orders.
  - **Margin-adjusted per-trade returns (Table 4, % of margin, incl. costs):**

    | Strategy | Vol % | Mean | P5 | P25 | Median | P75 | P95 |
    |---|---|---|---|---|---|---|---|
    | Put (single leg) | 34.2 | −5.6 | −100 | −100 | −0.7 | 0.6 | 182.0 |
    | Call (single leg) | 31.3 | −9.4 | −100 | −100 | −0.8 | 0.6 | 178.6 |
    | Put spread | 12.7 | **+0.1** | −100 | −76.7 | **+3.0** | 14.0 | 112.8 |
    | Call spread | 11.6 | −0.2 | −100 | −65.3 | **+3.3** | 16.5 | 110.5 |
    | **Iron condor** | 3.6 | **−1.1** | **−100** | **−24.0** | **+5.5** | 15.4 | 63.9 |
    | Butterfly | 3.2 | −3.5 | −100 | −100 | −7.2 | 14.8 | 228.8 |
    | Iron butterfly | 2.0 | −0.9 | −92.3 | −28.8 | −1.2 | 33.5 | 84.3 |
    | Condor | 0.8 | +0.6 | −100 | −48.8 | +3.0 | 15.0 | 108.3 |
    | Strangle | 0.3 | −1.5 | −100 | −71.2 | 0.0 | 0.5 | 159.4 |
    | Straddle | 0.3 | −0.7 | −87.7 | −28.3 | −0.1 | 2.1 | 105.5 |

  - Multi-leg positions net **+0.17 %** more than single-leg. Trades requiring an **upfront payment (debit) earn significantly negative returns** — "which reflects the average additional compensation for the option seller."
  - High-IV contracts and high-IV days are where retail loses most.
- **Relevance:** **The single most directly applicable source in this review.** It gives the empirical, cost-inclusive per-trade distribution of exactly the structures we are considering (0DTE iron condors and credit spreads), from which the 2-day P&L distribution can be simulated directly.
- **Caveats:** (a) It is a *retail behaviour* sample, not an optimised systematic strategy — a disciplined rules-based seller should do better than the mean, but probably not dramatically. (b) Direction of multi-leg trades (short vs long condor) is not fully separated. (c) Iron condor is only 3.6 % of volume, so the tail estimates are noisier. (d) Working paper.

### S6 — Almeida, Freire & Hizmeri (2025), "0DTE Asset Pricing"
- **Citation:** Almeida, C., G. Freire and R. Hizmeri. "0DTE Asset Pricing." Working paper, draft 23 May 2025 (first draft 20 Jan 2024). SSRN 4701401. Open PDF via FMA Derivatives 2025.
- **Type / venue / year:** **working paper**, extensively conference-presented (SoFiE 2024, MFA 2025, Paris December Finance 2024, ES Summer Meeting 2024) with named discussants including Oleg Bondarenko.
- **Citations:** not verified.
- **Quality verdict:** citation-worthy — **with caveats** (working paper, but very high quality; sample **6 Jan 2012 – 18 Mar 2025**, intraday).
- **Key findings:**
  - 0DTE options now ≈**half of all S&P 500 option volume**.
  - The 0DTE **variance risk premium is large and significantly positive**, but — unlike longer maturities — it is **driven almost entirely by compensation for UPSIDE risk**. In their Table OA.3 the upside component `VRP+` is strongly positive (≈0.88–1.97 annualised pts before May 2022; 1.11–1.97 after), while the downside component `VRP−` is **negative** (≈−0.10 to −0.26 before; −0.20 to −0.49 after). The aggregate 0DTE VRP is 1.6–3.3 annualised points and *smaller after May 2022*.
  - Only ~**30 % of 0DTE options (6 % of ATM ones)** satisfy stochastic-dominance price bounds under risk-averse preferences, vs **97 % of one-month options** — violations increase monotonically as maturity shortens.
  - **Decisive for us:** the benchmark strategy of *always writing the delta-hedged ATM 0DTE call* earns per-trade Sharpe ratios of **−0.016 to +0.017 before costs** and **−0.042 to −0.010 AFTER costs**, at every entry time from 10:00 to 14:00. Their smarter SSD-violation strategy earns 0.10–0.19 after costs, but its profitability **"dissipates" after May 2022** as the 0DTE market became more efficient and integrated with the underlying.
- **Relevance:** The strongest evidence against naive 0DTE premium selling. Also the source of a genuinely actionable, counterintuitive tilt: at 0DTE the *call/upside* side carries the premium, not the put side.
- **Caveats:** Working paper; the delta-hedged benchmark is *ATM*, and OTM structures with defined risk may behave differently; "after costs" uses the worst case (always cross to bid/ask), which is more pessimistic than good limit-order execution.

### S7 — Bandi, Fusari & Renò (2023–2024), "0DTE Option Pricing"
- **Citation:** Bandi, F. M., N. Fusari and R. Renò. "0DTE Option Pricing." Draft 15 Mar 2024, first draft 7 Jul 2023. SSRN 4503344. Reported as forthcoming/published in the *Journal of Finance*.
- **Type / venue / year:** working paper → top-journal forthcoming, 2023–2024.
- **Quality verdict:** citation-worthy — **yes** (for the pricing/hedging point only).
- **Key findings:** Closed-form Edgeworth-type expansions of the log-return characteristic function specifically for ultra-short tenors; skewness and kurtosis adjustments depend on non-affine return characteristics. **Significant improvements in pricing and hedging vs. state-of-the-art models.** Ends with "suggestive results on nearly instantaneous predictability" via instantaneous return and variance risk premia.
- **Relevance:** A methodological warning: **standard Black–Scholes / affine-model deltas and IVs are materially mis-specified at 0DTE.** The "16-delta" strike that a broker feed reports for a 0DTE option is not a reliable probability estimate. Use realised-distribution or expected-move sizing as a cross-check.
- **Caveats:** A pricing paper, not a strategy paper. No tradeable P&L numbers.

### S8 — Israelov & Nielsen (2014), "Covered Call Strategies: One Fact and Eight Myths"
- **Citation:** Israelov, R. and L. N. Nielsen (2014). *Financial Analysts Journal* 70(6), 23–31. Open PDF at aqr.com.
- **Type / venue / year:** peer-reviewed practitioner journal (FAJ), **2014** (the user's "2015" is the calendar year of some reprints; the issue is Nov/Dec 2014).
- **Quality verdict:** citation-worthy — **with caveats**: FAJ is refereed and the decomposition is rigorous, but the authors are AQR, which sells alternative-risk-premium products; treat directional conclusions as mildly interested.
- **Key findings:**
  - BXM vs S&P 500, **1 Jul 1986 – 31 Dec 2013** (excess of 3-month LIBOR): annualised excess return **4.4 % vs 5.4 %**; volatility **13.4 % vs 18.5 %**; Sharpe **0.33 vs 0.29**; worst drawdown **−43.0 % vs −61.7 %**; beta **0.67**, with **upside beta 0.63 but downside beta 0.78** — the covered call keeps more of the downside than of the upside.
  - Decomposition: a covered call = long equity + short straddle + an *uncompensated* equity-reversal exposure. **Roughly two-thirds of the risk is the equity risk premium; one-third is the short-straddle (volatility) exposure.** The short-volatility component realises a **Sharpe near 1.0 but contributes only ~10 % of total risk**; the reversal component contributes ~25 % of risk for little return.
  - Stylised example (18 % implied vs 16 % realised vol): the ATM covered call earns **2.94 %/yr from equity exposure and 2.76 %/yr from the VRP**; only **~11 % of the collected option premium ($0.23 of $2.07) is VRP compensation**. A 4 %-OTM covered call earns 6.65 %/yr = **4.60 % equity + 2.05 % VRP**.
- **Relevance:** **Answers Q4 definitively and kills the "income strategy" idea for a 2-day window.** The harvestable option alpha in a covered call / cash-secured put is ~2–3 % *per year*, i.e. ~**0.025 % over 2.5 trading days ≈ $25 on $100k**. Everything else you would collect is equity beta — an unhedged directional bet dressed up as income.
- **Caveats:** AQR authorship; the stylised numbers assume a 2-vol-point VRP.

### S9 — Wilshire Analytics for Cboe (2019), "Options-Based Benchmark Indexes: Performance, Risk and Premium Capture (June 1986–Dec. 2018)"
- **Citation:** Wilshire Analytics, March 2019, prepared for Cboe. cdn.cboe.com/resources/spx/wilshire-options-based-benchmark-indexes-2019.pdf
- **Type / venue / year:** **industry research, sponsor-funded** ("Prepared for" Cboe), 2019.
- **Quality verdict:** citation-worthy — **with caveats**. Numbers are auditable index statistics, but the study is **paid for by the exchange that profits from options volume**, and the indexes are frictionless (explicitly "do not take into account significant factors such as transaction costs and taxes") and partly back-tested. Use the numbers, discount the conclusions.
- **Key findings (32.5 years, 30 Jun 1986 – 31 Dec 2018):**
  - Annualised return / vol: **BXMD 10.2 % / 12.8 %**, **S&P 500 9.8 % / 14.9 %**, **PUT 9.5 % / ~9.9 %**, **CMBO 9.6 % / ~10.9 %**, **BXM 9.2 % / ~12.1 %**, PPUT 6.6 %.
  - Sharpe: BXMD 0.80, S&P 500 0.66, CMBO 0.84, PPUT 0.55 (as printed; layout garbled in the PDF text extraction — treat exact assignment with care). PUT's Sharpe is stated to be **46 % greater** than the S&P 500's.
  - Max drawdowns: **PUT −35.53 %, BXM −35.81 %, CMBO −38.13 %, PPUT −38.92 %, BXMD −42.73 %, S&P 500 −50.95 %.**
  - Skewness: BXMD −1.11, CMBO −1.53, S&P 500 −0.81. Option-selling indexes have **fatter tails and more negative skew**.
  - **VIX exceeded subsequent realised volatility by at least 1 % and by as much as 54 % in all but one of the past 21 years.**
- **Relevance:** Establishes that index premium-selling is a *long-horizon* Sharpe improvement of maybe +0.1 to +0.2 with materially negative skew — again a multi-year proposition, not a 2-day one.
- **Caveats:** sponsor conflict; frictionless indexes; monthly rebalancing only.

### S10 — Cboe Benchmark Indexes Fact Sheet (2020)
- **Citation:** Cboe Exchange, Inc., "Benchmark Indexes" fact sheet, cdn.cboe.com/resources/indices/documents/benchmarks-fact-sheet.pdf (data through 31 Dec 2019).
- **Type / venue / year:** **industry factsheet / marketing**, ~2020.
- **Quality verdict:** citation-worthy — **with caveats** (exchange marketing; index values are objective, framing is not; back-tested pre-launch data).
- **Key findings — the defined-risk vs undefined-risk comparison (max drawdown, 2006–2019):**
  - **CNDR (Cboe S&P 500 Iron Condor Index) −13.7 %** ← *defined risk*
  - PUT (PutWrite) −32.7 %, BXM (BuyWrite) −35.8 %, PXEF −37.0 %, VXTH −37.4 %, PUTR −38.1 %, BXEA −43.6 %, VPN −48.1 %
  - **S&P 500 −51.0 %**, Russell 2000 −52.9 %, MSCI EM −61.6 %, S&P GSCI −80.9 %
  - CNDR rules (from the Cboe methodology): monthly, sell ~**−20 delta** SPX put and ~**+20 delta** SPX call, buy ~**5 delta** put and ~5 delta call as wings, hold T-bills against it.
- **Relevance:** This is the cleanest single statistic for the risk-averse user: **the same premium-selling exposure, with wings bought, cut the worst drawdown from −33 %/−36 % to −13.7 % — a ~60 % reduction in tail loss.** Directly justifies "always buy the wings."
- **Caveats:** CNDR's *return* is materially lower than PUT/BXM (the wings cost money); the fact sheet does not print CNDR's annualised return, so I have not stated one. No transaction costs.

### S11 — Augustin, Cheng & Van den Bergen (2021), "Volmageddon and the Failure of Short Volatility Products"
- **Citation:** Augustin, P., I.-H. Cheng and L. Van den Bergen (2021). *Financial Analysts Journal* 77(3), 35–51. DOI 10.1080/0015198X.2021.1913040. Open version in the U. Toronto TSpace repository.
- **Type / venue / year:** peer-reviewed practitioner journal (FAJ), 2021.
- **Quality verdict:** citation-worthy — **yes**.
- **Key findings:** On **5 Feb 2018** short-volatility ETPs lost **>90 % of value in a single day**; inverse-vol ETPs lost ~**$3 billion in 50 minutes**. XIV fell from ~$108 to ~$4 (**−96 %**) and was terminated 21 Feb 2018. VIX rose from 17.31 to 37.32 (**+115 %**) in one session. Context: the S&P 500 VIX Short-Term Futures Index had **64.0 %** average trailing 90-day volatility over 2007–2017, vs **17.4 %** for the S&P 500. Mechanism: hedge- and leverage-rebalancing feedback loops in a concentrated market, analogous to 1987 portfolio insurance.
- **Relevance:** The canonical tail event for short volatility, and the reason a **2-day window is not "too short to be dangerous"** — Volmageddon *was* one afternoon. Also the reason to have no undefined-risk legs whatsoever.
- **Caveats:** About levered ETPs specifically, not about option sellers directly; a defined-risk seller would have lost the wing width, not 96 %.

### S12 — Gao, Xing & Zhang (2018), "Anticipating Uncertainty: Straddles around Earnings Announcements"
- **Citation:** Gao, C., Y. Xing and X. Zhang (2018). *Journal of Financial and Quantitative Analysis* 53(6), 2587–2617. DOI 10.1017/S0022109018000285. **Note: JFQA, not RFS** (the brief said RFS).
- **Type / venue / year:** peer-reviewed journal, JFQA, 2018.
- **Quality verdict:** citation-worthy — **yes**, with an execution caveat (see below).
- **Key findings (OptionMetrics, individual stocks, **Jan 1996 – Dec 2013**, delta-neutral ATM straddles, day 0 = announcement):**

  | Window | Equal-weight return | t | Dollar-OI-weight return | t |
  |---|---|---|---|---|
  | [−3,−1] | **+2.62 %** | 9.67 | +1.37 % | 3.81 |
  | [−3, 0] | **+3.34 %** | 6.71 | +1.10 % | 2.00 |
  | [−3,+1] | +2.10 % | 2.99 | −0.67 % | −1.06 |
  | [−1, 0] | +2.59 % | 7.44 | +0.54 % | 1.78 |
  | [ 0,+1] | **−0.33 %** | −1.04 | **−1.37 %** | −3.07 |

  - Baseline: straddles on individual stocks **generally earn negative and significant returns** outside earnings.
  - The pre-announcement gain is *larger* for smaller, more volatile, higher-kurtosis firms with **less volume and higher transaction costs** — i.e. precisely where you cannot trade it.
- **Relevance / the exploitable pattern:** The robust pattern is **BUY the straddle ~3 days before the announcement and exit at or before the announcement** — the opposite of the popular "sell the IV crush" folklore. The IV-crush trade (short straddle over [0,+1]) is significant only in the **dollar-open-interest-weighted** (large, liquid) sample, at **−1.37 %** for the long side.
- **Caveats:** **All returns are computed on closing bid-ask midpoints, with no transaction costs.** Single-name equity option spreads are wide (see S14/S5), and a 1–3 % gross edge is comparable to a round-trip spread. Also, the calendar matters: **the first week of September is a near-empty earnings window**, so this pattern is largely unavailable to us on 2–4 Sep.

### S13 — Dubinsky, Johannes, Kaeck & Seeger (2019), "Option Pricing of Earnings Announcement Risks"
- **Citation:** Dubinsky, A., M. Johannes, A. Kaeck and N. J. Seeger (2019). *Review of Financial Studies* 32(2), 646–687.
- **Type / venue / year:** peer-reviewed journal, RFS, 2019. Open version in the VU Amsterdam research portal.
- **Quality verdict:** citation-worthy — **yes**.
- **Key findings (verified at abstract level only):** Reduced-form models and estimators that **separate earnings-announcement price uncertainty from ordinary day-to-day volatility** using option prices. The anticipated announcement uncertainty is **quantitatively large, time-varying, and predictive of future realised volatility**. Quantifies the effect of announcements on formal option pricing models.
- **Relevance:** Method, not a signal: it tells you the correct way to strip the earnings jump out of an implied vol before comparing implied to realised. If we ever compare "implied move vs realised move," this is the right decomposition.
- **Caveats:** **Paywalled for the numeric tables** — I did not extract the implied-vs-realised magnitudes. Listed under "Paywalled / wanted."

### S14 — Muravyev & Pearson (2020), "Options Trading Costs Are Lower than You Think"
- **Citation:** Muravyev, D. and N. D. Pearson (2020). *Review of Financial Studies* 33(11), 4973–5014. DOI 10.1093/rfs/hhaa010. Open working-paper version: cicfconf.org/sites/default/files/paper_745.pdf.
- **Type / venue / year:** peer-reviewed journal, RFS, 2020.
- **Quality verdict:** citation-worthy — **yes**.
- **Key findings (equity options, **Apr 2003 – Oct 2006**, tick data):**
  - Average **quoted spread 8.1 cents/share**; conventionally measured **effective spread 6.2 cents**.
  - For the ~**40 %** of trades that time execution against high-frequency option-fair-value movement, the timing-adjusted effective spread is only **1.3 cents — 21 % of the conventional effective spread and 16 % of the quoted spread.** By the last sample month this was **1.1 cents** and the timing share had grown to **54 %**.
  - Averaged over *all* trades, the timing-adjusted effective spread is **67 % of the conventional effective spread and 53 % of the quoted spread**; it fell from 5.5 to 3.5 cents over the sample.
  - Quoted spreads rise steeply with moneyness (**<7 cents OTM vs 11 cents ITM**) but the timing-adjusted spread is nearly flat (**4 → 6 cents**, and completely flat at 5 cents for large ITM trades). The residual ≈1.5 cents is the market maker's own delta-hedging cost in the stock (stock spread 1.4 cents).
- **Relevance:** **The core execution result: most of the quoted spread is avoidable through patience and timing, not through better routing.** Concretely: place limit orders at or inside the mid on the whole multi-leg package; do not lift the offer. Also: prefer **OTM** strikes, whose quoted spreads are narrowest in cents.
- **Caveats:** 2003–2006 equity options, pre-penny-pilot for many classes; index and 0DTE spreads today behave differently (see S5, which reports 0DTE effective spreads of **5–12 % of mid**, far worse in relative terms).

### S15 — Constantinides, Jackwerth & Savov (2013), "The Puzzle of Index Option Returns"
- **Citation:** Constantinides, G. M., J. C. Jackwerth and A. Savov (2013). *Review of Asset Pricing Studies* 3(2), 229–257. Open PDF at pages.stern.nyu.edu/~asavov.
- **Type / venue / year:** peer-reviewed journal, RAPS, 2013.
- **Quality verdict:** citation-worthy — **yes**.
- **Key findings:** Builds a panel of S&P 500 call and put portfolios **daily rebalanced to constant maturity, moneyness and unit market beta** (1986–2010), making standard linear factor methods applicable (the leverage-adjusted returns are near-normal). Leverage-adjusted returns **decrease in the strike-to-price ratio**, contrary to Black–Scholes. Only factors capturing **jumps in the index and jumps in market volatility**, and to a lesser extent volatility and liquidity, explain the cross-section. Crucially, the required factor premia are **economically and statistically different across calls vs puts, maturities and moneyness** — evidence of **market segmentation**, not one unified premium.
- **Relevance:** The main methodological caution. There is no single "option risk premium" you can dial up by selling anything; the compensation is specific to jump exposure, and it is *segmented*. It also explains why 0DTE (extreme jump-sensitivity) behaves differently from 30-day options.
- **Caveats:** Ends 2010; pre-0DTE.

### S16 — Dim, Eraker & Vilkov (2024), "0DTEs: Trading, Gamma Risk and Volatility Propagation"
- **Citation:** Dim, C., B. Eraker and G. Vilkov. Working paper, SSRN 4692190, 2024.
- **Type / venue / year:** **working paper**, 2024 (WFA-portal, Oxford Mathematical Institute seminar).
- **Quality verdict:** citation-worthy — **with caveats** (working paper).
- **Key findings:** Contrary to the "0DTE amplifies crashes" narrative, **high 0DTE open-interest gamma is associated with LOWER realised intraday volatility**, and does not propagate overnight. Intraday 0DTE volume shocks do not amplify recent index returns. The dampening comes from a shift in market makers' hedging needs, driven mainly by *previously accumulated longer-dated positions that become 0DTE*, not by same-day trading.
- **Relevance:** Modest good news for a short-gamma book: the systemic "0DTE doom loop" story is not supported. Do not build the strategy on an expectation of 0DTE-driven crash amplification, and do not use it as a scare argument either.
- **Caveats:** Working paper; contested (see S17); "on average" results say nothing about the conditional tail.

### S17 — Brogaard, Han & Won (2023), "Does 0DTE Options Trading Increase Volatility?"
- **Citation:** Brogaard, J., J. Han and P. Y. Won. Working paper, SSRN 4426358, April 2023.
- **Type / venue / year:** **working paper**, 2023.
- **Quality verdict:** citation-worthy — **with caveats** (working paper; contradicts S16).
- **Key findings:** Index 0DTE monthly volume grew from **0.08 million contracts (Jan 2011) to 34.4 million (Aug 2023)**, ~**48 % of index option trading**. Using the staggered introduction of weekly options as an instrument, a one-standard-deviation increase in 0DTE trading raises volatility by **9.10 % relative to its mean (15.91 % of its standard deviation)**.
- **Relevance:** The direct counterweight to S16. Net read: **the literature is genuinely unsettled on whether 0DTE flow raises or dampens realised volatility.** Do not condition the strategy on either view.
- **Caveats:** Working paper; IV identification is contestable; opposite sign to S16.

### S18 — Adams, Fontaine & Ornthanalai (2024), "The Market for 0DTE: The Role of Liquidity Providers in Volatility Attenuation"
- **Citation:** Adams, G., J.-S. Fontaine and C. Ornthanalai. Working paper (Bank of Canada / University of Toronto), SSRN 4881008, 2024.
- **Type / venue / year:** **working paper**, central-bank affiliated, 2024. (This is the paper the brief referred to as "Adams, Fontaine & Ornthanalai (0DTE asset pricing)"; the "0DTE Asset Pricing" title belongs to Almeida/Freire/Hizmeri — see S6.)
- **Quality verdict:** citation-worthy — **with caveats** (working paper, but central-bank research quality; intraday 2019–2023 data).
- **Key findings:** Option market makers' intermediation of 0DTE SPX options **lowers** index volatility on average, with realised index volatility **60–90 annualised basis points lower on days with 0DTE trading**.
- **Relevance:** Third data point on the same contested question, siding with S16.
- **Caveats:** Working paper; average effect only.

---

## Evidence table

| # | Claim | Supporting sources | Contradicting / qualifying | Confidence |
|---|---|---|---|---|
| C1 | A **variance risk premium exists in index options**: implied variance systematically exceeds subsequent realised variance | S1 (Carr–Wu), S2 (Bakshi–Kapadia), S3 (Coval–Shumway), S9 (VIX > RV in 20 of 21 years) | — | **High** |
| C2 | The VRP is **much weaker/absent in single-name options** than in index options | S1 (weak for the 35 stocks), S4 (single-name IV driven by call demand, not put-hedging), S12 (single-name straddles earn negative returns generally) | — | **High** |
| C3 | The VRP is **economically small per unit of time**: ~10–11 % of an ATM option's premium, ~2–3 % per year of notional in a covered call | S2 (−12.18 % of call price per 14–60 day trade), S8 (11 % of premium; 2.05–2.76 %/yr) | — | **High** |
| C4 | **A 0DTE VRP exists but is largely eliminated by transaction costs** | S6 (short delta-hedged ATM 0DTE call: Sharpe −0.042 to −0.010 after costs), S5 (60 % of retail 0DTE losses are costs; effective spreads 5–12 % of mid) | S5 (credit orders made +$122k/day net; iron condor median +5.5 % of margin) | **Medium-high** |
| C5 | The **0DTE edge shrank after May 2022** (daily expirations) | S6 (SSD strategy profit "dissipates"; smaller VRP after May 2022), S5 (retail losses accelerated to $350k/day after May 2022) | — | **Medium** |
| C6 | At 0DTE the premium sits on the **upside/call side**, not the downside | S6 (VRP+ strongly positive, VRP− negative) | S2 (at 14–60 DTE, far-OTM calls had *positive* delta-hedged gains — but different maturity and 1988–1995 sample); S4 (index put demand drives IV) | **Low-medium** |
| C7 | **Defined-risk selling has dramatically smaller drawdowns** than undefined-risk selling | S10 (CNDR −13.7 % vs PUT −32.7 %, BXM −35.8 %), S11 (short-vol ETPs −90 % in one day), S5 (iron condor P5 = −100 % of margin, i.e. bounded, vs single-leg tails) | — | **High** |
| C8 | **Multi-leg / credit structures outperform single-leg / debit structures** for short-dated trading | S5 (multi-leg +0.17 % vs single-leg; credit +$122k/day vs debit −$364k/day; spread medians +3.0/+3.3 %, IC median +5.5 %) | S6 (naive short delta-hedged ATM is negative net of costs) | **Medium-high** |
| C9 | Even the best defined-risk 0DTE structure has **mean per-trade return ≈ 0 or slightly negative after costs**, with a **high win rate** (positive median) | S5 (IC: mean −1.1 %, median +5.5 %), S6 (negative net Sharpe for the naive benchmark) | — | **Medium-high** |
| C10 | **Covered calls / cash-secured puts are mostly equity beta**, not option alpha | S8 (two-thirds of risk from equity; VRP 2.05–2.76 %/yr), S9 (PUT/BXM returns and drawdowns track equity) | — | **High** |
| C11 | **Buying** ATM straddles ~3 days before earnings has positive gross returns; the popular "sell the IV crush" is much weaker | S12 (+2.62 % [−3,−1], +3.34 % [−3,0]; post-announcement short only −1.37 % and only in the liquid subsample) | S12 itself: midpoint pricing, no transaction costs; effect strongest where costs are highest | **Medium** (gross), **Low** (net of costs) |
| C12 | **Most of the quoted option spread is avoidable** through patient limit-order placement | S14 (1.3 vs 6.2 vs 8.1 cents; 40→54 % of trades time execution), S5 (retail price improvement halves effective spreads) | S5 (even with price improvement, 0DTE effective spreads remain 5–6 % of mid) | **High** |
| C13 | **Option transaction costs at 0DTE are large relative to the edge** and widen into expiry | S5 (5.0–6.0 % retail, 9.6–12.5 % non-retail; spreads widen approaching expiry), S6 (costs flip Sharpe from +0.017 to −0.033) | — | **High** |
| C14 | Short-dated structures are the **only** way to accrue meaningful theta in a 2-day window | Arithmetic from ATM straddle value ≈0.8·σ·S·√T (0DTE ≈0.76 % of spot/day vs 30-DTE ≈0.07 %/day), consistent with S8's small annual VRP | — | **High** (it is arithmetic) |
| C15 | Option-selling returns have **strongly negative skew and fat tails** | S9 (skewness −1.11 to −1.53 vs −0.81 for S&P 500), S11, S5 (P5 = −100 % of margin) | — | **High** |
| C16 | 0DTE flow's effect on realised volatility is **unsettled** | S16 + S18 (dampens: −60 to −90 annualised bp) | S17 (amplifies: +9.10 % of mean volatility per 1 s.d.) | **Low** (genuinely contested) |
| C17 | Standard model deltas/IVs are **mis-specified at 0DTE** | S7 (non-affine skew/kurtosis corrections materially improve pricing and hedging), S6 (94 % of ATM 0DTE options violate risk-averse price bounds) | — | **Medium-high** |
| C18 | Over 2.5 trading days, **no options strategy's edge is statistically distinguishable from noise** | Arithmetic: a generous daily Sharpe of 0.1 gives t ≈ 0.1·√2.5 ≈ 0.16; S6's realised per-trade Sharpes are ≤0.02 gross and negative net | — | **High** |

---

## Answers to research questions 1–6

### Q1 — Volatility risk premium: magnitude, robustness, index vs single-name, and short-dated evidence

**Magnitude and robustness.** The VRP is about as robust as anything in empirical asset pricing. It shows up in three independent measurement designs that all agree in sign:

- *Delta-hedged portfolios* (S2): buying and delta-hedging S&P 500 calls loses **0.05 % of the index level on average, 0.10 % for ATM**, or **−12.18 % of the option price** per 14–60-day trade, negative in **68–72 %** of ATM cases, statistically significant in every moneyness/maturity cell (1988–1995).
- *Zero-beta straddles* (S3): **−3 % per week** for the buyer, 1986–1995.
- *Model-free variance swaps* (S1): index variance swap rates systematically exceed realised variance across five indexes.
- *Index level* (S9): VIX exceeded subsequent realised volatility by 1–54 % in **20 of 21 years**.

**But the magnitude is small per unit of time.** S8 pins it: with 18 % implied vs 16 % realised vol, only **~11 % of the collected option premium** is VRP compensation; annualised, the VRP contributes **2.05–2.76 % per year** to a covered call. That is the number that matters for horizon reasoning.

**Index vs single-name.** The premium is an *index* phenomenon. S1 finds it much weaker and often insignificant for the 35 individual stocks. S4 explains why: index IV is driven by one-sided **put-hedging demand** (a genuine insurance premium), whereas single-name IV is driven by **call demand** (lottery-seeking, which if anything makes single-name calls expensive but with no stable, harvestable structure). S12 confirms single-name straddles "generally earn negative and significant returns" — so there *is* a single-name short-vol premium, but S12 also shows it reverses around the one event we might want to trade (earnings). **Implication: trade index ETFs, not single names.**

**Short-dated (0–7 DTE) evidence.** This is where the classic result *does not carry over cleanly*:

- S6 finds a large, significant 0DTE VRP — but decomposed, it is **almost entirely upside** (`VRP+` ≈ +0.9 to +2.0 annualised points; `VRP−` **negative**, −0.10 to −0.49). And **the naive harvest fails**: writing the delta-hedged ATM 0DTE call earns per-trade Sharpe of **−0.042 to −0.010 after transaction costs** at every entry time between 10:00 and 14:00, over 2012–2025.
- S6 also documents that the 0DTE market **became more efficient after May 2022**: only ~30 % of 0DTE options (6 % of ATM) satisfy risk-averse price bounds vs 97 % of one-month options, and the profitable mispricing strategy's returns "stagnate" post-2022.
- S5 gives the cost-inclusive retail cross-section: **credit orders made money (+$122k/day aggregate), debit orders lost ($364k/day)**; multi-leg beat single-leg by 0.17 %; iron condor median margin-adjusted return **+5.5 %** but mean **−1.1 %**.
- S7 adds that 0DTE options need **non-affine skew/kurtosis corrections** — your broker's delta is not a reliable probability.

**Verdict for Q1:** the VRP is real, robust, index-concentrated, and *small*. At 0DTE it still exists but is concentrated in upside variance and is roughly the same size as the transaction costs required to harvest it.

### Q2 — Defined-risk premium-selling structures and the tail-risk history

**Return and drawdown evidence.**
- Long-horizon Cboe benchmarks (S9, 1986–2018): PUT 9.5 %/yr at 9.9 % vol, BXM 9.2 % at ~12 %, BXMD 10.2 % at 12.8 %, vs S&P 500 9.8 % at 14.9 %. Sharpe improvement of roughly +0.1 to +0.2. Skewness **−1.11 to −1.53** vs −0.81 for the index. So: *slightly* better Sharpe, *distinctly* worse skew.
- Defined-risk versions cost return but transform the tail. **CNDR's maximum drawdown 2006–2019 was −13.7 % vs PUT −32.7 %, BXM −35.8 %, S&P 500 −51.0 %** (S10). Buying the wings cut the worst loss by roughly 60 %.
- At the trade level, S5's iron condor row shows the same structure in miniature: **P5 = −100 % of posted margin** — i.e. a total loss of the capital *allocated to that trade*, and no more. A short strangle's P5 is also −100 % of margin, but margin for an undefined-risk strangle is a *fraction* of the possible loss, so the true tail is unbounded.

**The three stress episodes.**
- **Aug 2015** (24 Aug flash crash): SPX gapped ~5 % lower at the open, VIX printed above 50. Undefined-risk sellers faced margin calls at the worst possible quotes; defined-risk sellers lost exactly the wing width. I did not find a peer-reviewed quantification of option-seller losses for this date and have not invented one.
- **Feb 2018 "Volmageddon"** (S11): VIX **17.31 → 37.32 (+115 %) in one session**; short-vol ETPs **−90 %+ in a day**, ~**$3bn lost in 50 minutes**, XIV **−96 %** and terminated. A 16-delta short SPX strangle would have lost many multiples of the credit; a 16-delta iron condor with 5-wide wings would have lost at most the wing width minus the credit.
- **Mar 2020**: index drawdowns of the magnitude that produced BXM's −35.8 % and PUT's −32.7 % index-level drawdowns (S10 covers 2006–2019, so Mar 2020 sits just outside; S9's −35.53 %/−35.81 % figures cover 1986–2018 and are dominated by 2008).

**Verdict for Q2:** defined-risk structures give up a meaningful share of the premium and cap the disaster. For a risk-averse operator with a hard deadline and a public scoreboard, that trade is clearly correct: **never sell a naked or unwinged option in this window.**

### Q3 — Earnings announcements

**The exploitable pattern is the opposite of the folklore.** S12 (JFQA 2018, 1996–2013):

- Straddles bought **3 days before** and held **to the day before** the announcement: **+2.62 %** (t = 9.67) equal-weighted, **+1.37 %** (t = 3.81) dollar-OI-weighted.
- Held **through** the announcement date: **+3.34 %** (t = 6.71) equal-weighted.
- Held to **day +1**: the equal-weighted return falls to +2.10 % and the OI-weighted return turns **negative (−0.67 %, t = −1.06)**.
- The isolated **[0,+1]** post-announcement window: **−0.33 %** (t = −1.04) equal-weighted, **−1.37 %** (t = −3.07) OI-weighted.

So: the *pre-announcement* build-up in uncertainty is systematically **under**priced (buy vol), and the *post-announcement* crush is real but modest and only statistically significant in the large-and-liquid subsample.

**Is it robust?** Gross, yes — large t-statistics, 18 years, consistent across weighting schemes. Net, doubtful: **all returns use closing bid-ask midpoints with no transaction costs**, and the effect is strongest exactly where costs are highest (small firms, low volume, wide spreads) — the authors say so themselves and use it as their explanation. S13 provides the correct machinery for separating announcement uncertainty from ordinary volatility but I could not extract its magnitudes (paywalled).

**For our window:** 2–4 September is essentially between earnings seasons. Even if the pattern were net-profitable, the tradeable universe over three sessions would be a handful of names with wide single-name option spreads — the worst possible cost environment (see C2, C13). **Recommendation: do not build the strategy on earnings. At most, treat it as an optional, small, opportunistic long-straddle/long-strangle sleeve on a liquid large cap reporting on 3 or 4 Sep, sized at ≤0.5 % of capital, and only if the spread is tight.**

### Q4 — "Portfolio income" strategies: alpha or beta + VRP?

**Overwhelmingly beta plus a thin slice of VRP.** S8 decomposes a covered call into long equity + short straddle + an uncompensated equity-reversal exposure and reports:

- **~2/3 of the risk is the equity risk premium**, ~1/3 is the short-straddle exposure; the equity-reversal component contributes ~25 % of risk for essentially no return.
- The short-volatility component has a **Sharpe near 1.0 but supplies only ~10 % of total risk**.
- In the stylised 18 %-implied / 16 %-realised example: the ATM covered call earns **2.94 %/yr from equity + 2.76 %/yr from VRP**; the 4 %-OTM version **4.60 % equity + 2.05 % VRP**.
- BXM vs S&P 500 1986–2013: **4.4 % vs 5.4 %** excess return, **13.4 % vs 18.5 %** vol, Sharpe **0.33 vs 0.29**, drawdown **−43.0 % vs −61.7 %**, beta 0.67 — but **upside beta 0.63 vs downside beta 0.78**: you keep more of the falls than of the rises.

**Relevance in a 2-day window: essentially zero.** A 2.0–2.8 %/yr VRP is **0.020–0.028 % over 2.5 trading days**, i.e. **$20–$28 on $100,000 of notional exposure**. Whatever P&L a covered call or cash-secured put shows on Friday morning will be, to three significant figures, **the directional move of the underlying** — an unhedged equity bet with a small negative-skew overlay, not an income strategy. If the agent runs covered calls or CSPs, it should say so honestly in the write-up rather than present them as premium harvesting.

### Q5 — THE HORIZON QUESTION

**The theta arithmetic.** For an ATM straddle, value ≈ `0.8 · σ · S · √T` (T in years). At σ = 15 %:

| Structure | Straddle value (% of spot) | One-day decay (% of spot) |
|---|---|---|
| 0DTE ATM | 0.76 % | **0.76 %** (all of it) |
| 7-DTE ATM | 2.00 % | ~0.15 % |
| 30-DTE ATM | 4.14 % | **~0.07 %** |
| 45-DTE ATM | 5.07 % | ~0.056 % |

So a 0DTE structure accrues roughly **11× more theta per day** than a 30–45 DTE structure. **Only short-dated structures can produce a visible number in 2.5 days.**

**But theta is not edge.** Theta and gamma are the same coin: the seller collects `0.76 % of spot` per day and pays out the realised move. The *edge* is only the VRP slice — S8's ~11 % of premium, so **≈ 0.084 % of spot per day** gross, against a daily P&L standard deviation on the order of the straddle value itself (**≈ 0.76 % of spot**). That is a theoretical daily Sharpe of **~0.11**. S6's *measured* per-trade Sharpe for the naive 0DTE short is **+0.002 to +0.017 gross and −0.042 to −0.010 net of costs** — an order of magnitude worse than the theory, and the difference is exactly the bid-ask spread.

**Therefore, over 2.5 sessions the t-statistic of any edge is ≈ 0.1 × √2.5 ≈ 0.16.** The realised P&L will be **~100 % noise**. This is the most important single conclusion in this review, and it should be stated plainly in the submission.

**Candidate strategies with expected and worst-case P&L per $100,000.** All figures assume the stated *risk budget*, use S5's empirical, cost-inclusive per-trade distribution for 0DTE structures, and treat the three sessions (Wed, Thu, half-Fri) as ~2.5 independent trades.

**Strategy A — Daily 0–1 DTE SPY/QQQ iron condors, short strikes ~10–16 delta, wings bought, risk budget 3 % of capital per day ($3,000 defined max loss/day).**
Using S5's iron condor distribution (mean −1.1 %, median +5.5 %, P25 −24 %, P75 +15.4 %, P5 −100 %, P95 +63.9 % of margin):

| Outcome | Per day | Over 2.5 sessions |
|---|---|---|
| Median | +$165 | **+$410 (+0.41 %)** |
| Mean (true EV) | −$33 | **−$83 (−0.08 %)** |
| 75th pct | +$460 | ~+$1,150 |
| 25th pct | −$720 | ~−$1,800 |
| 5th pct (one bad day) | −$3,000 | **−$3,000 to −$4,500** |

Probability of at least one ≤P25 day in 2.5 sessions ≈ **52 %**; at least one ≤P5 day ≈ **12 %**.
Scaling to a **10 % daily risk budget** multiplies everything by 3.3: median +$1,370, 5th percentile ≈ **−$10,000 to −$15,000**.

**Strategy B — 1–7 DTE index credit spreads (single-sided, e.g. put credit spreads only, or call credit spreads only per S6's upside-VRP result), risk budget 3 % of capital per day.**
S5's put/call spread rows: mean **+0.1 % / −0.2 %**, median **+3.0 % / +3.3 %**, P25 **−76.7 % / −65.3 %**, P95 **+112.8 % / +110.5 %**.
Per day on $3,000: median **+$90 to +$99**, mean ≈ **$0**, 25th percentile **−$2,000 to −$2,300**, tail **−$3,000**.
Over 2.5 sessions: median **≈ +$230**, EV ≈ $0, 5 % tail ≈ **−$4,000**. Wider distribution than the condor because a single-sided spread is a directional bet. *Note the mean here is the closest thing to zero-or-positive in the whole S5 table.*

**Strategy C — Short-dated covered calls / cash-secured puts on a liquid ETF, notional 30 % of capital ($30,000).**
Option-alpha component over 2.5 days ≈ **2.5 %/yr × (2.5/252) × $30,000 ≈ $7**. Directional component: $30,000 × a 2.5-day SPY move with σ ≈ 0.8 %/day → 1-σ ≈ **±$380**, 5 % tail ≈ **−$800**, and a 3 % two-day market drop → **−$900**. **The option contributes nothing; this is a pure equity bet.** Include only as a small, honestly-labelled beta sleeve, if at all.

**Strategy D — Earnings straddle purchase (S12), ≤0.5 % of capital ($500 premium).**
Gross expected return +1.4 % to +3.3 % of premium → **+$7 to +$17**. Round-trip single-name option spread of 3–8 % of premium → **−$15 to −$40**. **Net expectation is negative or indistinguishable from zero**, and the September calendar is nearly empty. Not recommended as a core strategy; acceptable as a one-trade demonstration of breadth.

**Risk of ruin.** With defined-risk structures only, "ruin" is bounded by design: the worst single-day loss equals the day's risk budget. At a 3 %/day budget the absolute floor over three sessions is **−9 %**; at 10 %/day it is **−30 %**. With *undefined*-risk structures (naked strangles), a Feb-2018-scale event (S11: VIX +115 %, index −4 % in one session) can produce a loss of 5–20× the credit collected — on a $100k account that is a plausible **−30 % to −60 % in one afternoon**. There is no acceptable reason to accept that in a 2.5-day evaluation.

**Confronting "long-term conservative positions are better."** The user's intuition is correct about *investing* and inapplicable to *this task*:

1. The literature's "conservative" option strategies (covered calls, cash-secured puts, monthly iron condors) earn their edge at a rate of **2–3 % per year**. Over 2.5 trading days that is **$20–$30 on $100k**. It is not a strategy; it is a rounding error.
2. What those strategies *would* actually deliver in 2.5 days is **equity beta** — an unhedged, undiversified directional bet with negative skew (S8: downside beta 0.78 vs upside beta 0.63). That is *less* conservative than it feels.
3. The only structures with material 2-day carry are 0–7 DTE, and their post-cost expected value is approximately **zero** (S6, S5), with a **positive median and a fat negative tail** (S5: median +5.5 %, mean −1.1 %, P5 −100 %).
4. Therefore the correct reading of "conservative" for a 2.5-day evaluation is **not "hold long-dated safe positions"** but **"cap the tail and keep the variance small enough that the noise cannot embarrass you."** Small defined-risk short-dated positions dominate large long-dated ones on exactly the risk dimension the user cares about.
5. And because **three of the four judging criteria are not P&L**, the expected *score* is maximised by a small, well-reasoned, fully-explained book plus excellent technology and presentation — not by maximising expected P&L that the literature says you cannot earn anyway.

### Q6 — Execution realism

**Spreads are the binding constraint.**
- S5: 0DTE SPX **effective spreads are 5.0–6.0 % of mid for retail (with Cboe price improvement) and 9.6–12.5 % without**, and they **widen approaching expiry**. Sell orders receive better spreads than buy orders (market makers are net short 0DTE and want the other side).
- S2: the ATM delta-hedged loss of $0.43 per call was *approximately the size of the $0.375 bid-ask spread* — i.e. in the classic sample the entire premium was one spread.
- S6: crossing the spread flips the naive 0DTE short from Sharpe +0.017 to **−0.033**.
- S5: **60 % of retail 0DTE losses are transaction costs**, and >$90m of the $125m aggregate loss.

**Most of the spread is avoidable.** S14 is the key result: the timing-adjusted effective spread is **1.3 cents vs 6.2 cents conventional and 8.1 cents quoted** for the ~40–54 % of trades that time execution. Averaged over all trades, patient execution captures **47 % of the quoted spread**. Quoted spreads rise steeply with moneyness (<7 cents OTM, 11 cents ITM) but the *achievable* spread is nearly flat (4–6 cents) — so **OTM strikes are cheaper to trade in cents, and the visible quoted spread overstates the real cost**.

**Concrete execution rules this implies:**
1. **Never send a market order.** Send limit orders on the whole multi-leg package.
2. Start at the **mid of the package** (the net credit implied by the four leg mids) and walk toward the bid in small increments over 30–90 seconds. Accept non-fills — a missed trade costs nothing; a crossed spread costs ~10–25 % of the credit on a 4-leg 0DTE condor.
3. **Fewer legs is cheaper.** A 2-leg vertical costs half the crossing risk of a 4-leg condor. Given S5's finding that put spreads and call spreads have *better* mean returns (+0.1 %/−0.2 %) than iron condors (−1.1 %), and given S6's finding that the 0DTE premium is upside-concentrated, a **single-sided credit spread may dominate the full condor** once costs are counted.
4. **Trade only the most liquid underlyings**: SPY, QQQ, IWM (and SPX/XSP if available). Penny-wide near-ATM strikes, deep books, and — per S5 — the largest price-improvement mechanisms.
5. **Avoid the last 30–60 minutes before expiry** for entries: S5 documents spreads widening into expiry. Enter mid-morning, when S6's Sharpes are least bad and S5 says 64.6 % of retail volume trades with 3–24 hours to expiry.
6. **Do not chase high-IV contracts.** S5: "retail trades are particularly poor in high-IV contracts and in high-IV times"; S2: delta-hedged underperformance is *greater* when volatility is high.

**How paper NBBO fills differ from live.**
- *Paper is optimistic* in that: it fills at NBBO with no queue position, no market impact, no adverse selection, and no partial-fill legging risk on multi-leg packages beyond the stated 10 % random partials. In live trading a 4-leg 0DTE package at mid frequently does not fill at all, and when it does you often get worse than NBBO mid.
- *Paper is pessimistic (or at least unrealistic) in one way*: if fills require the order to be **marketable**, then a mid-price limit will simply never fill in paper, whereas a real complex-order book (Cboe COB/AIM) routinely fills multi-leg packages **between** the synthetic bid and offer. Practically, this means in paper you may be pushed toward crossing — which is exactly the behaviour the literature says destroys the edge.
- *The free "indicative" options feed compounds this*: derived/indicative quotes can be stale or wider than the true NBBO, so the paper NBBO you fill against may not correspond to a price you could have got live, in either direction.
- **Budget honestly:** assume roughly **half the quoted spread per leg** as the realistic round-trip cost, and state that assumption in the submission. On a 4-leg 0DTE SPY condor with $0.02–$0.05 quoted leg spreads and a $0.20 credit, that is **$0.04–$0.10 of the $0.20 credit — 20–50 %.** This single number is why the strategy must use few legs, wide-liquid underlyings, and patient limits.
- **American-style assignment / pin risk:** SPY/QQQ/IWM options are American-style and physically settled. A short leg that finishes even slightly ITM can be assigned, converting a defined-risk spread into an overnight equity position. **Close all short legs before the close on expiry day**, or use cash-settled index options if available. This risk is not in the papers but is a real mechanism-level hazard in exactly the structures recommended here.

---

## Design implications

Each recommendation carries its justifying sources and an honest confidence level.

1. **Adopt an explicit "expected alpha ≈ 0" posture and say so in the submission.**
   Design the agent to *control variance and tail risk*, not to maximise expected P&L. Justification: S6 (net-of-cost Sharpe negative for naive 0DTE selling), S5 (mean −1.1 % for 0DTE iron condors), S8 (2–3 %/yr VRP ⇒ ~$25 over 2.5 days), plus the t ≈ 0.16 arithmetic. **Confidence: high.** This is also the most *differentiating* thing you can present to judges: almost every competitor will claim an edge they cannot have.

2. **Core strategy (rank 1): short-dated, defined-risk index credit spreads.**
   Underlyings **SPY, QQQ** (add **IWM** only for diversification, never for size). **DTE 0–2**, entered **09:45–11:00 ET**. Short strike **10–16 delta**; wings bought **1–2 strikes** further out (SPY $1–$2 wide). **Risk budget: 3 % of capital ($3,000 defined max loss) per session, split across 2–4 independent positions**, never more than 4 % on any one day and never more than **9 % cumulative** across the three sessions.
   Justification: S5 (multi-leg > single-leg by 0.17 %; credit > debit by $486k/day; put/call spread medians +3.0 %/+3.3 %; iron condor median +5.5 %), S10 (defined risk cuts max drawdown from −33 % to −13.7 %), S14 (OTM strikes have the narrowest achievable spreads), S1/S3 (index VRP, not single-name).
   Expected: **median +$400 to +$600 over 2.5 sessions, EV ≈ 0, 5 % tail ≈ −$3,000 to −$4,500.**
   **Confidence: medium-high** on the structure, **medium** on the sizing being right for the objective.

3. **Prefer single-sided credit spreads over full iron condors when the cost model says so.**
   S5's iron condor mean (−1.1 %) is *worse* than the put spread (+0.1 %) and call spread (−0.2 %) means, and a condor doubles the number of legs to cross. Build the agent so it can trade either, and choose based on the *realised* package spread it observes.
   Justification: S5 (Table 4), S14 (crossing cost scales with legs), S6 (upside-concentrated 0DTE VRP argues for the call side specifically).
   **Confidence: medium.** The condor's advantage is delta-neutrality and a higher median; the spread's advantage is cost. Let the agent measure.

4. **Tilt the short strikes toward the call/upside side at 0DTE — cautiously.**
   S6 finds the 0DTE VRP is driven almost entirely by upside compensation (`VRP+` strongly positive, `VRP−` negative). Practical form: place the call short strike *closer* (≈16 delta) and the put short strike *further* (≈8–10 delta), producing an asymmetric condor.
   **Confidence: low-medium.** One working paper; and S2 found the *opposite* sign for far-OTM calls at 14–60 DTE in 1988–1995. Implement it as a small tilt, not as the thesis, and disclose the uncertainty.

5. **Hard execution rules (this is where the edge actually is or isn't).**
   (a) Multi-leg package limit orders only, never market orders. (b) Start at the package mid; walk toward the bid in ≤3 steps over ≤90 seconds; then cancel. (c) Reject any trade whose modelled round-trip cost exceeds **25 % of the credit**. (d) Prefer OTM strikes. (e) Avoid the final 45 minutes for *entries*. (f) Close all short legs before 15:50 ET on expiry day to avoid assignment.
   Justification: S14 (1.3 vs 8.1 cents; 47 % of quoted spread saved on average), S5 (0DTE effective spreads 5–12 % of mid; spreads widen into expiry; 60 % of retail losses are costs), S6 (costs flip the sign of the Sharpe).
   **Confidence: high.** This is the best-supported operational recommendation in the review.

6. **Never sell an unwinged option. No naked calls, no naked puts, no short strangles, no ratio spreads with unhedged short legs.**
   Justification: S11 (−90 % in one session, XIV −96 %, VIX +115 %), S10 (CNDR −13.7 % vs PUT −32.7 %), S9 (option-selling skewness −1.11 to −1.53). Even if Alpaca paper permits it, a Volmageddon-scale afternoon inside a 2.5-day window is a live possibility, and the downside is unbounded in a way judges will notice.
   **Confidence: high.**

7. **Add a small long-gamma / tail sleeve: ~15–20 % of the risk budget in a far-OTM put debit spread on SPY, 2–7 DTE.**
   It has negative expected value on its own (S3: buying vol loses ~3 %/week; S5: debit orders lose), but it truncates the 5 % tail of the credit book and demonstrates in the write-up that the agent understands the asymmetry it is running. Size so that the tail sleeve's cost is ≤0.3 % of capital over the whole event.
   Justification: S11 (tail realism), S15 (jump risk is the priced factor — you are short it, so buy some back), S9 (negative skew of premium selling).
   **Confidence: medium.** This is a presentation-and-prudence recommendation as much as an expected-value one, and should be labelled as such.

8. **Do not run covered calls or cash-secured puts as an "income" strategy.**
   If you hold equity at all, label it as a directional view. Justification: S8 (2.05–2.76 %/yr VRP ⇒ ~$25 over 2.5 days; two-thirds of risk is equity beta; downside beta 0.78 > upside beta 0.63), S9.
   **Confidence: high.**

9. **Treat earnings as optional and small (≤0.5 % of capital), and if traded, BUY the straddle pre-announcement rather than selling it.**
   Justification: S12 (+2.62 % [−3,−1], +3.34 % [−3,0]; post-announcement short significant only in the liquid subsample at −1.37 %). Caveat: all S12 returns are mid-price and cost-free, single-name spreads are wide, and 2–4 September is an almost empty earnings calendar.
   **Confidence: low** for net profitability; **medium** for the direction of the pattern.

10. **Do not condition the strategy on any view about 0DTE flow amplifying or dampening volatility.**
    S16 and S18 say it dampens (−60 to −90 annualised bp on 0DTE days); S17 says it amplifies (+9.10 % of mean volatility per 1 s.d.). The literature is genuinely split.
    **Confidence: high** that the question is unsettled; **low** on either direction.

11. **Do not trust broker-reported deltas at 0DTE as probabilities.**
    S7 shows 0DTE surfaces require non-affine skew/kurtosis corrections and that standard models materially mis-price and mis-hedge; S6 finds 94 % of ATM 0DTE options violate risk-averse price bounds. Cross-check strike selection against an **expected-move / realised-distribution** estimate (e.g. the straddle price as the market's own 1-σ estimate) rather than delta alone.
    **Confidence: medium-high.**

12. **Instrument everything and present the distribution, not the point estimate.**
    Log every quoted spread, every fill vs mid, every modelled-vs-realised cost. In the submission, show the *ex ante* P&L distribution (median, mean, 5th percentile) alongside the realised number, so that a good or bad draw is interpretable. Justification: the whole of Q5 — with t ≈ 0.16 the realised P&L carries almost no information, and saying so credibly is worth more than pretending otherwise.
    **Confidence: high.**

**Ranked strategy candidates:**

| Rank | Strategy | Median 2.5-day P&L | EV | 5 % tail | Confidence |
|---|---|---|---|---|---|
| 1 | 0–2 DTE SPY/QQQ defined-risk credit spreads / asymmetric condors, 10–16Δ, 3 %/day risk | +$400 to +$600 | ≈ $0 | −$3,000 to −$4,500 | Medium-high |
| 2 | 1–7 DTE single-sided index credit spreads (slightly lower theta, lower cost, fewer legs) | +$230 to +$400 | ≈ $0 | −$3,000 to −$4,000 | Medium |
| 3 | Small long-gamma tail sleeve (put debit spread) as an overlay, not standalone | −$150 to −$300 | slightly negative | +$1,000 to +$2,500 in a crash | Medium |
| 4 | Earnings long straddle, ≤0.5 % capital | ≈ $0 | slightly negative net of costs | −$500 | Low |
| 5 | Short-dated covered calls / CSPs as "income" | ±$400 (pure beta) | ≈ equity drift | −$900 | High that it is *not* an option strategy |

---

## Follow-up reading

| Paper | Tag | Why |
|---|---|---|
| Bondarenko, O., "Why Are Put Options So Expensive?" (*Quarterly Journal of Finance*, 2014) and his Cboe PUT-index studies | new idea (brief mentioned it; not verified this pass) | The canonical "put overpricing is not explained by any standard model" result; would strengthen or qualify C1 for the *put* side specifically, which matters for our put-spread wing |
| Bryzgalova, Pavlova & Sikorskaya, "Retail Trading in Options and the Rise of the Big Three Wholesalers" (*Journal of Finance*) | cited in S5 | The methodological reference for identifying retail option trades; gives independent numbers on retail option P&L and price improvement |
| Bogousslavsky & Muravyev, "An Anatomy of Retail Option Trading" (SSRN 4682388) | new idea (surfaced in search) | The most recent comprehensive retail option P&L study; likely updates S5's cost figures to a more recent sample |
| Li, Musto & Pearson, on multi-leg/complex option strategies (cited in S5) | cited in S5 | The identification method behind S5's strategy classification; would let us check whether "iron condor" in Table 4 means *short* condors |
| SEC DERA, "Hope at a Reasonable Price: Customer Use of Limit Orders in the 0DTE Market" (March 2025) | new idea | A **regulator-authored** study directly on limit-order use and execution quality in 0DTE — precisely our Q6. Blocked by a 403 this pass (see Paywalled/wanted) |
| Vilkov, G., "0DTE Trading Rules" (SSRN 4641356) | new idea | An explicit rules-based 0DTE strategy paper by one of the S16 authors; would give a second cost-inclusive backtest to compare against S5's distribution |
| Cboe, "0DTE Index Options and Market Volatility: How Large is Their Impact?" (gammasqueezes.pdf) | new idea | Exchange-side evidence on the S16/S17 dispute; industry-sponsored, so read for data not conclusions |
| Constantinides, Jackwerth & Savov, "Mispriced Index Option Portfolios" (*Financial Management*, 2020) | cited in S15 | The follow-up that asks whether the index-option mispricing survives realistic trading frictions — directly relevant to whether any of this is implementable |
| Dew-Becker, Giglio & Kelly, on the term structure of variance risk premia (cited in S5) | cited in S5 | Would tell us how the VRP is distributed across horizons — the exact question in Q5 |
| Israelov & Nielsen, "Covered Calls Uncovered" (*FAJ*, 2015; SSRN 2444999) | cited alongside S8 | The companion paper with the full performance attribution; would sharpen the beta-vs-VRP split |

---

## Paywalled / wanted

| Item | Identifier | What we still need |
|---|---|---|
| Carr & Wu (2009), "Variance Risk Premiums", *RFS* 22(3), 1311–1341 | DOI **10.1093/rfs/hhn038** · https://academic.oup.com/rfs/article-abstract/22/3/1311/1581057 | The per-index VRP magnitude tables (average variance swap rate minus realised variance, and the Sharpe ratio of short variance swaps) — I verified the abstract and 435 citations but not the numbers |
| Dubinsky, Johannes, Kaeck & Seeger (2019), "Option Pricing of Earnings Announcement Risks", *RFS* 32(2), 646–687 | https://academic.oup.com/rfs/article-abstract/32/2/646/5001193 · open copy at https://research.vu.nl/ws/portalfiles/portal/108247883/Option_Pricing_of_Earnings_Announcement_Risks.pdf | The implied-vs-realised earnings-move magnitudes and the estimated announcement jump volatility. (The VU open PDF looked reachable but I did not fetch it this pass — worth trying first, it may not need university access) |
| SEC DERA (2025), "Hope at a Reasonable Price: Customer Use of Limit Orders in the 0DTE Market" | https://www.sec.gov/files/dera-hope-reasonable-prc-2503.pdf | Blocked with **HTTP 403** for both WebFetch and curl with a Chrome UA. Direct browser download needed. This is the single most on-point source for Q6 (limit-order placement in 0DTE) |
| Beckmeyer, Branger & Gayda, SSRN abstract page | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4404704 | SSRN returns **403** to automated fetches. The FoFI 2024 open PDF was used instead and contains the full paper; the SSRN page would only add the citation count and any newer version |
| Bandi, Fusari & Renò, "0DTE Option Pricing" | SSRN 4503344 · https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4503344 (403) | The published *Journal of Finance* version and its Section 10 "0DTE risk premia" numbers (instantaneous return and variance risk premium estimates and their predictive R²) |
| Coval & Shumway (2001), *JF* 56(3) | DOI **10.1111/0022-1082.00352** · JSTOR 222539 | The full return tables by moneyness (I have only the headline −3 %/week from the abstract) |
| Bollen & Whaley (2004), *JF* 59(2), 711–753 | DOI **10.1111/j.1540-6261.2004.00647.x** | The magnitude of the net-buying-pressure coefficients (how many vol points of richness per unit of demand) |
| Augustin, Cheng & Van den Bergen (2021), *FAJ* 77(3), 35–51 | DOI **10.1080/0015198X.2021.1913040** · open at https://utoronto.scholaris.ca/bitstreams/98fc477b-df23-4394-915b-d48dcd4642ef/download | I used the abstract/summary; the open TSpace copy has the full rebalancing-loop quantification if we want it |
| Cboe CNDR / BFLY **annualised returns** (as opposed to drawdowns) | https://cdn.cboe.com/api/global/us_indices/governance/CNDR_Methodology.pdf and the index history on Cboe/Bloomberg | The fact sheet prints CNDR's drawdown (−13.7 %) but not its return. Needed to state the return give-up from buying wings |

---

## Method log

**Searches run (WebSearch):** Beckmeyer/Branger/Gayda 0DTE retail; Bandi/Fusari/Renò 0DTE pricing; Muravyev & Pearson trading costs; Cboe CNDR/BFLY/PUT/BXM performance and drawdowns; Carr & Wu variance risk premiums; Bakshi & Kapadia delta-hedged gains; Israelov & Nielsen covered calls; Coval & Shumway expected option returns; Bollen & Whaley net buying pressure; 0DTE academic literature 2024–2025 (VRP, Sharpe, selling); Gao/Xing/Zhang earnings straddles; Dubinsky et al. earnings announcement risk; short straddles into earnings net of costs; Feb 2018 Volmageddon magnitudes; Augustin/Cheng/Van den Bergen; Constantinides/Jackwerth/Savov; Brogaard/Han/Won and Adams/Fontaine/Ornthanalai; Dim/Eraker/Vilkov; SPX 0DTE iron condor backtests with transaction costs.

**Documents fetched and read in full text** (curl with a Chrome User-Agent + `pdftotext -layout`, then targeted `grep`/`sed` rather than end-to-end reading):
Beckmeyer/Branger/Gayda FoFI-2024 PDF (1,435 lines — abstract, introduction, Tables 1/3/4, spread and P&L sections);
Almeida/Freire/Hizmeri FMA-2025 PDF (2,930 lines — abstract, introduction, Tables 6/7/OA.3);
Bandi/Fusari/Renò NFA PDF (2,254 lines — abstract and Section 10 headings);
Bakshi & Kapadia RFS open PDF (2,790 lines — abstract, Table 1 Panel A, sample period);
Israelov & Nielsen FAJ/AQR PDF (605 lines — Tables 1 and 2, decomposition example);
Wilshire-for-Cboe 2019 PDF (1,298 lines — key highlights, Exhibits 4/5/6/8);
Cboe benchmarks fact sheet (154 lines — drawdown table);
Muravyev & Pearson CICF working-paper PDF (2,145 lines — introduction, Section 5, sample period);
Gao/Xing/Zhang JFQA PDF via Tsinghua mirror (1,754 lines — abstract, Table 3 Panels A and B, methodology note on midpoint pricing).

**Could not verify / failed:**
- **Semantic Scholar API was rate-limited (HTTP 429) on every attempt** across the session, including with a browser User-Agent. Citation counts are therefore missing for most cards; the only verified count is Carr & Wu (**435**, from RePEc/IDEAS). This is flagged on each card.
- **SSRN abstract pages return HTTP 403** to both WebFetch and curl; I worked around this by using conference/university-hosted open PDFs of the same papers, which I confirmed match the SSRN titles, authors and dates.
- **SEC DERA 0DTE limit-order paper returns HTTP 403** to both tools (curl received an HTML block page, not the PDF). Listed under Paywalled/wanted; it is the most valuable missing item.
- **Cboe CNDR/BFLY annualised returns** are not printed on the fact sheet and I did not find them in a citable source; I deliberately did **not** state a CNDR return.
- A **small-model WebFetch summary of Gao/Xing/Zhang contradicted the search snippet** (it claimed pre-announcement straddle returns were negative). I resolved this by extracting the actual PDF text: the abstract and Table 3 confirm **+2.62 % [−3,−1]** and **+3.34 % [−3,0]**. Noted here because it is a reminder that WebFetch summaries of PDFs are unreliable for numbers.
- The user's brief attributed **Gao/Xing/Zhang to RFS** (it is **JFQA 2018**) and **"0DTE Asset Pricing" to Adams/Fontaine/Ornthanalai** (that title belongs to **Almeida/Freire/Hizmeri**; Adams/Fontaine/Ornthanalai wrote *"The Market for 0DTE: The Role of Liquidity Providers in Volatility Attenuation"*). Both corrected above. **Israelov & Nielsen is FAJ 2014**, not 2015.

**Not researched (out of scope by instruction):** Alpaca API documentation and order-type mechanics; the live earnings calendar for 2–4 September 2026; any backtesting or code.

**Approximate reading volume:** ~19 web search result sets and ~14 fetched documents; roughly **95,000–110,000 tokens** of source material passed through context, well under the 250k budget. Nine PDFs were converted locally and grepped rather than read end-to-end, which is where most of the saving came from. Elapsed effort ≈ one hour.

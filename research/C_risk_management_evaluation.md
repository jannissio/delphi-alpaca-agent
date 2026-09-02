# Review C — Risk Management, Position Sizing, Hedging and Evaluation

Focused literature review for the lablab.ai x Alpaca "AI Trading Agents Hackathon".
Scope: sizing under fat tails, drawdown/stop rules, cost of hedging, Greeks budgets for a
short-dated book, regulatory pre-trade controls as a gate template, and honest evaluation of a
~2.5-session live window.

Builds on review A (options evidence) and review B (LLM evidence); those conclusions are taken
as given and are **not** re-derived here.

---

## Kurzfassung (Deutsch)

1. **Kelly ist bei unserer Ertragsverteilung exakt null.** Mit der Verteilung aus Review A
   (Mittelwert −1,1 % der Margin) ist der wachstumsoptimale Kapitalanteil f\* = 0 %. Erst bei
   einer unterstellten (unbelegten) Kante von +2 % läge Voll-Kelly bei 17,4 %, Viertel-Kelly bei
   4,4 % des Kapitals pro Sitzung.
2. **Empfehlung: 2 % Risiko pro Sitzung, maximal 6 % kumuliert** (statt der vorgeschlagenen
   3 %/9 %). Das liegt deutlich unter Viertel-Kelly selbst im optimistischen Szenario und ist
   damit eine reine Varianzkontroll-Entscheidung, keine Ertragswette.
3. **Arithmetik bei 2 %:** absoluter Worst Case über 3 Sitzungen = −5,88 % (−5.881 $),
   Wahrscheinlichkeit 0,0125 %. P05 = −2,26 %, P01 = −3,29 %. Bei 3 % wären es −8,73 %
   Worst Case — noch tragbar, aber ohne Ertragsgegenwert.
4. **Chopra/Ziemba:** Für Log-Investoren wiegen Fehler im Mittelwert gegenüber Varianz- und
   Kovarianzfehlern etwa 100:3:1. Wir kennen den Mittelwert nicht — also fraktionales Kelly,
   und zwar sehr klein.
5. **Hedging-Verdikt: Nein.** Israelov (2019) zeigt, dass Put-Schutz (PPUT) über 1986–2016 zu
   **schlechteren** Drawdowns führte als schlichtes Reduzieren der Aktienquote: 36,5 % S&P +
   63,5 % Cash lieferten dieselben 2,5 % p. a.; über 250 Tage −32,1 % (geschützt) vs. −20,9 %
   (reduziert); Divestment gewann in 97–100 % der Fenster.
6. **Konsequenz für den Wunsch "mehr Risiko nur mit Hedge":** Der Hedge kauft das Risikobudget
   nicht zurück. Weniger Risiko ist der Hedge. Die Long-Gamma-Sleeve (~0,3 % des Kapitals)
   bleibt — aber als **Demo- und Erklärbarkeits-Baustein**, nicht als Risikorechtfertigung.
7. **Gates statt Stopps.** Kaminski & Lo (2014): Unter der Random-Walk-Hypothese ist die
   "Stopping Premium" **immer negativ**. Preisbasierte Stopps auf 0-DTE-Spreads bezahlen den
   Spread zweimal ohne Erwartungswertgewinn. Stattdessen: Struktur begrenzt den Verlust
   (gekaufte Flügel), plus harte Tageslimits.
8. **Gate-Vorlage aus der Regulatorik:** SEC Rule 15c3-5, MiFID II RTS 6 Art. 12/15/17 und
   FINRA 15-09 liefern eine 1:1 in Code abbildbare Checkliste (Preis-Collars, max. Ordervolumen,
   Message-Limits, Kill-Switch, Pre-Trade statt Post-Trade, Deployment-Kontrolle).
9. **Knight Capital (2012)** ist der Lehrfall: 460 Mio. $ in 45 Minuten. Das Limit existierte
   (2 Mio. $ auf dem 33-Konto) — es war nur **nicht an die Orderausgabe gekoppelt**. Jedes
   unserer Limits muss *blockierend* sein, nicht nur alarmierend.
10. **Pin-Risiko:** SPY/QQQ sind amerikanisch und physisch geliefert; OCC übt ab 0,01 $ im Geld
    automatisch aus. Ein zugeteilter Short-Leg ohne ausgeübten Flügel erzeugt eine
    Aktienposition über Nacht, die das "definierte Risiko" sprengt. Deshalb: **Flat vor
    15:45 ET, hart.** Cash-abgerechnete Indexoptionen (SPX/XSP) wären strukturell besser.
11. **Ehrliche Auswertung:** Bei N = 10 Trades beträgt der Standardfehler der geschätzten Kante
    10,3 % der Margin — das 95-%-Konfidenzintervall ist etwa zehnmal breiter als der gesuchte
    Effekt. Für |t| = 2 bräuchte man ~1.058 Trades, bei Harvey/Liu/Zhus |t| = 3 ~2.380.
12. **Wir berichten deshalb keinen Sharpe, keine Trefferquote, keine annualisierte Rendite.**
    Wir berichten Prozessmetriken: Gate-Trefferzähler, ex-ante vs. ex-post Greeks, Slippage
    gegen Mid, realisierter vs. erlaubter Drawdown, Determinismus-Replay.
13. **Benchmarks:** SPY Buy-and-Hold über dieselben Handelsstunden, Cboe CNDR/PUT als
    Strategie-Analoga, plus eine Monte-Carlo-Zufallseinstiegs-Simulation derselben Struktur als
    "Glücks-Nulllinie" — P&L wird gegen diese Verteilung, nicht gegen null, eingeordnet.
14. **Arnott/Harvey/Markowitz (2019)** liefern das Berichtsprotokoll: alle Versuche zählen,
    Stichprobe ex ante festlegen, echtes Out-of-Sample gibt es nur im Live-Handel, Modell
    während des Laufs nicht nachjustieren.
15. **Ein-Seiten-Writeup:** "AI logic, risk gates, Alpaca infrastructure" wird zur Gate-Tabelle
    mit Quelle je Zeile — das ist unser stärkstes Differenzierungsmerkmal gegenüber P&L-Glück.

---

## Source cards

### S1 — Israelov (2019), "Pathetic Protection: The Elusive Benefits of Protective Puts"
- **Citation:** Israelov, R. 2019. "Pathetic Protection: The Elusive Benefits of Protective Puts."
  *The Journal of Alternative Investments* 21 (3): 6–33. DOI 10.3905/jai.2018.1.066.
  SSRN 2934538. Open PDF: `images.aqr.com/-/media/AQR/Documents/Journal-Articles/Pathetic-Protection-JAI-Wint19.pdf`
- **Type:** Peer-reviewed journal (JAI, CAIA official publication) by an AQR principal.
- **Citations:** 11 (OpenAlex, journal version) + 3 (SSRN version). Low count, but the journal is
  the standard venue for this literature and the paper is widely cited in practitioner work.
- **Quality:** **Citation-worthy: yes.** Peer-reviewed, uses a public index (Cboe PPUT), method is
  transparent and replicable; the one caveat is that the author sells alternatives to puts.
- **Key findings (numbers):**
  - Sample: 1 July 1986 – 19 May 2016 (PPUT vs SPX, excess of cash).
  - SPX realized **5.8 %** annualized geometric excess return; **PPUT 2.5 %**.
  - **Investing 36.5 % in SPX and 63.5 % in cash produced the same 2.5 % compound annualized
    excess return as PPUT** — i.e. the entire protection bought nothing that de-levering did not.
  - Regression: r_protected = −15 bp/month + 0.74 · r_equity, R² = 0.85 →
    **−1.8 % annualized alpha, t = −2.0**. Consistent with Israelov & Nielsen (2015b)'s −2.0 %
    for delta-hedged 5 % OTM puts (Mar 1996 – Jun 2014).
  - **Drawdowns, protected vs. return-matched divested:** 20-day windows **−9.6 % vs −6.6 %**;
    250-day windows **−32.1 % vs −20.9 %**. Protection is *worse* on both horizons.
  - **Divesting delivered better peak-to-trough drawdowns 97 % of the time over the shortest
    windows and 100 % of the time over windows longer than about half a year.**
  - Upside: over 20-day horizons the 99th-percentile rally was 15.0 % (protected) vs 12.3 %
    (divested) — a real but small convexity benefit.
  - When protection *does* win: "when a very large crash occurs prior to the options' expiration."
- **Relevance:** Directly answers Q3 and kills the "more risk is fine if I hedge it" premise.
- **Caveats:** Monthly, ~5 % OTM, index-level protection. It does **not** test an intraday
  long-gamma sleeve on a 0-2 DTE book, which is a different instrument with a different horizon.
  Do not over-extend the claim.

### S2 — AQR (2019), "Chasing Your Own Tail (Risk), Revisited"
- **Citation:** Thapar, A., L. Nielsen, and D. Villalon. November 2019. *Chasing Your Own Tail
  (Risk), Revisited.* AQR Capital Management white paper. (Updates Berger, Nielsen & Villalon 2011.)
- **Type:** Industry research white paper (not peer-reviewed).
- **Citations:** Not indexed in OpenAlex as a journal work.
- **Quality:** **Citation-worthy: with caveats.** Well-argued and numerate, but it is marketing-
  adjacent house research from a firm that sells the recommended alternatives. Use it as
  corroboration of S1, never as the sole support for a claim.
- **Key findings (numbers):**
  - Over the eight years to June 2019, a **5 % OTM put-protected US 60/40 portfolio earned
    7.0 % vs 9.0 % for the unprotected portfolio** — a ~2 %/yr drag, "almost exactly the same as
    it's been long term."
  - A put-protected portfolio "has been less effective at mitigating losses and the length of
    drawdowns than most investors might expect."
  - The insurance benefit "relies crucially on getting two things right: 1) buying an option
    shortly before a market drawdown, and 2) having the option's expiration align" with it.
  - Proposed alternatives: risk parity, managed futures / trend, defensive equities — i.e.
    *diversification and lower risk*, not purchased convexity.
- **Relevance:** Q3, and the "timing is the whole game" point that applies to a tail sleeve held
  for 2.5 days.
- **Caveats:** Conflicted author. Sample is a bull market, which the paper concedes.

### S3 — Kaminski & Lo (2014), "When Do Stop-Loss Rules Stop Losses?"
- **Citation:** Kaminski, K. M., and A. W. Lo. 2014. "When do stop-loss rules stop losses?"
  *Journal of Financial Markets* 18: 234–254. DOI 10.1016/j.finmar.2013.07.001.
  Open PDF via MIT DSpace 1721.1/114876.
- **Type:** Peer-reviewed journal.
- **Citations:** 67 (OpenAlex, journal version) + 19/2 on two SSRN versions.
- **Quality:** **Citation-worthy: yes.** Top-tier microstructure journal, Andrew Lo, formal
  propositions plus empirics.
- **Key findings (numbers):**
  - Defines the **"stopping premium"** — the expected-return difference per unit time between a
    strategy with and without the stop-loss overlay.
  - **Proposition 1: under the Random Walk Hypothesis the stopping premium is always negative.**
    In the authors' own summary: "under the most common return-generating process, the Random
    Walk Hypothesis, the stopping premium is always negative."
  - Under AR(1) momentum (φ ∈ (0,1)) or regime-switching the stopping premium **can** be
    positive; under mean reversion (φ ∈ (−1,0)) it is negative.
  - Empirics: daily US index/bond futures, **January 1993 – November 2011**. In one calibration,
    stopping over monthly intervals raised return by **1.5 %**, cut volatility by **5 %**, and
    raised the Sharpe ratio by **as much as 20 %**.
  - Crucially: benefits appear **at longer sampling frequencies**; they found stop-losses to be of
    no value at short-term sampling frequencies.
- **Relevance:** Q2. This is the strongest available argument against putting a price-based
  stop-loss on an intraday 0-2 DTE options book.
- **Caveats:** The paper studies a stop-loss on a *buy-and-hold underlying* that switches to
  bonds, not on a short-option position. The transfer is by analogy, and I flag it as such: the
  short-gamma payoff is not the underlying's payoff. What transfers cleanly is the *frequency*
  result (no value intraday) and the random-walk baseline.

### S4 — Ziemba & MacLean, "Using the Kelly Criterion for Investing" (Kelly chapter)
- **Citation:** Ziemba, W. T., and L. C. MacLean. "Using the Kelly Criterion for Investing."
  Chapter 1 in *Stochastic Optimization Methods in Finance and Energy*, Springer.
  Open PDF: `webhomes.maths.ed.ac.uk/mckinnon/blackouts/StochOptFinanceAndEnergySpringer/Chap1_KellyZiemba.pdf`
  Companion: MacLean, Thorp & Ziemba, "Good and Bad Properties of the Kelly Criterion"
  (2010/2011/2012; OpenAlex 21 + 17 + 11 citations across versions) and MacLean, Thorp & Ziemba,
  *The Kelly Capital Growth Investment Criterion* (World Scientific, 2011).
- **Type:** Peer-reviewed book chapter (Springer), by the field's principal authors.
- **Citations:** Chapter not separately indexed; the sibling survey articles have 11–21 each and
  Thorp's "The Kelly Criterion in Blackjack, Sports Betting, and the Stock Market" (2006/2008)
  has **84–159** on OpenAlex.
- **Quality:** **Citation-worthy: yes.** Authoritative primary source for both the good and the
  bad properties, written by people with no incentive to oversell Kelly.
- **Key findings (numbers):**
  - Kelly maximizes asymptotic long-run growth but "is actually very risky short term since its
    Arrow–Pratt risk aversion index is the reciprocal of wealth" — essentially zero.
  - **Betting exactly twice the Kelly fraction gives a growth rate of zero** (plus the risk-free
    rate). "Since the growth rate and the security are both decreasing for f > f\*, it follows
    that **it is never advisable to wager more than f\***."
  - **Chopra & Ziemba (1993): errors in the means average about 20 times more important than
    errors in covariances, with variance errors about double the covariance errors; and the
    relative importance is risk-aversion dependent — for the extreme log (Kelly) investor with
    essentially zero risk aversion the errors are worth about 100:3:1. "So log investors must
    estimate means well if they are to survive."**
  - Half-Kelly is "a toned down version of full Kelly that provides a lot more security to
    compensate for its loss in long-term growth."
  - Simulation (40 yearly decisions, 3000 scenarios, equity-vs-cash, Merton x\* = 1.5288):
    min final wealth by Kelly fraction — **0.26k: $2,368; 0.52k: $701; 0.78k: −$4,970;
    1.05k: −$133,456; 1.31k: −$6.86m; 1.57k: −$102.5m** on the same initial stake. "For the most
    aggressive strategy (1.57k), it is possible to lose 10,000 times the initial wealth."
  - Concluding point 4: "**no matter how favorable the investment opportunities are or how long
    the finite horizon is, a sequence of bad scenarios can lead to very poor final wealth
    outcomes, with a loss of most of the investor's initial capital.**"
- **Relevance:** Q1, entire section. The 100:3:1 result is the single best justification for
  quarter-Kelly-or-less when the mean is unknown.
- **Caveats:** The simulations are long-horizon (40 periods); our horizon is 3. That makes the
  case for fractional Kelly *stronger*, not weaker — Kelly's advantages are asymptotic and we
  have no asymptote.

### S5 — Grossman & Zhou (1993), "Optimal Investment Strategies for Controlling Drawdowns"
- **Citation:** Grossman, S. J., and Z. Zhou. 1993. "Optimal Investment Strategies for
  Controlling Drawdowns." *Mathematical Finance* 3 (3): 241–276.
  DOI 10.1111/j.1467-9965.1993.tb00044.x.
- **Type:** Peer-reviewed journal.
- **Citations:** **403** (OpenAlex).
- **Quality:** **Citation-worthy: yes.** Canonical, heavily cited, Sanford Grossman.
- **Key findings:**
  - Formalizes the constraint **W_t ≥ α·M_t**, where M_t is the running maximum of wealth and
    α ∈ (0,1) is the permitted drawdown floor.
  - **Main result: the optimal policy invests in the risky asset in proportion to the "surplus"
    W_t − α·M_t.** Risk-taking scales down continuously as wealth approaches the floor and goes
    to zero at the floor — it is not a binary on/off switch.
  - Maximizes the asymptotic long-run growth rate subject to the drawdown constraint.
- **Relevance:** Q2. Gives a *principled, citable* form for the drawdown gate: size proportional
  to remaining budget, rather than trade-full-size-then-stop-dead.
- **Caveats:** Continuous-time, frictionless, single risky asset with constant investment
  opportunity set. Klass & Nowicki (2005) show the strategy is not always optimal in discrete
  time. We use the *shape* of the result, not the formula.

### S6 — Goldberg & Mahmoud (2016), "Drawdown: From Practice to Theory and Back Again"
- **Citation:** Goldberg, L. R., and O. Mahmoud. 2016. "Drawdown: from practice to theory and
  back again." *Mathematics and Financial Economics.* arXiv:1404.7493v5.
- **Type:** Peer-reviewed journal (arXiv preprint read).
- **Citations:** OpenAlex reports 1 — clearly a metadata artifact; the paper is well known in the
  drawdown literature. **Treat the count as unreliable, not as evidence of low impact.**
- **Quality:** **Citation-worthy: yes.** Berkeley CRMR, formal risk-measure theory.
- **Key findings:**
  - Maximum drawdown is "one of the most widely used indicators of risk in the fund management
    industry, but **one of the least developed in the context of measures of risk**."
  - Defines **Conditional Expected Drawdown (CED)** = the tail mean of the *distribution* of
    maximum drawdowns: CED_α(X) = E(μ(X) | μ(X) > DT_α).
  - CED is **degree-one positively homogeneous** (so it can be linearly attributed to factors)
    and **convex** (so it can be used in optimization); it is a *deviation measure* in the sense
    of Rockafellar et al. (2002, 2006).
  - Drawdown is **inherently path-dependent and sensitive to serial correlation**; the empirical
    study fitting AR(1) models to US Equity and US Bonds finds substantially higher correlation
    between the autoregressive parameter and CED than with Expected Shortfall or volatility.
- **Relevance:** Q2 and Q6. The decisive framing: **maximum drawdown is a draw from a
  distribution**. Our realized 3-session max drawdown is one sample and is uninformative on its
  own; what we can honestly report is the realized value *against the ex-ante distribution*.
- **Caveats:** Theoretical; no directly transferable numeric thresholds.

### S7 — SEC Rule 15c3-5, Market Access Rule (2010) + Small Entity Compliance Guide
- **Citation:** US Securities and Exchange Commission. *Risk Management Controls for Brokers or
  Dealers with Market Access*, Exchange Act Rule 15c3-5, Release 34-63241, adopted 3 Nov 2010;
  Small Entity Compliance Guide, `sec.gov/rules/final/2010/34-63241-secg.htm`.
- **Type:** Regulator document (binding rule + official staff guide).
- **Quality:** **Citation-worthy: yes.** Primary regulatory text; the strongest possible source
  for "these are the controls a serious trading system is required to have."
- **Key required controls (verbatim structure from the SEC guide):**
  1. "systematically limit the financial exposure of the broker or dealer that could arise as a
     result of market access";
  2. "ensure compliance with all regulatory requirements that are applicable in connection with
     market access";
  3. "**prevent the entry of orders that exceed appropriate pre-set credit or capital thresholds,
     or that appear to be erroneous**";
  4. "prevent the entry of orders unless there has been compliance with all regulatory
     requirements that must be satisfied **on a pre-order entry basis**";
  5. "prevent the entry of orders that the broker-dealer or customer is restricted from trading,
     **restrict market access technology and systems to authorized persons**, and assure
     appropriate surveillance personnel receive **immediate post-trade execution reports**";
  6. **"direct and exclusive control"** of the financial and regulatory risk controls;
  7. a system for **regularly reviewing effectiveness** and "no less frequently than annually"
     conducting and documenting a review;
  8. **annual CEO certification** that the controls comply with the rule.
- **Relevance:** Q5, the backbone of the gate checklist. Note especially #4 — *pre-order entry*,
  not post-trade — and #6, control must not be delegable to the thing being controlled.
- **Caveats:** Applies to broker-dealers, not retail algo authors. We adopt it as a **design
  template**, and must say so; claiming we are "compliant with 15c3-5" would be false.

### S8 — SEC Administrative Proceeding, Knight Capital Americas LLC (2013)
- **Citation:** In the Matter of Knight Capital Americas LLC, SEC Admin. Proc. File No. 3-15570,
  Exchange Act Release No. 34-70694, 16 October 2013.
  `sec.gov/files/litigation/admin/2013/34-70694.pdf`. $12 million penalty; first enforcement
  action under Rule 15c3-5.
- **Type:** Regulator document (settled enforcement order — findings are agreed facts).
- **Quality:** **Citation-worthy: yes.** Primary source, exceptionally detailed forensics.
- **Key findings (numbers and named failures):**
  - On 1 August 2012, in **approximately forty-five minutes**, Knight's router sent **millions of
    child orders** while attempting to fill just **212 customer orders**, accumulated an
    unintended multi-billion-dollar portfolio and **lost more than $460 million**.
  - Root cause: **"Power Peg"** functionality, discontinued in 2003 but "**remained present and
    callable**"; a repurposed feature flag re-activated it. In 2005 the cumulative-share tracking
    was moved earlier in the sequence and **"Knight did not retest the Power Peg code after
    moving the cumulative quantity function."**
  - Deployment: code was deployed to only 7 of 8 servers; **"Knight did not have a second
    technician review this deployment"** and had **no written code development and deployment
    procedures** for the affected system.
  - **The limit existed and did not fire:** "Knight assigned a **$2 million gross position
    limit** to the 33 Account, but **it did not link this account to any automated controls**
    concerning Knight's overall financial exposure."
  - Monitoring was human-only: **"PMON relied entirely on human monitoring and did not generate
    automated alerts regarding the firm's financial exposure. PMON also did not display the
    limits for the accounts or trading groups"** — and it **"experienced delays during high
    volume events... resulting in reports that were inaccurate."**
  - No output cross-check: "Knight did not have sufficient controls to monitor the output from
    SMARS, **such as a control to compare orders leaving SMARS with those that entered it**."
  - No kill: "Knight also **did not have procedures in place to halt SMARS's operations in
    response to its own aberrant activity**."
  - The one price control was a **9.5 % collar off NBBO** — which "would not prevent the entry of
    erroneous orders in circumstances in which the National Best Bid or Offer moved by less than
    9.5 percent" and did not apply to pre-open orders.
  - **Incident response made it worse:** with no incident-response procedures, staff uninstalled
    the new code from the seven correct servers, "**This action worsened the problem**."
- **Relevance:** Q5. Every one of these maps to a gate we can implement in an afternoon. The
  narrative value for the write-up and the pitch is very high.
- **Caveats:** An extreme institutional case; the *mechanisms* transfer, the scale does not.

### S9 — MiFID II RTS 6, Commission Delegated Regulation (EU) 2017/589
- **Citation:** Commission Delegated Regulation (EU) 2017/589 of 19 July 2016 supplementing
  Directive 2014/65/EU with regard to regulatory technical standards specifying the
  organisational requirements of investment firms engaged in algorithmic trading ("RTS 6").
  EUR-Lex ELI: `eur-lex.europa.eu/eli/reg_del/2017/589/oj/eng`.
- **Type:** Regulator document (binding EU technical standard).
- **Quality:** **Citation-worthy: yes.** This is the most *explicitly itemized* list of algo
  pre-trade controls in any regulation, which makes it ideal as a code checklist.
- **Key required controls:**
  - **Article 15 — Pre-trade controls on order entry:** (1) **price collars** — automatically
    block or cancel orders outside set price parameters; (2) **maximum order values**;
    (3) **maximum order volumes**; (4) **maximum message limits**; (5) **repeated automated
    execution throttles** — limit how many times a strategy is applied, with the system
    automatically disabling after a predetermined number of executions until re-enabled by
    staff. Plus market and credit risk limits based on capital base, clearing arrangements,
    strategy and risk tolerance.
  - **Article 12 — Kill functionality:** ability to "cancel immediately, as an emergency measure,
    any or all of its unexecuted orders submitted to any or all trading venues," with
    identification of which algorithm and which trader/client is responsible for each order.
  - **Article 13 — Automated surveillance:** automated monitoring of orders and transactions
    generating alerts and reports, with ex-post analysis at sufficient time granularity.
  - **Articles 5–8 — Testing and deployment:** development/testing methodology with senior
    management authorisation; **conformance testing** against venue systems; a testing
    environment **separated from production**; **controlled deployment with predefined limits**
    on instruments, price/value/order numbers, positions and venues.
  - **Article 9 — Annual self-assessment and validation report** by the risk-management function,
    with internal audit review and senior-management approval.
  - **Article 17 — Post-trade controls:** continuous market and credit risk assessment,
    **reconciliation of electronic trading logs against venue/broker records**, real-time
    calculation of outstanding exposure, and for derivatives, controls on maximum long/short and
    overall strategy positions.
- **Relevance:** Q5. Articles 15 and 12 give the literal names of gates; Article 17 gives us the
  reconciliation duty that becomes our ex-ante/ex-post Greeks check.
- **Caveats:** EU law, not applicable to a US paper account. Design template only.

### S10 — FINRA Regulatory Notice 15-09 (March 2015)
- **Citation:** FINRA. March 2015. *Guidance on Effective Supervision and Control Practices for
  Firms Engaging in Algorithmic Trading Strategies.* Regulatory Notice 15-09.
  `finra.org/rules-guidance/notices/15-09`.
- **Type:** Regulator document (guidance; effective practices, not rules).
- **Quality:** **Citation-worthy: yes**, but note it is guidance ("firms should consider"), not a
  binding requirement.
- **Key effective practices, verbatim, across the five areas** (General Risk Assessment and
  Response; Software/Code Development and Implementation; Software Testing and System Validation;
  Trading Systems; Compliance):
  - "implementing a development and change management process that tracks the development of new
    trading code or material changes to existing code," with review of test results and approval
    protocols;
  - "employing **redundant or multiple system validations** before introducing new or materially
    changed code into production";
  - "**archiving code versions in a retrievable manner**";
  - "maintaining, at a minimum, a **basic summary description of algorithmic strategies** that
    enables supervisory, compliance and regulatory staff to understand the intended function of
    an algorithm **without the need to resort... to direct code review**";
  - "providing mechanisms by which the firm may **quickly disable the algorithm or supporting
    platform with a minimal number of steps**";
  - "where feasible, **deploying new algorithmic strategies in a pilot phase of limited size,
    increasing only as results are confirmed**";
  - "when deploying new code, maintaining **heightened scrutiny** of the impacted trading
    account, including **real-time monitoring**";
  - "conducting any significant testing in a **development environment that is segregated**" from
    production; "**maintaining a record of testing protocols and results**";
  - "implementing controls, monitors, alerts and **reconciliation processes** that enable the firm
    to quickly identify whether an algorithm is experiencing unintended results";
  - "**documenting and periodically reviewing parameter settings** for the firm's risk controls";
  - "placing appropriate controls and limitations on a **trader's ability to overwrite or
    otherwise evade system controls**";
  - "implementing controls to **manage outbound message volume via threshold parameters**."
- **Relevance:** Q5, particularly the software-engineering half of the checklist (version
  archiving, plain-language strategy description, one-step disable, pilot sizing, no-override).
  The "summary description understandable without code review" practice is essentially a
  regulator asking for the one-page write-up the judges want.
- **Caveats:** Guidance, US broker-dealers.

### S11 — Bailey & López de Prado (2014), "The Deflated Sharpe Ratio"
- **Citation:** Bailey, D. H., and M. López de Prado. 2014. "The Deflated Sharpe Ratio:
  Correcting for Selection Bias, Backtest Overfitting, and Non-Normality." *The Journal of
  Portfolio Management* 40 (5): 94–107. SSRN 2460551. Open PDF at davidhbailey.com.
- **Type:** Peer-reviewed journal (JPM 40th Anniversary Special Issue).
- **Citations:** **110** (OpenAlex, journal version).
- **Quality:** **Citation-worthy: yes.**
- **Key findings:**
  - DSR computes the probability that an observed Sharpe ratio is statistically significant after
    correcting jointly for (i) **the number of independent trials N**, (ii) **the variance of the
    backtest results**, (iii) **the sample length T**, and (iv) **the skewness and kurtosis** of
    returns.
  - "After a sufficient number of trials, it is guaranteed that a researcher will always find a
    misleadingly profitable strategy, a false positive."
  - Worked example: a strategy that looks acceptable becomes non-significant once trials are
    counted — at **N = 46 independent trials** the DSR is 0.9505 (just above the 95 % bar), and
    the investor's actual case falls below it. "If the strategy had exhibited Normal returns...
    after N = 88 independent trials" the conclusion would have differed — **non-normality alone
    halved the tolerable number of trials**.
  - Also introduces **Minimum Track Record Length (MinTRL)** and Minimum Backtest Length.
  - Practical stopping rule via the secretary problem / 1/e-law: "sample a fraction 1/e of them
    (roughly 37 %) at random and measure their performance," then take the first that beats them.
- **Relevance:** Q6. Gives us the formal reason not to quote a Sharpe ratio and the vocabulary
  (trials counted, non-normality, sample length) to explain why.
- **Caveats:** Designed for backtests with many observations. Our N is so small that DSR is not
  even computable in a meaningful way — which is itself the point to report.

### S12 — Harvey, Liu & Zhu (2016), "…and the Cross-Section of Expected Returns"
- **Citation:** Harvey, C. R., Y. Liu, and H. Zhu. 2016. "… and the Cross-Section of Expected
  Returns." *The Review of Financial Studies* 29 (1): 5–68. NBER WP 20592.
- **Type:** Peer-reviewed journal (top-3 finance).
- **Citations:** **2,123** (OpenAlex).
- **Quality:** **Citation-worthy: yes.** Field-defining.
- **Key findings:**
  - Given the extent of data mining, "it does not make economic or statistical sense to use the
    usual significance criteria for a newly discovered factor" with t > 2.0.
  - **A new factor needs to clear a much higher hurdle: a t-statistic greater than 3.0.**
  - Provides a time series of historical significance cutoffs from 1967 onward, allowing for
    correlation among tests and missing data.
  - Conclusion: most claimed research findings in financial economics are likely false.
- **Relevance:** Q6. Sets the bar we will explicitly say we cannot clear, and by how much.

### S13 — Arnott, Harvey & Markowitz (2019), "A Backtesting Protocol in the Era of Machine Learning"
- **Citation:** Arnott, R. D., C. R. Harvey, and H. Markowitz. 2019. "A Backtesting Protocol in
  the Era of Machine Learning." *The Journal of Financial Data Science* 1 (1): 64–74.
  SSRN 3275654. Open PDF at people.duke.edu/~charvey.
- **Type:** Peer-reviewed journal.
- **Citations:** **68** (OpenAlex, journal version).
- **Quality:** **Citation-worthy: yes.** A Nobel laureate co-author and an explicit,
  reproducible checklist — an ideal template for the write-up.
- **Key findings — the seven-point protocol (decoded from the exhibit):**
  1. **Research Motivation** — (a) Does the model have a solid economic foundation? (b) Did the
     economic foundation or hypothesis exist *before* the research was conducted?
  2. **Multiple Testing and Statistical Methods** — (a) Did the researcher keep track of all
     models and variables tried, both successful and unsuccessful? (b) Full accounting of
     interaction variables? (c) Did they investigate all variables in the agenda, or cut the
     research as soon as they found a good model?
  3. **Data and Sample Choice** — sensible data; integrity checks; transformations chosen in
     advance and robust to minor changes; reasonable outlier-exclusion rules; winsorization level
     chosen before modelling.
  4. **Cross-Validation** — (a) Awareness that **true out-of-sample tests are only possible in
     live trading**; (b) steps to eliminate out-of-sample iteration; (c) is out-of-sample
     analysis representative of live trading, e.g. **are trading costs and data revisions taken
     into account**?
  5. **Model Dynamics** — resilience to structural change; overcrowding risk; **steps to minimize
     the tweaking of a live model**.
  6. **Complexity** — minimize the curse of dimensionality; simplest practicable specification;
     interpret the model's predictions rather than using it as a black box.
  7. **Research Culture** — reward the quality of the science rather than the finding of a
     winning strategy; understand that most tests will fail; seek the truth, not something that
     works.
  - Key number: "**Given 20 randomly selected strategies, one strategy will likely exceed the
    two-sigma threshold (t-statistic of 2.0 or above) purely by chance. As a result, the
    t-statistic of 2.0 is not a meaningful benchmark if more than one strategy is tested.**"
  - "Hubris is our enemy. A protocol is a simple step."
- **Relevance:** Q6 and the write-up. Protocol 4(a) — "true out-of-sample only exists in live
  trading" — is the one genuinely favourable statistical thing we can say about our 2.5 days.
- **Caveats:** Aimed at long-horizon factor research; the *spirit* transfers, several specifics
  do not.

### S14 — OCC exercise-by-exception / assignment mechanics
- **Citation:** Options Clearing Corporation, exercise-by-exception ("Ex-by-Ex") procedure, as
  described in OCC Info Memos and OIC's `optionseducation.org` reference library; underlying
  disclosure document: OCC, *Characteristics and Risks of Standardized Options* (the ODD).
- **Type:** Clearing-house / SRO-adjacent educational material (not peer-reviewed).
- **Quality:** **Citation-worthy: with caveats.** The $0.01 threshold is consistently reported by
  OCC/OIC and by brokers, but I read it via OIC's FAQ and secondary summaries rather than a
  clean primary OCC rule page; see "Paywalled / wanted".
- **Key findings:**
  - Exercise-by-exception is an administrative procedure in which **OCC automatically exercises
    expiring options that are in the money by a threshold amount unless the clearing member
    instructs otherwise**. For equity options the threshold is **$0.01 per contract in the money**
    for customer, firm and market-maker accounts.
  - It is a procedure **between OCC and its clearing members**; the customer's broker may apply a
    different value, and the customer still needs to communicate contrary instructions.
  - SPY/QQQ options are **American-style and physically settled**; SPX/XSP index options are
    **European-style and cash-settled**, so early assignment is impossible and expiration
    resolves to a known cash amount.
- **Relevance:** Q4. This is the mechanical basis for the hard "flat before 15:45 ET" gate.
- **Caveats:** Secondary sourcing on the exact threshold; broker policies vary. Verify with the
  executing broker before relying on any specific number.

### S15 — tastytrade "manage at 50 % / 21 DTE" practitioner research
- **Citation:** tastytrade research segments on managing winners at 50 % of max profit and
  managing at 21 days to expiration (various dates); secondary summaries via TalkMarkets and
  tastytrade support documentation.
- **Type:** Industry/broker marketing research and blog content.
- **Citations:** None; not indexed.
- **Quality:** **Citation-worthy: NO.** Methodology is not published in reproducible form, there
  is no peer review, the publisher is a brokerage with a direct commercial interest in trade
  frequency, and independent attempts to replicate (e.g. "Sweet Volatility") report different
  conclusions. I could not obtain the underlying P&L distributions or standard errors.
- **What is claimed:** closing at 50 % of the credit received raises win rate; managing at 21 DTE
  produced "the same P/L as holding to expiration" but with smaller losses than holding 45-day
  positions open.
- **Relevance to us: near zero, and this is the finding.** The 21-DTE rule is defined on a
  45-DTE entry cycle. **Our structures are 0–2 DTE — 21 DTE never occurs inside our universe**,
  so the rule is not merely unsupported, it is inapplicable. The 50 %-of-credit profit target is
  a plausible *variance-reduction* heuristic (it removes gamma exposure early) and we may use it
  for that reason, but we must not present it as evidence-backed.
- **Caveats:** Listed here explicitly so that it is on the record as *rejected*, not overlooked.

---

## Evidence table

| # | Claim | Supporting sources | Contradicting / qualifying | Confidence |
|---|---|---|---|---|
| C1 | Full Kelly is far too aggressive under parameter uncertainty; fractional Kelly is the standard response | S4 (Ziemba/MacLean; Chopra-Ziemba 100:3:1 for log investors; 2× Kelly ⇒ zero growth), S11 (estimation/selection bias inflates apparent edge) | None found | **Supported — high** |
| C2 | With the review-A distribution (mean −1.1 % of margin) the growth-optimal fraction is exactly zero | S4 (Kelly theory) + own computation on review-A numbers | Only if the true mean is positive, which is unproven | **Supported — high** (conditional on review A's mean) |
| C3 | Errors in the estimated mean dominate all other estimation errors for a log/Kelly investor | S4 (Chopra & Ziemba 1993, 20:1 general, 100:3:1 for log investors) | None found | **Supported — high** (single primary source, but it is the primary source) |
| C4 | Buying put protection produces *worse* drawdowns than simply holding less risk, per unit of return | S1 (PPUT: −32.1 % vs −20.9 % over 250 days; divesting wins 97–100 % of windows), S2 (2 %/yr drag, protection "less effective... than most investors might expect") | S1 itself: protection wins "when a very large crash occurs prior to the options' expiration"; S2 is a conflicted publisher | **Supported — high** (two sources, one peer-reviewed; S2 not independent of S1 — same firm — so treat as 1.5 sources) |
| C5 | Under a random walk, a stop-loss overlay has strictly negative expected value; benefits require momentum/regime persistence and appear only at longer sampling frequencies | S3 (Proposition 1; "no value at short-term sampling frequencies") | S3 also shows +1.5 % return / −5 % vol / +20 % Sharpe at monthly intervals — so the claim is frequency-conditional, not absolute | **Supported — medium-high** (single source, but peer-reviewed with a formal proposition; transfer to short options is by analogy) |
| C6 | Drawdown limits should scale position size continuously with remaining budget rather than switch off abruptly | S5 (optimal investment ∝ surplus W−αM) | Klass & Nowicki (2005): not always optimal in discrete time | **Supported — medium-high** |
| C7 | A single realized maximum drawdown carries almost no information; drawdown must be treated as a distribution | S6 (CED = tail mean of the MDD *distribution*; path-dependent, serial-correlation sensitive), S11 (sample length is one of four inflation sources) | None found | **Supported — high** |
| C8 | Pre-trade, automated, blocking controls are the regulatory standard; monitoring-only controls are known to fail | S7 (pre-order-entry requirement; direct and exclusive control), S9 (RTS 6 Art. 15 pre-trade controls), S8 (PMON "relied entirely on human monitoring"; $2m limit not linked to order entry), S10 (one-step disable) | None found | **Supported — very high** (four independent regulator/enforcement sources) |
| C9 | A limit that is not wired into the order path is not a limit | S8 (the $2m 33-Account limit existed and did nothing) | None found | **Supported — high** (single case, but it is a settled SEC finding of fact) |
| C10 | Incident response must be pre-scripted; ad-hoc remediation during a live incident can amplify losses | S8 (uninstalling correct code "worsened the problem"), S10 (one-step disable), S9 (Art. 12 kill functionality) | None found | **Supported — high** |
| C11 | With N ≈ 2–10 trades, no return-based performance statistic (Sharpe, win rate, annualized return) is meaningful | S11 (sample length, non-normality, trials), S12 (t > 3.0 hurdle), S13 (t = 2.0 not meaningful after >1 test) + own power computation (N ≈ 1,058 trades for t = 2 at a +2 % edge) | None found | **Supported — very high** |
| C12 | True out-of-sample evidence exists only in live trading — the one statistical virtue of our live window | S13 (Protocol 4a), S11 (holdout reuse degrades to in-sample) | Does not rescue the sample size (C11) | **Supported — high** |
| C13 | American-style physically-settled options (SPY/QQQ) carry pin and assignment risk that can break a "defined-risk" spread; European cash-settled index options do not | S14 (Ex-by-Ex at $0.01; American vs European settlement) | Sourcing on the exact $0.01 threshold is secondary | **Supported — medium-high** (mechanism certain; threshold needs primary confirmation) |
| C14 | The tastytrade "21 DTE / 50 % profit" management rules are evidence for our use case | — | S15: not reproducible, conflicted publisher, and structurally inapplicable to a 0–2 DTE book | **Rejected** |
| C15 | There exists a published academic standard for delta/gamma/vega/theta limits per unit of capital | — | Searched; found only vendor and blog material, no academic or regulatory standard | **Not supported — no source found.** Limits must be derived from the max-loss budget instead (see Q4) |

---

## Answers to research questions 1–6

### Q1 — Position sizing under fat tails for option selling

**The framework.** Kelly (1956) maximizes E[log W], which maximizes the asymptotic growth rate
and, per Breiman (1961), minimizes expected time to large goals. Thorp (2006) carried it into
blackjack, sports betting and markets. The essential warning comes from the same authors
(S4): the Kelly bettor's Arrow–Pratt risk aversion is 1/W, i.e. **essentially zero**, which is
why "automatic use of the Kelly strategy in any investment situation is risky and can be very
dangerous."

**Three facts that force fractional Kelly:**
1. **Overbetting is catastrophically asymmetric.** Betting exactly 2f\* yields a growth rate of
   *zero*; beyond f\* both growth and security decline, so "it is never advisable to wager more
   than f\*" (S4). In the Ziemba/MacLean simulation, minimum final wealth degrades from **+$2,368
   at 0.26·Kelly to −$102.5 million at 1.57·Kelly** on the same stake.
2. **The mean is the parameter you cannot estimate, and it is the one that matters most.**
   Chopra & Ziemba (1993), reported in S4: errors in means are ~20× as costly as covariance
   errors in general, and **~100:3:1 for the log investor**. With N ≈ 10 trades our standard
   error on the mean is 10.3 % of margin (computed below) — we are estimating the single most
   important parameter with essentially no precision.
3. **Kelly's advantages are asymptotic; we have three sessions.** S4's own conclusion: "no matter
   how favorable the investment opportunities are or how long the finite horizon is, a sequence
   of bad scenarios can lead to very poor final wealth outcomes."

Half-Kelly is the conventional compromise ("a toned down version of full Kelly that provides a
lot more security", S4); quarter-Kelly is common where parameter uncertainty is severe. Our
uncertainty is worse than severe — the point estimate of our edge is *negative*.

**Applying it to a bounded, negatively-skewed, high-win-rate credit spread.** Using review A's
0DTE iron-condor distribution (mean −1.1 %, median +5.5 %, P25 −24 %, P5 −100 % of margin), I
calibrated a five-point discrete distribution that reproduces the quantiles and the mean exactly
(assumptions stated in §"Sizing and ruin arithmetic"). Its moments: **mean −1.1 %, SD 32.5 %,
skewness −1.31, excess-of-normal kurtosis 4.72** — bounded below at −100 %, capped above at the
credit, exactly the shape described.

**Kelly result:**

| Assumed true mean return on margin | Full Kelly f\* | Half-Kelly | Quarter-Kelly |
|---|---|---|---|
| **−1.1 % (review A as measured)** | **0 %** | 0 % | 0 % |
| 0.0 % (break-even) | 0 % | 0 % | 0 % |
| +2.0 % (optimistic; assumes we beat the average 0DTE condor) | 17.4 % | 8.7 % | 4.4 % |
| +5.0 % (very optimistic) | 38.6 % | 19.3 % | 9.7 % |

**The Kelly-optimal fraction at the measured edge is exactly zero.** This is not a rhetorical
flourish — for a negative-mean bet, every positive f reduces E[log W]. Any positive size we take
is therefore *not* justified by growth optimality; it is justified by the fact that we are
required to trade options to enter, and by the option value of demonstrating a process.

**Recommendation: 2 % of capital at risk per session, 6 % cumulative cap** (I recommend
tightening review A's proposed 3 %/9 %). Rationale:
- 2 % is **less than half of quarter-Kelly even under the optimistic +2 % edge assumption** —
  i.e. it is conservative against a hypothesis we cannot support.
- It keeps the absolute worst case (three consecutive total losses) at **−5.88 %**, which is
  survivable and, importantly, *presentable*.
- The difference between 2 % and 3 % in expected P&L is −0.07 % vs −0.10 % of capital: **the
  larger size buys nothing but variance.** That is the whole argument in one line.

### Q2 — Drawdown control and stop rules

**Drawdown-based sizing beats drawdown-based halting.** Grossman & Zhou (1993) (S5) solve for the
policy that keeps W_t ≥ α·M_t and find the optimal exposure is **proportional to the surplus
W_t − α·M_t**. The practical translation: risk per session should shrink continuously as the
cumulative drawdown budget is consumed, rather than running at full size until a cliff. Concretely,
with a 6 % cumulative floor and 2 % nominal per session:

`risk_today = 2% × (remaining_budget / total_budget)`, floored at 0.

So a −2 % first day cuts day 2 to ~1.33 %, and a further −2 % cuts day 3 to ~0.67 %. This has the
side benefit of making a run of losses self-terminating without a discontinuous "trading halted"
event, which is both better risk management and a better demo.

**Daily loss limits should still exist as a hard backstop.** RTS 6 Article 15 (S9) requires
"market and credit risk limits based on capital base... and risk tolerance" plus a **repeated
automated execution throttle** that disables the strategy after a predetermined number of
executions "until re-enabled by staff." That is the correct template: a soft, continuous sizing
taper *plus* a hard, blocking daily-loss kill.

**Stop-losses on short option positions: the evidence says be very careful.** Kaminski & Lo (2014)
(S3) prove that **under the Random Walk Hypothesis the stopping premium is always negative** —
a stop-loss on a random-walk asset is a pure cost. They find positive stopping premia only under
momentum or regime-switching processes, and only **at longer sampling frequencies**; they
explicitly find "stop-losses to be of no value to investors using short-term sampling
frequencies." Their best result (+1.5 % return, −5 % volatility, +20 % Sharpe) came from
**monthly** stopping intervals on 1993–2011 futures data.

For our book that argues *against* a price-triggered stop on the spread:
- Intraday SPY over a few hours is close enough to a random walk that we should expect a negative
  stopping premium.
- A stop-loss on a short spread crosses the bid-ask **twice** (exit, and any re-entry), and
  review A already established that transaction costs consume the entire 0DTE edge.
- Stops on short gamma are triggered precisely when liquidity is worst and spreads widest.

**But there is a genuine counter-consideration specific to short options that Kaminski & Lo do
not cover:** a short gamma position's loss accelerates, and the *max* loss is realized abruptly
near the strike. This is why the correct control is **structural, not reactive** — the bought
wing caps the loss at entry, before any price path occurs. Review A already prescribes always
buying the wings; that decision *is* the stop-loss, executed at t=0 at a known price, and it
dominates a reactive stop because it costs a known premium instead of an unknown slippage.

**Recommendation:**
- **No price-based stop-loss on individual spreads.** The bought wing is the loss cap.
  (Cite S3 for why a reactive stop is not free.)
- **Yes to a hard daily-loss kill** at the session budget — this is a *portfolio* control that
  halts *new risk*, not a stop that liquidates into a spike.
- **Yes to continuous drawdown-scaled sizing** per S5.
- **Yes to a time-based exit** (flat before 15:45 ET) — this is not a stop-loss, it is
  elimination of an unbounded risk (Q4).
- A 50 %-of-credit profit-taking rule is acceptable **as variance reduction only**, on the honest
  grounds that it removes gamma exposure early. We must not cite tastytrade for it (S15).

### Q3 — Hedging and the cost of protection

**Is buying protection worth it? On the evidence: no, and it is worse than the naive alternative.**

Israelov (2019) (S1) is the decisive result. Over July 1986 – May 2016:
- SPX earned 5.8 % annualized excess return; the Cboe 5 % Put Protection Index (PPUT) earned 2.5 %.
- **36.5 % SPX + 63.5 % cash earned the same 2.5 %** — the protection contributed nothing that
  simply holding less could not.
- **Return-matched, the protected portfolio had *worse* drawdowns: −9.6 % vs −6.6 % over 20 days,
  −32.1 % vs −20.9 % over 250 days.**
- **Divesting produced better peak-to-trough drawdowns 97 % of the time over the shortest windows
  and 100 % of the time over windows longer than about half a year.**
- The drag: **−1.8 % annualized alpha, t = −2.0**, consistent with the volatility risk premium.

The mechanism matters for us: "equity drawdowns have lives of their own that may not conveniently
coincide with option expiration cycles." A put protects a *defined window*, but drawdowns are
*path* events. AQR (S2) states the same condition operationally: the benefit "relies crucially on
getting two things right: 1) buying an option shortly before a market drawdown, and 2) having the
option's expiration align" with it. Over 2.5 days our probability of getting both right is
essentially our probability of correctly timing a crash — which review B already established the
LLM cannot do.

Israelov's own exception is the one honest counter-case: protection wins "when a very large crash
occurs prior to the options' expiration."

**Implication for the user's wish "higher risk only with hedging": the wish must be declined, and
the reason is citable.** A hedge does not buy back risk budget. Israelov's finding is precisely
that a hedged-but-larger position is *dominated* by a smaller unhedged one at the same expected
return, on the very metric the user cares about (drawdown). The correct sentence for the write-up:
**"We treat position size, not purchased convexity, as our primary risk control, because the
evidence says purchased convexity does not reliably reduce drawdowns (Israelov 2019)."**

**Verdict on the ~0.3 % long-gamma tail sleeve: keep it, but reclassify it.** It should be funded
and described as:
- a **demonstration and explainability asset** — it makes the Greeks dashboard show a
  non-degenerate gamma/vega profile, which is far more compelling to judges than a flat book, and
  it exercises the long-option code path;
- a **structural counterweight** to a short-gamma book, sized so small that its cost is
  immaterial (0.3 % of $100k = $300, i.e. ~0.12 % of capital per session across 2.5 sessions);
- **not** a justification for larger short-premium size, and **not** claimed as an
  expected-value-positive tail hedge.

The write-up should state the cost honestly: at ~0.3 % of capital the sleeve is a rounding error
against a 2 % session budget, and we expect it to expire worthless most of the time. Framing it
as a deliberate, costed, *disclosed* bet — rather than as protection — is more credible than
claiming a hedging benefit the literature says we will not get.

### Q4 — Greeks-based risk budgets for a short-dated book

**Finding first: I could not find an academic or regulatory standard for Greek limits per unit of
capital.** Searches returned only vendor guides and blogs (see C15). Every published limit
framework I could locate is firm-specific and unpublished. So rather than invent a citation, the
honest and stronger approach is to **derive the budget from the max-loss constraint**, which is
exactly what RTS 6 Article 17 asks for: "for derivatives, controls on maximum long/short and
overall strategy positions" plus "real-time calculation of outstanding exposure" (S9).

**The key structural insight: for defined-risk spreads, the Greeks limits are a monitoring layer,
not the binding constraint.** Max loss is known and bounded *at entry* — it is
`(width − credit) × 100 × contracts`. No path of delta, gamma or vega can produce a loss larger
than that. Therefore:
- The **binding** gate is the max-loss budget (2 % of capital per session).
- The **Greeks** gates exist for early warning, for detecting a book that has drifted from its
  intended shape, and — per review B — for the ex-ante vs ex-post reconciliation that is our real
  process evidence.

**Proposed limits for a $100,000 book (derived, not cited — label them as such):**

| Greek | Limit | Derivation |
|---|---|---|
| Net delta | \|Δ$\| ≤ 5 % of capital = **$5,000 SPY-equivalent** | A 1 % index move then contributes ≤ $50 = 0.05 % of capital from delta alone — an order of magnitude inside the session budget. Keeps the book recognisably market-neutral. |
| Net dollar gamma | \|ΔΔ$ per 1 % move\| ≤ **2 % of capital = $2,000** | After a 2 % gap, delta cannot exceed ~$4,000 + starting delta, keeping the *post-gap* delta still inside a manageable band. Gamma is the dominant 0DTE risk; this is the limit that actually constrains contract count. |
| Net vega | \|vega\| ≤ **0.25 % of capital per vol point = $250** | At 0–2 DTE vega is structurally tiny; a breach means the book has drifted to longer tenor than intended. Diagnostic, not protective. |
| Net theta | **No limit — a target plus a reconciliation** | Theta is the intended revenue. Record ex-ante expected theta and compare to realized decay P&L; a large gap is the signal, not the level. |
| Max loss (binding) | **≤ 2 % of capital per session, ≤ 6 % cumulative** | Q1. This is the gate that blocks orders. |

**Pin risk and early assignment — why to be flat before 15:45 ET.** SPY and QQQ options are
**American-style and physically settled**. Two distinct hazards (S14):
1. **Exercise by exception.** OCC automatically exercises options in the money by as little as
   **$0.01** unless instructed otherwise. If the short leg of a spread finishes $0.01 ITM and the
   long wing finishes OTM, the wing is *not* exercised and does not offset. The result is an
   assigned stock position — roughly **$65,000 of SPY notional per contract** at SPY ≈ 650 —
   carried overnight or over a weekend, against a spread whose "defined risk" was a few hundred
   dollars. **The defined-risk property is destroyed at expiration, not during the day.**
2. **Pin risk proper.** With the underlying oscillating around the short strike into the close,
   you cannot know whether you will be assigned, so you cannot know your resulting position or
   hedge it. The exposure is decided after you can no longer trade.
3. **Early assignment** on deep-ITM short calls before an ex-dividend date is the classic
   additional trigger for physically-settled equity options; short puts with near-zero extrinsic
   value are the other. Check the ETF distribution calendar before selling calls.

Hence the gate: **all short-dated positions flat by 15:45 ET, enforced by a scheduled
liquidation task with escalating aggressiveness, not by an LLM decision.** The buffer should be
15 minutes, not 5, because the liquidation itself may need several attempts in a widening market.
For the Friday 09:30–11:00 window, flat by 10:50 ET regardless of P&L.

**Cash-settled index options (SPX/XSP) are structurally superior here** — European-style, so no
early assignment is possible; cash-settled, so expiration resolves to a known cash amount and the
maximum loss computed at entry remains the maximum loss. XSP is the 1/10-size S&P index option,
which is the right granularity for a $100k account. *(Whether the broker supports index options is
a platform question I was instructed not to research; the strategy should be written so that the
instrument is a configuration parameter, and the risk write-up should note that SPY/QQQ requires
the 15:45 flatten gate while SPX/XSP would not.)*

**Margin and buying power for spreads.** Under the standard US treatment, a vertical credit spread
with both legs in the same expiry and the long leg protecting the short is margined at its
**maximum loss** — `(strike width − net credit) × 100 × contracts` — rather than as a naked short.
This is what makes "2 % of capital at risk" both a risk statement and a buying-power statement,
and it is why the wings are non-negotiable: without them the position is naked-short-margined and
the risk is unbounded. The exact treatment must be confirmed with the executing broker before
sizing; a **pre-trade buying-power check** is on the gate list precisely because this assumption
could be wrong.

### Q5 — Regulatory pre-trade risk controls as a design template

The three regulatory sources converge on the same architecture, and the Knight order shows what
happens when each piece is missing. The synthesis:

**Principle 1 — controls must be PRE-trade, not post-trade.** SEC 15c3-5 requires preventing order
entry "unless there has been compliance with all regulatory requirements that must be satisfied
**on a pre-order entry basis**" (S7). RTS 6 Article 15 lists the pre-trade controls by name (S9).
Knight's PMON was a *post-execution position monitoring system* — it saw the disaster and could
not stop it (S8).

**Principle 2 — controls must BLOCK, not alert.** Knight had a **$2 million gross position limit**
on the 33 Account; "it did not link this account to any automated controls." PMON "relied entirely
on human monitoring and did not generate automated alerts," "did not display the limits," and
"experienced delays during high volume events... resulting in reports that were inaccurate" (S8).
**Every limit in our system must be a function that returns reject/accept on the order path.**

**Principle 3 — the controlled system must not be able to disable its own controls.** 15c3-5
requires "direct and exclusive control" of the risk controls (S7); FINRA 15-09 asks for "controls
and limitations on a trader's ability to overwrite or otherwise evade system controls" (S10).
Mapped to our architecture, and consistent with review B: **the LLM is a caller of the gate, never
a configurer of it.** Thresholds live in a config file the model cannot write.

**Principle 4 — one-step kill.** RTS 6 Article 12: cancel immediately "any or all of its
unexecuted orders" (S9). FINRA 15-09: "quickly disable the algorithm or supporting platform with
a **minimal number of steps**" (S10). Knight had none (S8).

**Principle 5 — output must be reconciled against input.** Knight lacked "a control to compare
orders leaving SMARS with those that entered it" (S8); RTS 6 Article 17 requires "reconciliation
of electronic trading logs" and "real-time calculation of outstanding exposure" (S9).

**Principle 6 — deployment is a risk control.** Knight deployed to 7 of 8 servers with no second
reviewer and no written procedure, and left dead code "present and callable" (S8). FINRA 15-09
asks for change management, "redundant or multiple system validations," archived code versions,
and pilot-sized deployment (S10). RTS 6 Articles 5–8 require a segregated test environment and
controlled deployment with predefined limits (S9).

**Principle 7 — incident response must be written in advance.** Knight had no incident-response
procedures; its ad-hoc remediation "**worsened the problem**" (S8).

The concrete 1:1 mapping is the checklist below.

### Q6 — Evaluation and honest reporting of a 2-day live window

**What is NOT meaningful.** With N ≈ 2–10 trades, no return-based statistic can be reported
honestly. My own computation on the review-A distribution (SD = 32.5 % of margin):

| True edge per trade | N needed for \|t\| = 2.0 | N needed for \|t\| = 3.0 (Harvey/Liu/Zhu) |
|---|---|---|
| +2 % of margin | **1,058 trades** | **2,380 trades** |
| +5 % of margin | 169 trades | 381 trades |
| +10 % of margin | 42 trades | 95 trades |

**At N = 10 the standard error on the estimated edge is 10.3 % of margin; the 95 % confidence
interval is ±20.2 %, roughly ten times wider than the ~2 % effect we would be trying to detect.**
Harvey, Liu & Zhu (2016) put the credible hurdle at |t| > 3.0 (S12); Arnott, Harvey & Markowitz
(2019) note that "given 20 randomly selected strategies, one will likely exceed the two-sigma
threshold purely by chance" (S13). Bailey & López de Prado (2014) show that sample length,
non-normality and trial count jointly inflate any observed Sharpe (S11) — and our returns are
skewed −1.31 with fat tails, exactly the case DSR was built to deflate. **Therefore: no Sharpe
ratio, no win rate, no annualized return, no "profit factor."** Reporting them would be the
single most obvious sign of an unserious submission.

**What IS meaningful with N = 2–10.** Every one of these is a *deterministic property of our
process*, measurable exactly, with no sampling error:

1. **Gate adherence:** count of orders proposed, blocked, and by which gate. Target: zero gate
   breaches; every block logged with the rule name and the value that tripped it.
2. **Realized vs ex-ante risk:** for each position, max loss computed at entry vs worst realized
   mark-to-market. A defined-risk book must never exceed its stated max loss — this is a
   *falsifiable* claim we can demonstrate.
3. **Max intraday drawdown vs the limit**, presented against the ex-ante drawdown *distribution*
   (S6: drawdown is a distribution, one realization is not an estimate).
4. **Ex-ante vs ex-post Greeks reconciliation** (review B's metric; RTS 6 Art. 17's duty):
   predicted delta/gamma/vega/theta at entry vs realized attribution at exit.
5. **Execution quality:** slippage vs the NBBO mid at decision time, per leg, in dollars and in
   basis points of the credit. This is where review A's "costs eat the edge" conclusion becomes
   *measurable in our own data*.
6. **LLM veto rate and veto reasons:** how often the regime/news layer blocked a trade the
   deterministic layer would have taken, with the reason string.
7. **Determinism / replay:** re-run the recorded market data and decision log; assert the system
   reproduces the same orders. This directly answers "is this a real system or a demo," and it is
   the cheapest high-credibility artifact we can produce.
8. **Time-to-flat:** measured seconds from the 15:45 trigger to a flat book.

**P&L attribution.** Decompose realized P&L into theta, delta, vega and gamma components rather
than reporting a single number. For each position and each mark-to-mark interval:

`ΔP&L ≈ Θ·Δt + Δ·ΔS + ½·Γ·(ΔS)² + ν·Δσ + residual`

Report the four components plus the unexplained residual and the transaction-cost line
separately. This is valuable for three reasons: (a) it shows whether we earned what we intended to
earn (theta) or got paid for something we did not intend (a directional delta bet); (b) the
residual size is a direct check on our pricing and Greeks code; (c) a positive P&L that turns out
to be 90 % delta is *luck*, and saying so is far more impressive than banking it.

**Benchmarks — three, not one:**
1. **SPY buy-and-hold over the same hours** (09:30–16:00 Wed/Thu, 09:30–11:00 Fri), the naive
   alternative any judge would think of. Also report SPY's realized move, because our
   strategy's outcome is mostly a function of it.
2. **Cboe CNDR and PUT indices** as strategy-family analogues — review A already establishes
   CNDR's −13.7 % vs PUT's −32.7 % max drawdown (2006–2019), which is the defined-risk case in one
   number. Israelov's use of PPUT (S1) is the methodological precedent for benchmarking against a
   public option index rather than an unhedged one.
3. **A random-entry Monte Carlo of the same structure** — same instruments, same sizing, same
   number of trades, entry times drawn at random within the session — run over historical data to
   produce a *distribution* of 2.5-day outcomes. **Report our realized P&L as a percentile of
   that distribution.** This is the honest "luck baseline" and the single most defensible number
   in the entire report: it directly answers "how much of this was skill?" with "here is where we
   landed in the distribution of doing it at random, and the distribution is wide."

**Reporting protocol.** Adopt Arnott, Harvey & Markowitz (2019) (S13) explicitly:
- State the economic hypothesis (volatility risk premium; review A) **before** the results, and
  note that we formed it before trading.
- **Count and disclose every variant tried**, including the ones that failed. Protocol 2(a).
- Fix the evaluation window and metrics **before** Wednesday's open; do not choose the flattering
  window afterwards. Protocol 3.
- State plainly that "true out-of-sample tests are only possible in live trading" (Protocol 4a) —
  this is the one statistical point that genuinely favours us, and it should be made once,
  precisely, not oversold.
- Include trading costs in every comparison (Protocol 4c).
- **Do not tweak the model mid-run** (Protocol 5c). If we change anything between sessions, say
  so and treat the sessions as separate samples.

---

## Risk-gate checklist

Each row maps a regulatory or academic control to a concrete code-level gate. Thresholds are
suggestions for a $100,000 paper account and should live in a version-controlled config file the
LLM cannot modify. **Every gate returns accept/reject on the order path — none is alert-only.**

| # | Gate name | Rule | Suggested threshold ($100k) | Source |
|---|---|---|---|---|
| 1 | `gate_capital_threshold` | Reject any order whose max loss would push cumulative session risk above the session budget | 2 % = **$2,000** per session | SEC 15c3-5 "pre-set credit or capital thresholds" (S7); Knight $2m limit not linked (S8) |
| 2 | `gate_cumulative_drawdown` | Reject all new risk if cumulative realized+unrealized loss since start exceeds the campaign budget | 6 % = **$6,000** over 3 sessions | S5 (drawdown constraint W ≥ αM); RTS 6 Art. 15 risk limits (S9) |
| 3 | `gate_drawdown_taper` | Scale today's budget by remaining/total budget before sizing — continuous, not binary | `2% × remaining/6%` | Grossman & Zhou (1993): exposure ∝ surplus (S5) |
| 4 | `gate_defined_risk_only` | Reject any order that leaves a naked short leg; every short must have a bought wing in the same expiry | Hard reject, no override | Review A; margin treatment (Q4); RTS 6 Art. 17 derivative position controls (S9) |
| 5 | `gate_price_collar` | Reject any limit price more than X % away from the NBBO mid at decision time | **5 %** of mid, and reject if the option's bid-ask spread exceeds 15 % of mid | RTS 6 Art. 15 "price collars" (S9); Knight's 9.5 % collar was too loose to help (S8) |
| 6 | `gate_max_order_value` | Reject any single order whose notional or max loss exceeds a cap | max loss ≤ **$1,000** per order (half the session budget) | RTS 6 Art. 15 "maximum order values" (S9) |
| 7 | `gate_max_order_volume` | Reject orders above a contract-count cap | ≤ **10 contracts** per order | RTS 6 Art. 15 "maximum order volumes" (S9) |
| 8 | `gate_message_rate` | Reject/queue if orders+cancels exceed a rate limit | ≤ **20 orders/minute**, ≤ 200/session | RTS 6 Art. 15 "maximum message limits" (S9); FINRA 15-09 outbound message thresholds (S10) |
| 9 | `gate_execution_throttle` | Auto-disable the strategy after N executions until manually re-enabled | **30 fills/session**, then halt | RTS 6 Art. 15 "repeated automated execution throttle" (S9) |
| 10 | `gate_duplicate_order` | Reject an order with the same instrument/side/quantity within a cooldown window | 60-second dedupe key | SEC 15c3-5 duplicative-order controls (S7) |
| 11 | `gate_erroneous_price` | Reject if the quote is stale, crossed, locked, or zero-bid; reject if the mid moved >2 % since the decision was formed | stale > **5 s**; mid drift > 2 % | SEC 15c3-5 "appear to be erroneous" (S7); Knight had "no mechanism to test whether their systems were relying on stale data" (S8) |
| 12 | `gate_greeks_budget` | Reject if the post-trade book would breach any Greek limit | \|Δ$\| ≤ $5,000; \|Γ$ per 1 %\| ≤ $2,000; \|vega\| ≤ $250/vol pt | Derived (Q4) — **no published standard found**; RTS 6 Art. 17 position controls (S9) |
| 13 | `gate_buying_power` | Pre-trade check that the broker's reported buying power covers the spread's max loss with a margin of safety | require **1.25×** the computed max loss | SEC 15c3-5 capital thresholds (S7); Q4 margin caveat |
| 14 | `gate_time_window` | Reject any opening order outside the permitted entry window | no new risk before **09:45** or after **15:00** ET; Friday no new risk after 10:15 | Operational; avoids the open auction (Knight's collar did not apply to pre-open orders, S8) |
| 15 | `gate_flatten_deadline` | Scheduled task force-closes all positions before the close; escalating limit prices; not an LLM decision | flat by **15:45 ET** (Fri: 10:50 ET) | Pin risk / exercise-by-exception at $0.01 (S14); Q4 |
| 16 | `gate_assignment_watch` | Block new short calls in a name within N days of an ex-dividend date; alert on any deep-ITM short leg | ex-div window **2 sessions** | Early-assignment mechanics (S14) |
| 17 | `gate_event_veto` | LLM/news layer may veto a trade; it may never *authorise* one that a deterministic gate rejected | veto-only, one direction | Review B; separation of duties |
| 18 | `gate_llm_output_schema` | Reject any LLM output that is not a valid enum/label; the model never emits prices, strikes, deltas or quantities | strict schema validation, reject on parse failure | Review B; SEC 15c3-5 "direct and exclusive control" (S7) |
| 19 | `kill_switch` | One command cancels all open orders and flattens all positions; also bound to a single keystroke and a file-flag the loop checks each cycle | < **5 seconds** to all-cancel | RTS 6 Art. 12 kill functionality (S9); FINRA 15-09 "minimal number of steps" (S10); Knight had none (S8) |
| 20 | `gate_daily_loss_kill` | Hard halt of all new risk when the session loss limit is hit — independent code path from gate 1 | **$2,000** realized+unrealized | RTS 6 Art. 15 (S9); Knight: automatic P&L shutdown existed for *some* groups only (S8) |
| 21 | `recon_order_echo` | After each cycle, compare orders sent to orders acknowledged by the broker; halt on mismatch | any mismatch ⇒ halt | Knight: no control "to compare orders leaving SMARS with those that entered it" (S8); RTS 6 Art. 17 reconciliation (S9) |
| 22 | `recon_position` | Reconcile the internal position book against the broker's positions every cycle; halt on divergence | any divergence ⇒ halt | RTS 6 Art. 17 (S9); Knight's 33 Account held unreconciled positions from multiple sources (S8) |
| 23 | `deploy_no_dead_code` | No unreachable/disabled strategy code paths in the deployed artifact; no feature flags that re-enable retired behaviour | code review + grep for disabled branches | Knight's Power Peg "remained present and callable" (S8) |
| 24 | `deploy_version_pin` | Log the git commit hash and full config with every order; archive code versions | hash in every order tag | FINRA 15-09 code archiving (S10); RTS 6 Art. 5–8 (S9) |
| 25 | `deploy_paper_first` | Every change runs a full replay against recorded data before touching the live loop; pilot with 1-contract size on first live use | mandatory | FINRA 15-09 pilot phase + segregated test environment (S10); RTS 6 Art. 7 (S9) |
| 26 | `incident_runbook` | Written, pre-agreed incident procedure: kill first, diagnose second; never modify code during a live incident | one page, written before Wednesday | Knight: no incident procedures; remediation "worsened the problem" (S8) |
| 27 | `audit_log` | Append-only structured log of every decision, input, gate evaluation, order and fill, with timestamps | full session, replayable | RTS 6 Art. 13 ex-post analysis at time granularity (S9); FINRA 15-09 record of testing/results (S10) |
| 28 | `strategy_description` | Maintain a plain-language description of what the algorithm does, sufficient to understand it without reading code | the one-page write-up | FINRA 15-09, verbatim practice (S10) |
| 29 | `config_immutability` | Risk thresholds live outside the agent's writable scope; the agent cannot edit its own limits | filesystem permissions / separate module | SEC 15c3-5 "direct and exclusive control" (S7); FINRA 15-09 no-override (S10) |
| 30 | `post_session_review` | End-of-session automated report: gates hit, Greeks reconciliation, slippage, P&L attribution | run after each close | RTS 6 Art. 9 self-assessment (S9); SEC 15c3-5 regular review (S7) |

---

## Sizing and ruin arithmetic

**Assumptions (stated explicitly, per Arnott et al. Protocol 3):**
- Outcome distribution from review A (Beckmeyer, Branger & Gayda 2023, 0DTE iron condors, returns
  as % of margin): **mean −1.1 %, median +5.5 %, P25 −24 %, P5 −100 %.**
- I calibrated a five-point discrete distribution reproducing the quantiles and matching the mean
  to four decimal places:

  | Return on margin | Probability | Cumulative |
  |---|---|---|
  | −100 % | 0.05 | 0.05 |
  | −33 % | 0.20 | 0.25 |
  | −8 % | 0.25 | 0.50 |
  | +20 % | 0.25 | 0.75 |
  | +30 % | 0.25 | 1.00 |

  Moments: mean −1.10 %, SD 32.5 %, skewness −1.31, kurtosis 4.72. The +20 %/+30 % upper points
  imply a credit-to-max-loss ratio of ~0.3, i.e. a credit of about 23 % of the strike width —
  reasonable for 10–16 delta short strikes. **If the real credit ratio is lower, the upper tail
  shrinks and every number below gets worse, not better.**
- Three sessions treated as **independent**. This is the most questionable assumption: a
  volatility regime shift would correlate the three days and fatten the joint left tail. Treat all
  tail probabilities below as **optimistic lower bounds**.
- "Risk per session" f = the fraction of capital placed at max-loss risk that session, deployed as
  a single risk unit.

**Kelly fraction estimate:**

| Assumed true mean return on margin | Full Kelly f\* | Half-Kelly | Quarter-Kelly | Growth rate g at f\* |
|---|---|---|---|---|
| **−1.1 % (as measured)** | **0.0 %** | 0.0 % | 0.0 % | 0.00000 |
| 0.0 % (break-even) | 0.0 % | 0.0 % | 0.0 % | 0.00000 |
| +2.0 % | 17.4 % | 8.7 % | 4.4 % | +0.00179 |
| +5.0 % | 38.6 % | 19.3 % | 9.7 % | +0.01034 |
| +10.0 % | 63.9 % | 32.0 % | 16.0 % | +0.03639 |

**Three-session outcome distribution by risk per session** (125-outcome exact enumeration):

| f per session | Mean P&L | Median | P25 | P05 | P01 | Worst case | P(intra-run dd > 5 %) | P(dd > 10 %) | P(≥1 max-loss day) |
|---|---|---|---|---|---|---|---|---|---|
| **1 %** | −0.03 % | +0.07 % | −0.36 % | −1.13 % | −1.65 % | **−2.97 %** | 0.00 % | 0.00 % | 14.26 % |
| **2 % ← recommended** | −0.07 % | +0.14 % | −0.72 % | −2.26 % | −3.29 % | **−5.88 %** | 0.01 % | 0.00 % | 14.26 % |
| **3 % (review A proposal)** | −0.10 % | +0.20 % | −1.09 % | −3.38 % | −4.91 % | **−8.73 %** | 0.73 % | 0.00 % | 14.26 % |
| **5 %** | −0.16 % | +0.33 % | −1.82 % | −5.63 % | −8.11 % | **−14.26 %** | 9.89 % | 0.35 % | 14.26 % |
| **10 %** | −0.33 % | +0.61 % | −3.69 % | −11.23 % | −15.84 % | **−27.10 %** | 19.75 % | 8.01 % | 14.26 % |

**Absolute worst case (three consecutive total losses), $100,000 account** — probability
0.05³ = **0.0125 %** under independence:

| f | Worst-case equity | Worst-case return |
|---|---|---|
| 1 % | $97,030 | −2.97 % |
| **2 %** | **$94,119** | **−5.88 %** |
| 3 % | $91,267 | −8.73 % |
| 5 % | $85,738 | −14.26 % |
| 10 % | $72,900 | −27.10 % |

**Dollar view at the recommended 2 %** (scale the 3 % row by 2/3, or directly): median +$135,
P25 −$725, P05 −$2,260, P01 −$3,290, worst −$5,881, best ≈ +$1,816.

**Reading of the table — the argument in three lines:**
1. **Ruin is not the risk; pointless variance is.** Even at 10 % per session, three total losses
   only cost 27 % — a defined-risk book cannot blow up an account in three days. The real cost of
   sizing up is the P05/P01 column, which scales linearly while the mean stays pinned at
   approximately zero.
2. **Going from 2 % to 3 % changes the mean from −0.07 % to −0.10 % and the P01 from −3.29 % to
   −4.91 %.** We would be buying 49 % more left-tail for a *worse* expectation.
3. **P(at least one maximum-loss session) = 14.26 % regardless of f.** A −100 % day is a
   14-in-100 event over our window; the only lever we control is how much it costs. This is the
   number to put on the slide.

---

## Evaluation and reporting plan

**Header line for the write-up:** *"We do not claim a statistically detectable edge. We claim a
risk process that behaved exactly as specified, and we report the evidence for that claim."*

**A. Metrics we report (all deterministic, none sampling-limited)**

| Metric | Definition | Why it is meaningful at N ≈ 2–10 | Source |
|---|---|---|---|
| Gate hit counts | Orders proposed / blocked, by gate name | Exact count, no inference | S7, S9, S10 |
| Max-loss adherence | For every position: ex-ante max loss vs worst realized mark | Falsifiable claim about the structure | Q4; RTS 6 Art. 17 (S9) |
| Realized vs allowed drawdown | Max intraday drawdown vs the 2 %/6 % limits, plotted against the ex-ante drawdown distribution | Drawdown is a distribution, not a point (S6) | S6 |
| Greeks reconciliation | Ex-ante Δ/Γ/ν/Θ at entry vs realized attribution | Directly tests our pricing code | Review B; RTS 6 Art. 17 (S9) |
| Slippage vs mid | Per leg, $ and bp of credit, vs NBBO mid at decision time | Makes review A's cost conclusion measurable in our own data | Review A; S13 Protocol 4c |
| LLM veto rate | Vetoes / proposals, with reason strings | Shows the AI layer did something auditable | Review B |
| Determinism replay | Re-run recorded data; assert identical order sequence | Binary pass/fail, no statistics | S9 Art. 13; S10 |
| Time-to-flat | Seconds from 15:45 trigger to flat book | Operational, exact | Q4 |

**B. P&L attribution.** Decompose into `Θ·Δt + Δ·ΔS + ½Γ(ΔS)² + ν·Δσ + residual + costs`.
Report all six lines. State explicitly whether the P&L came from the intended source (theta) or
from an unintended directional bet (delta) — a profitable delta outcome is luck and we will label
it as such.

**C. Benchmarks (three).**
1. **SPY buy-and-hold over identical hours** — plus SPY's realized move, since our outcome is
   largely a function of it.
2. **Cboe CNDR and PUT** as strategy-family analogues (review A: CNDR −13.7 % vs PUT −32.7 % max
   drawdown 2006–2019). Israelov's benchmarking against PPUT rather than an unhedged index (S1) is
   the methodological precedent.
3. **Random-entry Monte Carlo of the identical structure** — same instruments, same sizing, same
   trade count, entry times drawn uniformly within the session, over historical data. **Report our
   realized P&L as a percentile of that distribution.** This is the luck baseline and the single
   most defensible number in the report.

**D. What we explicitly refuse to report, and why.** Sharpe ratio, win rate, annualized return,
profit factor. Justification, one line each, citing S11 (sample length + non-normality + trials
inflate observed Sharpe; our skew is −1.31), S12 (credible hurdle is |t| > 3.0), S13 (t = 2.0 is
meaningless after more than one test), and our own power calculation (**~1,058 trades needed for
|t| = 2 at a +2 % edge; ~2,380 at |t| = 3; at N = 10 the 95 % CI on the edge is ±20.2 % of
margin**).

**E. Protocol adherence statement.** A short section mapping our process to Arnott, Harvey &
Markowitz's seven points (S13): hypothesis formed ex ante from published evidence (review A);
count of variants tried disclosed; evaluation window and metrics fixed before Wednesday's open;
live trading acknowledged as the only true out-of-sample; trading costs included everywhere;
no mid-run model tweaks (and disclosure if any occur); simplest practicable specification;
and — Protocol 7 — an explicit statement that we expected this to fail to produce detectable alpha
and designed the report accordingly.

---

## Follow-up reading

- **MacLean, Thorp & Ziemba (2010), "Long-term capital growth: the good and bad properties of the
  Kelly and fractional Kelly capital growth criteria," *Quantitative Finance*** — *cited in S4*.
  The dedicated good/bad-properties treatment; would give a cleaner citation than the book chapter.
- **Chopra, V. K., and W. T. Ziemba (1993), "The effect of errors in means, variances and
  covariances on optimal portfolio choice," *Journal of Portfolio Management*** — *cited in S4*.
  Primary source for the 20:1 and 100:3:1 results; worth citing directly rather than second-hand.
- **MacLean, Sanegre, Zhao & Ziemba (2004) and MacLean, Zhao & Ziemba (2009)** — *cited in S4*.
  Strategies that reduce the Kelly fraction to stay above a pre-specified wealth path with high
  probability. This is *exactly* our drawdown-taper gate and would be the ideal citation for it.
- **Klass & Nowicki (2005), "The Grossman and Zhou investment strategy is not always optimal,"
  *Statistics & Probability Letters*** — *cited in S5 discussion*. The discrete-time
  counter-result; needed if we lean hard on Grossman-Zhou.
- **Israelov & Nielsen (2015a, 2015b)** — *cited in S1*. Source of the −2.0 % annualized return
  on delta-hedged 5 % OTM puts, and of the "time-varying equity exposure adds risk" result.
- **Berger, Nielsen & Villalon (2011), "Chasing Your Own Tail (Risk)"** — *cited in S2*. The
  original paper; S2 is only the update.
- **Bhansali & Davis on tail hedging** — *new idea, not yet located*. The task named these
  authors; I did not find an open version within the time box. Would provide the pro-tail-hedge
  side of the argument, which currently rests entirely on AQR-affiliated authors (S1, S2) — a real
  gap in the evidence base for Q3.
- **Rockafellar, Uryasev & Zabarankin (2002, 2006), deviation measures** — *cited in S6*.
  Foundation for treating CED as a coherent risk measure.
- **Harvey & Liu (2018)** — *cited in S13*. The ongoing work on optimizing the false-positive /
  missed-discovery trade-off.
- **Gawande, *The Checklist Manifesto* (2009)** — *cited in S13*. Rhetorically useful for the
  write-up: our gate table *is* a pre-flight checklist, and that framing is judge-friendly.
- **Cboe SPX/XSP contract specifications** — *new idea*. If index options are available, XSP
  removes gates 15 and 16 entirely; worth confirming the settlement mechanics from Cboe primary
  documentation.

---

## Paywalled / wanted

| Item | Why wanted | Access status |
|---|---|---|
| Grossman & Zhou (1993), *Mathematical Finance* 3(3):241–276, DOI 10.1111/j.1467-9965.1993.tb00044.x | Exact statement of the optimal policy and the α-parameterization; I have the result from secondary summaries only, not from the paper's own text | Wiley paywall; no open version found |
| Kelly, J. L. (1956), "A New Interpretation of Information Rate," *Bell System Technical Journal* 35:917–926 | The origin; would be nice to cite directly | Not fetched; widely available but OpenAlex search failed to return it (search returned unrelated works) |
| Chopra & Ziemba (1993), *JPM* | The 20:1 / 100:3:1 numbers used in Q1 come to me **via S4**, not from the original | JPM paywall |
| MacLean, Thorp & Ziemba (2010), *Quantitative Finance* 10(7):681–687 | The canonical "good and bad properties" article | Taylor & Francis paywall; OpenAlex confirms existence (11–21 citations across versions) |
| Beckmeyer, Branger & Gayda (2023) 0DTE paper | The distribution underpinning **all** of §"Sizing and ruin arithmetic" — I used review A's reported quantiles without independent verification | Per instructions, not re-researched here; **flagged as a single point of failure for the sizing analysis** |
| OCC, *Characteristics and Risks of Standardized Options* (the ODD), and the primary OCC rule text for exercise-by-exception | To confirm the $0.01 threshold from a primary source rather than OIC FAQ / broker summaries | Not fetched within the time box |
| tastytrade underlying study data | To evaluate the 50 %/21 DTE claims properly | Not published; **this is itself the reason to reject S15** |
| Bhansali & Davis on tail hedging | The counterweight to S1/S2, both AQR-affiliated | Not located in an open version |
| Goldberg & Mahmoud published version, *Mathematics and Financial Economics* | I read the arXiv v5; page/volume numbers for a clean citation | Springer paywall |

---

## Method log

**Time box:** ~1 hour. **Sources examined in depth:** 15 (target was 10–16).

**Tools and workarounds.**
- WebSearch + WebFetch only, as instructed; no browser automation used.
- **WebFetch could not read any of the PDFs** — it returned raw binary/encoded streams for all of
  them (AQR ×2, Kelly chapter, Arnott, FINRA, Goldberg-Mahmoud). Workaround: the fetched PDFs are
  cached to disk by the tool, so I ran the local `pdftotext -layout` binary over the cached files
  and grepped the text. This recovered every paper cleanly and was far cheaper in context than
  re-fetching. **Recommendation for future reviews in this project: fetch the PDF once, then
  `pdftotext` the cached copy rather than fighting WebFetch.**
- **sec.gov rate-limited** a Chrome-User-Agent curl ("Request Rate Threshold Exceeded"). Retrying
  with a compliant `-A "Research Agent <email>"` User-Agent per SEC's Fair Access guidelines
  succeeded immediately. The Knight order PDF was fetched the same way.
- **The Arnott et al. seven-point protocol exhibit is set in a Caesar-shifted (+3) display font**,
  so `pdftotext` produced `5HVHDUFK0RWLYDWLRQ` for "ResearchMotivation". I decoded it with a
  four-line Python shift. The decoded protocol in S13 is therefore reconstructed, not copy-pasted;
  it matches the paper's prose sections, but treat the exhibit wording as near-verbatim rather
  than exact.
- **OpenAlex** was used for existence/venue/citation counts as instructed; Semantic Scholar was not
  touched. OpenAlex reports **1 citation** for Goldberg & Mahmoud, which is clearly a metadata
  artifact — flagged in S6 rather than reported as a quality signal.
- Kelly and ruin arithmetic computed with two short Python scripts (exact 125-outcome enumeration
  for the three-session distribution; grid search on f for Kelly). Scripts are in the scratchpad at
  `.../scratchpad/sizing.py`.

**Judgement calls made.**
- **I recommend 2 % per session rather than review A's 3 %.** The arithmetic showed the mean is
  approximately zero at every size while the left tail scales linearly, so the larger size is
  strictly worse. Flagging this as a deliberate deviation from review A's proposal.
- **I graded tastytrade as NOT citation-worthy** and said so explicitly (S15, C14) rather than
  omitting it, because a hackathon write-up that cites broker marketing research would be a
  credibility liability. Its 21-DTE rule is also structurally inapplicable to a 0–2 DTE book.
- **I report that no academic standard for Greek limits exists** (C15) rather than dressing up
  blog thresholds as literature, and derived limits from the max-loss budget instead. The derived
  numbers in Q4 are labelled as derived.
- **S1 and S2 are both AQR-affiliated** and are therefore *not* two independent sources for the
  anti-hedging claim; I marked this in the evidence table (C4) and flagged the missing
  Bhansali/Davis counterweight as a real gap.
- **The three-session independence assumption is optimistic**; all tail probabilities in the
  sizing table are lower bounds. Stated in the assumptions.
- Kaminski & Lo studies stops on a long underlying, not on short options; **I flagged the transfer
  as analogical** (S3 caveats, C5) rather than asserting it, and grounded the actual
  recommendation in the structural argument (the bought wing is the stop, priced at t=0).

**Not done (out of scope by instruction):** no Alpaca documentation research; no re-derivation of
reviews A or B; no full reading of any PDF over ~40 pages (I grepped and read targeted sections of
the Israelov, Kaminski-Lo, Kelly, Arnott, DSR, Knight and FINRA documents rather than reading them
end to end).

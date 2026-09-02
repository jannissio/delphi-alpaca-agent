# F1 — Four Paywalled Sources, Read in Full, Checked Against the Design

> **Superseded in part (added 2026-09-02, evening).** Every Sharpe ratio, net-of-cost mean and conditional
> out-of-sample figure quoted from Vilkov (V) below predates the author's own correction of August 2026
> (`KNOWN-ISSUES.md` in github.com/vilkovgr/0dte-strategies, "Transaction-cost unit-scale error"): half-spreads
> had been charged at 1/100 of their true size. After the fix "no structure retains a materially positive net
> Sharpe ratio" and the iron butterfly/condor bucket moves from -0.96 to -2.67. What survives is the median realised
> 0DTE variance risk premium of about 0.0011 % of the underlying from 10:00 ET to expiration and the qualitative
> conclusion that 0DTE multi-leg structures do not survive realistic frictions, which the correction strengthens.
> The E-V rows are kept for the record and must not be quoted without this note. README, WRITEUP and SLIDES cite the
> corrected result.

Report F1. Author: Claude (Opus 5) research agent. Date: 2026-09-02.
Scope: the four papers the user obtained via university access, read completely, extracted, and checked
against the decisions recorded in `research/STATE_OF_THE_ART.md` sections 1, 3, 6 and 8.

Source short codes: **V** = Vilkov, *0DTE Trading Rules*; **D** = Dim/Eraker/Vilkov, *0DTEs: Trading,
Gamma Risk and Volatility Propagation*; **F** = Fu/Li/Musto/Pearson (SEC DERA), *Hope at a Reasonable
Price*; **C** = Carr/Wu, *Variance Risk Premiums*.

---

## 1. Summary — ten decision-relevant findings

1. **The unconditional 0DTE iron condor loses money over the full sample, and it is not close.** SPXW
   condors/butterflies entered 10:00 ET and held to the 16:00 close, 09/2016–02/02/2026, n = 1,319 days:
   mean −0.0030 % of spot at mid, −0.0082 % after half-spread plus 0.5 bp, annualised Sharpe −0.24 → −0.65
   (V Table 3, p. 16). Our "EV about zero" is optimistic once entry frictions are charged, and V charges
   **entry only** — we also pay an exit. (E-V3)
2. **But the condor is the *best-behaved* of the seven templates and the recent regime is on our side.**
   It has the lowest loss probability (45.0 %), the lowest 1 % expected shortfall (0.587 % of spot) and the
   least skew (−0.47) of the seven structures V tests (Table 4, p. 17). In the 01/2024–02/2026 subsample
   *every* condor width is profitable: the ±1 %-short/±2 %-wing condor earns +0.0126 % of spot per day,
   SR 1.31 p.a., 25th percentile +0.01 (V Table A2, p. 41) — while in 01/2022–12/2023 the same structures
   lost (SR −0.35 to −1.64, Table A1, p. 40). The structural-break test is insignificant (t = 1.18, p = 0.24).
   Honest framing: **regime-conditional, not an edge.** (E-V5, E-V6, E-V7)
3. **Wider is better, and our wings are far too narrow.** In 2024–2026 mean PNL and Sharpe rise monotonically
   with condor width (SR 0.39 → 0.82 → 1.31 as short strikes move from ±0.3 % to ±0.5 % to ±1 % of spot).
   Our "wings 1 to 2 dollars on SPY" is 0.15–0.3 % of spot; nothing in this literature was tested that
   narrow, and at that width four legs of half-spread eat 30–60 % of the credit. Recommend wings 0.5–1.0 %
   of spot (SPY $3–$6). (E-V8, E-V9)
4. **The call-heavy asymmetry is contradicted.** The risk reversal (long OTM call / short OTM put) is the
   only structure with positive mean, median *and* 25th percentile in V's full sample (+0.0100 to +0.0153 %
   of spot, SR 0.25–0.53; Table 1, p. 14) and stays positive in 2024–2026. A profitable long-call/short-put
   position means the **put side was the richer sale at 0DTE**, not the call side. Recommend: symmetric,
   delta-neutral condor; drop the 1.25×/1.5× asymmetry and the VIX-tercile neutralisation rule. (E-V11)
5. **A high-implied-variance veto is now weakly supported by direct 0DTE evidence.** Sorting on the 10:00 ET
   0DTE implied variance, condor mean PNL is +0.0016 % (low tercile), +0.0005 % (mid) and **−0.0111 %**
   (high); High−Low = −0.0127, t = −0.93, p = 0.35 (V Table 7, p. 23). Sign right, significance weak.
   Recommend a half-size rule in the top tercile rather than a hard veto. (E-V12)
6. **GEX stays rejected — and now we can cite the test.** D measures market-maker net gamma from Cboe
   open-close volume split by trader type (MM / customer / pro-customer / firm / broker-dealer), accumulated
   from 180 days before expiry (pp. 13–15). Alpaca gives neither the trader-type split nor open/close flags,
   so it is not reconstructable. D also tests the version we *could* build — total start-of-day open-interest
   gamma — and finds **no significant effect** on daily volatility (Table IA.3), and finds that raw 0DTE
   volume loses significance once lagged variance is controlled (Table IA.2). (E-D1, E-D6, E-D7)
7. **The real gamma effect is large but invisible to us:** a 1 SD rise in MM 0DTE net gamma cuts the next
   30-minute log realised variance by 7.3–8.5 % of an SD (D Table 1, p. 21), and the intraday-momentum
   strategy earns **10 bp per hour more** in the lowest-gamma quartile than the highest (p. 27). MMs are net
   long gamma about two-thirds of the time, so 0DTE hedging *dampens* volatility on average — the tailwind
   for a short-gamma condor, which we simply cannot time. (E-D3, E-D4, E-D5)
8. **The execution rules need re-parameterising in ticks, not percent.** In modern SPXW the ATM 0DTE quoted
   spread is **one tick 64.7 % of the time and two ticks 35.3 %** (F, p. 4–5). A midpoint limit order fills
   **within one second** 58–63 % of the time for options under $3 and ~71 % for options over $3, at a net
   effective cost of $0.021–0.024 versus $0.050 for a marketable order (F Table 5, Panel B). The penalty for
   waiting and then crossing is only **$0.006–0.007** for options under $3. Our "skip if quoted spread > 15 %
   of mid" and "price collar 5 % of mid" would veto essentially every 0DTE SPY contract we want to trade
   (one tick on a $0.30 option is 17 % of mid). (E-F3, E-F5, E-F6, E-F9)
9. **Do not always walk toward the touch.** At a four-tick spread the **midpoint is the cost-minimising
   placement** ($0.042–0.044 net) — one tick past the mid is *worse* ($0.058–0.060) despite an 85–89 % fill
   rate (F Table 7, Panel B). Only at a three-tick spread does crossing the mid by one tick pay ($0.032 vs
   $0.038). Concrete walking rule in §5. (E-F7, E-F8)
10. **SPY over QQQ is now quantified, and the size of the whole prize is small.** Carr & Wu: the 30-day
    variance risk premium is −2.74 per $100 notional on SPX (t = −8.39) versus −3.93 on QQQ (t = −2.62);
    annualised Sharpe of shorting index variance 0.98 (SPX) versus 0.55 (QQQ / NDX); and when measured with
    *bid* option prices the SPX premium survives (−2.34, t = −7.44) while QQQ's dies (t = −1.39)
    (C Tables 3 and 8). At Sharpe 0.98 the expected Sharpe over 2.5 sessions is **0.098** — a 54 % chance of
    a positive outcome. That is the whole edge, before frictions. (E-C2, E-C3, E-C4, E-C9)

---

## 2. Source cards

### V — Vilkov (2026), "0DTE Trading Rules"

| Field | Value |
|---|---|
| Author | Grigory Vilkov, Frankfurt School of Finance & Management (sole author) |
| Version | 18 March 2026, 44 pp. (30 pp. main text + appendix). No DOI or SSRN number printed in the PDF; the DEV bibliography cites an earlier version as "Vilkov, G., 2023, *0DTE Trading Rules*, Working paper, Frankfurt School" |
| Status | Unpublished working paper. Not indexed in OpenAlex as of 2026-09-02 |
| Citation-worthiness | **Top working paper.** Author is a co-author of the refereed DEV paper and is well cited in the 0DTE literature. It is not peer-reviewed; cite it as a working paper and never as settled fact |
| Data | Cboe 30-minute option bars (NBBO, sizes, OHLC, volume, IV, Greeks) for SPXW; ThetaData 1-minute SPX/VIX bars; 09/2016 – 02 Feb 2026; 1,319 usable 0DTE days at the 10:00 ET entry |
| Method | Interpolate the 0DTE cross-section over moneyness 0.98–1.02 in 0.001 steps (Akima), build seven standardised templates (straddle/strangle, iron butterfly/condor, risk reversal, bull-call, bear-put, call- and put-ratio spreads), hold to the 16:00 cash settlement, express PNL as (payoff − mid)/spot × 100. Frictions added in layers: mid → half of the observed leg bid-ask → plus 0.5 bp of underlying. Conditional part: strategy-specific L2 logistic classification of sign(net PNL) on 10:00 ET information only, expanding and 252-day rolling windows, OOS from April 2019 |
| Friction caveat | **Entry frictions only.** Positions are European and cash-settled at 16:00, so no exit cost is charged. We close at 15:15 on an American ETF; our realistic cost is roughly double the half-spread term |

Verbatim (abstract): *"The evidence, therefore, points to selective timing opportunities rather than to a
broad unconditional edge."*

### D — Dim, Eraker & Vilkov (2025), "0DTEs: Trading, Gamma Risk and Volatility Propagation"

| Field | Value |
|---|---|
| Authors | Chukwuma Dim (George Washington U.), Bjørn Eraker (Wisconsin), Grigory Vilkov (Frankfurt School) |
| Version | 6 June 2025, 46 pp. + Online Appendix. SSRN 4692190 (OpenAlex lists the 2024 SSRN preprint, doi 10.2139/ssrn.4692190; no journal record found) |
| Status | Acknowledgements thank "the Editor and three anonymous referees" → at least revise-and-resubmit at a refereed journal. Cite as a refereed-stage working paper |
| Citation-worthiness | **Strongest of the three working papers.** Referee-reviewed, WFA/SoFiE presented, and the merged successor draft (Adams, Dim, Eraker, Fontaine, Ornthanalai & Vilkov 2025, SSRN 5641974) is already circulating |
| Data | Cboe DataShop: 30-min option bars 2012–04/2024; **10-minute open-close volume summary split by trader type (MM, customer, pro-customer, firm, broker-dealer), C1 platform, 2021–06/2023**; enhanced OPRA transactions; DTN IQFeed 1-minute SPX/SPY/ES bars |
| Method | Reconstruct intraday open interest per trader type by accumulating buy/sell (and open/close) order imbalance from 180 days before expiry; convert to cash gamma. Regress next-30-minute log realised variance on MM 0DTE net gamma with date and year × weekday × time fixed effects, three lags of RV/return/volume, Newey-West(5). Identification: IV using MM net gamma in the same intraday window five trading days earlier (first-stage F 21–83); placebo tests on public and private information; quantile regressions on volume jumps; daily 1-minute structural VAR with generalised IRFs |

### F — Fu, Li, Musto & Pearson (2025), "Hope at a Reasonable Price: Customer Use of Limit Orders in the 0DTE Market"

| Field | Value |
|---|---|
| Authors | Lei Fu (Purdue / SEC), Su Li (SEC Office of Asset Management), David K. Musto (Wharton), Neil D. Pearson (Illinois) |
| Version | 16 March 2025 (inner abstract dated 14 March 2025), 48 pp. SEC DERA Working Paper Series. No DOI; not in OpenAlex |
| Status | **Regulator staff working paper** with a standard SEC non-endorsement disclaimer. Two of four authors are senior academics (Musto, Pearson) |
| Citation-worthiness | High for microstructure facts — it uses regulator-grade MIDAS/OPRA data no academic dataset matches — but it is not peer-reviewed and the disclaimer must be reproduced if we quote it |
| Data | SPXW trades and quotes from the OPRA feed via MIDAS, 1 July 2020 – 28 September 2023 (456 early + 358 late trade dates; split at 25 April 2022, the first Tuesday-expiry week) |
| Method | (i) Discover and correct an OPRA sequencing defect: the BBO *caused by* a trade is time-stamped before the trade, so 38 % of trades appear to execute strictly inside the BBO. Their re-sequencing algorithm matches 99.9 % of trades. (ii) Use quote condition codes B/O/C to identify customer interest, then isolate two order types where the customer is provably first in line: market-turning orders (MTOs, improve the BBO) and pick-offs (POs, last order standing). (iii) Net effective spread of an MTO = fill-probability-weighted mix of the filled price and a marketable order submitted one second later, both measured against the **pre-submission** BBO midpoint |

Verbatim (conclusion, p. 19): *"The retail public may be losing money on these trades but they are not
losing it to transactions costs but rather to the usual effect of high demand on supply."*

### C — Carr & Wu (2009), "Variance Risk Premiums"

| Field | Value |
|---|---|
| Authors | Peter Carr (Bloomberg / Courant, NYU), Liuren Wu (Baruch College, CUNY) |
| Venue | *The Review of Financial Studies* 22(3), 1311–1341, 2009. doi 10.1093/rfs/hhn038, advance access 10 April 2008 |
| Status | **Peer-reviewed, top-three finance journal.** The canonical VRP measurement paper |
| Citation-worthiness | Highest of the four. Use it for anything about the existence, sign, magnitude and time variation of the index variance risk premium |
| Data | OptionMetrics closing CBOE quotes, January 1996 – February 2003; 5 stock indexes (SPX, OEX, DJX, NDX, QQQ) and 35 individual stocks; 978–1,780 active days each |
| Method | Synthesise the 30-day variance swap rate as a 1/K²-weighted portfolio of OTM options (model-free, robust to jumps up to a quantified approximation error); realised variance from daily returns; VRP defined ex post as RV − SW (dollar) and ln(RV/SW) (log return). Newey-West(30) t-statistics throughout. Robustness: jump/discretisation error, bid vs ask synthesis, errors-in-variables via Kalman-filter MLE, bull/bear subsamples |

---

## 3. Evidence table

Confidence key: **H** = directly measured, large sample, robust; **M** = directly measured but weak
significance or one specification; **L** = suggestive, sign only.

| ID | Finding | Number | Page | Src | Conf |
|---|---|---|---|---|---|
| E-V1 | Positive 0DTE VRP exists but is tiny | Median realised VRP 10:00 ET → expiry ≈ **0.0011 % of underlying**; even at zero realised variance the whole OTM time value is only ~0.20 % of spot | 11 | V | H |
| E-V2 | 0DTE templates are all near zero at mid | Full sample means (% of spot/day): strangle −0.0046, **iron condor −0.0030**, risk reversal +0.0141, bull-call −0.0062, call-ratio −0.0105, bear-put +0.0074, put-ratio +0.0168 | 16 (T3) | V | H |
| E-V3 | Frictions flip / deepen the sign | Iron condor: mid −0.0030 → half-spread −0.0032 → +0.5 bp **−0.0082**; SR p.a. −0.24 → **−0.65**. Friction = half of the observed leg bid-ask **at entry only** + 0.5 bp | 16 (T3) | V | H |
| E-V4 | Condor is the least dangerous template | Loss probability **45.0 %** (lowest of 7), ES1% **0.5866 %** of spot (lowest), worst day −0.7146 %, worst 5-day −1.6477 %, skew −0.47. Strangle for contrast: 70.4 % loss prob., ES 1.2781 %, worst day −2.5113 %, skew +4.62 | 17 (T4) | V | H |
| E-V5 | Condor median is positive, mean is not | 0.99/0.995/1.005/1.01 full sample: mean −0.0058, **median +0.04**, P25 −0.11, P75 +0.09, min −0.50, P1 −0.43, skew −0.71, n = 1,319 | 14 (T1) | V | H |
| E-V6 | 2022–2023 was a condor graveyard | Means (% spot): 0.995/0.997/1.003/1.005 −0.0041 (SR −0.76); 0.99/0.995/1.005/1.01 −0.0203 (**SR −1.64**); 0.98/0.99/1.01/1.02 −0.0057 (SR −0.35). n = 344 | 40 (TA1) | V | H |
| E-V7 | 01/2024–02/2026 was the opposite | 0.995/0.997/1.003/1.005 +0.0021 (SR 0.39); 0.99/0.995/1.005/1.01 **+0.0080 (SR 0.82)**; 0.98/0.99/1.01/1.02 **+0.0126 (SR 1.31)**, median +0.02, P25 +0.01, min −0.99, skew −3.78. n = 421 | 41 (TA2) | V | H |
| E-V8 | Wider condors dominate in the recent regime | Sharpe monotone in width: 0.39 → 0.82 → 1.31 as short strikes move ±0.3 % → ±0.5 % → ±1 % of spot | 41 (TA2) | V | M |
| E-V9 | The 2022-vs-2024 break is not statistically identified | Iron condor post-2022 coefficient +0.0130, **t = 1.18, p = 0.240**, vol ratio 0.97, n = 3,541 pre / 4,290 post, date-clustered | 16 (T2) | V | H |
| E-V10 | Condor PNL is *not* explained by realised variance or skewness | RV-only adj. R² **0.002**; adding realised skewness the RS coefficient is 0.006 (t = 1.32), all specs fail BH-FDR (q = 0.113 / 0.130 / 0.161). Contrast risk reversal: RS coefficient 0.137 (t = 6.09), R² 0.335 | 20 (T5), 22 (T6) | V | H |
| E-V11 | The put side, not the call side, was the richer 0DTE sale | Long-call/short-put risk reversal is the only structure with mean, median **and** P25 positive: +0.0100 (0.995/1.005) and +0.0153 (0.99/1.01) % of spot, SR 0.25 / 0.53, n = 1,319; still positive in 2024–2026 (+0.0059 to +0.0075). Author's caveat: "the average effect is small … which limits implementability", and may partly reflect the index's upward drift | 14 (T1), 41 (TA2), 13–14, 18 | V | M |
| E-V12 | High implied variance is where condors lose | 0DTE implied-variance terciles at 10:00 ET: condor mean **+0.0016 (low) / +0.0005 (mid) / −0.0111 (high)**; H−L −0.0127, **t = −0.93, p = 0.353**. Put-ratio and bear-put spreads do the opposite (put-ratio H−L +0.0455, t = 1.75, p = 0.080) | 23 (T7) | V | M |
| E-V13 | Conditional timing of the condor works out of sample | Logistic, 10:00 ET information only, representative moneyness 0.995/0.997/1.003/1.005: hit rate 63.9 % (expanding) / 63.1 % (rolling), mean net **+0.446 / +0.442 bp** of underlying per day, **SR net 0.82**, n = 1,061 OOS days (Apr 2019 – Feb 2026) | 27 (T10), 28 (T11) | V | M |
| E-V14 | …but only by *reversing* the condor half the time | Long share of the credit structure **47.8 %** — the rule sells the condor on fewer than half of days and buys it on the rest. Worst day −17.5 bp, max DD −204 bp | 28 (T11) | V | H |
| E-V15 | Direction beats magnitude as a forecasting target | Direct return prediction SR −0.43 to +0.48; logistic hard mapping SR up to **1.07** (ridge) / 1.06 (random forest); soft mapping weaker in 4 of 5 families | 26 (T9) | V | H |
| E-V16 | Diversified baskets, not single strategies | EW top-3-by-SR basket **SR 1.27**, top-3-by-mean 1.17, all-strategies 1.01; best single strategy is the put-ratio spread (SR 1.26 expanding, 2.578 bp/day) — but a 1×2 with open downside | 28 (T11), 27 (T10) | V | M |
| E-V17 | V's own "GEX" features are not dealer inventory | Explicit: "flow-style and exposure-style proxies based on traded volume, open interest, and leg Greeks; they are **not a dealer-inventory reconstruction**", and the headline conditional tables use only market state + lagged PNL | 8, 24 | V | H |
| E-V18 | Entry time barely matters unconditionally | Alternative entries (16:00 previous day, 13:00, 15:00): "main qualitative findings are unchanged"; "full-sample unconditional patterns are broadly similar across entry times" | 12, 15 | V | M |
| E-V19 | The last hour is where the skew risk concentrates | 15:00→16:00 regressions have higher R² and realised skewness dominates even more strongly (risk reversal R² 0.606, bull-call 0.233) | 43 (TA4), 20 | V | M |
| E-D1 | MM net gamma requires trader-type-split Cboe data | Built from the Cboe **open-close volume summary** (buys/sells for MMs; buy-open/buy-close/sell-open/sell-close for others), accumulated from 180 days before expiry, at 30-minute intervals, converted with bar-level cash gammas | 13–15 | D | H |
| E-D2 | 0DTE net gamma → next 30-min variance | 1 SD rise in MM 0DTE net gamma ⇒ log RV falls by **7.3–8.5 % of an SD**; non-0DTE (1 day–1 month) equivalent −22.9 %, so the 0DTE effect is **32 %** of all longer maturities combined. n = 4,910–6,150, NW(5) | 21 (T1) | D | H |
| E-D3 | Market makers are usually long 0DTE gamma | Positive for most of 01/2021–06/2023; about **one third** of observations negative, with average magnitude roughly **three times smaller** than positive gamma. Customers are the net gamma sellers | 18, fn. 14 | D | H |
| E-D4 | The destabilising branch is the weaker one | Positive-gamma coefficient **−0.064***, negative-gamma coefficient **−0.022** — 65 % smaller. Interactions with high RV, volume surge and negative return are all insignificant and 3–7× smaller than the base | 26 (T3) | D | H |
| E-D5 | The tradable gamma signal is worth ~10 bp/hour | Intraday momentum strategy (SPY, sign of return since prior close, 60-min hold): **10 bp per hour** difference between the top and bottom 0DTE net-gamma quartiles, monotone; non-0DTE quartiles insignificant | 27 (Fig 5) | D | H |
| E-D6 | The aggregate-open-interest proxy does not work | Regressing daily log RV on **total** start-of-day 0DTE OI cash gamma interacted with overnight and lagged variance: all 0DTE coefficients insignificant (−0.007, −0.020, −0.264, all n.s.), n = 1,601. "confirming the importance of knowing market makers' inventory" | IA-6 (TIA.3) | D | H |
| E-D7 | Raw 0DTE volume is not a volatility signal either | Positive coefficient on lagged 0DTE volume (0.237***) turns insignificant (0.023, 0.058) once five lags of daily variance are added; with the volume *ratio* it flips negative (−0.066*, −0.078**). n = 1,684 | IA-4 (TIA.2) | D | H |
| E-D8 | 0DTE volume jumps do not propagate returns | KS and Anderson-Darling fail to reject equal distributions in every subperiod (full sample KS 0.025 p = 0.118, AD 0.705 p = 0.169). Quantile regressions, n = 99,707: every past-return × volume-jump interaction insignificant; only Q90/Q95 show volume jumps weakly *reducing* positive returns (−0.010**, −0.019**) | 37 (T7), 38 (T8) | D | H |
| E-D9 | Market integration is rising but the volatility effect is not | Correlation of 0DTE and underlying volume changes 0.27 (2012–19) → 0.43 (2020–24); variance response to a 1 SD 0DTE volume shock 0.18 → 0.26 SD units — "economically negligible and statistically insignificant" | 40–41 | D | M |
| E-D10 | 0DTE hedging flow is genuinely large | Projected 30-min MM rebalancing "routinely exceeding 5 % of the intraday volume", larger for 0DTE than any other DTE bucket | 19, 48 (Fig A1) | D | M |
| E-D11 | 0DTE turnover vs risk | 0DTE absolute cash-delta turnover ≈ **2×** 1DTE and **>4×** the 2–4-week bucket; 0DTE open-interest cash gamma ≈ **half** of all 1-week-to-1-month options combined; SPY open-interest risk ≈ 1/6 of index options despite ~30 % of the volume | 17, 47 (TA1) | D | H |
| E-D12 | No information channel | MM net gamma is not predicted by lagged RV/returns/volume (all coefficients ≤ 0.04, n.s.), and does not move in the 30 or 60 minutes before abnormal news (all coefficients n.s., both bottom-up and macro news) | 31 (T5), 34 (T6) | D | H |
| E-F1 | The OPRA sequencing defect | **38 %** of SPXW trades appear to execute strictly inside the prevailing BBO — impossible. 89.3 % of trades out of sequence in July 2020, 37.8 % in sequence by January 2023, 16.3 % by September 2023 | 9, 31 (T3) | F | H |
| E-F2 | Consequence: prior cost estimates are suspect | The paper names Beckmeyer, Branger & Gayda (2023) as comparing trade prices to the BBO *that the trade caused*. Its conclusion: retail is "not losing it to transactions costs" | 1, 19 | F | H |
| E-F3 | Modern SPXW 0DTE quoted spreads are 1–2 ticks | ATM BBO at ~13:00: July 2020 one tick **0.5 %** of the time, ≥3 ticks **76 %**; July 2023 one tick **64.7 %**, two ticks **35.3 %**, wider only rarely and mostly at the close | 4–5, 25 (Fig 3) | F | H |
| E-F4 | Customers are the liquidity supply at our strikes | Customer presence at the bid peaks at ~**60 %** of the day at **0.5–0.75 % OTM** in July 2023 (was ~40 % at 1.0–1.5 % OTM in July 2020); >80 % at the offer for far-OTM; negligible >0.5 % ITM. ~60 % of LOB trades are against quotes with customer interest, of which 81 % (early) / 69 % (late) are MTO or PO | 12, 26–27 (Fig 4), 32 (T4) | F | H |
| E-F5 | Midpoint fill rates within **one second**, price < $3 | Two-tick spread, order at mid: early 40.2–50.2 %, **late 57.6–62.8 %**. Net effective spread late **$0.021–0.024** vs $0.050 for a marketable order | 32–33 (T5) | F | H |
| E-F6 | Same, price > $3 ($0.10 tick) | Two-tick spread at mid: early 57.8–60.8 %, **late 70.8–71.4 %**; net effective spread **$0.040–0.041** vs $0.100 | 33 (T5 C/D) | F | H |
| E-F7 | Three-tick spread, late, < $3 | One tick inside own side (not crossing mid): **34.4–36.9 %** fill, net $0.038–0.040. One tick past mid: **86.9–89.9 %** fill, net **$0.032–0.033**. Marketable $0.075 | 34 (T6 B) | F | H |
| E-F8 | Four-tick spread, late, < $3 — **the midpoint wins** | One tick inside: 30.3–32.5 %, net $0.054–0.057. **At mid: 61.3–65.3 %, net $0.042–0.044.** One tick past mid: 84.2–89.0 %, net $0.058–0.060. Marketable $0.100 | 36 (T7 B) | F | H |
| E-F9 | Adverse selection of *not* filling is small for cheap options | Marketable order one second after an unfilled mid MTO: **$0.056–0.057** vs the $0.050 baseline (< $3) — a $0.006–0.007 penalty. For > $3 it is $0.141 vs $0.100 — a $0.041 penalty | 16, 32–33 (T5) | F | H |
| E-F10 | Counterparty revenue is under half a tick | Realised spreads on filled MTOs ~2.5 ¢ at 1 s early, about half that late, below a penny at 1 minute late; "always less than half the quoted spread, generally less than half a tick" | 17 | F | H |
| E-F11 | Resting (pick-off) orders carry drift risk | PO realised spreads **grow** from 1 s to 1 min (they fill when the market moves against you) whereas MTO realised spreads **shrink**. PO cost sits near that of the most aggressive MTOs | 18, 38 (T8) | F | H |
| E-F12 | Retail-sized order flow | **66 %** of MTO trades and **68 %** of PO trades are for exactly one contract; a further 23 % / 21 % for two to five | 4 | F | H |
| E-F13 | Multi-leg is a different, less friendly book | Complex (COM) trades: BCO share 44–56 %, of which MTO/PO falls from 59 % to 37 %. All the fill and cost numbers above are **single-leg** | 13, 32 (T4) | F | H |
| E-F14 | Slightly-OTM 0DTE calls fall under $3 (5 ¢ tick) by mid-day | Calls 0.375–0.5 % OTM enter the $0.05-tick range in the middle of the session; just-OTM calls only in the last hour (January 2023) | 11, 24 (Fig 2) | F | M |
| E-C1 | Index implied variance exceeds realised | SPX mean RV 4.07 vs SW **6.81** (×100, annualised); OEX 4.53/6.90; DJX 4.39/6.98; NDX 16.69/19.12; QQQ 22.61/**26.54** | 1320 (T2) | C | H |
| E-C2 | Magnitude and significance by index | (RV − SW)×100: SPX **−2.74 (t = −8.39)**, OEX −2.36 (−7.02), DJX −2.58 (−6.37), NDX −2.43 (−2.54), QQQ **−3.93 (−2.62)**. Log VRP: SPX **−0.66 (t = −11.83)**, QQQ −0.29 | 1321 (T3) | C | H |
| E-C3 | Annualised Sharpe of shorting 30-day index variance | SPX **0.98**, OEX 0.85, DJX 0.87, **NDX 0.55, QQQ 0.55** | 1321 (T3), 1322 | C | H |
| E-C4 | SPX survives the full quoted spread; QQQ does not | Synthesising the swap rate from **bid** option prices: SPX −2.34 (**t = −7.44**), DJX −1.94 (−4.94), NDX −1.40 (**t = −1.43, n.s.**), QQQ −2.07 (**t = −1.39, n.s.**) | 1333–34 (T8) | C | H |
| E-C5 | Premium is an index phenomenon | Only 7 of 35 single stocks significantly negative in dollar terms (23 of 35 in log terms). Cross-section: LRP = 0.0061 − **0.3283**·β_V, t = −2.96, R² 18.4 % | 1322–23 | C | H |
| E-C6 | Dollar premium grows with the vol level, proportional premium does not | RV = a + b·SW: SPX **b = 0.455, t = −4.60** against b = 1 (0.618 after errors-in-variables MLE correction, still < 1) ⇒ VRP ≈ a − 0.545·SW. In logs **b = 0.919, t = −0.68 (not different from 1)** | 1329 (T6), 1336 (T9) | C | H |
| E-C7 | The premium is not predictable | Mean non-overlapping 30-day autocorrelation **−0.023** (dollar) and **−0.006** (log). "although return variance is strongly predictable, investors have priced this predictability into options" | 1323–24 | C | H |
| E-C8 | It survives both market regimes, but shrinks proportionally in high vol | SPX 1996–3/2000: −2.89 (t = −8.99), log −0.76. 3/2000–2/2003: −2.52 (t = −7.83), log **−0.52**, while SW rose 6.12 → 7.83 | 1337 (T10) | C | H |
| E-C9 | Derived: the prize over our window | Sharpe 0.98 p.a. ⇒ per-day Sharpe 0.062 ⇒ over 2.5 sessions **≈ 0.098**, i.e. ≈ **54 %** probability of a positive result under normality, gross of all frictions and of the 0DTE horizon penalty | derived from 1322 | C | H |
| E-C10 | The authors themselves warn off Sharpe | "given the nonlinear payoff structure, caution should be applied when interpreting Sharpe ratios on derivative trading strategies"; actual profitability depends on quote availability and spreads | 1322 | C | H |

---

## 4. Design check

| # | Decision | What the four papers say | Verdict | Recommended change |
|---|---|---|---|---|
| 1 | **0DTE iron condor on SPY, defined risk, wings always bought** | V: unconditional condor loses after entry frictions (−0.0082 % of spot/day, SR −0.65, n = 1,319; E-V3) but is the **safest** template — 45 % loss probability, lowest ES1 %, skew −0.47 vs +4.62 for the strangle (E-V4). Recent regime positive (E-V7). C: the underlying premium is genuinely there and is an SPX phenomenon (E-C2) | **Refines** | Keep the structure. Restate the expectation: *median positive, mean around zero to slightly negative, 45 % of sessions red.* Drop "EV about zero" as a headline; V's number for the full sample is negative |
| 2 | **SPY over QQQ** | C: SPX Sharpe 0.98 vs QQQ 0.55; SPX t = −8.39 vs QQQ −2.62; at bid prices SPX survives (t = −7.44) while QQQ dies (t = −1.39) (E-C3, E-C4). D: SPY option open-interest risk is ~1/6 of index options, "more speculative and retail character" (E-D11) | **Supports, strongly** | Make SPY-only the default for all three sessions. QQQ adds no premium per unit of risk and its VRP does not survive its own spread |
| 3 | **Call-heavy asymmetry: short call 1.25×, short put 1.5× implied move** | V: the long-call/short-put risk reversal is the only structure with mean, median and P25 positive (+0.0100 / +0.0153 % of spot, SR 0.25 / 0.53) across 1,319 days, and still positive in 2024–2026 (E-V11). That implies the **put** was the dearer sale at 0DTE. It is directly about 0DTE SPXW, not extrapolated; but no t-statistic is given for the mean, the skewness is +2.0 to +5.6 (lottery-driven), and V warns the result may partly reflect the index's upward drift | **Contradicts** (moderate strength) | **Go symmetric.** Short call and short put both at the same multiple of the implied remaining move. Removes a free parameter and a contradiction between Reports A, D and E |
| 4 | **Neutralise the asymmetry in the top VIX tercile** | V Table 7: the high-implied-variance tercile is precisely where skew structures earn *most* (risk reversal +0.0482, put-ratio +0.0455, t = 1.75) and where condors lose (−0.0111) (E-V12). The rule points the wrong way on both counts | **Contradicts** | Delete the rule. Replace with the vol-level size taper in row 6 |
| 5 | **Strikes anchored at 1.25×/1.5× the implied remaining move** | At VIX ≈ 15 the 10:00 ET 0DTE ATM straddle implies ≈ 0.73 % of spot; 1.25× ≈ 0.91 %, 1.5× ≈ 1.09 %. That lands on V's **best 2024–2026 geometry** (short strikes ±1 %: +0.0126 % of spot, SR 1.31; E-V7, E-V8). But the credit at that distance is only ~11 % of a 1 %-wide spread, and four legs of round-trip half-spread then consume 27–54 % of it | **Supports the anchor, refines the multiple** | Keep the implied-move anchor. Use **1.0×–1.25×** for the short strikes (≈ ±0.5 % to ±0.9 % of spot) and require **credit ≥ 25 % of the wing width** as a hard gate; if the gate fails, move the shorts closer, not further |
| 6 | **Wings 1–2 dollars wide on SPY** | Nothing in this literature tests wings narrower than 0.2 % of spot. V's tested geometries have wings **0.2–1.0 % of spot** away from the short strike, and the widest is both the best in 2024–2026 (SR 1.31) and the least bad in 2022–2023 (SR −0.35 vs −1.64 for the 0.5 % version) (E-V6, E-V7, E-V8) | **Contradicts** | Widen to **$3–$6 on SPY** (0.5–1.0 % of spot). Fewer contracts at the same 2 % max loss, better credit-to-friction ratio, better regime robustness |
| 7 | **Max loss 2 % per session, 6 % cumulative, ≤10 contracts/order** | V's condor ES1 % is 0.587 % of spot and the worst observed day −0.715 % (E-V4). With a $3.20-wide SPY condor (max loss ≈ $250/contract) a 2 % cap allows ~8 contracts; with a $6.40-wide condor ~4. F: 66–68 % of the customer limit orders that actually fill are for **one** contract (E-F12) — a 10-lot is far above the modal resting order and will fill more slowly | **Supports, refines** | Keep 2 %/6 %. Cap at **6 contracts per package** and slice anything larger into two orders. Size from the wing width, never from the credit |
| 8 | **Regime gate VIX/VIX3M < 0.95; no IV-rank / IV-level gate** | Neither paper measures the VIX term structure — **silent** on the gate itself. On the *level*: V gives the first direct 0DTE evidence that condors lose in the top implied-variance tercile (−0.0111 vs +0.0016, t = −0.93; E-V12). C says the dollar premium is *larger* when the swap rate is high (b = 0.455 << 1) but the proportional premium is flat (log b = 0.919) and actually smaller in the high-vol subsample (log −0.52 vs −0.76) (E-C6, E-C8) | **Refines** | Keep the term-structure gate (it rests on Johnson 2017, not on these papers). **Add a level taper, not a veto**: half size when the 0DTE implied remaining move is in the top tercile of its trailing 60-day distribution. Consistent with both V and C |
| 9 | **No GEX signal** | D: the measured signal needs Cboe trader-type open-close data (E-D1). The version buildable from Alpaca — total open-interest gamma — has **no significant effect** (E-D6), and raw 0DTE volume loses significance under lagged-variance controls (E-D7) and does not propagate returns (E-D8). Yet the true signal is worth 10 bp/hour (E-D5) | **Supports, decisively** | Keep the rejection and now *cite the falsification*: "we tested the proxy we could compute; the paper that owns the real data reports it does not work." Log this as a deliberate, evidenced omission — it is a presentation asset |
| 10 | **Entries Wed 10:00–11:00 and 12:30–13:30; Thu after 10:15** | V: 10:00 ET is the paper's reference entry and the only one for which conditional OOS results exist; unconditional patterns at 13:00, 15:00 and prior-day 16:00 are "broadly similar" (E-V18). F: quoted spreads are widest at the close, not mid-session (E-F3); our short strikes are in the cheap $0.05-tick regime from mid-day (E-F14). Day-of-week and macro-day effects: **not analysed by either paper** | **Supports 10:00, silent otherwise** | No change. Keep 10:00–11:00 as primary and note in the write-up that it is the entry the only OOS-validated 0DTE protocol uses |
| 11 | **Friday NO_TRADE (NFP)** | Both papers silent on macro announcements; V explicitly lists "extend event conditioning" as future work | **Silent** | No change. The rule stands on the BLS calendar, not on these sources — say so |
| 12 | **Flat by 15:15 ET** | V's last-hour regressions show the 15:00→16:00 window is where realised skewness dominates most strongly and fits are highest (E-V19); the condor's whole tail risk is a directional-skew event. D: MM net gamma decreases monotonically through the day toward expiry (p. 18), i.e. the volatility-dampening cushion thins out late | **Supports** | No change. Add the skew-concentration argument to the justification |
| 13 | **No price stop; the long wing is the stop** | V: the wings cut the tail roughly in half versus the naked strangle (ES1 % 0.587 vs 1.278 % of spot; worst day −0.71 vs −2.51 %; skew −0.47 vs +4.62) (E-V4) | **Supports** | No change |
| 14 | **Package limit orders only, never market orders** | F: a midpoint limit fills within **one second** 58–71 % of the time and costs less than half a marketable order; the penalty for failing and then crossing is $0.006–0.007 on options under $3 (E-F5, E-F6, E-F9) | **Supports, strongly** | No change. Quote the fill rates in the write-up |
| 15 | **Start at mid, walk toward the natural side in steps** | F: at a **four-tick** spread the midpoint is the cheapest placement ($0.042–0.044) and walking one tick past the mid is *worse* ($0.058–0.060) despite an 85–89 % fill (E-F8). Only at three ticks does one tick past the mid pay ($0.032 vs $0.038) (E-F7). Resting passively (pick-off) means filling as the market moves against you (E-F11) | **Refines** | Replace "walk toward the touch in three steps" with the tick-conditional rule in §5 |
| 16 | **Price collar 5 % of mid; skip contracts with quoted spread > 15 % of mid** | F: one tick on a $0.30 0DTE option is 17 % of mid, and 1–2-tick spreads are now the **normal** state of the SPXW 0DTE book (E-F3). Both rules would veto almost every contract we want and the collar is finer than the tick | **Contradicts** | Re-express both in **ticks**: reject a leg whose quoted spread exceeds 3 ticks; collar = ±2 ticks around the package mid. Percentage rules only apply to the *package credit*, not to leg mids |
| 17 | **Expected paper-trading fills at NBBO when marketable** | F's fill statistics describe a real limit-order book with customer priority. Alpaca's paper engine fills only marketable orders. **The literature does not transfer to the simulator** | **Out of scope** | State explicitly in the write-up that our simulated fills are a modelling assumption, and report the gap between our modelled net effective spread (from F) and what the simulator actually gave us. This comparison is a free, honest process metric |
| 18 | **"60 % of retail 0DTE losses are transaction costs"** (synthesis §1 bullet 5) | F identifies the OPRA sequencing defect that inflates measured customer costs, names Beckmeyer et al. as affected, and concludes retail is "not losing it to transactions costs but rather to the usual effect of high demand on supply" (E-F1, E-F2) | **Contradicts** | Soften the claim to: "quoted spreads look large but customers who use non-marketable limit orders pay less than half of them; retail 0DTE losses are mostly bad expected payoffs, not fees." Keeps our execution discipline while fixing an incorrect citation |
| 19 | **Median +$135 to +$400/session, P05 ≈ −$2,300, floor −$5,881** | V's 2024–2026 distribution for the ±0.5 %-short/±1 %-wing condor: median +0.05 %, mean +0.008 %, P25 −0.01 %, P1 −0.42 % of spot per contract-equivalent. At 8 contracts (2 % cap, ~$250 max loss each) that is **median ≈ +$256, mean ≈ +$41, P1 ≈ −$2,000** per session — before exit costs (E-V7) | **Supports the median, refines the mean** | Keep the median band; lower the mean to "+$40 or less, plausibly negative after the exit leg." State that the same 2 % cap with $6.40-wide wings gives only ~4 contracts and a median near **+$51** — the wider, more robust geometry buys robustness with median P&L |
| 20 | **No Sharpe claims; report process metrics and benchmarks** | C explicitly warns against Sharpe on nonlinear derivative payoffs and against reading synthetic-swap Sharpes as achievable (E-C10). V reports median, loss probability, ES1 % and worst-day rather than leaning on means (E-V4) | **Supports** | Add two reporting lines: **loss probability** and an **ES1 % analogue**, and express session P&L as % of underlying notional so it is directly comparable to V's 0.0080–0.0126 %/day benchmark. That is a better benchmark than CNDR |
| 21 | **Long-gamma sleeve ≤ 0.3 % of capital, demo only** | V: long far-OTM strangles were the *positive* tail trade in 2024–2026 (0.98/1.02 strangle mean +0.0100 % of spot, SR 0.49, skew +13.4) — the payoff is real but entirely lottery-shaped (E-V7 context, Table A2) | **Supports** | No change. It is a demonstration, and V's numbers say the expected value is a coin flip on a fat tail |

---

## 5. Concrete parameters to adopt

**Strike rule** (E-V7, E-V8, E-V11, E-V12)

```
implied_move  = ATM 0DTE straddle mid at entry, in % of spot          # market's own estimate
short_call_K  = spot * (1 + 1.10 * implied_move)     # symmetric — no call tilt
short_put_K   = spot * (1 - 1.10 * implied_move)
wing_width    = max(3.00 USD, 0.005 * spot)          # SPY: $3.20 at spot 640
gate_credit   : reject if package credit < 0.25 * wing_width
gate_delta    : |net delta| <= 0.05 per contract after rounding to listed strikes
```
Rationale: 1.10× the implied move at VIX ≈ 15 puts the shorts near ±0.8 % of spot, between V's ±0.5 %
geometry (2024–26 SR 0.82) and the ±1 % geometry (SR 1.31), while the credit gate stops us from selling a
premium too thin to survive four legs of spread. Symmetric because E-V11 points the *opposite* way from the
call tilt and E-V12 kills the neutralisation trigger.

**Sizing** (E-V4, E-F12)

```
contracts = floor( 0.02 * equity / (100 * wing_width - credit*100) )
contracts = min(contracts, 6)                       # then slice into orders of <= 5
cumulative cap 6 % of starting equity, taper linearly with realised drawdown
half size if implied_move is in the top tercile of its trailing 60 session-days
```

**Entry / exit windows** (E-V18, E-V19, E-F3, E-F14)

```
Wed  10:00-11:00 ET primary, 12:30-13:30 ET secondary, no entry 13:55-14:15
Thu  after 10:15 ET only
Fri  NO_TRADE, logged with reason = NFP 08:30 ET
Exit all legs by 15:15 ET, escalating limits from 15:05
No new entry after 14:00 ET on any day
```

**Order-walking rule** (E-F5 → E-F11, E-F13)

Work in ticks ($0.05 below $3, $0.10 at or above $3), on the *package*, never on legs.

```
w = package quoted width in ticks (sum over legs of leg width, rounded)

if any leg width > 3 ticks:            reject the structure, pick different strikes
if w <= 2 ticks:                       single limit at package mid; wait 30 s; cancel
if w == 3 ticks:                       start at mid, wait 20 s;
                                       step 1 tick toward the natural side, wait 20 s;
                                       cancel                                    # E-F7
if w == 4 ticks:                       start at mid, wait 45 s; cancel.
                                       Do NOT step past the mid                  # E-F8
collar: never place worse than mid +/- 2 ticks
never send a marketable package order; a non-fill costs nothing
```
Why: at three ticks, one tick past the mid raises the fill rate 36 % → 88 % and *lowers* the expected cost
($0.038 → $0.032). At four ticks the same step raises the fill rate 63 % → 87 % but *raises* the cost
($0.043 → $0.059) — the extra fills are exactly the ones where the market has moved. And because all our
legs are under $3, the penalty for waiting and then giving up is only $0.006–0.007 per leg, so patience is
nearly free. Caveat to state in the write-up: F's numbers are **single-leg**; complex-order books are
thinner (customer-interest share of complex trades falls from 59 % to 37 %), so treat these fill rates as
an upper bound.

**Regime rule** (E-V12, E-C6, E-C8)

```
full size   : VIX/VIX3M < 0.95  AND  implied_move not in top trailing tercile
half size   : 0.95 <= VIX/VIX3M < 1.00  OR  implied_move in top trailing tercile
no new sale : VIX/VIX3M >= 1.00
veto        : implied 0DTE move < realised 5-10 day intraday move   (unchanged)
```
Note for the write-up: Carr & Wu say the *dollar* premium grows with the volatility level (b = 0.455,
t = −4.60) while the *proportional* premium does not (log b = 0.919). So high vol pays more dollars per unit
of exposure but not more per unit of risk — which is exactly why the response should be a size taper rather
than a hard veto, and why we size from the wing width rather than from the credit.

**Reporting additions** (E-V4, E-C10)

```
report: session P&L in % of SPY notional traded  -> compare to V's 0.0080-0.0126 %/day (2024-26)
report: loss probability across sessions          -> V benchmark 45.0 %
report: worst session vs V's worst day -0.7146 % of spot
report: modelled net effective spread (from F's tables) vs actual Alpaca fill vs package mid
do NOT report: Sharpe (C p.1322 warns against it for nonlinear payoffs)
```

---

## 6. Follow-up sources cited in these papers, worth reading

| Title | Why it matters to us | Likely access |
|---|---|---|
| Li, Musto & Pearson (2023), *Costs of executing complex options trades*, SEC DERA WP | **Highest priority.** F's numbers are single-leg; this is the same team on exactly our problem — multi-leg package execution cost | Free on sec.gov/dera |
| Adams, Dim, Eraker, Fontaine, Ornthanalai & Vilkov (2025), *Do S&P500 Options Increase Market Volatility? Evidence from 0DTEs*, SSRN 5641974 (rev. 3 Dec 2025) | The merged successor to D; consolidates the gamma-channel evidence. Only needed if the GEX question is reopened | Free on SSRN |
| Bogousslavsky & Muravyev (2025), *An Anatomy of Retail Option Trading*, SSRN 4682388 | Retail 0DTE P&L decomposition using better data than Beckmeyer et al.; would settle the "what fraction of retail losses is cost" question that F reopens | Free on SSRN |
| Muravyev & Pearson (2020), *Options trading costs are lower than you think*, RFS 33(11) | Already cited as A-K9 but not read in full; the direct source of the "patient limit orders avoid 84 % of the quoted spread" claim | Paywalled, university access |
| Almeida, Freire & Hizmeri (2025), *0DTE Asset Pricing*, SSRN 4701401 | The source behind most of Report D's V1/V5/V6/V12 claims; the intraday spread and smile-symmetry evidence should be verified first-hand since it drives the call-tilt question | Free on SSRN |
| Bandi, Fusari & Renò (2023/24), *0DTE Option Pricing*, SSRN 4503344 | Pricing model for ultra-short options; relevant to the "standard deltas are misspecified at 0DTE" claim (A-K10) that justifies our implied-move anchor | Free on SSRN |
| Baltussen, Da, Lammers & Martens (2021), *Hedging demand and market intraday momentum*, JFE 142(1) 377–403 | D's closest antecedent for the last-hour trend effect that threatens a short-gamma condor into the close | Paywalled, university access |
| Johannes, Kaeck, Seeger & Shah (2024), *Expected 1DTE Option Returns*, Columbia GSB WP | If we ever consider 1DTE instead of 0DTE, this is the only dedicated source | Likely free |
| Knox, Londono, Samadi & Vissing-Jorgensen (2025), *Equity Premium Events*, SSRN 4773692 | Fed staff; the event-conditioning framework V names as the natural next step — directly relevant to our macro-calendar gates | Free on SSRN |
| Vasquez, Amaya, Pearson & Garcia-Ares (2025), *0DTE Index Options and Market Volatility: How Large Is Their Impact?*, ITAM / Cboe WP | Source of the 3.3 pp annual / 6.4 pp 30-minute numbers already in the synthesis (V8); worth having first-hand if we quote them | Likely free |

---

## 7. Method log

**Fully read, cover to cover, via `pdftotext -layout` extractions:**

- `0DTE Trading Rules.txt` — 2,420 lines. Main text, all seven tables, conclusion, references and appendix
  Tables A1–A4 read. Figures 1–6 and A1–A7 are axis-label garble in the extraction and were used only for
  their captions; every number reported above comes from a table or from body text, not from a figure.
- `DTEs Trading, Gamma Risk and Volatility Propagation.txt` — 2,295 lines. Main text, Tables 1–8,
  Appendix Table A1, and Online Appendix sections IA.1.1–IA.1.4 with Tables IA.1–IA.4, all read.
- `hope-reasonable-prc-2503.txt` — 1,764 lines. Full text plus Tables 1–8 read. The Internet Appendix
  (Tables IA.1–IA.4, worked OPRA examples) was skimmed; it contains illustrative message sequences, no
  additional statistics.
- `Variance Risk Premiums.txt` — 1,986 lines. Full text, Tables 1–10, all read. Tables 4 and 5 (CAPM and
  Fama-French explanations of the VRP) were read but are not decision-relevant and are summarised in one
  line (classic factors explain only a small part; the premium is an independent risk factor).

**Table reconstruction.** Several tables in V (Tables 5, 6, 10, 11) and D (Tables 1–5) lost their column
alignment in extraction. Every number quoted above was cross-checked against (a) the obs-count column,
(b) the narrative text on the same or adjacent page, and (c) a second table reporting the same quantity.
Where a mapping could not be confirmed to that standard, the number is not reported. Specifically:
V Table 10's 14 numeric rows were mapped to strategy × protocol using the obs counts and confirmed by the
narrative ("put ratio spreads … 2.58 bps mean net and an SR of 1.26 in the expanding specification"; "iron
butterfly/condor structures still retain an attractive Sharpe ratio of 0.82") and by V Table 11.
V Table 6's rows were mapped by obs counts (5,337 / 6,403 / 4,270 / 8,540) and cross-checked against
V Table 5 Panel B; this is what establishes that the iron condor's regression coefficients, unlike the risk
reversal's, do **not** survive Benjamini-Hochberg adjustment.

**Nothing unreadable.** No pages were missing or corrupted in any of the four extractions.

**Web use.** Three OpenAlex queries only, to verify bibliographic status: DEV is indexed as SSRN preprint
doi 10.2139/ssrn.4692190 (2024) with no journal record; V's *0DTE Trading Rules* is not indexed; F is not
indexed. Carr & Wu's venue, volume, pages and DOI were taken from the running head and copyright line of
the PDF itself (RFS 22(3) 2009, doi 10.1093/rfs/hhn038). No web search was used for any substantive claim.

**Out of scope, present in the same folder, not read for this report:** `Expected Returns and Large Language
Models.txt`, `Option_Pricing_of_Earnings_Announcement_Risks.txt`, `Reproducibility in the TradingAgents
Framework.txt`, `The Deflated Sharpe Ratio….txt`. The last two are directly relevant to the evaluation
section of the write-up and should be assigned to a separate agent.

**Derived numbers** (arithmetic by this agent, flagged as such wherever used): the 2.5-session Sharpe of
0.098 in E-C9; the implied-move-to-moneyness conversion at VIX 15 in design row 5; and the contract counts
and median-P&L translations in design row 19. All inputs to those calculations are cited table values.

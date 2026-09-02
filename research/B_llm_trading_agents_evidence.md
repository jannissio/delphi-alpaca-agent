# B — LLM Trading Agents: Evidence Review

**Purpose:** evidence base for a one-page justification of the division of labor between an LLM orchestrator and a deterministic quantitative options core, for the lablab.ai × Alpaca "AI Trading Agents Hackathon" (deadline 2026-09-04 15:00 UTC).
**Compiled:** 2026-09-01. **Method:** web search + direct fetch of arXiv/PDF sources; abstracts, results tables and conclusions only.
**Reading note:** every number below was read out of the source itself unless explicitly flagged `[UNVERIFIED]`.

---

## Kurzfassung (Deutsch)

1. Die Evidenz, dass LLMs aus **Text** (Nachrichten-Headlines) handelbares Signal ziehen, ist real und mehrfach repliziert: Lopez-Lira & Tang messen für eine GPT-4-Headline-Strategie eine annualisierte Sharpe Ratio von 2,97 (S1).
2. Dieses Signal ist aber **extrem fragil gegenüber Transaktionskosten**: bei 10 bps Round-Trip fällt die Sharpe Ratio von 2,97 auf 1,29, bei 20 bps ist die Strategie unprofitabel — bei ~190 % Tages-Turnover (S1).
3. Der Effekt **zerfällt über die Zeit**: Sharpe 6,54 (Q4 2021) → 3,68 (2022) → 2,33 (2023) → 1,22 (Jan–Mai 2024) `[UNVERIFIED, aus Suchtreffer]`. Das Alpha ist Adoptions-abhängig, nicht strukturell.
4. **Look-ahead-Bias ist real, aber nicht der Hauptgrund** für gute Backtests: Glasserman & Lin finden, dass der "Distraction Effect" stärker wirkt (S2); He et al. zeigen mit chronologisch konsistenten Modellen, dass der Bias "modest" ist (S5).
5. Der prominenteste "LLM schlägt Analysten"-Befund (Kim/Muhn/Nikolaev) wurde **2025 zurückgezogen**, ebenso ein zweites Paper derselben Gruppe — Replikation scheiterte (S4). Das ist die wichtigste Warnung im ganzen Feld.
6. **LLM-Multi-Agent-Trading-Frameworks (TradingAgents, FinMem, FinCon) sind methodisch schwach**: 3 Monate, 3–5 Mega-Cap-Tech-Titel, keine Transaktionskosten, Sharpe 8,21 (S6). Solche Zahlen sind ein Overfitting-Signal, kein Qualitätssignal.
7. Unabhängige Re-Evaluierungen sind ernüchternd: unter Leakage-Kontrolle erklärt sich die Rendite von LLM-Agenten fast vollständig durch **Markt- und Style-Exposure**, kaum Selektions-Alpha (S10); bei sauberer Ausführungslogik schlagen LLM-Agenten Buy-and-Hold **nicht** (S11, S19).
8. Zu **Optionen** existiert fast nichts. Der einzige direkt passende Beitrag (S12) macht genau das, was wir planen: LLM als **Semantic Parser** in eine typisierte Zwischensprache, Ausführung und Greeks-Validierung deterministisch. Dessen semantische Genauigkeit liegt bei nur 0,698 — d. h. ~30 % der Intents werden falsch kodiert, wenn niemand deterministisch prüft.
9. LLMs sind **überkonfident** (RLHF belohnt selbstsichere Antworten, S14) und ihre **Risikopräferenzen sind ein Artefakt des Alignments** (10 % mehr "Ethik" → 2–8 % weniger Risikoappetit, prompt-resistent, S15). Ein LLM darf deshalb **keine Positionsgröße** bestimmen.
10. **Empfohlene Arbeitsteilung:** LLM für unstrukturierte Information, Regime-/Event-Klassifikation, Strategie-*Auswahl* aus einem festen Menü, Orchestrierung, Erklärung und **Veto**. Deterministischer Code für Pricing, Greeks, Sizing, Ausführung und harte Risiko-Gates. Das LLM darf ablehnen, aber nie überschreiben.
11. **Bewertung:** Mit 2 Handelstagen ist P&L statistisch bedeutungslos. Bailey et al.: schon 7 unabhängige Trials auf 2 Jahren Daten erzeugen eine In-Sample-Sharpe von 1 bei wahrer Sharpe von 0 (S16); Harvey/Liu/Zhu fordern t > 3,0 (S17).
12. Wir sollten deshalb **Prozessmetriken** melden — Risk-Gate-Adhärenz, Entscheidungs-Latenz, Veto-Rate, Ex-ante/Ex-post-Greeks-Abweichung, Slippage — und P&L nur mit Benchmark (SPY Buy-and-Hold, CBOE PUT/CNDR) und expliziter Unsicherheitsangabe.
13. **Gegenüber dem Alpaca-Referenzartikel (S18):** dessen Human-Gate widerspricht "autonom"; 32 % Approval-Quote heißt, ein Mensch trifft die eigentliche Entscheidung. Wir ersetzen ihn durch einen deterministischen Pre-Trade-Validator plus LLM-Kritiker mit Veto-Recht.
14. Behalten sollten wir vom Alpaca-Artikel: rollenspezifische Agenten mit **strukturiertem Proposal-Schema**, den LLM-freien Risk Guard, OCO-Brackets und das Regime-Gating (ihr eigenes "Lesson Learned": der Contrarian-Agent brauchte Regime-Gating).
15. **Unser Alleinstellungsmerkmal:** Optionen-first, Greeks-validiert, LLM als Regime-Klassifikator und Veto-Instanz, ehrliche Evaluations-Story mit Benchmark und Prozessmetriken statt Sharpe-Theater.

---

## Source cards

### S1 — Lopez-Lira & Tang, "Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models"
- **Citation:** Alejandro Lopez-Lira, Yuehua Tang. arXiv:2304.07619 (v1 Apr 2023 → v6 Oct 2025); SSRN 4412788.
- **Type / venue / year:** Working paper (arXiv + SSRN), 2023–2025. Widely presented (Jacobs Levy Center, FoFI 2024).
- **Citation count:** not verified (Semantic Scholar API unreachable, see method log). Anecdotally the most-cited paper in this literature.
- **Quality verdict:** **citation-worthy: yes.** Strongest design in RQ1: sample deliberately starts **after** the model knowledge cutoff, full cost sensitivity analysis, model-size ladder, 12 LLMs compared.
- **Key findings (verified in v6 full text):**
  - Sample **Oct 2021 – May 2024**, chosen explicitly to be out-of-sample vs. GPT training data; **~105,742 overnight observations**, **4,123 unique companies**.
  - Long-short daily strategy on GPT-4 headline scores: **annualized Sharpe 2.97** (overnight news), **2.63** intraday, **34 bps/day** mean, **58% headline hit rate**, **93.3% portfolio-day hit rate** for the (non-tradable) initial reaction.
  - **Model-size ladder:** GPT-4 SR 2.97 > GPT-3.5 SR 1.66 > DistilBART-MNLI SR 1.26 > **negative** SR for GPT-1, GPT-2, Llama2-7b. "Financial reasoning is an emerging capacity of complex LLMs."
  - **Transaction costs (decisive):** 5 bps round-trip → cumulative return still >300%; **10 bps → >100%**; **20 bps → unprofitable**. Turnover ≈ **190% per day** at full rebalancing. At 10 bps, Sharpe drops **2.97 → 1.29**; a 25%-partial-rebalance variant (turnover ≈46%/day) holds **SR 1.34**.
  - Not a small-cap artifact: excluding sub-$5 and sub-20th-NYSE-percentile stocks still yields >300% cumulative (pre-cost).
  - GPT-4 beats supervised embedding models when data is scarce (intraday, n=26,109: OpenAI-embedding SR 1.71 vs GPT-4 SR 2.63).
  - Decay over time: SR **6.54 (Q4 2021) → 3.68 (2022) → 2.33 (2023) → 1.22 (Jan–May 2024)** `[UNVERIFIED — from search snippet of an earlier version, not located in v6 text I read]`.
- **Relevance to us:** this is the single best citation for "LLM text signal is real." It is *also* the best citation for "and it dies at 20 bps." Options round-trips cost far more than 20 bps, so **we must not build a high-turnover LLM-headline strategy**; use the text signal as a *filter/regime input*, not as the P&L engine.
- **Caveats:** working paper, not peer-reviewed; equity-only; pre-cost headline numbers get quoted far more often than the cost-adjusted ones; heavy reliance on a single vendor news feed matched to tickers.

### S2 — Glasserman & Lin, "Assessing Look-Ahead Bias in Stock Return Predictions Generated by GPT Sentiment Analysis"
- **Citation:** Paul Glasserman, Caden Lin. arXiv:2309.17322 (Sep 2023). Published: *The Journal of Financial Data Science* 6(1), p.25 (2024).
- **Type / venue / year:** **Peer-reviewed journal** (JFDS 2024) + arXiv preprint.
- **Citation count:** not verified.
- **Quality verdict:** **citation-worthy: yes.** Peer-reviewed, and it is the paper that *defines the two failure modes* everyone else now cites (look-ahead bias vs. distraction effect).
- **Key findings:** Two distinct contaminations are separated: (a) **look-ahead bias** — the LLM may know what happened after the article; (b) **distraction effect** — general knowledge of the named company interferes with reading the text's sentiment. Their debiasing method **anonymizes company identifiers** in the headline. Result: **anonymized headlines outperform original headlines in-sample**, i.e. the distraction effect dominates look-ahead bias. The effect is **strongest for large, well-known companies**. Out-of-sample, look-ahead bias vanishes but distraction persists, so anonymization is useful **live**, not only for backtesting.
- **Relevance to us:** directly actionable — when we ask the LLM to score news or classify an event, **strip the ticker/company name** from the text and pass identity separately as structured metadata. Cheap to implement, defensible in the write-up, and a concrete "we read the literature" signal to judges.
- **Caveats:** exact Sharpe deltas for original vs. anonymized are in the full paper, which I did not read end-to-end; the mechanism ("distraction") is inferred, not causally isolated.

### S3 — Chen, Kelly & Xiu, "Expected Returns and Large Language Models"
- **Citation:** Yifei Chen, Bryan T. Kelly, Dacheng Xiu. SSRN 4416687 (2023–2025).
- **Type / venue / year:** Working paper; 2023 GSU-RFS FinTech Conference **Best Paper Award**.
- **Citation count:** not verified.
- **Quality verdict:** **citation-worthy: with caveats.** Author credibility is top-tier (Kelly/Xiu are the standard reference for financial ML) and it is the strongest *methodological* claim in RQ1 — but I could not extract the numbers at source (SSRN blocked; the Jacobs Levy PDF stream was not text-extractable).
- **Key findings (as reported in secondary summaries, `[UNVERIFIED at source]`):** LLM **embeddings** (ChatGPT and LLaMA family) of news predict the cross-section of returns; portfolios formed on LLM-implied expected returns deliver **economically meaningful Sharpe ratios after transaction costs** and are **not driven by look-ahead bias**; they substantially beat bag-of-words and Word2Vec text representations; the signal contains information **incremental to** return reversal and firm characteristics; predictability **persists for several days in small stocks but dissipates quickly in large stocks**, consistent with limits to attention and arbitrage.
- **Relevance to us:** the "survives transaction costs" claim is the counterweight to S1's fragility, and the embedding approach (as opposed to prompting) is the cheaper, more deterministic way to use an LLM on text. It also supports treating LLM text signal as a **multi-day drift** signal, which matters: multi-day horizons are compatible with options premiums; intraday is not.
- **Caveats:** numbers unverified by me — **do not quote a specific Sharpe from this paper in the write-up.** Cite the qualitative claim only. See "Paywalled / wanted".

### S4 — Kim, Muhn & Nikolaev, "Financial Statement Analysis with Large Language Models" — **WITHDRAWN**
- **Citation:** Alex Kim, Maximilian Muhn, Valeri Nikolaev. arXiv:2407.17866. v1 2024-07-25, v2 2024-11-10, **v3 2025-02-20 (withdrawn)**.
- **Type / venue / year:** Withdrawn working paper.
- **Quality verdict:** **citation-worthy: yes — but only as a cautionary tale. Never cite its results.**
- **Key findings and the withdrawal (verified verbatim):**
  - Original claims: GPT-4 given **standardized and anonymous** financial statements "outperforms financial analysts in its ability to predict earnings changes directionally", is "on par with a narrowly trained state-of-the-art ML model", and "trading strategies based on GPT's predictions yield a higher Sharpe ratio and alphas".
  - arXiv comment field, verbatim: *"A co-author identified inconsistencies in the data and analyses while attempting to replicate past analyses from the working paper. Accordingly, we have temporarily withdrawn the working paper from circulation while we review the research findings."*
  - Nikolaev's Chicago Booth faculty page confirms and extends this: a **second** paper, *"Bloated Disclosures: Can ChatGPT Help Investors Process Information?"*, was also withdrawn — *"his analyses did not yield results supporting the reported findings. I have reviewed and confirmed these inconsistencies, and we have withdrawn the working paper from circulation."* The authors state they *"decided to review certain other LLM-based working papers for similar issues."*
- **Relevance to us:** this is the strongest single argument for our architecture. The most-publicized "LLM beats human analysts" result in accounting **failed replication by its own authors**. Therefore: do not put the LLM on the critical path for a numeric judgment that a deterministic model can make. Also a great line for the write-up and the presentation.
- **Caveats:** withdrawal ≠ proof the effect is absent; a corrected version may appear. Describe it accurately as *withdrawn pending review*, not as "debunked" or "fraud".

### S5 — He, Lv, Manela & Wu, "Chronologically Consistent Large Language Models"
- **Citation:** Songrun He, Linying Lv, Asaf Manela, Jimmy Wu. arXiv:2502.21206 (v1 Feb 2025, v3 Jul 2025). Models: **ChronoBERT / ChronoGPT**.
- **Type:** Working paper / arXiv. **Citation count:** not verified.
- **Quality verdict:** **citation-worthy: yes.** It is the most rigorous available answer to "how big is look-ahead bias really?" because it builds the counterfactual model rather than estimating the bias.
- **Key findings:** They pretrain a suite of LLMs that **only ever see text available at each point in time**, eliminating lookahead bias and training leakage by construction. Despite the constraint, the models **match or beat standard BERT** on NLP benchmarks and stay competitive with larger open-weight models. In the asset-pricing application (predicting next-day stock returns from news), ChronoBERT/ChronoGPT achieve **Sharpe ratios comparable to a much larger Llama model**. Headline conclusion: **"lookahead bias is modest"** in this application — weaker language comprehension is compensated by the downstream regression.
- **Relevance to us:** two things. (a) It licenses us to use an off-the-shelf frontier LLM without apologizing endlessly about leakage — the bias is real but second-order. (b) It reinforces that the LLM's contribution is **text comprehension**, and the *quantitative* mapping to a position should be a separate, fitted/deterministic layer.
- **Caveats:** "modest" is application-specific (daily news → next-day returns); says nothing about leakage in *agentic* settings where tickers and dates are passed verbatim (see S9, S10, where leakage is large).

### S6 — Xiao, Sun, Luo & Wang, "TradingAgents: Multi-Agents LLM Financial Trading Framework"
- **Citation:** Yijia Xiao, Edward Sun, Di Luo, Wei Wang. arXiv:2412.20138 (v1 Dec 2024 → v7 Jun 2025). Tauric Research. Comment: *"Oral @ Multi-Agent AI in the Real World"* (workshop).
- **Type:** arXiv preprint + workshop oral + very widely forked GitHub project. **Citation count:** not verified; GitHub stars reported as **80k+** `[UNVERIFIED — from a secondary blog]`.
- **Quality verdict:** **citation-worthy: with caveats — cite it for the *architecture*, never for the *results*.**
- **Key findings (architecture — the part worth citing):** roles mirroring a trading firm: **fundamental / sentiment / technical analysts → Bull and Bear researcher agents that debate → trader → risk-management team with differing risk profiles**. Two model tiers: `o1-preview` for "deep thinking" (analysts, researchers, traders), `gpt-4o`/`gpt-4o-mini` for "quick thinking" (retrieval, summarization). ~**11 LLM calls and 20+ tool calls per prediction**.
- **Key findings (results — the part to attack):** Backtest **2024-01-01 to 2024-03-29 (≈3 months)** on **AAPL, GOOGL, AMZN** (universe drawn from AAPL/NVDA/MSFT/META/GOOGL). Reported: **CR 26.62% / 24.36% / 23.21%**, **AR 30.5% / 27.58% / 24.90%**, **Sharpe 8.21 / 6.39 / 5.60**, **MDD 0.91% / 1.69% / 2.11%**, vs. baselines Buy-and-Hold, MACD, KDJ+RSI, ZMR, SMA. **Transaction costs are not mentioned anywhere in the methodology or results.**
- **Relevance to us:** the analyst→researcher→trader→risk-manager role decomposition is the recurring, defensible pattern and judges will recognize it. Adopt the *shape*; reject the *evaluation*.
- **Caveats (severe, and worth stating explicitly in our write-up):** a **Sharpe of 8.21** over a 3-month window is not a performance claim, it is an overfitting diagnostic — a **0.91% max drawdown** on a single mega-cap in Q1 2024 is implausible as a repeatable property. Three tickers, one quarter, one of the strongest tech tape in years, no costs, no seeds/repeats reported, universe selected ex post. See S19 for an independent reproduction that fails to beat buy-and-hold.

### S7 — Yu et al., "FinMem: A Performance-Enhanced LLM Trading Agent with Layered Memory and Character Design"
- **Citation:** Yangyang Yu, Haohang Li, Zhi Chen, Yuechen Jiang, Yang Li, Denghui Zhang, Rong Liu, Jordan W. Suchow, et al. arXiv:2311.13743 (v1 Nov 2023, v2 Dec 2023).
- **Type:** arXiv preprint (subsequently an AAAI-symposium-track paper `[UNVERIFIED]`). **Citation count:** not verified.
- **Quality verdict:** **citation-worthy: with caveats.** Cite for the memory design, which is the genuinely reusable idea; results not verified at source.
- **Key findings (architecture):** three modules — **Profiling** (agent character/risk persona), **Memory** with **layered message processing** matching "the cognitive structure of human traders" and an **adjustable cognitive span**, and **Decision-making**. Memories decay and are promoted/demoted across layers; the agent "self-evolves its professional knowledge". Emphasis on **interpretability and real-time tuning**.
- **Relevance to us:** this is the citation for a **trade journal / episodic memory**: short-term (today's regime, open positions, recent fills), mid-term (this week's realized vs. expected Greeks), long-term (durable lessons, e.g. "short vol into an FOMC print has lost 3 times"). Cheap to build, highly demo-able, and it makes the agent look genuinely autonomous rather than stateless.
- **Caveats:** evaluation tickers/period/Sharpe not extracted at source (abstract only); the "character design" component is unfalsifiable as specified; same in-sample-window concerns as S6.

### S8 — Yu et al., "FinCon: A Synthesized LLM Multi-Agent System with Conceptual Verbal Reinforcement for Enhanced Financial Decision Making"
- **Citation:** Yangyang Yu, Zhiyuan Yao, Haohang Li, Zhiyang Deng, Yupeng Cao, Zhi Chen, Jordan W. Suchow, Rong Liu, et al. arXiv:2407.06567 (v1 Jul 2024, v3 Nov 2024). Reported as **NeurIPS 2024** `[UNVERIFIED — the arXiv comment field lists keywords, not a venue]`.
- **Type:** arXiv preprint; conference paper if the NeurIPS acceptance is confirmed. **Citation count:** not verified.
- **Quality verdict:** **citation-worthy: with caveats.** If NeurIPS 2024 is confirmed it is the most credible *peer-reviewed* multi-agent trading architecture; results still unverified by me.
- **Key findings (architecture):** a **manager–analyst communication hierarchy** modeled on real investment firms; **Conceptual Verbal Reinforcement (CVRF)** — the system episodically self-critiques and distills **conceptualized investment beliefs** that are then **selectively propagated only to the nodes that need the update**, which the authors argue improves performance *and* cuts peer-to-peer communication cost. A dedicated **risk-control component** triggers the self-critique. Generalizes across **single-stock trading and portfolio management**.
- **Relevance to us:** two directly transferable ideas. (1) **Selective belief propagation** — don't broadcast every reflection to every agent; write the lesson to the specific role that needs it. Cheap, and a good architectural talking point. (2) **Risk control as the trigger for reflection**, i.e. a losing/blocked trade is what causes learning. Both fit our 2-day window: we can show belief updates in the journal between day 1 and day 2.
- **Caveats:** tickers, periods and performance numbers not in the abstract page and not extracted; "verbal reinforcement" is not reinforcement learning and has no convergence guarantee; the ablations are the part that would need scrutiny.

### S9 — Li, Zeng, Xing, Xu & Xu, "Profit Mirage: Revisiting Information Leakage in LLM-based Financial Agents"
- **Citation:** Xiangyu Li, Yawen Zeng, Xiaofen Xing, Jin Xu, Xiangmin Xu. arXiv:2510.07920 (Oct 2025).
- **Type:** arXiv preprint. **Citation count:** not verified.
- **Quality verdict:** **citation-worthy: yes** (as a critique). The framing is precise and the term is memorable.
- **Key findings:** Verbatim from the abstract: most LLM financial-agent systems exhibit a **"profit mirage": dazzling back-tested returns evaporate once the model's knowledge window ends**, due to inherent information leakage in LLMs. They examine leakage along four dimensions, build **FinLake-Bench** as a leakage-aware evaluation resource, and propose **FactFin** (Strategy Code Generator + RAG + Monte Carlo Tree Search + Counterfactual Simulator) which uses **counterfactual perturbations** to push agents toward causal factors rather than memorized patterns; reported to improve out-of-sample generalization.
- **Relevance to us:** gives us the one-sentence critique of every competitor's backtest, and the constructive move we should copy: **perturb the inputs** (anonymize tickers, jitter dates) and check whether the agent's decision changes for a *reason*. If a decision flips only because the ticker was visible, it was memory, not analysis.
- **Caveats:** exact percentage gaps not on the abstract page; FactFin's own evaluation has the usual self-reported-improvement problem.

### S10 — Zhu et al., "From Knowing to Doing: A Memory-Controlled Benchmark for LLM Trading Agents on Stock Markets" (KTD-Fin)
- **Citation:** Taojie Zhu, Wentao Zhao, Rui Sun, Beidi Luan, Jiacheng Lu, Sinuo Wang, Jing Li, Daxin Jiang, et al. arXiv:2605.28359 (May 2026).
- **Type:** arXiv preprint (benchmark). **Citation count:** not verified (too recent).
- **Quality verdict:** **citation-worthy: yes.** The single most decisive negative result for RQ2, because it does return *attribution* rather than just reporting returns.
- **Key findings:** Identifies two evaluation vulnerabilities: (i) long backtests overlap model knowledge cutoffs, so **memorized information substitutes for reasoning**; (ii) raw returns conflate **market beta and style exposure** with genuine stock-selection skill. Their **data-side masking protocol** anonymizes identifiers and calendar information **consistently across prompts and tools**. Findings: masking **substantially changed agent reasoning**, pushing agents from ticker-based to anonymized factor-based approaches; a representative model **traded when tickers were visible but declined to trade when they were anonymized**. Attribution result, verbatim: LLM agents' cumulative returns under leakage-controlled evaluation are **"largely explained by passive market and style exposure, with limited evidence of persistent stock-selection alpha."** Ten frontier LLM agents, **CSI300 (China), 2024–2026 window**.
- **Relevance to us:** the "declines to trade when tickers are anonymized" result is the most damning single fact in this literature and belongs in our presentation. Design consequence: **do not ask the LLM to pick tickers.** Give it a fixed, liquid universe and ask it to classify regime and select a *structure*. Also: report our P&L **net of SPY beta**, because judges' P&L criterion will otherwise reward market direction, not skill.
- **Caveats:** Chinese A-share market (CSI300), so transfer to US equity options is an assumption; very recent, not peer-reviewed; masking calendar information also removes legitimately usable seasonality.

### S11 — Yao & Zheng, "Beyond Agent Architecture: Execution Assumptions and Reproducibility in LLM-Based Trading Systems"
- **Citation:** Junyi Yao, Zihao Zheng. arXiv:2606.08285 (Jun 2026).
- **Type:** arXiv preprint (audit + case study + checklist). **Citation count:** not verified (too recent).
- **Quality verdict:** **citation-worthy: yes.** A coded audit of 30 trade-relevant studies plus a reproducible case study — exactly the kind of source that makes our evaluation section credible.
- **Key findings:**
  - **Coded audit of 30 studies** on: point-in-time controls, temporal splits, execution timing, transaction costs, turnover treatment, artifact release. Conclusion: papers report architectural novelty far more clearly than the assumptions that determine reproducibility.
  - **Case study:** 10 large-cap US equities (AAPL, AMZN, GOOG, JNJ, JPM, META, MSFT, NFLX, NVDA, PG), **2020-01-02 → 2024-06-26**; signal formed **after close of day t**, evaluated on **next-day close-to-close** return; cost scenarios **0 / 10 / 25 bps** per unit turnover.
  - At **10 bps**: Buy-and-Hold CR **1.1995**, AR **0.7057**, **Sharpe 3.1958**; LLM-proxy scaffold CR **1.3068**, AR **0.7616**, **Sharpe 2.8685**; structured-only CR **1.1558**, Sharpe **2.4299**. I.e. the scaffold edges out buy-and-hold on raw return but **loses on Sharpe**.
  - Cost sensitivity: LLM-proxy CR **1.4710 (0 bps) → 1.3068 (10 bps) → 1.0806 (25 bps)** — a **26.5% erosion** by 25 bps.
  - Deliverable: a **minimum reporting checklist** (Table XVIII): universe definition and inclusion rules, data provenance and access dates, point-in-time discipline, train/val/test split dates, execution timing semantics, cost and slippage model, model versions/prompts/tool config, seeds or retry policy, artifact release status.
- **Relevance to us:** we should adopt their checklist verbatim as the structure of our "how we evaluated" section. It is a one-page, judge-legible way to look more rigorous than every other team.
- **Caveats:** the "LLM" in the case study is a deterministic **proxy scaffold**, not a live LLM — so it measures execution-assumption sensitivity, not LLM skill; the authors explicitly note there is no sampling temperature or model-version drift inside the case study, i.e. **it does not measure LLM non-determinism**.

### S12 — Luo et al., "From Natural Language to Executable Option Strategies via Large Language Models" (OQL)
- **Citation:** Haochen Luo, Zhengzhao Lai, Junjie Xu, Yifan Li, Tang Pok Hin, Yuan Zhang, Chen Liu. arXiv:2603.16434 (2026-03-17), cs.AI.
- **Type:** arXiv preprint. **Citation count:** not verified (too recent).
- **Quality verdict:** **citation-worthy: yes.** The only source I found that puts LLMs and *options* together in a way that is directly architectural, and it independently validates our planned design.
- **Key findings:**
  - Problem framing, verbatim: *"LLMs excel at general code generation, yet translating natural-language trading intents into correct option strategies remains challenging."*
  - Solution: **Option Query Language (OQL)** as an intermediate representation, so the **LLM acts as a semantic parser, not a code generator**, feeding a **deterministic execution engine**. Formally `P(y|x,D) = Σ_z P_θ(z|x)·P_φ(y|z,D)` — LLM owns `z` (the parse), deterministic engine owns `y` (the executable strategy).
  - Design principles: **role-based abstraction** (each strategy family has a fixed leg-role schema, e.g. Short Call / Long Put, guaranteeing structural validity); **scoped filtering** (leg-level `WHERE` vs. strategy-level `HAVING`); **semantic soft-matching** for linguistic ambiguity.
  - Deterministic validation layer: **Black-Scholes-Merton Greeks (Delta, Gamma, Vega, Theta, Rho)**, net Greeks, **maximum loss**, reward-to-risk, terminal payoff `Π(S_T) = Σ_i q_i·d_i·(P_i(S_T) − p_i)`, real option chains with strikes/maturities/premiums/volumes.
  - Evaluation: **200 labeled natural-language instructions**, 5 underlyings (**SPY, NVDA, AAPL, GOOG, TSLA**), **2025 market data only**. Metrics: Validity Rate, Strategy Match, Semantic Accuracy; plus Win Rate, ROC, margin-call risk.
  - Results: **Validity Rate ≥ 0.87** across models; best **GPT-4.1 (VR 0.935, Semantic Accuracy 0.698)**; **DeepSeek-Chat/OQL cuts Risk@90 to 18.6% vs 46.1% with a plain SQL baseline**; best Win Rate **60.9%** (DeepSeek-Chat); OQL gives an **88.5% prompt-cache hit rate**.
- **Relevance to us: this is our architecture, externally validated.** Two headline numbers for the write-up: (a) **Semantic Accuracy of only 0.698 even for the best model** — roughly **3 in 10 option intents are mis-encoded**, which is precisely why a deterministic validator must sit between the LLM and the broker; (b) **structured intermediate representation cuts risk-of-ruin from 46.1% to 18.6%** vs. letting the model emit queries freely. Adopt: a typed strategy schema with fixed leg roles, LLM fills slots, code prices legs, computes net Greeks and max loss, and rejects anything violating limits.
- **Caveats:** very recent, not peer-reviewed; BSM assumptions; American-option and IV/execution-gap limitations acknowledged; win rates on 200 instructions over 2025 data are not a strategy backtest.

### S13 — Asaad, Hamidi & Bereyhi, "Regime-aware financial volatility forecasting via in-context learning"
- **Citation:** Saba Asaad, Shayan Mohajer Hamidi, Ali Bereyhi. arXiv:2603.10299 (2026-03-11). Comment: **"Published as a conference paper at ICLR 2026 Workshop on Advances in Financial AI."**
- **Type:** Workshop paper (ICLR 2026 workshop) + arXiv. **Citation count:** not verified (too recent).
- **Quality verdict:** **citation-worthy: with caveats.** Workshop-tier and short (11 pages, 1 figure), but it is the closest thing to "LLMs and volatility regimes" that exists, and it compares against the right baselines.
- **Key findings:** An LLM forecasts volatility via **in-context learning with no fine-tuning**. Three stages: initial prompting with historical returns and variance; **oracle-guided refinement** that uses ground-truth feedback to build high-quality demonstrations **labeled by volatility regime (high/low)**; and **conditional demonstration sampling based on the estimated current regime**. Data: **S&P 500, NASDAQ Composite, EUR/USD**, 70/30 train-test split. Baselines: rolling mean, **HAR, GARCH(1,1), GJR-GARCH**, one-shot LLM, random demonstration selection. Result (S&P 500): regime-aware ICL **MAE 1.14×10⁻⁴, RMSE 4.51×10⁻⁴**; **high-volatility MAE improves ~27% vs GJR-GARCH**; explicit **trade-off** — better high-regime accuracy costs low-regime accuracy.
- **Relevance to us:** direct support for the specific job we want the LLM to do: **classify the volatility regime**, then let deterministic code choose the structure conditioned on that label. The 27% high-vol improvement is exactly the regime where option structure selection matters most (short premium vs. long premium, wide vs. tight wings). The trade-off finding argues for using the LLM label as a *gate*, not as a continuous input.
- **Caveats:** workshop paper, small; "oracle-guided refinement" uses ground-truth labels to build demonstrations, which is a leakage surface if not carefully time-split; no options P&L, only forecast error; a HAR/GARCH baseline is easy to beat on MAE and hard to beat on economic value.

### S14 — Leng, Huang, Zhu & Huang, "Taming Overconfidence in LLMs: Reward Calibration in RLHF"
- **Citation:** Jixuan Leng, Chengsong Huang, Banghua Zhu, Jiaxin Huang. arXiv:2410.09724 (v1 Oct 2024, v2 Feb 2025). OpenReview `l0tg0jzsdL`.
- **Type:** arXiv + OpenReview (conference submission). **Citation count:** not verified.
- **Quality verdict:** **citation-worthy: yes** for the *mechanism* claim; the specific ECE numbers are in the full paper, which I did not read.
- **Key findings:** Verbatim: **"RLHF tends to lead models to express verbalized overconfidence in their own responses."** Root cause identified: **reward models used in PPO have an inherent bias toward high-confidence scores regardless of actual response quality** — the model is trained to sound sure. Two fixes proposed (PPO-M: include explicit confidence in reward-model training; PPO-C: adjust rewards by deviation from an EMA), both requiring no extra labels; evaluated on **Llama3-8B and Mistral-7B** across six benchmarks, reducing calibration error while preserving capability.
- **Relevance to us:** this is the citation for **"never size a position on the LLM's stated confidence."** Every framework in RQ2 (including the Alpaca article, S18) asks the agent for a confidence score, and this paper explains why that number is systematically inflated by the training procedure. Our design: the LLM emits a *categorical* label plus a rationale; **position size is a deterministic function of measured quantities** (IV rank, distance to earnings, account equity, existing net Greeks), never of `confidence: 0.85`.
- **Caveats:** general-purpose NLP benchmarks, not finance; the strong claim is about *verbalized* confidence, and logit-based uncertainty may behave differently; 8B-class open models, not frontier models.

### S15 — Ouyang, Yun & Zheng, "AI as Decision-Maker: Ethics and Risk Preferences of LLMs"
- **Citation:** Shumiao Ouyang, Hayong Yun, Xingjian Zheng. arXiv:2406.01168 (v1 Jun 2024, v3 Jun 2025), econ.GN.
- **Type:** arXiv working paper (economics). **Citation count:** not verified.
- **Quality verdict:** **citation-worthy: yes.** Large model sample (50 LLMs) and a clean, quantified causal-ish claim; economics-style, so it will read as credible to finance-literate judges.
- **Key findings:** Behavioral tasks elicit risk profiles across **50 different LLMs**. Models show **stable but diverse** risk profiles. Central result: **ethical alignment training (harmlessness/helpfulness/honesty) significantly amplifies risk aversion** — verbatim, *"a ten percent ethics increase cuts risk appetite two to eight percent"*. The induced caution **persists against prompt variation** — you cannot simply prompt it away — and it propagates into economic forecasting. The authors frame it as a tension between safety alignment and economically productive risk-taking.
- **Relevance to us:** decisive for the division of labor. An aligned LLM's risk appetite is a **property of its alignment training, not of the market**, and it is **not promptable**. So "you are an aggressive options trader" in a system prompt does not reliably move behavior, while an explicit numeric risk budget in code does. Corollary for a 2-day hackathon: an LLM left to size trades will likely be *too timid* to produce P&L — another reason to put sizing in deterministic code with an explicit, tunable risk budget.
- **Caveats:** the ethics↔risk elasticity depends on their operationalization of "ethics"; complementary studies find the opposite sign for some model families (GPT/Llama more risk-averse than humans, DeepSeek/Qwen less; GPT-4.1 statistically indistinguishable from humans on gambling propensity) `[UNVERIFIED — from search snippets of adjacent papers, see Follow-up reading]`. The safe, well-supported claim is **heterogeneity and prompt-resistance**, not a universal direction.

### S16 — Bailey, Borwein, López de Prado & Zhu, "Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample Performance"
- **Citation:** David H. Bailey, Jonathan M. Borwein, Marcos López de Prado, Qiji Jim Zhu. *Notices of the American Mathematical Society* **61(5), 458–471 (2014)**.
- **Type:** **Peer-reviewed journal** (AMS Notices). **Citation count:** not verified; canonical in the field.
- **Quality verdict:** **citation-worthy: yes.** Read at source (full PDF text extracted).
- **Key findings (verified verbatim from the paper):**
  - **"if only five years of data are available, no more than forty-five independent model configurations should be tried"** — beyond that, *"we are almost guaranteed to produce strategies with an annualized Sharpe ratio IS of 1 but an expected Sharpe ratio OOS of zero."*
  - **"After trying only seven independent strategy configurations, the expected maximum SR IS is 1 for a two-year long backtest, while the expected SR OOS is 0."**
  - Minimum Backtest Length bound: **MinBTL < 2·ln[N] / E[max_N]²** (years), where N is the number of independent trials.
  - **"a backtest which does not report the number of trials N used to identify the selected configuration makes it impossible to assess the risk of overfitting."**
  - Overfitting need not produce *negative* OOS performance in the absence of memory — but combined with over-leverage it is "still very damaging"; technical-analysis filter strategies are called out as especially prone.
- **Relevance to us:** the honest framing device for our results section. Every LLM-agent paper we cite (S6 above all) violates this: none report N. And it tells us what to say about our own 2-day window — with a handful of trades, **no Sharpe we compute is meaningful**, and saying so out loud is a credibility asset in front of judges who know this paper.
- **Caveats:** assumes IID Normal returns and independent trials (the authors call the independence assumption "quite conservative"); options returns are neither Normal nor IID, so treat the numbers as order-of-magnitude discipline, not exact thresholds.

### S17 — Harvey, Liu & Zhu, "…and the Cross-Section of Expected Returns"
- **Citation:** Campbell R. Harvey, Yan Liu, Heqing Zhu. *Review of Financial Studies* **29(1), 5–68 (2016)** (received Oct 2014, accepted Jun 2015, Ed. Andrew Karolyi).
- **Type:** **Peer-reviewed top-3 finance journal.** **Citation count:** not verified; canonical.
- **Quality verdict:** **citation-worthy: yes.** Read at source (full PDF text extracted).
- **Key findings (verified verbatim):** *"Hundreds of papers and factors attempt to explain the cross-section of expected returns. Given this extensive data mining, it does not make sense to use the usual criteria for establishing significance… A new factor needs to clear a much higher hurdle, with a t-statistic greater than 3.0. We argue that most claimed research findings in financial economics are likely false."* Their collection comprises **316 factors** and they note it *"likely underrepresents the factor population."* Benchmark for contrast: Fama-MacBeth (1973) reported **t = 2.57** for market beta, comfortably over the then-usual cutoff of 2.0. Multiple-testing framework with family-wise error and false-discovery-rate adjustments (w and d set at 5%).
- **Relevance to us:** the second half of the honesty argument. If a *published, peer-reviewed* factor needs t > 3.0, then a 2-day, ~n-trade live result needs no statistical claim at all. Use it to justify reporting **process quality** rather than significance.
- **Caveats:** about cross-sectional equity factors, not about agent systems or options; the t > 3.0 hurdle is a multiple-testing correction for a specific published-factor population, so cite it as an *analogy and standard of rigor*, not a literal test we must pass.

### S18 — Panteleev, "Building a Multi-Agent AI Trading System on Alpaca"
- **Citation:** Fedor Panteleev (CPO, CUSP Wealth). Alpaca Learn blog, May 2026. https://alpaca.markets/learn/building-a-multi-agent-ai-trading-system-on-alpaca
- **Type:** **Industry blog post** (vendor-published). **Quality verdict:** **citation-worthy: with caveats** — cite as the reference design judges will know and as an engineering artifact, never as evidence. Conflict of interest: published by the broker whose API it uses, authored by an executive of a wealth platform.
- **Key findings (verified from the article):**
  - Pipeline: **Data Layer → Regime Screener → 5 isolated agents → Critic → Human Gate → Risk Guard → Alpaca Execution → Position Monitor.**
  - Five agents on the same snapshot: **Momentum** (breakouts, RSI, volume), **Macro** (FRED, yield curve, VIX, sector rotation), **StatArb** (pairs, rolling correlation, dislocation scores), **Contrarian** (oversold, sentiment, insider activity), **Exotic** (calendar effects, earnings binaries).
  - **Structured proposal schema** (this is the best idea in the article): ticker, direction, thesis, entry conditions, take-profit %, stop-loss %, horizon in days, **macro alignment (WITH/AGAINST)**, confidence score.
  - **Critic agent** enforces governance: S&P 500 only, no ETFs, no crypto, leverage ≤ 1.0x, max single position 10%.
  - **Human gate:** explicit APPROVE / REJECT / REVISE on **every** trade. Funnel **March 18 – April 5: 82 proposals → 26 approved (32%)**.
  - **Deterministic risk guard (Python, no LLM):** 10% single position, 30% sector, 1.0x leverage, **drawdown halts at 5% daily / 10% weekly / 15% total**.
  - **Execution:** market orders on entry (acknowledged simplification), **OCO bracket** (take-profit + stop-loss, GTC) on exit.
  - **Results (paper trading, 15 trading days, S&P 500 −4.2% over the window):** **~48% win rate (12 of 25 closed trades)**; TP:SL ratios 2:1 to 2.7:1. By agent: **Macro +$1,046 / 7 trades (+1.89% avg)**, **Momentum +$413 / 5 (+1.11%)**, **Exotic +$141 / 4 (+1.21%)**, **Contrarian −$232 / 8 (−0.35%)**, **StatArb −$69 / 1 (−0.88%)** → **≈ +$1,299 total realized**. Net exposure de-risked from 63.6% (Mar 18) to 0.82% (Mar 24).
  - **Macro alignment worked:** proposals flagged WITH macro averaged **+1.62%** vs AGAINST **+0.21%**.
  - **Stated limitations (author's own):** paper trading, "limited, simulated", does not reflect liquidity, execution, transaction costs or behavioral factors. **Lessons:** the Contrarian agent needed **automatic regime gating** in trending markets ("discovering this through live losses is the slower way to learn it"); monitor data-source rate limits from day one. **Next iterations: options strategies, limit orders, live testing.**
- **Critical assessment (this is what judges will want to hear):**
  1. **The human gate contradicts "autonomous."** With 82 proposals filtered to 26 approvals, a human made the actual selection decision — a **68% human rejection rate** means the reported P&L measures a human-plus-LLM team, not an agent. For a hackathon whose rules require autonomy, this is the design's central weakness and our clearest differentiator.
  2. **n = 25 closed trades over 15 days.** A 48% win rate on 25 trades has a standard error of about ±10 percentage points; it is indistinguishable from a coin flip. Per S16/S17, no inference is available here. The article is honest that this is limited, but the number will nonetheless be quoted at us.
  3. **Per-agent attribution on 1–8 trades each** (StatArb: a single trade) is noise, not evidence of which agent works. Do not copy this as an evaluation method.
  4. **Market orders on entry** are the weakest engineering choice, and it matters far more for options than for equities, where spreads are wide.
  5. **The "+1.62% vs +0.21% macro alignment" result** is the most interesting finding and is essentially a **regime-gating** argument — consistent with S13. It is also, by their own admission, what the Contrarian agent lacked.
  6. **What to keep:** the structured proposal schema; the LLM-free deterministic risk guard with explicit numeric limits; OCO brackets; regime screening ahead of agents; per-agent isolation on a shared snapshot; honest limitation disclosure.
- **Caveats:** vendor blog, no peer review, no code release verified, single 15-day window in a falling market, no transaction costs.

### S19 — "Reproducibility in the TradingAgents Framework" — **could not access**
- **Citation:** Proceedings of the 2026 International Conference on Artificial Intelligence and Fintech. DOI **10.1145/3800973.3801029**.
- **Type:** Conference paper (ACM). **Quality verdict:** **citation-worthy: with caveats — numbers unverified at source** (ACM returned HTTP 403 to both WebFetch and curl with a Chrome UA).
- **Key findings `[UNVERIFIED — from search-result summary only]`:** an independent reproduction of TradingAgents (S6) reporting that **without cherry-picking, both LLM configurations failed to outperform the passive benchmark**: **Qwen3:30B 18.1% ± 2.8%**, **GPT-4o 15.8% ± 4.2%**, versus **19.1% for Google buy-and-hold**, over **May–July 2025**. Conclusion: LLM-based trading agents do not currently justify their complexity relative to simple buy-and-hold.
- **Relevance to us:** if verified, this is the single best rebuttal slide to the TradingAgents Sharpe-8.21 claim, and the **± figures are direct evidence of run-to-run non-determinism** (a ±4.2% spread on a ~16% return means the seed matters as much as the strategy). **Fetch with university access before quoting.**

---

## Evidence table

| # | Claim | Supporting sources | Contradicting / qualifying sources | Confidence |
|---|---|---|---|---|
| C1 | LLMs extract genuinely return-predictive signal from news text, out-of-sample relative to their knowledge cutoff | S1 (GPT-4 SR 2.97, sample post-cutoff), S3 (LLM embeddings, incremental to characteristics), S5 (chronologically consistent models retain comparable Sharpe) | S4 (the flagship "beats analysts" result was withdrawn — but that is financial statements, not news) | **High** |
| C2 | That signal does **not** survive realistic transaction costs at high turnover | S1 (20 bps round-trip → unprofitable; SR 2.97→1.29 at 10 bps; ~190%/day turnover), S11 (26.5% CR erosion at 25 bps) | S3 claims Sharpe survives costs `[UNVERIFIED]` — likely because embeddings-based portfolios trade less | **High** |
| C3 | The news-sentiment edge decays as LLM adoption spreads | S1 (SR 6.54→1.22 across 2021Q4→2024 `[UNVERIFIED]`; theory section models adoption → efficiency) | — (no contradicting source found; single-source, hence lower confidence) | **Medium** |
| C4 | Look-ahead bias exists but is **not** the dominant contaminant in headline-sentiment backtests | S2 (distraction effect > look-ahead bias), S5 ("lookahead bias is modest") | S9 ("profit mirage": returns evaporate past the knowledge window), S10 (masking changes behavior drastically) | **Medium** |
| C5 | In **agentic** settings (tickers/dates passed verbatim in prompts and tools), leakage is large and behavior-changing | S10 (model declines to trade when tickers anonymized; returns explained by market+style), S9 (profit mirage across four leakage dimensions) | S5 (bias modest — but tests a non-agentic, embedding-style setup) | **Medium-High** |
| C6 | Published LLM multi-agent trading results are not trustworthy as performance evidence | S6 (SR 8.21, 3 tickers, 3 months, no costs, no N reported), S11 (audit of 30 studies: execution assumptions under-reported), S9, S10, S19 `[UNVERIFIED]` | S8 (FinCon, possibly NeurIPS-reviewed) is the least weak, but its numbers were not verified here | **High** |
| C7 | LLM trading agents do not reliably beat buy-and-hold once evaluation is clean | S11 (scaffold Sharpe 2.87 vs B&H 3.20 at 10 bps), S19 `[UNVERIFIED]` (15.8–18.1% vs 19.1% B&H), S10 (returns ≈ passive market + style) | S6, S7, S8 all claim large outperformance — but see C6 | **Medium-High** |
| C8 | A recurring, defensible architecture is: role-specialized analysts → debate/critic → trader → separate risk manager, with memory and reflection | S6 (analyst/researcher-debate/trader/risk team), S8 (manager–analyst hierarchy + CVRF + risk-triggered self-critique), S7 (layered memory + profiling), S18 (5 analysts + critic + risk guard) | None on the pattern; all contradicting evidence is about *results*, not *structure* | **High** (as a pattern; **low** that it causes returns) |
| C9 | Constraining the LLM to a typed intermediate representation, with deterministic pricing/Greeks validation, materially reduces risk | S12 (Risk@90 46.1% → 18.6% vs free-form SQL; VR ≥ 0.87), S18 (LLM-free deterministic risk guard) | — | **Medium-High** (single primary source, but a clean controlled comparison) |
| C10 | LLMs mis-encode a substantial fraction of option intents without validation | S12 (best model Semantic Accuracy **0.698**) | — | **Medium** (single source, 200 instructions) |
| C11 | LLMs are systematically overconfident, and RLHF is a cause | S14 (reward models biased toward high confidence regardless of quality; RLHF → verbalized overconfidence) | — (broad literature agrees; I verified one primary source) | **Medium-High** |
| C12 | LLM risk preferences are model/alignment artifacts, are heterogeneous, and resist prompting | S15 (50 LLMs; +10% ethics → −2–8% risk appetite; "persists against prompts"), plus adjacent cross-cultural work showing opposite signs by family `[UNVERIFIED]` | Adjacent work reports GPT-4.1 indistinguishable from humans `[UNVERIFIED]` — direction varies, heterogeneity does not | **Medium** |
| C13 | LLM agents are non-deterministic run-to-run in ways that matter for P&L | S19 `[UNVERIFIED]` (±2.8% and ±4.2% std across runs on ~16–18% returns) | S11 explicitly does **not** measure this (deterministic scaffold) | **Low-Medium** — needs verification |
| C14 | With a 2-day live window and a handful of trades, P&L and Sharpe carry no statistical information | S16 (7 trials on 2 years ⇒ IS Sharpe 1, OOS 0; N must be reported), S17 (t > 3.0 hurdle; most findings likely false), S18 (n=25 over 15 days, 48% win rate ≈ coin flip) | — | **High** |
| C15 | LLMs can usefully classify volatility regimes, and regime conditioning improves high-vol forecasting | S13 (~27% MAE improvement vs GJR-GARCH in high-vol regime), S18 (macro-aligned +1.62% vs against +0.21%; contrarian agent failed for lack of regime gating) | S13 itself notes the trade-off: low-regime error worsens | **Medium** |
| C16 | The literature on LLMs trading **options** is essentially empty | S12 is the only direct hit found; S13 is volatility forecasting, not options; no LLM options-trading agent paper found in any search | S18 lists options only as *future* work | **Medium-High** (absence of evidence from ~6 targeted searches) |

---

## Answers to research questions 1–6

### RQ1 — Can LLMs extract return-predictive signal from news/text? Effect size, costs, look-ahead?

**Yes, the signal is real; no, it is not free money; and the look-ahead correction is not what kills it — costs are.**

*Effect size.* The best-designed study (S1) deliberately samples **after** the model's knowledge cutoff (Oct 2021 – May 2024, 4,123 firms) and finds a GPT-4 headline long-short strategy with **annualized Sharpe 2.97**, **34 bps/day**, **58% headline hit rate**. Effect size scales with model capability: **2.97 (GPT-4) → 1.66 (GPT-3.5) → 1.26 (DistilBART) → negative (GPT-1/2, Llama2-7b)**. This is an emergent-capability pattern, not a prompt trick. S3 independently finds LLM *embeddings* of news predict the cross-section, incremental to reversal and firm characteristics, and beating bag-of-words/Word2Vec.

*Transaction costs — the decisive constraint.* S1's own sensitivity analysis: **5 bps → >300% cumulative; 10 bps → >100%; 20 bps round-trip → unprofitable**, at **~190% daily turnover**. Sharpe falls **2.97 → 1.29** at 10 bps. Reducing rebalancing to 25% (turnover ~46%/day) preserves **SR 1.34** — i.e. *turnover reduction is worth more than signal strength*. S11 corroborates the shape independently: **26.5% cumulative-return erosion** going from 0 to 25 bps. S3 claims survival after costs, plausibly because embedding-based portfolios turn over less.

*Look-ahead corrections.* Two independent, well-designed attacks find the bias **smaller than expected**. S2 anonymizes company identifiers and finds anonymized headlines **outperform** in-sample — the "distraction effect" (general company knowledge polluting sentiment reading) is stronger than look-ahead, and worst for large caps. S5 builds LLMs that only ever saw point-in-time text (ChronoBERT/ChronoGPT) and concludes **"lookahead bias is modest"**, with Sharpe comparable to much larger models. **However**, this conclusion is specific to non-agentic, text→return setups. In agentic setups it inverts: S10 shows a model that **trades when tickers are visible and declines to trade when they are anonymized**, and S9 names the general phenomenon a **"profit mirage"**.

*Negative results / replication.* The most important entry in this whole review: **S4 was withdrawn by its own authors in Feb 2025** after a co-author failed to replicate it, and a **second** paper from the same group ("Bloated Disclosures") was withdrawn for the same reason. The headline claim "GPT-4 beats human analysts at predicting earnings direction" currently has **no standing**.

*Net answer for us:* use LLM text signal as a **low-turnover conditioning input** (regime, event risk, direction bias) rather than as a high-frequency alpha, and anonymize entity names when scoring text.

### RQ2 — LLM multi-agent trading frameworks: architectures, evaluation, flaws

**Recurring architectural patterns (defensible, worth copying):**
1. **Role specialization over the same snapshot** — fundamental / sentiment / technical / macro analysts producing structured proposals (S6, S18).
2. **Adversarial review before commitment** — Bull vs. Bear researcher debate (S6), a Critic agent (S18), episodic self-critique (S8). Reduces single-chain confabulation.
3. **A separate risk-manager role**, ideally with *different* risk profiles or, better, no LLM at all (S6 risk team; S18 deterministic Python guard).
4. **Layered memory with decay and reflection** — short/mid/long-term memory, character/profile, self-evolving lessons (S7); **selectively propagated** conceptual beliefs rather than broadcast (S8).
5. **Two-tier model routing** — expensive reasoning model for judgment, cheap model for retrieval/summarization (S6: `o1-preview` + `gpt-4o-mini`).
6. **A structured proposal schema** with mandatory fields, so downstream code can validate (S18) — and, taken to its logical end, a **typed intermediate representation** the LLM fills in as a semantic parser (S12).

**Evaluation protocols and their flaws:**

| Framework | Evaluation | Flaws |
|---|---|---|
| TradingAgents (S6) | AAPL/GOOGL/AMZN, **Jan–Mar 2024** (3 months), vs B&H/MACD/KDJ+RSI/ZMR/SMA | **No transaction costs.** Sharpe **8.21**, MDD **0.91%** — implausible. 3 tickers, ex-post-selected mega-cap tech in a strong bull tape. No seeds/repeats. Number of trials N not reported (S16 violation). |
| FinMem (S7) | "scalable real-world financial dataset"; tickers/period not in abstract | Small ticker set; period overlaps model knowledge; "character design" unfalsifiable. |
| FinCon (S8) | single-stock trading + portfolio management | Numbers not in abstract; "verbal reinforcement" has no convergence guarantee; ablation quality unverified. |
| Alpaca reference (S18) | 15 trading days, **25 closed trades**, paper account | n far too small; **human approval gate** contaminates attribution; per-agent P&L on 1–8 trades. |

**Independent re-evaluations — the part that matters:**
- **S11** audits **30 trade-relevant studies** and finds execution assumptions (point-in-time control, execution timing, costs, turnover, survivorship, split discipline) systematically under-reported. Its own clean case study (10 large caps, 2020–2024, next-day close-to-close, 10 bps): LLM-proxy Sharpe **2.87** vs buy-and-hold **3.20** — *worse risk-adjusted*.
- **S10** applies consistent identifier + calendar masking across prompts *and tools*, then attributes returns: LLM agents' returns are **"largely explained by passive market and style exposure, with limited evidence of persistent stock-selection alpha."**
- **S9** names the failure mode: **"profit mirage"** — backtest returns evaporate past the knowledge window.
- **S19** `[UNVERIFIED]` reproduces TradingAgents and reports **failure to beat buy-and-hold** (15.8%±4.2% and 18.1%±2.8% vs 19.1%).

**Verdict:** the *architecture* literature is useful; the *performance* literature is not. Copy the org chart, cite the critics, and make no performance claim ourselves.

### RQ3 — LLMs and options / volatility specifically

**This is nearly empty, and that is our creativity opening.** Across roughly six targeted searches I found:
- **One directly relevant paper on LLMs and options: S12** (arXiv:2603.16434, March 2026) — and it is a *strategy-construction* paper, not a trading-agent paper. It translates natural language into option structures via a typed intermediate language (OQL) and validates deterministically with BSM Greeks, max loss and payoff. Best model semantic accuracy **0.698**; structured IR cuts Risk@90 from **46.1% to 18.6%**.
- **One relevant paper on LLMs and volatility regimes: S13** (ICLR 2026 workshop) — regime-labeled in-context demonstrations, **~27% high-vol MAE improvement over GJR-GARCH**, with an explicit accuracy trade-off in the low-vol regime.
- **Nothing** on: an autonomous LLM agent actually trading options; LLMs forecasting the implied-volatility *surface*; LLMs pricing or hedging Greeks; LLMs classifying VIX regimes for position sizing; LLM-based event-risk filtering (earnings/FOMC) for premium selling.
- The Alpaca reference design (S18) lists **options as future work** — its author has not built it either.

**Explicit statement for the write-up:** *to our knowledge no published work demonstrates an autonomous LLM agent trading options with deterministic Greeks validation and event-risk gating; the closest prior work is S12 (LLM as semantic parser for option structures) and S13 (LLM regime-aware volatility forecasting), neither of which closes the loop to live execution.* That is a defensible originality claim — and it is safer than claiming novelty in equities, where the field is crowded.

### RQ4 — Where LLMs add value vs. where they hurt

**Where they hurt (evidence):**
- **Overconfidence is structural, not incidental.** RLHF actively rewards confident-sounding output; reward models are **biased toward high-confidence scores regardless of response quality** (S14). Therefore a `confidence: 0.85` field — which S18's schema and most frameworks contain — is not a probability and must not be multiplied into a position size.
- **Risk preferences are alignment artifacts and are prompt-resistant.** Across **50 LLMs**, a **10% increase in "ethics" alignment cuts risk appetite 2–8%**, and the induced caution **"persists against prompts"** (S15). You cannot prompt an aligned model into a calibrated risk stance; direction also varies by model family `[UNVERIFIED]`. Risk budget must live in code.
- **Numeric/structural encoding errors.** Even the best model encodes option intents correctly only **69.8%** of the time (S12). Free-form generation carries a **46.1% Risk@90**; the typed IR cuts it to **18.6%**.
- **Memorization masquerading as analysis.** Agents change behavior — including refusing to trade — when identifiers are masked (S10); the "profit mirage" (S9).
- **Non-determinism.** Run-to-run spreads of **±2.8% to ±4.2%** on ~16–18% returns `[UNVERIFIED, S19]`. Note that S11 explicitly could not measure this because its scaffold was deterministic — a gap in the literature.
- **Replication risk in the underlying claims themselves** (S4).

**Where they add value (evidence):**
- **Reading unstructured text** — the one capability with independent replication (S1, S3, S5) and a clean scaling law with model size (S1).
- **Regime and event classification** — S13's regime-conditioned forecasting improves high-vol accuracy ~27%; S18's own data shows macro-alignment sorting works (**+1.62% vs +0.21%**) and that the failing agent was the one **without** regime gating.
- **Semantic parsing into a constrained schema** — S12's central result: LLM as parser + deterministic engine beats LLM as generator, by a large risk margin.
- **Orchestration, critique and explanation** — the debate/critic pattern recurs everywhere (S6, S8, S18) and, whatever it does for returns, it produces the auditable rationale that a judge (and a regulator) wants to read.

**Derived division of labor:**

| Decision | Owner | Justification |
|---|---|---|
| Read news, filings, headlines; extract events | **LLM** (entity-anonymized) | S1, S3, S5; anonymization per S2 |
| Classify volatility/macro regime → categorical label | **LLM** | S13, S18 |
| Flag event risk (earnings, FOMC, CPI) within horizon | **LLM**, verified against a calendar | S18 exotic agent; S13 |
| Select a strategy *family* from a fixed menu | **LLM**, constrained to an enum | S12 (role-based abstraction) |
| Option pricing, Greeks, IV rank, payoff, max loss | **Code** | S12; S14 (no numeric trust) |
| Position sizing | **Code** | S15 (risk prefs are artifacts), S14 (confidence inflated) |
| Strike/expiry selection within the chosen family | **Code**, from deterministic rules on delta/DTE/IV | S12 (semantic accuracy 0.698) |
| Hard risk gates (max loss, net Greeks, concentration, drawdown halt) | **Code, no LLM** | S18's own guard; S16 |
| Order placement, order type, bracket construction | **Code** | S18 (market-order lesson) |
| **Veto** a code-generated candidate | **LLM** (may block, may never force) | S6/S8 critic pattern; asymmetric because a false "no" costs an opportunity, a false "yes" costs capital |
| Write the human-readable rationale and journal entry | **LLM** | S7, S8; presentation value |

The asymmetry is the key idea: **the LLM's authority is monotone-decreasing on risk.** It can shrink or block exposure; it cannot create or enlarge it.

### RQ5 — Evaluation best practice, and how to report a 2-day window honestly

**What the literature demands.**
- **Report N, the number of trials.** S16, verbatim: a backtest that does not report N *"makes it impossible to assess the risk of overfitting."* With **5 years of data, 45 independent configurations** suffice to manufacture an IS Sharpe of 1 with true Sharpe 0; with a **2-year backtest, only 7**. Bound: **MinBTL < 2·ln[N]/E[max_N]²**.
- **Raise the significance bar.** S17: a new factor needs **t > 3.0**, and *"most claimed research findings in financial economics are likely false"* — from 316 catalogued factors.
- **Deflate the Sharpe ratio** for selection bias, sample length and non-normality — Bailey & López de Prado's Deflated Sharpe Ratio (see Paywalled/wanted; the concept is described in S16's companion work).
- **Fix execution semantics and costs explicitly.** S11's checklist: universe and inclusion rules, data provenance and access dates, point-in-time discipline, split dates, execution timing (same-close vs next-open), cost/slippage model, model versions and prompts, seeds/retry policy, artifact release.
- **Attribute returns, don't just report them.** S10: decompose into market, style and selection; otherwise you are reporting beta.
- **Benchmark against passive.** S11 and S19 both make buy-and-hold the yardstick; both find the agent does not clear it.

**What is meaningful with 2 trading days — and what is not.**

*Not meaningful:* Sharpe ratio, Sortino, alpha, win rate, max drawdown, per-agent attribution, any t-statistic, any claim of edge. With ~10–30 trades, a 55% win rate is statistically indistinguishable from 45%. S18's own 48%-on-25-trades is the cautionary example. **Say this explicitly in the write-up** — judges scoring "technology implementation" reward the team that knows this.

*Meaningful — report these instead:*
1. **Risk-gate adherence:** number of candidate trades generated, number blocked by each deterministic gate, and **zero** breaches of max-loss / net-delta / net-vega / concentration / drawdown limits. A clean gate log is a verifiable engineering claim.
2. **Ex-ante vs. ex-post agreement:** for every filled structure, predicted max loss / net delta / net vega vs. realized. This proves the quantitative core is correct, independent of whether the trades made money.
3. **Execution quality:** fill price vs. mid at decision time (slippage in bps and in dollars), per leg. Options spreads are wide; showing you measured this is a differentiator (S18 used market orders and admitted it).
4. **Decision latency and cost:** wall-clock and token cost per decision (S6 needed ~11 LLM + 20+ tool calls per prediction; being cheaper is a real engineering result).
5. **Veto rate and veto quality:** how often the LLM critic blocked a code-generated candidate, with the reason; and a post-hoc look at whether vetoed candidates would have lost money. Small n, but it is *process* evidence.
6. **Leakage self-audit:** run a subset of decisions with entity names masked (S2, S10) and report whether the decision changes. If it does not, you have direct evidence your agent is reasoning rather than recalling — **no other team will show this.**
7. **Determinism check:** re-run the same market snapshot k times at fixed temperature and report the dispersion of decisions (addresses C13, which the literature has barely measured).
8. **Benchmarks, stated but not over-claimed:** SPY buy-and-hold over the identical window, and — because our strategies are option-based — the **Cboe S&P 500 PutWrite (PUT)** and **Condor (CNDR)** indices as the honest passive comparator for premium-selling structures. Two days of index data is not evidence either; present it as context, not proof.
9. **Trial count N:** report how many strategy configurations we tried before choosing. Per S16, this is the single most-omitted number in the field, and volunteering it is cheap credibility.

**Recommended sentence for the write-up:** *"Over a 2-day window our P&L is a draw from a distribution we cannot estimate; per Bailey et al. (2014) and Harvey, Liu & Zhu (2016), no performance inference is available at this sample size. We therefore report process metrics — risk-gate adherence, ex-ante/ex-post Greeks agreement, execution slippage, veto rate and a leakage self-audit — and present P&L alongside SPY and Cboe PUT/CNDR context without claiming edge."*

### RQ6 — Practitioner / open-source landscape, and a critique of the Alpaca article

**What judges will likely know:**
- **TradingAgents** (S6) — GitHub, Tauric Research; reported **80k+ stars** `[UNVERIFIED]`. The reference multi-agent architecture. Expect judges to recognize the analyst/researcher/trader/risk-manager shape.
- **FinRL / FinGPT** (AI4Finance Foundation) — FinRL is the deep-RL framework for quantitative finance with a **live Alpaca broker integration** in its deployment layer `[UNVERIFIED: ~15k+ stars]`; FinGPT is the open financial-LLM/fine-tuning project. Both are widely known and **both are complements, not competitors**, to our design: FinRL is RL over price series, FinGPT is a fine-tuned text model. Neither does options with Greeks validation.
- **AI Hedge Fund** — popular proof-of-concept, reported **45.3k stars** as of Jan 2026 `[UNVERIFIED]`.
- **FinRobot, QuantAgent, StockAgent, Alpha-GPT** — same family; not individually verified in this review (see Follow-up reading).
- **The Alpaca article** (S18) — the house reference; assume every judge has read it.

**Critique of the Alpaca reference design — what to keep, what to fix:**

*Keep:*
1. **Deterministic, LLM-free risk guard with explicit numeric limits** (10% position / 30% sector / 1.0x leverage / 5%-10%-15% drawdown halts). This is the single best decision in the article and matches every recommendation in this review.
2. **Structured proposal schema** with mandatory fields — it is what makes downstream validation possible; S12 shows the logical endpoint (a typed IR).
3. **Regime screener ahead of the agents**, and the **macro-alignment tag** (their own data: **+1.62% aligned vs +0.21% against**).
4. **OCO bracket exits** — pre-committed exits are the right answer for an autonomous agent, and they remove a class of LLM discretion.
5. **Agent isolation on a shared snapshot** — prevents one agent's narrative from contaminating the others before the critic stage.
6. **Honest limitation disclosure** — they name paper-trading and cost omissions up front. Copy the tone.

*Fix:*
1. **Remove the human gate.** It contradicts the hackathon's autonomy requirement, and at **82 → 26 (32%)** it means a human made the selection. Replace with: deterministic pre-trade validator (hard, unconditional) **+** an LLM critic with **veto-only** authority (can block, cannot approve into existence, cannot enlarge). Log every veto with its reason so the audit trail replaces the human.
2. **Add regime gating to every strategy, not just contrarian.** Their own post-mortem says the Contrarian agent needed it; S13 says regime conditioning is where LLMs help most. Make the regime label a **precondition** on the strategy menu.
3. **Replace market orders with limit orders at or inside the mid**, especially essential for options where spreads dominate. Their article flags this as future work.
4. **Trade options, not equities.** The hackathon mandates it; the article treats options as future work; and the literature (RQ3) is empty here.
5. **Stop attributing P&L to individual agents on tiny n.** One StatArb trade tells you nothing. Report gate adherence and decision quality instead.
6. **Add a leakage self-audit** (S2, S10) and a **determinism check** — neither appears in the article and both are cheap.
7. **Add ex-ante/ex-post Greeks reconciliation** — impossible in their equity design, natural in ours, and it is a genuine correctness proof for the quant core.

---

## Design implications

Each item: recommendation → justification → confidence.

1. **Two-layer architecture with a hard boundary: LLM proposes *categories*, code produces *numbers*.** The LLM's output schema must contain only enums, booleans, short strings and references — never a price, a quantity, a strike, a delta or a dollar amount. Everything numeric is computed by our pricing/Greeks module from market data.
   *Sources:* S12 (semantic accuracy 0.698; Risk@90 46.1%→18.6% with a typed IR), S14 (verbalized confidence is inflated by RLHF), S15 (risk preferences are alignment artifacts). **Confidence: high.**

2. **Typed strategy menu with fixed leg roles.** Define a small closed set — e.g. `CASH_SECURED_PUT`, `PUT_CREDIT_SPREAD`, `CALL_CREDIT_SPREAD`, `IRON_CONDOR`, `CALENDAR`, `LONG_STRADDLE`, `PROTECTIVE_PUT`, `NO_TRADE` — each with a fixed role schema. The LLM chooses one and fills constrained slots (underlying from a fixed universe, direction bias, horizon bucket). Code resolves strikes/expiries by deterministic rules (target delta, DTE band, IV-rank thresholds, min open interest, max bid-ask width).
   *Sources:* S12 (role-based abstraction, scoped filtering). **Confidence: high.**

3. **LLM owns the regime label; the regime label gates the menu.** A single categorical output (e.g. `VOL_REGIME ∈ {low, normal, elevated, stressed}` × `TREND ∈ {up, chop, down}`) computed from VIX level and term structure, realized vs. implied vol, and macro/news text. Code maps regime → allowed strategy families (short premium only in elevated-and-mean-reverting; long premium or no-trade in stressed).
   *Sources:* S13 (~27% high-vol MAE improvement from regime conditioning; but low-regime trade-off ⇒ use as a gate, not a continuous input), S18 (macro-aligned +1.62% vs +0.21%; contrarian failed for lack of gating). **Confidence: medium-high.**

4. **LLM owns the event-risk filter; the calendar has the final word.** The LLM reads news and flags binary events in the horizon; a deterministic earnings/FOMC/CPI calendar check is the actual gate. No short-premium position may straddle an unflagged binary event.
   *Sources:* S18 (Exotic agent: earnings binaries), S1 (LLM edge concentrates in news-driven categories: insider transactions +25.2 bps, earnings +316 bps for the larger Llama model). **Confidence: medium-high.**

5. **Anonymize entities in every text prompt.** Strip ticker and company name from headlines before the LLM scores them; pass identity separately as structured metadata that the LLM cannot use for recall.
   *Sources:* S2 (anonymized headlines outperform; distraction dominates look-ahead; worst for large caps), S10 (masking materially changes agent behavior). **Confidence: medium-high.** Cheap to implement; visibly literature-informed.

6. **Deterministic pre-trade validator with unconditional hard gates, executed on every candidate, no LLM in the path.** At minimum: max loss per position (defined-risk structures only); portfolio net delta / net vega / net theta bands; per-underlying and per-sector concentration; buying-power and margin check; max bid-ask width and min open interest; daily/total drawdown halt. A failed gate is a rejection, never a warning.
   *Sources:* S18 (their guard is the design's best feature), S16 (overfitting plus over-leverage is what is "very damaging"), S12 (deterministic Greeks/max-loss validation). **Confidence: high.**

7. **LLM critic has veto-only authority — monotone-decreasing on risk.** It reviews the fully-specified, already-validated candidate and may `BLOCK` or `REDUCE`, never `APPROVE_LARGER` or override a gate. Every veto is logged with a reason string. This replaces the Alpaca human gate while preserving its function.
   *Sources:* S6 (Bull/Bear debate), S8 (risk-triggered self-critique, selective belief propagation), S18 (critic agent + human gate), S14/S15 (asymmetric trust is warranted because LLM confidence and risk appetite are unreliable in the permissive direction). **Confidence: medium-high** on value, **high** on safety.

8. **Position sizing is a pure function of measured quantities.** `size = f(account_equity, risk_budget_per_trade, structure_max_loss, current_portfolio_greeks, regime_label)` — no LLM input, no `confidence` multiplier.
   *Sources:* S14 (RLHF-inflated confidence), S15 (risk preferences prompt-resistant and model-specific — including the risk of being *too timid* to trade at all in a 2-day window). **Confidence: high.**

9. **Memory as a structured trade journal, in three tiers.** Short-term (today's regime, open positions, fills, gate rejections), mid-term (this session's realized vs. expected Greeks and slippage), long-term (durable lessons, written only on a closed trade or a gate breach). Lessons are **routed to the specific role** that needs them, not broadcast.
   *Sources:* S7 (layered memory, decay, cognitive span), S8 (CVRF, selective propagation to the node needing the update). **Confidence: medium** on P&L effect, **high** on demo/presentation value — a visible day-1→day-2 belief update is exactly what "autonomous" looks like to a judge.

10. **Two-tier model routing.** A strong reasoning model for regime classification and the critic; a cheap fast model for retrieval, summarization and journal writing. Report tokens and latency per decision.
    *Sources:* S6 (`o1-preview` + `gpt-4o-mini`; ~11 LLM + 20+ tool calls per prediction — a cost baseline to beat). **Confidence: medium-high.**

11. **Low turnover by construction.** Multi-day option structures, not intraday rebalancing. S1's cost curve is the reason: at ~190% daily turnover the equity news signal dies at 20 bps, and option round-trips cost far more than 20 bps. Prefer defined-risk structures held to a bracket exit over frequent adjustment.
    *Sources:* S1 (25% partial rebalancing beats 100% after costs: SR 1.34 vs 1.29), S11 (26.5% erosion at 25 bps). **Confidence: high.**

12. **Bracket every entry; pre-commit the exit.** OCO with take-profit and stop-loss set at entry from deterministic rules, so no LLM discretion is needed to close. Use limit orders at/inside mid on entry.
    *Sources:* S18 (OCO brackets kept; market orders identified as the weak point). **Confidence: high.**

13. **Instrument for the honest evaluation from the first commit.** Log, per decision: timestamp, snapshot hash, regime label, candidate structure, every gate result, veto decisions + reasons, ex-ante Greeks and max loss, order and fill prices vs. mid, ex-post Greeks, tokens, latency. This log *is* the report.
    *Sources:* S11 (minimum reporting checklist), S16 (report N), S10 (attribute returns). **Confidence: high.**

14. **Run two cheap experiments during the live window that nobody else will run.** (a) **Leakage self-audit** — re-run a sample of decisions with the underlying masked; report whether the decision changes. (b) **Determinism check** — re-run one snapshot k times; report decision dispersion.
    *Sources:* S2, S9, S10 (leakage); S19 `[UNVERIFIED]` and the gap noted in S11 (non-determinism). **Confidence: medium** on what we will find, **high** on presentation value.

15. **Report P&L with explicit statistical humility and passive benchmarks.** SPY buy-and-hold over the identical window; Cboe **PUT** and **CNDR** indices as the option-strategy comparator; state the number of trades and the number of configurations tried (N).
    *Sources:* S16, S17 (no inference at this n), S11, S19 (buy-and-hold is the yardstick), S10 (separate beta from selection). **Confidence: high.**

### How we go beyond the Alpaca reference article

1. **Genuinely autonomous** — the human APPROVE/REJECT/REVISE gate is replaced by a deterministic validator plus an LLM veto with logged reasons. (S18's 32% approval rate shows the human was the decision-maker.)
2. **Options-first with real Greeks** — the article's own "next iteration"; ours is the product, with BSM/market Greeks computed in code and reconciled ex-post. Literature here is essentially empty (RQ3).
3. **Typed strategy IR instead of free-form proposals** — S12's evidence that this cuts Risk@90 from 46.1% to 18.6%; the article's schema is structured but untyped and unvalidated.
4. **Regime gating applied to every strategy**, not learned from live losses — their own lesson, implemented up front, backed by S13.
5. **Entity anonymization in text scoring** — S2/S10; absent from the article and from every framework we reviewed.
6. **Leakage self-audit and determinism check as live deliverables** — no team and no framework in this review does this.
7. **Limit orders at/inside mid, with measured slippage vs. mid** — the article uses market orders and says so.
8. **Evaluation reported per S11's checklist with N disclosed per S16**, and P&L benchmarked against SPY and Cboe PUT/CNDR — instead of a win rate on 25 trades.

---

## Follow-up reading

| Source | Tag | Why |
|---|---|---|
| Bailey & López de Prado, "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality", *Journal of Portfolio Management* 40(5), 2014 (SSRN 2460551) | cited in S16 | The exact DSR formula, if we want to deflate any backtest number we quote. |
| Bailey, Borwein, López de Prado & Zhu, "The Probability of Backtest Overfitting" (SSRN 2326253) | cited in S16 | PBO via combinatorially symmetric cross-validation — the practical companion to MinBTL. |
| Sarkar & Vafa, "Lookback for Lookahead" (2024) | cited in S1, footnote 4 | S1 cites it as the key evidence that one must sample after the knowledge cutoff. I did not locate it directly; worth reading for the formal argument. |
| Lopez-Lira, Tang & Zhu (2025) | cited in S1, footnote 4 | Second reference S1 gives for memorization/lookahead; likely the strongest current treatment. |
| "Look-Ahead-Bench: a Standardized Benchmark of Look-ahead Bias in Point-in-Time LLMs for Finance", arXiv:2601.13770 | new idea | A standardized leakage benchmark — would let us state our leakage posture in a comparable way. |
| "Detecting Lookahead Bias in LLM Forecasts", arXiv:2512.23847 | new idea | Detection method rather than prevention; useful for the self-audit in Design Implication 14. |
| Kim, Muhn & Nikolaev, "Bloated Disclosures: Can ChatGPT Help Investors Process Information?" | cited in S4 | The second withdrawn paper; read the withdrawal record, not the results. |
| FinAgent (Zhang et al., 2024), FinRobot, QuantAgent, StockAgent, Alpha-GPT | new idea | Not individually verified here. If a judge names one, we want a one-line architectural summary. Expect the same evaluation flaws as S6. |
| "Toward Expert Investment Teams: A Multi-Agent LLM System with Fine-Grained Trading Tasks", arXiv:2602.23330 | new idea | 2026 iteration of the multi-agent pattern; check whether it fixed the evaluation problems. |
| "Large Language Model Agents for Investment Management: Foundations, Benchmarks, and Research Frontiers", ACM ICAIF 2026 (10.1145/3768292.3770387) | new idea | ICAIF is the right venue for a credible survey; would consolidate RQ2 in one citation. |
| "Integrating Large Language Models in Financial Investments and Market Analysis: A Survey", arXiv:2507.01990 | new idea | Broad survey; useful for a single "the field looks like this" citation. |
| "Can Large Language Models Capture Human Risk Preferences? A Cross-Cultural Study", arXiv:2506.23107; "Risk Profiling and Modulation for LLMs", arXiv:2509.23058 | new idea | Would let us state the *direction* of LLM risk bias, not just its heterogeneity (currently `[UNVERIFIED]` in C12). |
| "StockGPT: A GenAI Model for Stock Prediction and Trading", arXiv:2404.05101 (Dat Mai) | new idea | A price-series generative model rather than a text model — a different, possibly cleaner baseline. |
| FinRL / FinRL-X (AI4Finance), "FinRL-X" @ DMO-FinTech Workshop, PAKDD 2026 | new idea | FinRL ships a live Alpaca broker integration; worth knowing what its deployment layer does before a judge asks. |
| Cboe PUT and CNDR index methodology documents | new idea | Needed to benchmark option-selling P&L honestly (Design Implication 15). |

---

## Paywalled / wanted

| Source | Identifier | What we need |
|---|---|---|
| Chen, Kelly & Xiu, "Expected Returns and Large Language Models" | SSRN **4416687** — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4416687 | The actual Sharpe ratios **before and after transaction costs**, the look-ahead-bias test, and the large-vs-small-cap split. SSRN blocked; the Jacobs Levy PDF (https://jacobslevycenter.wharton.upenn.edu/wp-content/uploads/2024/09/Kelly-WhartonJL.pdf) downloaded but its PDF stream was not text-extractable. **Do not quote numbers from S3 until this is fetched.** |
| "Reproducibility in the TradingAgents Framework" | DOI **10.1145/3800973.3801029**, Proc. 2026 Int. Conf. on AI and Fintech | Verify the reproduction numbers (Qwen3:30B 18.1%±2.8%, GPT-4o 15.8%±4.2%, GOOG B&H 19.1%, May–Jul 2025). ACM returned HTTP 403 to WebFetch and to curl with a Chrome UA. This is our strongest rebuttal to S6 — worth university access. |
| Glasserman & Lin (published version) | *Journal of Financial Data Science* 6(1), 25 (2024) — https://www.pm-research.com/content/iijjfds/6/1/25 | The exact Sharpe/return deltas for original vs. anonymized headlines. The arXiv preprint (2309.17322) is open and sufficient for the qualitative claim. |
| Bailey & López de Prado, "The Deflated Sharpe Ratio" | SSRN **2460551**; *J. Portfolio Management* 40(5), 2014 | The DSR formula itself, if we want to deflate any number. |
| Kim, Muhn & Nikolaev v1/v2 | arXiv:2407.17866v1 (still listed) | Only if we want the original numbers to describe *what was withdrawn*. Handle with care; do not present as findings. |
| FinCon venue confirmation | arXiv:2407.06567 | Confirm the NeurIPS 2024 acceptance (OpenReview) before describing it as peer-reviewed. |
| Semantic Scholar citation counts | api.semanticscholar.org | **All citation counts in this report are unverified** — the API returned HTTP 429 on every attempt from this network. An API key would fix this in one batch call. |

---

## Method log

**Searched (WebSearch):**
- Lopez-Lira & Tang Sharpe / transaction costs; Glasserman & Lin look-ahead + anonymization
- Kim/Muhn/Nikolaev withdrawal and replication failure
- Chen/Kelly/Xiu expected returns and LLMs
- LLM agent options trading / implied volatility / derivatives (2025–2026)
- Critical evaluation and reproducibility of LLM trading agents; "no better than buy and hold"
- LLM risk aversion / experimental economics / lottery-choice elicitation
- LLM overconfidence, miscalibration, RLHF, verbalized confidence
- LLM volatility forecasting, VIX regime classification
- Alpaca "Building a Multi-Agent AI Trading System" (Panteleev)
- FinGPT / FinRL / TradingAgents open-source landscape
- Bailey/López de Prado deflated Sharpe, MinBTL, Harvey/Liu/Zhu t > 3.0

**Fetched and read (WebFetch or curl + pdftotext):**
- arXiv abs: 2304.07619, 2309.17322, 2407.17866 (withdrawal verified verbatim), 2412.20138, 2311.13743, 2407.06567, 2502.21206, 2510.07920, 2605.28359, 2410.09724, 2406.01168
- arXiv HTML full text: 2412.20138v7 (experiments/results tables), 2606.08285, 2603.16434, 2603.10299
- Full PDFs downloaded and text-extracted locally: **2304.07619v6** (Lopez-Lira, cost-sensitivity and model-ladder sections read verbatim), **Notices of the AMS 61(5) 458–471** (Bailey et al., MinBTL passages read verbatim), **Harvey/Liu/Zhu RFS 2016** (abstract and t-statistic passages read verbatim)
- Nikolaev's Chicago Booth faculty page (withdrawal statements for both papers)
- Alpaca Learn blog (Panteleev) — full architecture and all performance numbers
- arXiv Atom API (batch, 11 IDs) for verified author lists, dates, journal refs and comment fields

**Could not verify / blocked:**
- **Semantic Scholar Graph API: HTTP 429 on every call**, including a slow background retry loop with 12s backoff and direct paper-ID lookups. **No citation count in this report is verified.**
- **ACM Digital Library: HTTP 403** (WebFetch and curl with Chrome UA) — S19's numbers are from a search-result summary only.
- **SSRN: blocked**; **alphaarchitect.com: Cloudflare challenge** (returned a "Just a moment..." interstitial to curl).
- **Chen/Kelly/Xiu numbers:** the Jacobs Levy PDF downloaded (1.9 MB) but its content stream was not extractable by the fetch tool.
- **Sarkar & Vafa "Lookback for Lookahead":** not fetched directly; known only as a citation inside S1.
- **FinMem / FinCon performance tables:** abstract pages only; tickers, periods and Sharpe numbers not extracted.
- **FinAgent, FinRobot, QuantAgent, StockAgent, Alpha-GPT:** not individually verified (time-boxed out; listed in Follow-up reading).
- GitHub star counts (TradingAgents 80k+, FinRL 15k+, AI Hedge Fund 45.3k) are from a secondary blog and are `[UNVERIFIED]`.

**Scope:** 18 sources carded (plus 1 inaccessible), 4 peer-reviewed (Glasserman & Lin JFDS 2024; Bailey et al. AMS Notices 2014; Harvey/Liu/Zhu RFS 2016; Asaad et al. ICLR 2026 workshop), 1 withdrawn, 1 industry blog, the rest arXiv working papers. Approximate tokens read: **~95k**. Elapsed: roughly one hour, within the time box.

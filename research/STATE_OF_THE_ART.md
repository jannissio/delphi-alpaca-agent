# Stand der Wissenschaft und Technik: Autonomer Options-Trading-Agent für den Alpaca-Hackathon

Synthese der Recherche-Berichte A bis E (Ordner `research/`). Stand: 2026-09-02, früher Morgen, alle fünf Berichte eingearbeitet. Autor: Claude (Fable 5.1) auf Basis von Opus-5-Recherche-Agenten. Jede Aussage trägt Quellen und ein Vertrauensniveau. Quellenkürzel wie `A-S5` verweisen auf Quellenkarte S5 in Bericht A.

**Lesehinweis zur Zeit:** Das Bewertungsfenster umfasst effektiv 2,5 US-Handelssitzungen: Mittwoch 2.9. und Donnerstag 3.9. voll, Freitag 4.9. von 15:30 bis 17:00 MESZ. Deadline 4.9. 17:00 MESZ.

---

## 1. Kurzfassung

1. **Es gibt in 2,5 Handelstagen keine statistisch realisierbare Options-Alpha-Erwartung.** Die Volatilitätsrisikoprämie ist real und robust, aber klein pro Zeiteinheit: rund 2 bis 3 Prozent pro Jahr, also etwa 25 US-Dollar auf 100.000 in unserem Fenster. Nach Transaktionskosten liegt der Erwartungswert kurzlaufender Prämienverkäufe bei etwa null. Der realisierte P&L ist zu praktisch 100 Prozent Rauschen, t-Wert etwa 0,16. (Vertrauen: hoch. A-S2, A-S3, A-S5, A-S6, A-S8)
2. **Deine Intuition "langfristig konservativ" ist als Anlagephilosophie richtig und für diese Aufgabe unanwendbar.** Langlaufende, "konservative" Optionspositionen liefern in 2,5 Tagen kein Theta, sondern reines Aktien-Beta mit negativer Schiefe. Konservativ heißt hier: Maximalverlust pro Position hart begrenzen, kleine Positionen, keine ungedeckten Short-Optionen. (Vertrauen: hoch. A-S8, A-S10, A-S11)
3. **Die einzige Struktur mit sichtbarem Zeitwertverfall im Fenster ist 0 bis 2 Tage Restlaufzeit auf Index-ETFs.** Ein 0DTE-Straddle verliert rund 0,76 Prozent des Spot pro Tag, ein 30-DTE-Straddle 0,07 Prozent, Faktor 11. (Vertrauen: hoch, Arithmetik. A-Q5)
4. **Definiertes Risiko schlägt undefiniertes Risiko eindeutig.** Der Cboe-Iron-Condor-Index hatte 2006 bis 2019 einen maximalen Drawdown von 13,7 Prozent gegenüber 32,7 Prozent für den PutWrite-Index und 51 Prozent für den S&P 500. Volmageddon am 5.2.2018 vernichtete Short-Vol-Produkte an einem Nachmittag. Ein 2,5-Tage-Fenster ist nicht zu kurz dafür. (Vertrauen: hoch. A-S10, A-S11)
5. **Die Ausführung entscheidet über Gewinn oder Verlust, nicht die Strategie.** Effektive Spreads bei 0DTE-SPX liegen bei 5 bis 12 Prozent des Mittelkurses pro Bein. 60 Prozent der Verluste von Privatanlegern in 0DTE sind Transaktionskosten. Geduldige Limit-Orders vermeiden rund 84 Prozent des quotierten Spreads. (Vertrauen: hoch. A-S5, A-S14)
6. **LLMs können Text lesen, aber keine Zahlen verantworten.** Der Nachrichten-Signal-Effekt ist real, stirbt aber bei 20 Basispunkten Kosten. Das prominenteste "LLM schlägt Analysten"-Paper wurde von den Autoren zurückgezogen. LLM-Agenten handeln anders, sobald man Ticker anonymisiert; ihre Renditen erklären sich durch Markt-Exposure. LLMs sind strukturell überkonfident und ihre Risikoneigung ist ein Alignment-Artefakt, das sich nicht wegprompten lässt. (Vertrauen: hoch bis mittel-hoch. B-S1, B-S4, B-S10, B-S14, B-S15)
7. **Daraus folgt die Arbeitsteilung:** Das LLM liefert nur Kategorien: Regime-Label, Event-Flag, Strategiefamilie aus einem festen Menü, Veto mit Begründung, Erklärtext. Deterministischer Code liefert alle Zahlen: Preise, Greeks, Strikes, Positionsgröße, Orders, harte Risk Gates. Die Autorität des LLM ist monoton fallend im Risiko: Es darf blockieren und verkleinern, nie vergrößern. (Vertrauen: hoch. B-S12, B-S14, B-S15)
8. **Zu LLM-Agenten, die Optionen handeln, ist die Literatur praktisch leer.** Ein einziges direkt einschlägiges Paper von März 2026 macht genau unser Design, LLM als semantischer Parser plus deterministische Greeks-Validierung, und misst nur 69,8 Prozent semantische Genauigkeit für das beste Modell. Das ist unser belastbarer Originalitätsanspruch. (Vertrauen: mittel-hoch. B-S12, B-RQ3)
9. **Die Bewertung muss ehrlich sein.** Mit einer Handvoll Trades sind Sharpe, Trefferquote und Alpha bedeutungslos; die Literatur fordert für publizierte Faktoren t größer 3. Wir berichten Prozessmetriken: Gate-Adhärenz, Ex-ante- gegen Ex-post-Greeks, Slippage gegenüber Mid, Veto-Rate, Leakage-Selbsttest, Determinismus-Check, plus P&L mit Benchmarks SPY, Cboe PUT und CNDR ohne Alpha-Anspruch. (Vertrauen: hoch. B-S11, B-S16, B-S17)
10. **Korrektur zu Bericht A:** Der Earnings-Kalender im Fenster ist nicht leer. Broadcom meldet Mittwoch nach Börsenschluss, bestätigt über die Investor-Relations-Seite, dazu Snowflake, HPE, am Donnerstag Zscaler, Lululemon, DocuSign, Samsara, Ciena vorbörslich. Berichte D und E zusammen: Wir handeln keine Einzeltitel-Earnings, in keine Richtung. Broadcom übertraf die implizite Bewegung in 10 von 16 Berichten; die Gewinnerseite ist ein Querschnittsmittel, kein Ein-Namen-Trade. Das Event-Gate blockt sichtbar. (Vertrauen: hoch. D-S16, E-D8)
11. **Kalendereffekte im Fenster sind tot oder zu klein.** Turn-of-the-Month-Tage +2 und +3, Vor-Labor-Day, Overnight-Prämie, Intraday-Momentum, Short-Term-Reversal: alle zusammen rund 0,2 bis 0,3 Prozent Drift gegen 1,4 Prozent Rauschen. Kein Richtungs-Tilt. Der einzige belastbare Edge ist die Gegenseite des Retail-Verhaltens: Retail kauft kurzlaufende Optionen 7:1 und verliert; die Call-Seite ist bei kurzer Laufzeit die reichere. Deshalb deltaneutral mit call-lastiger Asymmetrie. (Vertrauen: hoch für "kein Tilt", mittel für die Asymmetrie. E)
12. **Der Arbeitsmarktbericht am Freitag 08:30 ET ist der dominante Risikofaktor**, über den BLS-Kalender verifiziert. Keine Short-Optionen von Donnerstag in Freitag halten; Freitag ist Berichtstag. (Vertrauen: sehr hoch. D, E)

---

## 2. Was die Aufgabe wirklich bewertet

Vier Kriterien ohne veröffentlichte Gewichtung: P&L, Technology Implementation, Creativity & Originality, Presentation & Execution. Drei von vier sind nicht P&L. Da der P&L in 2,5 Tagen Rauschen ist, wird der erwartete Score maximiert durch ein kleines, verlustbegrenztes, vollständig begründetes Buch plus exzellente Technik und Präsentation. Ein großer negativer Ausreißer schadet mehr, als ein großer positiver nützt, weil er die Risk-Gate-Story zerstört. (A-Design 1, A-Q5)

Was die Jury vermutlich kennt: Alpacas Referenzartikel (Panteleev, Mai 2026) mit fünf LLM-Analysten, Kritiker-Agent, menschlichem Freigabe-Gate mit 32 Prozent Approval und deterministischem Risk Guard. Sein Human Gate widerspricht der Autonomie-Anforderung, seine 25 Trades sind statistisch ein Münzwurf, Market-Orders sind seine schwächste Stelle, Optionen nennt er als Zukunft. Genau dort setzen wir an. (B-S18)

---

## 3. Evidenz zu Optionsstrategien (Bericht A)

### 3.1 Gesicherte Befunde

| Nr. | Befund | Quellen | Vertrauen |
|---|---|---|---|
| K1 | Implizite Varianz übersteigt realisierte Varianz systematisch bei Indexoptionen | Carr/Wu 2009 RFS; Bakshi/Kapadia 2003 RFS; Coval/Shumway 2001 JF; VIX über realisierter Vol in 20 von 21 Jahren | hoch |
| K2 | Die Prämie ist ein Index-Phänomen, bei Einzeltiteln schwach oder abwesend | Carr/Wu 2009; Bollen/Whaley 2004 JF; Gao/Xing/Zhang 2018 JFQA | hoch |
| K3 | Die Prämie ist klein pro Zeit: rund 11 Prozent der ATM-Prämie, 2,05 bis 2,76 Prozent p. a. | Bakshi/Kapadia 2003; Israelov/Nielsen 2014 FAJ | hoch |
| K4 | 0DTE-Prämie existiert, wird aber von Kosten weitgehend aufgezehrt; naives Schreiben delta-gehedgter ATM-0DTE-Calls: Sharpe pro Trade minus 0,042 bis minus 0,010 nach Kosten | Almeida/Freire/Hizmeri 2025 WP; Beckmeyer/Branger/Gayda 2023 WP | mittel-hoch |
| K5 | 0DTE-Iron-Condors von Privatanlegern: Median plus 5,5 Prozent der Margin, Mittelwert minus 1,1 Prozent, P25 minus 24, P5 minus 100 | Beckmeyer/Branger/Gayda 2023 | mittel-hoch |
| K6 | Credit-Strukturen schlagen Debit-Strukturen; Multi-Leg schlägt Single-Leg | Beckmeyer/Branger/Gayda 2023 | mittel-hoch |
| K7 | Definiertes Risiko senkt den maximalen Drawdown um rund 60 Prozent | Cboe Fact Sheet 2020; Augustin/Cheng/Van den Bergen 2021 FAJ | hoch |
| K8 | Covered Calls und Cash-Secured Puts sind zu zwei Dritteln Aktien-Beta, Downside-Beta 0,78 gegen Upside-Beta 0,63 | Israelov/Nielsen 2014 | hoch |
| K9 | Der Großteil des quotierten Spreads ist durch geduldige Limit-Orders vermeidbar: 1,3 statt 8,1 Cent | Muravyev/Pearson 2020 RFS | hoch |
| K10 | Standard-Deltas sind bei 0DTE fehlspezifiziert; 94 Prozent der ATM-0DTE-Optionen verletzen Preisgrenzen risikoaverser Präferenzen | Bandi/Fusari/Renò 2024; Almeida et al. 2025 | mittel-hoch |
| K11 | Bei 0DTE sitzt die Prämie auf der Call-Seite, nicht auf der Put-Seite | Almeida et al. 2025, eine Quelle; Bakshi/Kapadia fanden bei 14 bis 60 DTE das Gegenteil | niedrig-mittel |
| K12 | Ob 0DTE-Volumen die Volatilität erhöht oder dämpft, ist offen | Dim/Eraker/Vilkov 2024 und Adams/Fontaine/Ornthanalai 2024 gegen Brogaard/Han/Won 2023 | niedrig |

### 3.2 Die Horizont-Arithmetik

ATM-Straddle-Wert näherungsweise 0,8 mal Sigma mal Spot mal Wurzel aus T. Bei 15 Prozent Vol:

| Struktur | Straddle-Wert in Prozent des Spot | Tageszerfall |
|---|---|---|
| 0DTE | 0,76 | 0,76 |
| 7 DTE | 2,00 | 0,15 |
| 30 DTE | 4,14 | 0,07 |
| 45 DTE | 5,07 | 0,056 |

Theta ist aber kein Edge. Der Verkäufer sammelt 0,76 Prozent und zahlt die realisierte Bewegung. Der Edge ist nur der VRP-Anteil, rund 11 Prozent der Prämie, also etwa 0,08 Prozent des Spot pro Tag gegen eine Tages-Standardabweichung von rund 0,76 Prozent. Theoretische Tages-Sharpe rund 0,1, gemessen nach Kosten negativ. (A-Q5)

### 3.3 Strategie-Kandidaten mit erwarteter Verteilung je 100.000 US-Dollar

Basis: die kosteninklusive Verteilung aus Beckmeyer et al., 2,5 unabhängige Sitzungen, Risikobudget 3 Prozent des Kapitals pro Sitzung.

| Rang | Strategie | Median 2,5 Tage | Erwartungswert | 5-Prozent-Tail | Vertrauen |
|---|---|---|---|---|---|
| 1 | 0 bis 2 DTE SPY/QQQ Credit Spreads oder asymmetrische Condors, Short-Strikes 10 bis 16 Delta, Wings gekauft | +400 bis +600 | etwa 0 | −3.000 bis −4.500 | mittel-hoch |
| 2 | 1 bis 7 DTE einseitige Index-Credit-Spreads | +230 bis +400 | etwa 0 | −3.000 bis −4.000 | mittel |
| 3 | Long-Gamma-Tail-Sleeve als Overlay, Put-Debit-Spread weit OTM | −150 bis −300 | leicht negativ | +1.000 bis +2.500 im Crash | mittel |
| 4 | Earnings-Long-Straddle, höchstens 0,5 Prozent Kapital | etwa 0 | leicht negativ netto | −500 | niedrig |
| 5 | Covered Calls oder CSPs als "Income" | ±400, reines Beta | Aktiendrift | −900 | hoch, dass es keine Optionsstrategie ist |

Risk of Ruin: Mit ausschließlich definiertem Risiko ist der absolute Boden bei 3 Prozent pro Tag über drei Sitzungen minus 9 Prozent. Mit ungedeckten Strangles wäre ein Ereignis wie Februar 2018 ein plausibler Verlust von 30 bis 60 Prozent an einem Nachmittag. (A-Q5)

### 3.4 Ausführungsregeln mit der besten Evidenz

1. Nie Market-Orders. Limit-Orders auf das gesamte Multi-Leg-Paket.
2. Start am Paket-Mid, in höchstens drei Schritten über höchstens 90 Sekunden Richtung Bid, dann Cancel. Nicht-Fills kosten nichts.
3. Trade ablehnen, wenn die modellierte Round-Trip-Kosten mehr als 25 Prozent des Credits betragen.
4. Wenige Beine: Zwei-Bein-Vertikale kosten halb so viel Crossing-Risiko wie Vier-Bein-Condors.
5. Nur liquideste Underlyings: SPY, QQQ, IWM nur zur Diversifikation.
6. Keine Entries in den letzten 45 Minuten vor Verfall, Spreads weiten sich.
7. Alle Short-Beine vor 15:50 ET am Verfallstag schließen: SPY und QQQ sind amerikanisch und physisch geliefert, Zuweisung macht aus einem Spread eine Übernacht-Aktienposition.
8. Keine High-IV-Kontrakte jagen: Privatanleger verlieren dort am meisten, delta-gehedgte Underperformance ist bei hoher Vol größer.

Paper-Trading-Realismus: Alpaca füllt nur marktfähige Orders am NBBO, mit 10 Prozent Zufalls-Teilfüllungen. Eine Mid-Limit-Order füllt im Paper womöglich nie, während echte Complex-Order-Books Pakete zwischen Bid und Ask füllen. Der kostenlose "indicative" Options-Feed kann stale oder breiter als das echte NBBO sein. Ehrliche Kostenannahme: etwa der halbe quotierte Spread pro Bein, was bei einem 4-Bein-0DTE-SPY-Condor 20 bis 50 Prozent des Credits sein kann. (A-Q6)

---

## 4. Evidenz zu LLM-Agenten im Trading (Bericht B)

### 4.1 Gesicherte Befunde

| Nr. | Befund | Quellen | Vertrauen |
|---|---|---|---|
| L1 | LLMs extrahieren aus Nachrichten renditeprädiktives Signal, out-of-sample zum Wissens-Cutoff; GPT-4-Headline-Strategie Sharpe 2,97, Effekt skaliert mit Modellgröße | Lopez-Lira/Tang 2023-25 WP; Chen/Kelly/Xiu WP (Zahlen unverifiziert); He et al. 2025 ChronoBERT | hoch |
| L2 | Das Signal überlebt realistische Kosten bei hohem Turnover nicht: 20 bp Round-Trip macht es unprofitabel bei 190 Prozent Tages-Turnover | Lopez-Lira/Tang; Yao/Zheng 2026 | hoch |
| L3 | Look-ahead-Bias ist real, aber in Text-zu-Rendite-Setups zweitrangig; der "Distraction Effect" dominiert, Anonymisierung der Firmennamen verbessert Ergebnisse | Glasserman/Lin 2024 JFDS; He et al. 2025 | mittel |
| L4 | In agentischen Setups ist Leakage groß: Ein Modell handelte bei sichtbaren Tickern und verweigerte bei anonymisierten; Renditen von LLM-Agenten sind weitgehend Markt- und Style-Exposure | Zhu et al. 2026 KTD-Fin; Li et al. 2025 "Profit Mirage" | mittel-hoch |
| L5 | Publizierte Multi-Agent-Ergebnisse sind als Performance-Evidenz unbrauchbar: TradingAgents Sharpe 8,21 auf 3 Titeln, 3 Monate, ohne Kosten | Xiao et al. 2024; Yao/Zheng 2026 Audit von 30 Studien | hoch |
| L6 | Das prominenteste "LLM schlägt Analysten"-Paper wurde von den Autoren zurückgezogen, ein zweites derselben Gruppe ebenfalls | Kim/Muhn/Nikolaev, arXiv 2407.17866 v3, Booth-Seite | hoch, verbatim geprüft |
| L7 | Typisierte Zwischenrepräsentation plus deterministische Greeks-Validierung senkt Risk@90 von 46,1 auf 18,6 Prozent; beste semantische Genauigkeit nur 0,698 | Luo et al. 2026 OQL | mittel-hoch, eine Quelle |
| L8 | RLHF erzeugt strukturell verbalisierte Überkonfidenz | Leng et al. 2024/25 | mittel-hoch |
| L9 | LLM-Risikopräferenzen sind Alignment-Artefakte, heterogen, prompt-resistent: 10 Prozent mehr Ethik-Alignment senkt Risikoappetit um 2 bis 8 Prozent | Ouyang/Yun/Zheng 2024/25, 50 LLMs | mittel |
| L10 | LLMs können Volatilitätsregime klassifizieren; Regime-Konditionierung verbessert High-Vol-Prognose um rund 27 Prozent gegenüber GJR-GARCH, mit Trade-off im Low-Vol-Regime | Asaad et al. ICLR 2026 Workshop; Alpaca-Artikel: macro-aligned +1,62 gegen +0,21 Prozent | mittel |
| L11 | Mit 2 Handelstagen tragen P&L und Sharpe keine statistische Information; 7 Trials auf 2 Jahren ergeben In-Sample-Sharpe 1 bei wahrer Sharpe 0; publizierte Faktoren brauchen t größer 3 | Bailey et al. 2014 AMS Notices; Harvey/Liu/Zhu 2016 RFS | hoch |
| L12 | Die Literatur zu LLM-Agenten, die Optionen handeln, ist praktisch leer | sechs gezielte Suchen, ein Treffer (Luo et al. 2026) | mittel-hoch |

### 4.2 Arbeitsteilung, aus der Evidenz abgeleitet

| Entscheidung | Eigentümer | Begründung |
|---|---|---|
| Nachrichten und Ereignisse lesen und extrahieren | LLM, Entitäten anonymisiert | L1, L3 |
| Volatilitäts- und Makro-Regime als kategorisches Label | LLM | L10 |
| Event-Risiko im Horizont flaggen | LLM, Kalender hat das letzte Wort | L10 |
| Strategiefamilie aus festem Menü wählen | LLM, auf Enum beschränkt | L7 |
| Pricing, Greeks, IV-Rank, Payoff, Max Loss | Code | L7, L8 |
| Positionsgröße | Code, nie ein Confidence-Multiplikator | L8, L9 |
| Strike- und Verfallswahl innerhalb der Familie | Code, Regeln nach Delta, DTE, IV | L7 |
| Harte Risk Gates | Code, kein LLM | L11, Alpaca-Guard |
| Orderaufgabe, Ordertyp, Bracket | Code | Alpaca-Lektion Market-Orders |
| Veto gegen einen Kandidaten | LLM, darf blockieren, nie erzwingen | Kritiker-Muster, asymmetrische Kosten |
| Begründungstext und Journal | LLM | Präsentationswert |

Kernidee: **Die Autorität des LLM ist monoton fallend im Risiko.**

### 4.3 Was wir vom Alpaca-Referenzartikel behalten und was wir ändern

Behalten: deterministischer, LLM-freier Risk Guard mit numerischen Limits; strukturiertes Proposal-Schema; Regime-Screener vor den Agenten; OCO-Bracket-Exits; Agenten-Isolation auf gemeinsamem Snapshot; ehrliche Limitations-Offenlegung.

Ändern: Human Gate durch deterministischen Validator plus LLM-Veto mit Log ersetzen; Regime-Gating auf jede Strategie; Limit- statt Market-Orders; Optionen statt Aktien; keine P&L-Attribution auf Einzelagenten bei winzigem n; Leakage-Selbsttest und Determinismus-Check ergänzen; Ex-ante- gegen Ex-post-Greeks-Abgleich.

---

## 5. Risikomanagement, Sizing, Hedging, Bewertung (Bericht C)

### 5.1 Gesicherte Befunde

| Nr. | Befund | Quellen | Vertrauen |
|---|---|---|---|
| R1 | Voll-Kelly ist unter Parameterunsicherheit viel zu aggressiv; doppeltes Kelly ergibt Wachstumsrate null; Fehler im Mittelwert wiegen für Log-Investoren 100:3:1 gegenüber Varianz- und Kovarianzfehlern | Ziemba/MacLean Springer-Kapitel; MacLean/Thorp/Ziemba 2010/11; Chopra/Ziemba 1993 | hoch |
| R2 | Mit der gemessenen Verteilung aus A, Mittelwert minus 1,1 Prozent der Margin, ist der Kelly-optimale Anteil exakt null. Erst bei unterstellten plus 2 Prozent Edge läge Viertel-Kelly bei 4,4 Prozent | Kelly-Theorie plus eigene Rechnung von C | hoch, bedingt auf A |
| R3 | Put-Schutz liefert pro Renditeeinheit schlechtere Drawdowns als einfach weniger Risiko: PPUT 2,5 gegen SPX 5,8 Prozent p. a.; 36,5 Prozent SPX plus 63,5 Prozent Cash liefern dieselben 2,5 Prozent; Divestment gewann 97 bis 100 Prozent der Fenster; Alpha minus 1,8 Prozent p. a., t = minus 2,0 | Israelov 2019 JAI; AQR 2019 Whitepaper, dieselbe Firma, also etwa 1,5 unabhängige Quellen | hoch |
| R4 | Unter Random Walk ist die Stopping-Prämie eines Stop-Loss immer negativ; Nutzen nur bei Momentum und nur auf monatlicher Frequenz, "no value at short-term sampling frequencies" | Kaminski/Lo 2014 JFM | mittel-hoch, Übertragung auf Short-Optionen per Analogie |
| R5 | Drawdown-Limits sollten die Positionsgröße stetig mit dem Restbudget skalieren, nicht binär abschalten: optimale Exposure proportional zum Überschuss über dem Drawdown-Boden | Grossman/Zhou 1993 Math. Finance, 403 Zitate; Einschränkung Klass/Nowicki 2005 | mittel-hoch |
| R6 | Ein einzelner realisierter Maximal-Drawdown trägt fast keine Information; Drawdown ist eine Verteilung | Goldberg/Mahmoud 2016; Bailey/López de Prado 2014 | hoch |
| R7 | Pre-Trade, automatisch, blockierend ist der regulatorische Standard; reine Überwachung versagt nachweislich | SEC Rule 15c3-5; MiFID II RTS 6 Art. 15; SEC-Verfügung Knight Capital 2013; FINRA 15-09 | sehr hoch, vier unabhängige Regulatorik-Quellen |
| R8 | Ein Limit, das nicht in den Orderpfad verdrahtet ist, ist kein Limit: Knights 2-Millionen-Limit existierte und tat nichts; 460 Millionen Verlust in 45 Minuten; Ad-hoc-Reparatur verschlimmerte es | SEC Admin. Proc. 3-15570 | hoch, festgestellter Sachverhalt |
| R9 | Mit N von 2 bis 10 Trades ist keine renditebasierte Statistik aussagekräftig; für t = 2 bei plus 2 Prozent Edge bräuchte man rund 1.058 Trades, für t = 3 rund 2.380; bei N = 10 ist das 95-Prozent-Intervall der Edge plus/minus 20 Prozent der Margin | Bailey/López de Prado 2014; Harvey/Liu/Zhu 2016; Arnott/Harvey/Markowitz 2019; eigene Power-Rechnung von C | sehr hoch |
| R10 | Amerikanische, physisch gelieferte Optionen tragen Pin- und Zuweisungsrisiko: OCC übt ab 0,01 Dollar im Geld automatisch aus; ein zugeteilter Short-Leg ohne ausgeübten Wing hinterlässt rund 65.000 Dollar SPY-Notional pro Kontrakt über Nacht | OIC/OCC-Mechanik, Primärquelle für 0,01-Schwelle noch offen | mittel-hoch |
| R11 | Es gibt keinen publizierten akademischen oder regulatorischen Standard für Greeks-Limits pro Kapitaleinheit; nur Vendor-Blogs | Suche ohne Treffer | nicht belegt, daher aus Max-Loss abgeleitet |
| R12 | Die tastytrade-Regeln "21 DTE, 50 Prozent Gewinn" sind keine zitierfähige Evidenz: nicht reproduzierbar, Interessenkonflikt, für 0 bis 2 DTE strukturell unanwendbar | Bericht C S15 | verworfen |

### 5.2 Sizing-Empfehlung: 2 Prozent pro Sitzung, 6 Prozent kumuliert

C verschärft die 3 Prozent aus A auf 2 Prozent. Begründung in einer Zeile: Von 2 auf 3 Prozent fällt der Erwartungswert von minus 0,07 auf minus 0,10 Prozent des Kapitals, während das 1-Prozent-Quantil von minus 3,29 auf minus 4,91 Prozent rutscht. Die größere Position kauft 49 Prozent mehr linken Tail für eine schlechtere Erwartung.

Drei-Sitzungen-Verteilung, exakte Enumeration auf der kalibrierten Fünf-Punkt-Verteilung aus A, Sitzungen als unabhängig angenommen, was optimistisch ist:

| Risiko pro Sitzung | Mittel | Median | P25 | P05 | P01 | Worst Case | P(mindestens ein Max-Loss-Tag) |
|---|---|---|---|---|---|---|---|
| 1 Prozent | −0,03 | +0,07 | −0,36 | −1,13 | −1,65 | −2,97 | 14,26 |
| **2 Prozent, empfohlen** | −0,07 | +0,14 | −0,72 | −2,26 | −3,29 | **−5,88** | 14,26 |
| 3 Prozent, Vorschlag A | −0,10 | +0,20 | −1,09 | −3,38 | −4,91 | −8,73 | 14,26 |
| 5 Prozent | −0,16 | +0,33 | −1,82 | −5,63 | −8,11 | −14,26 | 14,26 |
| 10 Prozent | −0,33 | +0,61 | −3,69 | −11,23 | −15,84 | −27,10 | 14,26 |

Alle Werte in Prozent des Kapitals. In Dollar bei 2 Prozent: Median plus 135, P25 minus 725, P05 minus 2.260, Worst Case minus 5.881, Best Case rund plus 1.816. Die Wahrscheinlichkeit von mindestens einem Totalverlust-Tag ist mit 14 Prozent unabhängig von der Größe; wir steuern nur, was er kostet.

Drawdown-Taper nach Grossman/Zhou: Tagesbudget gleich 2 Prozent mal Restbudget geteilt durch Gesamtbudget 6 Prozent. Ein Tag mit minus 2 Prozent reduziert Tag 2 auf 1,33 Prozent, ein weiterer auf 0,67 Prozent. Läufe von Verlusten beenden sich selbst, ohne diskontinuierlichen Halt.

### 5.3 Hedging-Verdikt: Nein, und der Grund ist zitierbar

Dein Wunsch "höheres Risiko nur mit Absicherung" wird von der Evidenz abgelehnt. Israelov 2019 zeigt, dass eine abgesicherte, größere Position von einer kleineren, unabgesicherten bei gleicher Rendite auf genau der Metrik dominiert wird, die dir wichtig ist: dem Drawdown. Der Hedge kauft kein Risikobudget zurück. Weniger Risiko ist der Hedge. Satz für das Write-up: "We treat position size, not purchased convexity, as our primary risk control, because the evidence says purchased convexity does not reliably reduce drawdowns (Israelov 2019)."

Die Long-Gamma-Sleeve von rund 0,3 Prozent des Kapitals bleibt, aber umetikettiert: als Demonstrations- und Erklärbarkeitsbaustein, der ein nicht-degeneriertes Greeks-Profil zeigt, nicht als Schutz und nicht als Rechtfertigung für mehr Short-Prämie. Ehrlich gesagt: Sie verfällt meistens wertlos, und das sagen wir.

Offene Lücke: Die Gegenposition zu Israelov, etwa Bhansali/Davis zu Tail-Hedging, wurde in der Zeit nicht gefunden; beide vorhandenen Quellen sind AQR-affiliiert.

### 5.4 Stopps: Struktur statt Reaktion

Kein preisbasierter Stop-Loss auf einzelnen Spreads. Der gekaufte Wing ist der Stop, zum Zeitpunkt null zu bekanntem Preis bezahlt; ein reaktiver Stop kreuzt den Spread zweimal genau dann, wenn die Liquidität am schlechtesten ist. Stattdessen: hartes Tages-Kill-Limit als Portfolio-Kontrolle, das neues Risiko stoppt statt in eine Spitze zu liquidieren; stetiger Drawdown-Taper; zeitbasierter Exit flat vor 15:45 ET, Freitag vor 10:50 ET, per geplantem Task mit eskalierenden Limit-Preisen, nicht per LLM-Entscheidung. Eine 50-Prozent-Gewinnmitnahme ist als reine Varianzreduktion akzeptabel, aber ohne tastytrade als Quelle.

### 5.5 Greeks-Budgets, abgeleitet statt zitiert

Für Defined-Risk-Spreads ist der Max-Loss die bindende Grenze; Greeks sind eine Monitoring-Schicht und die Basis für den Ex-ante-Ex-post-Abgleich. Abgeleitete Limits für 100.000 Dollar, als abgeleitet zu kennzeichnen: Netto-Delta höchstens 5.000 Dollar SPY-Äquivalent; Netto-Dollar-Gamma pro 1-Prozent-Bewegung höchstens 2.000 Dollar, das ist die Grenze, die die Kontraktzahl tatsächlich begrenzt; Netto-Vega höchstens 250 Dollar pro Vol-Punkt als Diagnostik; Theta ohne Limit, nur Ziel plus Abgleich.

Cash-abgerechnete Indexoptionen SPX oder XSP wären strukturell besser, da europäisch und ohne Zuweisung. Ob Alpaca sie anbietet, prüfe ich morgen früh; das Instrument wird ein Konfigurationsparameter.

### 5.6 Risk-Gate-Checkliste: 30 Gates aus der Regulatorik

Bericht C liefert eine Tabelle mit 30 Gates, jede Zeile mit Regel, Schwelle für 100.000 Dollar und Quelle, die 1:1 in Code abbildbar ist. Die sieben Prinzipien dahinter: Pre-Trade statt Post-Trade; blockieren statt alarmieren; das kontrollierte System darf seine Kontrollen nicht selbst konfigurieren, das LLM ist Aufrufer des Gates, nie Konfigurator; Ein-Schritt-Kill-Switch; Output gegen Input abgleichen; Deployment ist eine Risikokontrolle; Incident-Runbook vor dem Start schreiben. Die wichtigsten Gates: Kapital-Schwelle 2.000 Dollar pro Sitzung; kumulativer Drawdown 6.000 Dollar; nur definiertes Risiko, harte Ablehnung; Preis-Collar 5 Prozent vom Mid, Spread höchstens 15 Prozent vom Mid; höchstens 1.000 Dollar Max-Loss und 10 Kontrakte pro Order; Message-Rate 20 pro Minute; Duplikat-Schutz 60 Sekunden; Stale-Quote-Ablehnung über 5 Sekunden; Greeks-Budget; Buying-Power 1,25-fach; Entry-Fenster 09:45 bis 15:00 ET, Freitag bis 10:15; Flatten-Deadline 15:45 ET; LLM-Output-Schema strikt validiert; Kill-Switch unter 5 Sekunden; Order-Echo- und Positions-Abgleich jeden Zyklus mit Halt bei Abweichung; Git-Hash in jedem Order-Tag; Replay vor jedem Deployment; Config-Immutabilität. Diese Tabelle wird das Herz des Ein-Seiten-Write-ups.

### 5.7 Bewertungs- und Berichtsplan

Kopfzeile des Write-ups: "We do not claim a statistically detectable edge. We claim a risk process that behaved exactly as specified, and we report the evidence for that claim."

Berichtet werden nur deterministische Prozessgrößen ohne Stichprobenfehler: Gate-Trefferzähler; Max-Loss-Adhärenz pro Position; realisierter gegen erlaubter Drawdown vor der Ex-ante-Verteilung; Greeks-Abgleich; Slippage gegen Mid pro Bein; LLM-Veto-Rate mit Gründen; Determinismus-Replay; Time-to-Flat. P&L wird zerlegt in Theta, Delta, Gamma, Vega, Residuum und Kosten; ein Gewinn, der zu 90 Prozent Delta ist, wird als Glück etikettiert.

Drei Benchmarks: SPY Buy-and-Hold über identische Stunden; Cboe CNDR und PUT als Strategie-Analoga; eine Random-Entry-Monte-Carlo derselben Struktur auf historischen Daten, gegen die unser P&L als Perzentil berichtet wird. Das ist die ehrliche Glücks-Nulllinie und die verteidigungsfähigste Zahl im Bericht.

Ausdrücklich nicht berichtet: Sharpe, Trefferquote, annualisierte Rendite, Profit Factor. Protokoll nach Arnott/Harvey/Markowitz 2019: Hypothese ex ante aus A; alle Varianten gezählt und offengelegt; Fenster und Metriken vor Mittwoch fixiert; Live-Handel als einziges echtes Out-of-Sample; Kosten überall; keine Modelländerung im Lauf, sonst Offenlegung.

---

## 6. Volatilitätsdynamik, Timing und Ereigniskalender (Bericht D)

### 6.1 Gesicherte Befunde

| Nr. | Befund | Quellen | Vertrauen |
|---|---|---|---|
| V1 | Die Varianzrisikoprämie ist bei kürzeren Laufzeiten größer und bei 0DTE am größten: annualisiert 1,54 bis 2,96 Punkte bei 0DTE gegen 0,56 bei 1 DTE und 0,81 bei 22 DTE; Short-Varianz-Sharpe fällt monoton mit der Laufzeit | Almeida/Freire/Hizmeri 2025 Tabellen 1 und 2; Johnson 2017 JFQA | hoch |
| V2 | Die Steigung der VIX-Terminstruktur, nicht das Niveau, bestimmt die Profitabilität von Short-Vol; im untersten Steigungs-Quintil dreht die Prämie für 17 von 18 Varianz-Assets das Vorzeichen | Johnson 2017 JFQA, 113 Zitate; Simon/Campasano 2014 J. Derivatives | hoch |
| V3 | Die Praktiker-Regel "nur bei IV-Rank über 50 verkaufen" hat keine begutachtete Grundlage und widerspricht Johnson; 0DTE-Mispricing ist bei niedriger realisierter Varianz sogar besser ausnutzbar | Suche ohne Treffer; Almeida et al. Tabelle 7 | nicht belegt, Regel verworfen |
| V4 | Implizite Volatilität ist der beste einzelne Kurzfrist-Prädiktor realisierter Volatilität, nach oben verzerrt; die Verzerrung ist die Prämie | Poon/Granger 2003 JEL, 93 Studien; Christensen/Prabhala 1998 JFE; Bollerslev/Tauchen/Zhou 2009 RFS | mittel-hoch |
| V5 | 0DTE-Spreads sind bei Eröffnung und Schluss am weitesten und zwischen 10:00 und 14:00 ET am engsten; quotierbare Strike-Tiefe halbiert sich bis 14:00 | Almeida et al. Fig. 3 | mittel, eine Quelle |
| V6 | Die 0DTE-Prämie steigt über den Tag, aber die Streuung ebenso; risikoadjustiert ist sie über den Tag flach bei rund 0,16 bis 0,21 | Almeida et al. Tabelle 1, Rechnung von D | mittel |
| V7 | Die letzten 30 Minuten trenden in Richtung des Tagesverlaufs, getrieben von negativem Dealer-Gamma; genau die Exposure eines Short-Condors | Baltussen/Da/Lammers/Martens 2021 JFE, Out-of-Sample-R² 2,88 Prozent | hoch |
| V8 | Dealer-Gamma-Effekte auf Indexvolatilität sind real, aber klein: im Mittel dämpfend um 0,2 Punkte, maximal plus 6,4 Punkte auf 30-Minuten-Vol gegen 63,4 aus allen Ursachen | Amaya/Garcia-Ares/Pearson/Vasquez 2025, Cboe-Daten; Dim/Eraker/Vilkov; Adams et al. | mittel-hoch |
| V9 | Kein Pinning auf Indexebene einplanen; vor SPX-Verfall sogar Anti-Cross-Pinning | Golez/Jackwerth 2012 JFE; Ni/Pearson/Poteshman 2005 JFE nur Einzelaktien, 16,5 Basispunkte | mittel-hoch |
| V10 | Implizite Volatilität fällt nach planmäßigen Makro-Meldungen, realisierte bleibt erhöht; der Sprung passiert zur Meldung, nicht zur Eröffnung | Ederington/Lee 1993 JF und 1996 JFQA; Andersen/Bollerslev/Diebold/Vega 2003 AER | mittel-hoch, SPX-Größenordnungen nicht beschafft |
| V11 | Der Pre-FOMC-Drift ist seit 2015 verschwunden; ohnehin kein FOMC im Fenster | Lucca/Moench 2015 JF plus Kurov/Wolfe/Gilbert 2021 FRL, immer zusammen zitieren | belegt, irrelevant |
| V12 | Bei 0DTE ist der Smile symmetrisch, Puts und Calls gleich teuer; bei 5 bis 7 DTE sitzt die Prämie auf der Put-Seite, die Upside-Prämie wird negativ | Almeida et al. | mittel bei 0DTE, mittel-niedrig bei 5 bis 7 DTE |
| V13 | Optionsimplizierte Richtungssignale wie Skew und Put-Call-Ratio sind Querschnittssignale für Einzelaktien über Wochen bis Monate; die öffentliche Put-Call-Ratio ist die schwache Version | Xing/Zhang/Zhao 2010 JFQA; Pan/Poteshman 2006 RFS | nicht als Tilt nutzbar, deltaneutral bleiben |
| V14 | Der naive 0DTE-Edge ist seit Mai 2022 weitgehend stagniert; delta-gehedgtes Schreiben des ATM-0DTE-Calls hat netto meist negative Sharpe | Almeida et al. Abschnitt 5 | mittel |
| V15 | Earnings-Prämienverkauf auf Broadcom und Lululemon ist von den Daten nicht gedeckt: AVGO übertraf die implizite Bewegung in 10 von 16 Berichten, zuletzt implizit 8,7 gegen real minus 12,6 Prozent Schluss; LULU 6 von 8; ORATS: Short-Straddle-Verlustspanne minus 26,7 gegen Gewinnspanne plus 8,3 Prozent | earnings-watcher.com, Investing.com/Bloomberg, ORATS; alle nicht begutachtet, kleine Stichproben | mittel, richtungskonsistent |

### 6.2 Regime-Stand und Ereigniskalender im Fenster

Regime am 31.8.2026: VIX 14,92, VIX3M 17,53, Verhältnis 0,851, deutliches Contango, Tag 101 des Regimes. Das Regime-Gate steht auf "verkaufen". Das niedrige Niveau ist kein Veto, drückt aber die Prämie pro Einheit Tail-Risiko, also kleiner sizen. Der Agent liest das Verhältnis jeden Morgen live neu.

| Zeitpunkt ET / MESZ | Ereignis | Im Fenster | Konsequenz |
|---|---|---|---|
| Mi 08:15 / 14:15 | ADP-Beschäftigung | vorbörslich | Eröffnung abwarten |
| Mi 10:00 / 16:00 | Factory Orders | ja, gering | keine Verzögerung nötig |
| Mi 14:00 / 20:00 | Fed Beige Book | ja, gering bis mittel | 13:55 bis 14:15 kein neues Risiko |
| Mi nach Schluss | Broadcom, HPE, Snowflake | nein | Gap am Donnerstag; AVGO ist Top-5-Gewicht, 8,7 Prozent AVGO sind rund 20 Basispunkte SPX, mehr in QQQ |
| Do 08:30 / 14:30 | Erstanträge, Handelsbilanz | vorbörslich | mittel |
| Do 10:00 / 16:00 | ISM Services PMI | ja, höchste Relevanz im Fenster | Einstieg erst nach 10:15 |
| Do nach Schluss | Zscaler, Lululemon, DocuSign, Samsara | nein | Einzeltitel, Index-Effekt gering |
| Fr 08:30 / 14:30 | US-Arbeitsmarktbericht NFP | nein, 60 Minuten vor Fensterbeginn | dominanter Risikofaktor; Sprung liegt im Overnight-Gap |
| Mo 7.9. | Labor Day, Markt geschlossen | nach Fenster | Fed-Blackout ab Sa 5.9., Fed-Redner bis dahin möglich |

Nicht im Fenster: FOMC, Protokoll, CPI, PPI, JOLTS. FOMC ist 15. bis 16. September.

### 6.3 Timing-Regeln aus D

1. **Regime-Gate über die Terminstruktur, nicht über IV-Rank.** Verkaufen nur bei VIX/VIX3M unter 0,95; zwischen 0,95 und 1,00 halbe Größe; ab 1,00 keine neuen Short-Vol-Positionen. Vertrauen: hoch.
2. **0DTE gegenüber 1 bis 7 DTE bevorzugen**, Prämie 2- bis 4-fach reicher; Trade-off maximales Gamma offenlegen. Vertrauen: hoch.
3. **Einstieg 10:00 bis 11:00 ET primär, optional 12:30 bis 13:30**, nie 09:30 bis 10:00, aus Ausführungsgründen. Vertrauen: mittel.
4. **Flat bis 15:15 bis 15:30 ET**, nicht "wertlos verfallen lassen". Zusammen mit dem Pin-Risiko aus C ergibt sich: **flat bis 15:15 ET**. Vertrauen: hoch.
5. **Kein GEX-Einstiegssignal**; Dealer-Gamma nur als Risk-off-Overlay bei scharfem Intraday-Drawdown. Vertrauen: mittel-hoch.
6. **Keine Short-Optionen von Donnerstag Schluss in Freitag halten.** Alles mit Verfall Freitag wird innerhalb einer Sitzung eröffnet und geschlossen oder gar nicht. Vertrauen: hoch.
7. **Freitag 09:30 bis 10:00 keine neue Short-Prämie**; danach höchstens halbe Größe, besser nur managen und berichten. Da C ohnehin Flat bis 10:50 verlangt, ist Freitag faktisch ein Berichtstag mit einer geloggten NO_TRADE-Entscheidung. Vertrauen: mittel-hoch.
8. **Donnerstag Einstieg erst nach 10:15 ET**, nach ISM und Broadcom-Gap. Vertrauen: mittel-hoch.
9. **Mittwoch ist die sauberste Sitzung** und der primäre 0DTE-Tag; 13:55 bis 14:15 pausieren. Vertrauen: hoch für den Kalender.
10. **Wing-Struktur nach Laufzeit:** symmetrischer, deltaneutraler Iron Condor bei 0DTE; bei 1 bis 7 DTE Put-Credit-Spreads. Vertrauen: mittel beziehungsweise mittel-niedrig.
11. **Kein Richtungs-Tilt aus Skew oder Put-Call-Ratio**; deltaneutral bei Einstieg, Re-Zentrierung nur auf einem definierten Delta-Band. Vertrauen: hoch.
12. **Kein Pinning annehmen.** Vertrauen: mittel-hoch.
13. **Strike-Abstand am impliziten Move verankern, nicht am festen Delta:** 0DTE-ATM-Straddle-Preis als Marktschätzung der Restbewegung, Short-Strikes bei mindestens dem 1,25-fachen der impliziten Restbewegung; für die 16-Delta-Konvention gibt es keine begutachtete Grundlage. Vertrauen: mittel.
14. **IV-gegen-RV-Sanity-Check als Veto:** Liegt der implizite 0DTE-Move unter dem realisierten 5- bis 10-Tage-Intraday-Move, nicht verkaufen. Vertrauen: mittel.
15. **Earnings: keine Prämie auf AVGO, LULU, ZS, SNOW in die Meldung verkaufen.** Falls ein Earnings-Element für Kreativität gewünscht ist: definiertes Risiko, unter 0,25 Prozent des Kapitals, oder nach dem IV-Crush am Donnerstag ausdrücken. Vertrauen: mittel.
16. **Naiven Edge kleiner annehmen als Backtests suggerieren**; Spread explizit budgetieren. Vertrauen: mittel-hoch.

Auflösung eines Widerspruchs zwischen A und D: A schlägt bei 0DTE einen leichten Call-Tilt vor, D einen symmetrischen Condor; beide stützen sich auf Almeida et al. Entscheidung: Standard ist der symmetrische deltaneutrale 0DTE-Condor. Wenn die Kostenlogik aus A eine einseitige Vertikale erzwingt, ist bei 0DTE die Call-Seite mit niedrigem Vertrauen leicht bevorzugt, bei 1 bis 7 DTE die Put-Seite. Bericht E prüft, ob Richtungsmuster das ändern.

---

## 7. Kurzfristige Renditemuster, Kalendereffekte und Retail-Verhalten (Bericht E)

### 7.1 Gesicherte Befunde

| Nr. | Befund | Quellen | Vertrauen |
|---|---|---|---|
| S1 | Der Turn-of-the-Month-Effekt konzentriert sich auf Tag −1 und +1; unsere Tage Mittwoch (+2) und Donnerstag (+3) sind selbst in der Originalstichprobe einzeln nicht signifikant: +0,13 Prozent bei t = 1,84 und +0,08 Prozent bei t = 1,21, also 0,10 bis 0,16 Standardabweichungen der Tagesbewegung | McConnell/Xu 2008 FAJ; Han/Han/Tian 2024 FRL melden Verschwinden nach 2001, unverifiziert | hoch |
| S2 | Der Pre-Holiday-Effekt ist für Large Caps tot: S&P 500 1983 bis 2019 t = 0,93, DJIA t = 0,64 | Ko/Yang 2021; Chong et al. 2005; Ariel 1990 nur 1963 bis 1982 | hoch |
| S3 | Die Overnight-Prämie ist seit 2021 verschwunden: das 2- bis 3-Uhr-Fenster brachte 1998 bis 2020 3,7 Prozent p. a., seither etwa null; Overnight-Gap-Risiko ist unkompensiert | Boyarchenko/Larsen/Whelan 2026 Update; Lou/Polk/Skouras 2019 JFE | mittel-hoch |
| S4 | Intraday-Momentum ist real, repliziert, aber winzig und nur für die letzten 30 Minuten: Trefferquote 0,55, rund 2 bis 3 Basispunkte pro Tag, Mechanismus negatives Dealer-Gamma | Gao/Han/Li/Zhou 2018 JFE; Baltussen et al. 2021 JFE; Limkriangkrai et al. 2023 Replikation | hoch |
| S5 | Short-Term Reversal auf Tagesebene ist netto verschwunden | Blitz/van der Grient/Honarvar 2023; de Groot/Huij/Zhou; Cheng et al. 2017 | hoch |
| S6 | Retail kauft kurzlaufende Optionen und verliert: Kauf zu Verkauf 7:1, 97 Prozent der 0DTE-Trades starten als Kauf, 0DTE-Käufe im Mittel minus 4,6 Prozent; Verluste konzentrieren sich in Long-Positionen kurzlaufender Kontrakte; Verkäufer verdienen auch nach Kosten | Bogousslavsky/Muravyev 2025; Bryzgalova/Pavlova/Sikorskaya 2023 JF; de Silva/So/Smith 2026 Review of Finance | hoch, drei unabhängige Datensätze |
| S7 | Die Call-Seite ist bei kurzer Laufzeit die reichere Seite: dominierende Overlays sind "mostly calls, overwhelmingly short", am stärksten bei 7 Tagen und hoher ATM-IV; 69,4 Prozent des Retail-Volumens sind Calls; 0DTE-VRP ist Upside-getrieben | Constantinides/Czerwonko/Perrakis 2020 Financial Management, kosteninklusiv; Bryzgalova et al. 2023; Almeida et al. 2025; Gegenposition Bondarenko 2014 mit Daten 1987 bis 2000 und Monatslaufzeit | mittel |
| S8 | Die Varianzprämie sitzt am kurzen Ende: 1-Monats-Sharpe minus 1,3, jenseits von 3 Monaten etwa null | Dew-Becker/Giglio/Le/Rodriguez 2017 JFE; Constantinides et al. 2020 | mittel-hoch |
| S9 | Vier-Bein-Strukturen sind teuer: 0DTE Iron Condor brutto Sharpe 0,77, netto minus 0,20; Put-Ratio-Spreads brutto 1,18, netto 0,93 | Vilkov, 0DTE Trading Rules, über das GitHub-Replikationspaket des Autors | mittel, Working Paper |
| S10 | Das 0DTE-Ausführungsumfeld ist seit 2023 viel besser als die Literatur von 2020 bis 2022 suggeriert: ATM-SPXW-Spread ein Tick in 64,7 Prozent der Zeit gegen 0,5 Prozent im Juli 2020; 50 Prozent der Kunden-Limit-Orders zahlen null effektiven Spread | Fu/Li/Musto/Pearson 2025, SEC DERA, Primärquelle über sec.gov geholt | mittel-hoch |
| S11 | Der US-Arbeitsmarktbericht erscheint Freitag 4.9.2026 um 08:30 ET, über den BLS-Kalender als Primärquelle verifiziert | BLS September 2026 Release Calendar | sehr hoch |
| S12 | Post-Earnings-Drift ist ein 60-Tage-Phänomen, rückläufig, bei 0 bis 2 DTE nicht handelbar | Bernard/Thomas 1989; Chordia et al. 2014; Martineau 2019 | hoch |

Korrekturen an meinem Briefing durch E: de Silva/So/Smith heißt "...and Expected Announcement Volatility", Review of Finance 30(2) 2026; "Constantinides, Jackwerth & Savov 2020" ist tatsächlich Constantinides, Czerwonko & Perrakis 2020; "Dew-Becker, Giglio & Kelly" ist Dew-Becker, Giglio, Le & Rodriguez 2017.

### 7.2 Unser Fenster Tag für Tag

| | Mi 2.9. | Do 3.9. | Fr 4.9., 09:30 bis 11:00 ET |
|---|---|---|---|
| Kalender | TOM-Tag +2, 0,16 Sigma, niedriges Vertrauen | TOM-Tag +3, 0,10 Sigma, sehr niedrig | Vor Labor Day, etwa 0,1 Sigma, sehr niedrig |
| Makro | nichts von BLS | Produktivität revidiert, zweitrangig | NFP 08:30 ET |
| Earnings | AVGO, SNOW, HPE nach Schluss | CIEN vorbörslich; AVGO-Gap in QQQ rund 0,3 bis 0,4 Prozent bei 8 Prozent AVGO-Bewegung | keine |
| Richtungsurteil | flat, kein Tilt | flat, SPY statt QQQ | flat, kein Einstieg vor 09:45 bis 10:00 |

Summe aller Kalender-Punktschätzer über drei Tage: rund 0,2 bis 0,3 Prozent Drift gegen rund 1,4 Prozent Rauschen. Das ist kein Signal.

### 7.3 Designfolgen aus E

1. **Kein Richtungs-Tilt aus Kalender, Momentum oder Reversal.** Netto-Delta pro Sitzung etwa null. Vertrauen: hoch.
2. **Asymmetrie call-lastig, Netto-Delta bleibt null:** Short-Call näher, Short-Put weiter, so dimensioniert, dass das Netto-Delta flach ist. Drei unabhängige Quellen, eine Gegenquelle mit alten Daten. Reicht für die Strike-Platzierung, nicht für eine einseitige Call-Vertikale. Vertrauen: mittel.
3. **Bei erhöhtem VIX, oberes Terzil gegenüber 60 Tagen, Asymmetrie auf neutral oder Put-Seite zurücknehmen.** Legitime LLM-Aufgabe: Regime-Label liefern, Code setzt die Asymmetrie. Einzelquelle Vilkov, Tie-Breaker. Vertrauen: niedrig-mittel.
4. **Nur Same-Session-Positionen; kein Carry über Mittwoch Schluss.** Die Overnight-Prämie ist weg. Vertrauen: mittel-hoch.
5. **Freitag nicht vor 09:45 bis 10:00 ET einsteigen.** Mit der NO_TRADE-Entscheidung aus 8.1 ohnehin erledigt.
6. **Flat vor dem Schluss ist jetzt mechanistisch begründet**, nicht nur vorsichtig: negatives Dealer-Gamma treibt die letzten 30 Minuten. Vertrauen: hoch.
7. **Donnerstag SPY statt QQQ**, wegen des AVGO-Gaps; wenn QQQ, Strikes weiter. Vertrauen: mittel.
8. **Keine Einzeltitel-Earnings handeln.** Die Gewinnerseite ist ein Querschnittsmittel über Hunderte Meldungen; ein Name, ein Konto, ein Münzwurf mit fettem Tail. Vertrauen: hoch. Das kippt die optionale Broadcom-Straddle-Idee aus A endgültig: Sie entfällt, das Event-Gate bleibt.
9. **Geduldige Paket-Limit-Orders beibehalten**; das Vier-Bein-Kostenargument aus 2020 bis 2022 ist heute etwa doppelt zu pessimistisch, aber Condors sind nicht kostenlos und die Füllwahrscheinlichkeit ist das eigentliche Problem. Vertrauen: mittel-hoch.
10. **Wing-Kosten ehrlich benennen:** Wings senken den Tail-Verlust um rund zwei Drittel und fressen laut unverifizierten Sekundärzahlen seit 2010 den gesamten Ertrag. Für ein Überlebensmandat über drei Sitzungen trotzdem richtig. Vertrauen: niedrig-mittel bei den Zahlen.

Was Retail nachweislich falsch macht und der Agent deshalb nie tut: kurzlaufende Prämie kaufen; Prämie in ein bekanntes Vol-Event kaufen; den Spread kreuzen, Retail zahlte 6,4 Milliarden indirekte Kosten gegen 0,9 Milliarden Kommissionen; Mikrogrößen in breiten Spreads; Positionen über die These hinaus halten; auf frühe Gewinne hochskalieren, denn die Median-Trade gewinnt und sagt nichts über die Erwartung.

## 7b. Einordnung anderer ML-Ansätze: warum wir Reinforcement Learning bewusst nicht einsetzen

Kurzer eigener Prüfgang, keine Vollrecherche. Reinforcement Learning für Trading ist als Open-Source-Landschaft präsent, vor allem FinRL der AI4Finance Foundation: Liu et al., "FinRL: A Deep Reinforcement Learning Library for Automated Stock Trading in Quantitative Finance", NeurIPS 2020 Deep RL Workshop; Liu et al., "FinRL: Deep Reinforcement Learning Framework to Automate Trading in Quantitative Finance", ACM ICAIF 2021, DOI 10.1145/3490354.3494366; FinRL-Meta, NeurIPS 2021 Data-Centric AI Workshop. Qualitätsurteil: zitierfähig als Existenznachweis des Frameworks, Workshop- und Konferenzniveau, keine Performance-Evidenz. Dieselbe Gruppe räumt in Liu et al., "Deep Reinforcement Learning for Cryptocurrency Trading: Practical Approach to Address Backtest Overfitting", arXiv 2209.05559, 2022, das Backtest-Overfitting-Problem für DRL-Agenten explizit ein. Die 2024 bis 2026 erschienenen Arbeiten benennen übereinstimmend Nichtstationarität, niedriges Signal-Rausch-Verhältnis und Marktfriktionen als ungelöste Kernprobleme.

Konsequenz für uns, im Write-up in zwei Sätzen, mit Evidenz statt Kalenderargument (Fassung vom Abend des 2. September nach dem Audit und den nachgelesenen Quellen): Auf echten Optionsdaten mit identischen Kosten schlägt keiner von drei Deep-Hedging-Agenten eine klassische Regel (Kumar 2026, arXiv:2608.29025, fünf Jahre Bitcoin-Optionen auf Deribit, 11.546 Testepisoden; das regelbasierte Whalley-Wilmott-Band sparte 1,79 $ je Episode, 95-%-KI [-2,21, -1,39]); berichtete DRL-Trading-Gewinne überleben keine seed- und multiplizitätsbewusste Auswertung (Grądzki 2026, J. Finance and Data Science, DOI 10.1016/j.jfds.2026.100205, gelesen: 20 Seeds, Sharpe im Mittel 0,604 bei Standardabweichung 0,193 und Spanne 0,233 bis 0,855; "selecting the best-performing seed instead of reporting the mean inflates the reported Sharpe by 44%"; keine paarweise Algorithmus-Differenz überlebt die Holm-Korrektur, kleinstes adjustiertes p 0,085). Die Gegenzitation, Egebjerg 2026 (J. Financial Stability 84, 101535, gelesen), hedgt eine long Call-Position mit E-mini-Futures (Kosten etwa 1,06 bp im Future) und schlägt das Black-Scholes-Delta moderat (15-Minuten-Rebalancing: Standardabweichung 0,0278 % gegen 0,0410 % des Basiswerts); sie testet kein ungehedgtes Verkaufen, und ihre Beobachtung, dass 0DTE-Optionen "more fragile, with limited scope for recovery" bleiben, spricht für Flügel und Credit-Gate als einzige Kontrolle einer ungehedgten Struktur. Ein veröffentlichter RL-Iron-Condor-Agent existiert nicht (Volltextsuche arXiv, 0 Treffer; der einzige Condor-Treffer, Huang, Sun & Yang 2025, arXiv:2501.12397, ist stochastische Kontrolle unter einer beschränkten Martingal-Annahme). Das eine RL-förmige Teilproblem, das wir gern hätten, ist die Ausführungsleiter; sie braucht Millisekunden-Orderbuchdaten, die es im Basisplan nicht gibt. Wir liefern die harte Regelschicht, die Safe-RL-Systeme des Standes der Technik (Zhang, "Tail-Safe", arXiv:2510.04555) an ihre Lerner anbauen, und verzichten auf den Lerner. Hinzu kommt das Kalenderargument als zweiter Satz: 2,5 Handelstage, nichtstationäre 0DTE-Mikrostruktur seit 2022, Erwartungswert nahe null.

---

## 8. Abgeleitetes Zieldesign des Agenten

Konsolidiert aus A bis D. Jede Zeile hat ihre Quelle in den Abschnitten 3 bis 6. Bericht E kann die Richtungsfrage in 8.1 noch feinjustieren.

### 8.1 Strategie

| Element | Entscheidung | Herkunft |
|---|---|---|
| Underlying | SPY primär, QQQ sekundär zur Diversifikation, nie für Größe; Donnerstag nur SPY wegen des Broadcom-Gaps in QQQ. SPX oder XSP, falls Alpaca sie anbietet, weil europäisch und cash-settled | A K2, C R10, E D7 |
| Struktur | Deltaneutraler 0DTE Iron Condor mit call-lastiger Asymmetrie: Short-Call näher, Short-Put weiter, Netto-Delta etwa null; im oberen VIX-Terzil Asymmetrie auf neutral zurücknehmen. Fallback einseitige Vertikale, wenn der Paket-Spread über 25 Prozent des Credits liegt; dann bei 0DTE Call-Seite, bei 1 bis 7 DTE Put-Seite, beides niedriges Vertrauen | A Design 3, D R11, E D2, E D3 |
| Strikes | Abstand am impliziten Move verankert: Short-Call bei etwa dem 1,25-fachen, Short-Put bei etwa dem 1,5-fachen der impliziten Rest-Tages-Bewegung aus dem ATM-Straddle-Preis, dann Kontrakte je Seite so, dass Netto-Delta flach ist; Wings 1 bis 2 Strikes weiter, bei SPY 1 bis 2 Dollar breit; Delta nur als Cross-Check | D R14, E D2, A K10 |
| Risikobudget | 2 Prozent des Kapitals Max-Loss pro Sitzung, 6 Prozent kumuliert, stetiger Drawdown-Taper; auf 2 bis 4 Positionen verteilt; höchstens 1.000 Dollar Max-Loss und 10 Kontrakte pro Order | C 5.2 |
| Regime-Gate | VIX/VIX3M unter 0,95 voll, 0,95 bis 1,00 halb, ab 1,00 nichts Neues; IV-gegen-RV-Veto | D R1, R15 |
| Zeitfenster | Mittwoch: Einstieg 10:00 bis 11:00 ET, optional 12:30 bis 13:30, Pause 13:55 bis 14:15; Donnerstag: erst nach 10:15 ET; Freitag: keine neuen Trades, geloggte NO_TRADE-Entscheidung mit Begründung NFP, nur Berichterstattung | D R4, R8, R9, R10 |
| Exit | Flat bis 15:15 ET, Freitag bis 10:50 ET, per geplantem Task mit eskalierenden Limit-Preisen; kein preisbasierter Stop-Loss, der Wing ist der Stop; optional 50-Prozent-Gewinnmitnahme als Varianzreduktion | C 5.4, D R5 |
| Ausführung | Nur Multi-Leg-Limit-Orders am Paket-Mid, drei Schritte in 90 Sekunden Richtung Bid, dann Cancel; Trade ablehnen, wenn modellierte Round-Trip-Kosten über 25 Prozent des Credits | A 3.4 |
| Overlay | Long-Gamma-Sleeve: weit OTM Put-Debit-Spread auf SPY, 2 bis 7 DTE, Gesamtkosten höchstens 0,3 Prozent des Kapitals; etikettiert als Demonstration, nicht als Schutz | A Design 7, C 5.3 |
| Earnings | Keine Einzeltitel-Earnings handeln, weder Prämie verkaufen noch Straddles kaufen; das Event-Gate blockt Broadcom, Lululemon, Zscaler, Snowflake sichtbar und loggt die Begründung. Die Straddle-Idee aus A ist durch D und E verworfen | D R16, E D8 |
| Nie | Ungedeckte Short-Optionen, Market-Orders, Short-Optionen über Nacht, Covered Calls als Income, IV-Rank-Veto, GEX-Signal, Pinning-Logik, Richtungs-Tilt aus Skew oder Put-Call-Ratio | A, C, D |

Erwartung, ehrlich: Median über 2,5 Sitzungen rund plus 135 bis 400 Dollar, Erwartungswert etwa null bis leicht negativ, 5-Prozent-Quantil rund minus 2.300 Dollar, absoluter Boden minus 5.881 Dollar. Wahrscheinlichkeit eines Totalverlust-Tages 14 Prozent. Das steht so im Write-up.

### 8.2 Architektur: LLM entscheidet Kategorien, Code entscheidet Zahlen

```
Daten (alpaca-py + MCP)  →  Regime-Modul (LLM)  →  Strategie-Modul (Code)  →  Gate-Modul (Code, 30 Gates)
      │                          │                        │                          │
  Chains, Snapshots        VOL_REGIME, TREND,        Strikes, Kontrakte,        accept / reject
  mit Greeks/IV,           EVENT_RISK, Familie       Max Loss, Greeks           pro Order
  VIX, VIX3M, News,        aus festem Menü                 │                          │
  Makrokalender                                      Kritiker (LLM, nur Veto)  →  Execution (Code)
                                                                                    │
                                              Journal (LLM-Text + Code-Log)  ←  Fills, Recon, Flatten-Task
                                                                                    │
                                              Dashboard + Post-Session-Report (Code)
```

- **Regime-Modul, LLM:** liest anonymisierte Nachrichten, Makrokalender, VIX-Terminstruktur und gibt nur Enums zurück: VOL_REGIME in {low, normal, elevated, stressed}, TREND in {up, chop, down}, EVENT_RISK in {none, scheduled_minor, scheduled_major, unscheduled}, Strategiefamilie in {IRON_CONDOR_0DTE, PUT_CREDIT_SPREAD, CALL_CREDIT_SPREAD, LONG_GAMMA_SLEEVE, NO_TRADE}, plus Begründungstext. Schema strikt validiert; keine Zahl darf vom LLM kommen. (B 4.2)
- **Strategie-Modul, Code:** implizite Bewegung aus ATM-Straddle, Strikes, Kontraktzahl aus Max-Loss-Budget und Drawdown-Taper, Greeks, Kostenmodell.
- **Gate-Modul, Code:** die 30 Gates aus C, Config in einer Datei, die das LLM nicht schreiben kann; jedes Gate liefert accept oder reject auf dem Orderpfad.
- **Kritiker, LLM:** sieht den fertigen, validierten Kandidaten und darf BLOCK oder REDUCE sagen, nie APPROVE_LARGER; jedes Veto wird mit Grund geloggt. Ersetzt das menschliche Gate des Alpaca-Artikels.
- **Execution, Code:** Alpaca Trading API über alpaca-py für Orders; der Alpaca-MCP-Server ist das Werkzeug, mit dem der LLM-Orchestrator Chains, Snapshots und Konto liest; die Alpaca-CLI läuft in einem Cron-artigen Monitoring- und Recon-Job und im Flatten-Task, JSON-Output ins Log. Damit sind Trading API, MCP und CLI alle substanziell im Einsatz.
- **Journal, dreistufig:** kurzfristig Regime, Positionen, Fills, Gate-Ablehnungen; mittelfristig realisierte gegen erwartete Greeks und Slippage; langfristig Lehren, nur bei geschlossenem Trade oder Gate-Verstoß geschrieben und an die Rolle geroutet, die sie braucht. Sichtbare Belief-Updates zwischen Tag 1 und Tag 2. (B Design 9)
- **Zwei Modellstufen:** starkes Modell für Regime und Kritiker, günstiges Modell für Zusammenfassung und Journal; Featherless mit einem Open-Source-Modell für die Nachrichtenklassifikation, um den Partner sichtbar zu nutzen. Tokens und Latenz pro Entscheidung werden geloggt.
- **Zwei billige Experimente, die kein anderes Team zeigt:** Leakage-Selbsttest mit maskiertem Underlying, Determinismus-Check mit k Wiederholungen desselben Snapshots. (B Design 14)

### 8.3 Bewertung und Präsentation

- Kopfzeile: "We do not claim a statistically detectable edge. We claim a risk process that behaved exactly as specified."
- Berichtet: Gate-Trefferzähler, Max-Loss-Adhärenz, Drawdown gegen Ex-ante-Verteilung, Greeks-Abgleich, Slippage gegen Mid, Veto-Rate, Determinismus-Replay, Time-to-Flat, P&L-Zerlegung in Theta, Delta, Gamma, Vega, Residuum, Kosten.
- Benchmarks: SPY über identische Stunden, Cboe CNDR und PUT, Random-Entry-Monte-Carlo derselben Struktur mit unserem P&L als Perzentil. Die Monte-Carlo braucht historische Optionsdaten von Alpaca; falls die Zeit fehlt, eine vereinfachte Variante auf SPY-Intraday-Verteilung mit denselben Strike-Regeln, als solche gekennzeichnet.
- Nicht berichtet: Sharpe, Trefferquote, annualisierte Rendite, Profit Factor, mit Begründung.
- Protokoll nach Arnott/Harvey/Markowitz, Reporting-Checkliste nach Yao/Zheng, Anzahl getesteter Konfigurationen offengelegt.

### 8.4 Realistischer Zeitplan für Mittwoch

Setup ab dem Aufstehen etwa eine bis zwei Stunden. Ein minimal lauffähiger Agent mit Gates, Condor-Logik und Flatten-Task braucht danach vier bis fünf Stunden. Erste Trades realistisch im sekundären Fenster 12:30 bis 13:30 ET, also 18:30 bis 19:30 MESZ, nicht um 10:00 ET. Das ist in Ordnung: Das primäre Fenster verschiebt sich auf Donnerstag. Dashboard, Journal-Polish und Write-up am Donnerstag, Video und Slides am Freitag Vormittag.

---

## 9. Offene Entscheidungen für dich

1. **Sizing:** 2 Prozent pro Sitzung nach C oder 3 Prozent nach A. Empfehlung: 2 Prozent. Die Gegenrechnung aus C ist eindeutig.
2. **Earnings-Element:** Nach D und E entfällt der Broadcom-Straddle. Es bleibt das sichtbare Event-Gate mit geloggter Begründung. Falls du das anders siehst, sag es; die Evidenz dagegen ist aber eindeutig.
3. **Underlyings:** nur SPY, oder SPY plus QQQ. Empfehlung: Mittwoch nur SPY, QQQ ab Donnerstag, wenn alles stabil läuft.
4. **XSP statt SPY**, falls Alpaca Indexoptionen im Paper-Trading anbietet. Prüfe ich beim Setup.
5. **Freitag:** komplett NO_TRADE mit geloggter Begründung, oder ein einzelner kleiner Trade nach 10:15 ET. Empfehlung: NO_TRADE. Das ist die bessere Geschichte.
6. **Featherless:** für die Nachrichtenklassifikation einsetzen, ja oder nein. Empfehlung: ja, kleiner Aufwand, sichtbarer Partner-Einsatz.
7. **Paywall-Quellen:** welche aus Abschnitt 10 du über den Uni-Zugang holst. Priorität 1 bis 3 reichen.

---

## 10. Für deinen Uni-Zugang: gewünschte Paywall-Quellen

Priorität nach Nutzen für uns:

1. **SEC DERA (2025), "Hope at a Reasonable Price: Customer Use of Limit Orders in the 0DTE Market"**, https://www.sec.gov/files/dera-hope-reasonable-prc-2503.pdf. Blockiert per 403 für automatische Abrufe, im Browser vermutlich frei. Direkt unsere Ausführungsfrage.
2. **"Reproducibility in the TradingAgents Framework"**, DOI 10.1145/3800973.3801029, ACM 2026. Unabhängige Reproduktion, die Buy-and-Hold nicht schlägt. Bestes Gegenargument zu TradingAgents.
3. **Chen, Kelly & Xiu, "Expected Returns and Large Language Models"**, SSRN 4416687. Zahlen vor und nach Kosten. Bis dahin nur qualitativ zitieren.
4. **Carr & Wu (2009), RFS 22(3)**, DOI 10.1093/rfs/hhn038. Tabellen zur VRP-Größe pro Index.
5. **Dubinsky, Johannes, Kaeck & Seeger (2019), RFS 32(2)**. Implied gegen realized Earnings-Moves. Offene Kopie möglicherweise unter research.vu.nl.
6. **Bailey & López de Prado (2014), "The Deflated Sharpe Ratio"**, SSRN 2460551.
7. Coval & Shumway (2001) JF, Bollen & Whaley (2004) JF: nur für vollständige Tabellen, nicht kritisch.
8. **Vilkov, "0DTE Trading Rules"**, SSRN 4641356, plus Repo github.com/vilkovgr/0dte-strategies. Enthält offenbar Renditeverteilungen nach Einstiegszeit für 0DTE-Strategien. SSRN blockt automatische Abrufe, im Browser meist frei. Für die Timing-Frage die wertvollste ungelesene Quelle.
9. **Dim, Eraker & Vilkov, "0DTEs: Trading, Gamma Risk and Volatility Propagation"**, SSRN 4692190; offener Spiegel möglicherweise westernfinance-portal.org, Paper 950096.
10. **Ederington & Lee (1996), JFQA 31(4)**, DOI 10.2307/2331358: Größenordnung des IV-Rückgangs nach Meldungen. Nur, falls wir die NFP-Regel mit Zahl belegen wollen.

---

## 11. Kernbibliographie für das Write-up mit Qualitätsurteil

Vollständige Quellenkarten mit Zahlen stehen in den Berichten A bis E. Hier die Quellen, die im Ein-Seiten-Write-up und in den Slides tatsächlich zitiert werden sollten, mit Urteil. "Ja" heißt begutachtet und belastbar; "mit Vorbehalt" heißt Working Paper, Interessenkonflikt oder Einzelquelle; "nur Architektur" heißt Ergebnisse nicht zitieren.

**Optionsprämie und Strategie**
1. Bakshi, G. & Kapadia, N. (2003). Delta-Hedged Gains and the Negative Market Volatility Risk Premium. RFS 16(2). Ja.
2. Coval, J. & Shumway, T. (2001). Expected Option Returns. JF 56(3). Ja.
3. Carr, P. & Wu, L. (2009). Variance Risk Premiums. RFS 22(3). Ja; Tabellen paywalled.
4. Bollen, N. & Whaley, R. (2004). Does Net Buying Pressure Affect the Shape of Implied Volatility Functions? JF 59(2). Ja.
5. Israelov, R. & Nielsen, L. (2014). Covered Call Strategies: One Fact and Eight Myths. FAJ 70(6). Mit Vorbehalt, AQR.
6. Beckmeyer, H., Branger, N. & Gayda, L. (2023). Retail Traders Love 0DTE Options... But Should They? Working Paper, SSRN 4404704. Mit Vorbehalt; beste kosteninklusive Verteilung.
7. Almeida, C., Freire, G. & Hizmeri, R. (2025). 0DTE Asset Pricing. Working Paper, SSRN 4701401. Mit Vorbehalt; entscheidungsrelevanteste Quelle für Laufzeit und Timing.
8. Bandi, F., Fusari, N. & Renò, R. (2024). 0DTE Option Pricing. Journal of Finance, forthcoming. Ja, nur für die Fehlspezifikation von Deltas.
9. Constantinides, G., Jackwerth, J. & Savov, A. (2013). The Puzzle of Index Option Returns. RAPS 3(2). Ja.
10. Augustin, P., Cheng, I.-H. & Van den Bergen, L. (2021). Volmageddon and the Failure of Short Volatility Products. FAJ 77(3). Ja.
11. Cboe (2020). Benchmark Indexes Fact Sheet; Wilshire Analytics für Cboe (2019). Mit Vorbehalt, Exchange-Marketing; Zahlen nutzbar.
12. Gao, C., Xing, Y. & Zhang, X. (2018). Anticipating Uncertainty: Straddles Around Earnings Announcements. JFQA 53(6). Ja; brutto ohne Kosten.
13. Muravyev, D. & Pearson, N. (2020). Options Trading Costs Are Lower than You Think. RFS 33(11). Ja.

**Volatilitätsdynamik und Timing**
14. Johnson, T. (2017). Risk Premia and the VIX Term Structure. JFQA 52(6). Ja.
15. Simon, D. & Campasano, J. (2014). The VIX Futures Basis. Journal of Derivatives 21(3). Mit Vorbehalt.
16. Bollerslev, T., Tauchen, G. & Zhou, H. (2009). Expected Stock Returns and Variance Risk Premia. RFS 22(11). Ja.
17. Baltussen, G., Da, Z., Lammers, S. & Martens, M. (2021). Hedging Demand and Market Intraday Momentum. JFE 142(1). Ja.
18. Amaya, D., Garcia-Ares, P., Pearson, N. & Vasquez, A. (2025). 0DTE Index Options and Market Volatility. Cboe-Working-Paper. Mit Vorbehalt, Cboe-Daten.
19. Golez, B. & Jackwerth, J. (2012). Pinning in the S&P 500 Futures. JFE 106(3). Ja.
20. Ederington, L. & Lee, J. (1996). The Creation and Resolution of Market Uncertainty. JFQA 31(4). Ja; Größen nicht beschafft.
21. Andersen, T., Bollerslev, T., Diebold, F. & Vega, C. (2003). Micro Effects of Macro Announcements. AER 93(1). Ja; FX.
22. Poon, S.-H. & Granger, C. (2003). Forecasting Volatility in Financial Markets. JEL 41(2). Ja. Christensen, B. & Prabhala, N. (1998). JFE 50(2). Ja.
23. Xing, Y., Zhang, X. & Zhao, R. (2010). JFQA 45(3); Pan, J. & Poteshman, A. (2006). RFS 19(3). Ja, als Negativbefund für Richtungs-Tilt.

**LLM-Agenten**
24. Lopez-Lira, A. & Tang, Y. (2023-25). Can ChatGPT Forecast Stock Price Movements? arXiv 2304.07619. Ja, Working Paper mit starkem Design.
25. Glasserman, P. & Lin, C. (2024). Assessing Look-Ahead Bias in Stock Return Predictions Generated by GPT Sentiment Analysis. Journal of Financial Data Science 6(1). Ja.
26. He, S., Lv, L., Manela, A. & Wu, J. (2025). Chronologically Consistent Large Language Models. arXiv 2502.21206. Ja.
27. Kim, A., Muhn, M. & Nikolaev, V. (2024, zurückgezogen 2025). Financial Statement Analysis with Large Language Models. arXiv 2407.17866 v3. Nur als Warnung; als "withdrawn pending review" beschreiben.
28. Zhu, T. et al. (2026). From Knowing to Doing: A Memory-Controlled Benchmark for LLM Trading Agents. arXiv 2605.28359. Ja.
29. Li, X. et al. (2025). Profit Mirage: Revisiting Information Leakage in LLM-based Financial Agents. arXiv 2510.07920. Ja, als Kritik.
30. Yao, J. & Zheng, Z. (2026). Beyond Agent Architecture: Execution Assumptions and Reproducibility in LLM-Based Trading Systems. arXiv 2606.08285. Ja; Reporting-Checkliste.
31. Luo, H. et al. (2026). From Natural Language to Executable Option Strategies via Large Language Models. arXiv 2603.16434. Ja; einzige direkte LLM-Optionen-Quelle.
32. Asaad, S., Hamidi, S. & Bereyhi, A. (2026). Regime-aware Financial Volatility Forecasting via In-Context Learning. ICLR 2026 Workshop. Mit Vorbehalt.
33. Leng, J. et al. (2024/25). Taming Overconfidence in LLMs: Reward Calibration in RLHF. arXiv 2410.09724. Ja.
34. Ouyang, S., Yun, H. & Zheng, X. (2024/25). AI as Decision-Maker: Ethics and Risk Preferences of LLMs. arXiv 2406.01168. Ja.
35. Xiao, Y. et al. (2024/25). TradingAgents. arXiv 2412.20138. Nur Architektur. Yu, Y. et al. FinMem (2023), FinCon (2024). Nur Architektur.
36. Panteleev, F. (2026). Building a Multi-Agent AI Trading System on Alpaca. Alpaca Learn Blog. Mit Vorbehalt; Referenzdesign, das die Jury kennt.

**Risiko, Sizing, Bewertung**
37. Kelly, J. (1956). BSTJ 35; Thorp, E. (2006); MacLean, L., Thorp, E. & Ziemba, W. (2010). Good and Bad Properties of the Kelly Criterion. Quantitative Finance 10(7). Ja.
38. Chopra, V. & Ziemba, W. (1993). The Effect of Errors in Means, Variances and Covariances on Optimal Portfolio Choice. JPM. Ja; über Sekundärquelle.
39. Grossman, S. & Zhou, Z. (1993). Optimal Investment Strategies for Controlling Drawdowns. Mathematical Finance 3(3). Ja.
40. Kaminski, K. & Lo, A. (2014). When Do Stop-Loss Rules Stop Losses? JFM 18. Ja.
41. Israelov, R. (2019). Pathetic Protection: The Elusive Benefits of Protective Puts. JAI 21(3). Ja, AQR-Vorbehalt.
42. Goldberg, L. & Mahmoud, O. (2016). Drawdown: From Practice to Theory and Back Again. Mathematics and Financial Economics. Ja.
43. Bailey, D., Borwein, J., López de Prado, M. & Zhu, Q. (2014). Pseudo-Mathematics and Financial Charlatanism. Notices of the AMS 61(5). Ja.
44. Bailey, D. & López de Prado, M. (2014). The Deflated Sharpe Ratio. JPM 40(5). Ja.
45. Harvey, C., Liu, Y. & Zhu, H. (2016). ...and the Cross-Section of Expected Returns. RFS 29(1). Ja.
46. Arnott, R., Harvey, C. & Markowitz, H. (2019). A Backtesting Protocol in the Era of Machine Learning. JPM 46(1). Ja.

**Regulatorik als Design-Vorlage**
47. SEC (2010). Rule 15c3-5, Risk Management Controls for Brokers or Dealers with Market Access, Release 34-63241. Primärquelle.
48. ESMA / EU (2017). MiFID II RTS 6, Delegierte Verordnung 2017/589, Art. 12, 15, 17. Primärquelle.
49. FINRA (2015). Regulatory Notice 15-09, Guidance on Effective Supervision and Control Practices for Algorithmic Trading. Primärquelle.
50. SEC (2013). In the Matter of Knight Capital Americas LLC, Release 34-70694. Primärquelle; festgestellter Sachverhalt.

Wichtig im Write-up: Wir übernehmen die Regulatorik als Design-Vorlage und behaupten keine Compliance.

---

## 12. Revision am 2. September nach den Paywall-Quellen (Berichte F1 und F2)

Acht der gewuenschten Quellen aus Abschnitt 10 lagen am Morgen vor. Zwei Lese-Agenten haben sie vollstaendig gelesen und gegen das Zieldesign geprueft (`research/F1_user_sources_options.md`, `research/F2_user_sources_llm_events_eval.md`). Folgende Aenderungen an Abschnitt 8 sind uebernommen:

| Element | Vorher | Jetzt | Grund |
|---|---|---|---|
| Asymmetrie | Call-lastig, 1,25x Call und 1,5x Put | Symmetrisch, beide Shorts bei 1,10x des impliziten Move | Vilkov 2026, n = 1.319 Tage: der Risk Reversal long Call / short Put ist die einzige Struktur mit positivem Mittel, Median und P25; die Put-Seite war der reichere 0DTE-Verkauf. Die Neutralisierung im oberen VIX-Terzil entfaellt, weil Hochvol-Regime gerade dort verdienen (F1 E-V11, E-V12) |
| Wings | 1 bis 2 Dollar | max(3 Dollar, 0,5 Prozent des Spot) | Condor-Sharpe steigt monoton mit dem Abstand der Shorts; Wings von 0,15 bis 0,3 Prozent sind ungetestet und vier Beine Halbspread fressen den Credit (F1 E-V7, E-V8) |
| Credit-Gate | keines | Credit mindestens 20 Prozent der Wing-Breite | F1 empfiehlt 25 Prozent; 20 Prozent gewaehlt, weil die Spreadkosten separat mit 25 Prozent des Credits begrenzt sind |
| Kontrakte | bis 10 je Order | 5 je Order, 6 je Position | F1 E-V4, E-F12 |
| Regime-Taper | nur VIX/VIX3M | zusaetzlich halbe Groesse, wenn VIX1D im oberen Terzil der letzten 60 Sitzungen liegt | Condor-Mittel nach Terzil der impliziten Varianz +0,0016 / +0,0005 / -0,0111 Prozent, t = -0,93: Vorzeichen richtig, Signifikanz schwach, daher Taper statt Veto (F1 E-V12) |
| Spread-Filter und Collar | 15 Prozent des Mid, 5 Prozent Collar | in Ticks: kein Bein breiter als 3 Ticks, Leiter Mid, minus 1, minus 2 Ticks, letzte Sprosse Natural; Collar nie schlechter als Natural minus 1 Tick | SEC-Studie Fu/Li/Musto: moderne 0DTE-Spreads sind zu 65 Prozent ein Tick, zu 35 Prozent zwei; Prozent-Collars haetten fast jeden Kontrakt abgelehnt (F1 E-F5 bis E-F13). Die letzte Sprosse am Natural ist eine Konzession an den Alpaca-Papiersimulator, der nur marktfaehige Orders fuellt; die Fuell-Sprosse wird als Prozessmetrik berichtet |
| QQQ | sekundaer | gestrichen | Carr/Wu: SPX-VRP ueberlebt Bid-Preise (t = -7,44), QQQ nicht (t = -1,39) |
| GEX | abgelehnt | abgelehnt, jetzt mit Falsifikation | Dim/Eraker/Vilkov testen den einzigen Proxy, den wir bauen koennten (Open-Interest-Gamma): kein signifikanter Effekt |
| Kein Einstieg | nach 15:00 ET | nach 14:00 ET | letzte Stunde ist dort, wo realisierte Schiefe dominiert (F1 E-V19) |
| LLM-Sampling | Temperatur 0 | Temperatur 0, top_p, top_k = 1, Seed; drei Stimmen, Uneinigkeit ergibt NO_TRADE; Datum maskiert | Koviazin et al.: Temperatur 0 allein laesst 0,98 Bit Entscheidungsentropie; erst alle vier Parameter ergeben 0 (F2 5.2). Chen/Kelly/Xiu: Modellgroesse ist fuer Finanztext irrelevant, Llama-3-8B schlaegt 70B |
| Ereignisvarianz | Uhrregel | zusaetzlich geloggt: sigma_event aus zwei Verfallsterminen nach Dubinsky et al. 2019 Gleichung 4 | gibt der Freitag-Entscheidung eine gemessene Begruendung (F2 5.1); validiert am Brexit-Beispiel auf drei Nachkommastellen |
| Earnings-Begruendung | "Broadcom uebertraf den impliziten Move in 10 von 16" | Regel bleibt, Grund korrigiert: kurze Earnings-Straddles verdienen im Mittel (Dubinsky: -7,96 Prozent Straddle-Rendite, t = -13), brauchen aber 52 Trades fuer eine 95-Prozent-Aussage; wir haetten fuenf | F2 Kernaussage 4 |
| Bewertung | Prozessmetriken | plus die Arithmetik: MinTRL fuer Sharpe 0,5 / 1,0 / 2,0 bei Schiefe -1,5 und Kurtosis 6 = 2.860 / 751 / 207 Tage; mit T = 3 kann die Probabilistic Sharpe Ratio bei fetten Tails nie 95 Prozent erreichen; zwei getestete Konfigurationen erschoepfen das Multiple-Testing-Budget | Bailey/Lopez de Prado 2014, nachgerechnet in F2 5.3 |

Unveraendert bestaetigt: definiertes Risiko, Paket-Limit-Orders, kein Stop-Loss, flat bis 15:15 ET, Freitag NO_TRADE, 2 Prozent je Sitzung, keine Sharpe-Angaben. Ehrliche Erwartung nach Vilkov: der unbedingte Condor verliert ueber den Gesamtzeitraum leicht (mittlere Sitzung -0,008 Prozent des Spot nach Kosten), 45 Prozent rote Sitzungen; 2024 bis 2026 positiv, Regime-abhaengig, kein Edge.

## 13. Zweite Revision am 2. September: Conformal Condor (Bericht G) und Modellvergleich (Bericht H)

Zwei weitere Rechercheagenten haben am Nachmittag die Kernidee und die Modellfrage geprueft (`research/G_conformal_condor.md` mit `research/experiments/conformal_condor.py`; `research/H_tabular_ml_small_data.md` mit `research/experiments/model_comparison.py`). Ergebnis in einem Satz: Die Haelfte der Idee, die ein Theorem ist, wird gebaut; die Haelfte, die Hoffnung war, wird gestrichen und als negatives Ergebnis berichtet.

| Element | Vorher | Jetzt (ab Donnerstag 3. September) | Grund |
|---|---|---|---|
| Strike-Wahl | Shorts bei 1,10x des Straddle-implizierten Moves, fest | Shorts als Split-Conformal-Intervall auf dem Verhaeltnis realisierter Move / VIX-implizierter Move, Fenster 250 Sitzungen, Zielabdeckung 80 Prozent, alpha online angepasst (ACI, Gibbs und Candes 2021, gamma 0,005) | Abdeckung ist die Groesse mit Garantie; die feste Regel schwankt je nach Jahr zwischen 0,77 und 0,86 Abdeckung, im gestressten Regime faellt sie auf 0,46 bis 0,57 (G 5.4); konform bleibt sie in allen Regimen nahe 0,80 |
| Credit-Gate | Credit mindestens 15 Prozent der Wing-Breite | Gate 31: Credit/Wing (= risikoneutrale Wahrscheinlichkeit, jenseits der Spread-Mitte zu schliessen, Breeden-Litzenberger 1978) minus konformer p-Wert derselben Distanz mindestens 0,05 | Erwartete Auszahlung eines Pakets ist in erster Ordnung Wing mal (Q minus P); die Regel hat keinen freien Parameter, die 5 Punkte entsprechen den modellierten Handelskosten von vier Beinen; historisch stimmt das Vorzeichen von P minus Break-even in 13 von 15 Regime-Buckets mit dem realisierten Ergebnis ueberein (G 5.5) |
| Gestrichen | Kelly-Sizing aus geschaetzten Wahrscheinlichkeiten; volle Dichteschaetzung aus der Kette; breitere Intervalle als Ertragsquelle | Kelly nur als Exponat im Protokoll; Q nur als erste Ableitung (Credit/Wing); Breite unveraendert | Kelly ist bei b = 0,2 und p = 0,80 negativ, Standardfehler 0,15 bei 250 Sitzungen; der Gewinn breiterer Intervalle verschwindet, sobald der Credit mit der Breite skaliert (G 5.1, 5.7) |
| Regime-Modell | logistische Regression | unveraendert, mit Offenlegung | Auf dem Handelshorizont (10:30 bis Schluss) ist das Modell schlechter als eine Konstante, aber dort gibt es nur zwei Jahresbloecke; auf dem Horizont mit 15 Bloecken ist es das beste Einzelmodell. TabPFN v2, TabICL v2, XGBoost, LightGBM und ein Logit-XGBoost-Mittel unter identischem Protokoll getestet: kein Modell schlaegt zwoelf Koeffizienten dort, wo Inferenz moeglich ist; 21 Konfigurationen offengelegt (H 4) |
| Lizenzen | ungeprueft | TabICL v2 BSD-3 (Code und Gewichte), Mitra und TabDPT Apache-2.0, XGBoost Apache-2.0, LightGBM MIT; TabPFN v2 kommerziell nutzbar nur mit Namensnennungsklausel, TabPFN 2.5 und neuer nicht-kommerziell und zugangsbeschraenkt | H 6; kein Foundation-Modell wird ausgeliefert, also entsteht keine Lizenzpflicht im Repo |
| Berichtsfehler | Horizont B "2018-2026, OOS 2021-2026" | "2020-07 bis 2026, OOS 2022-2026"; Annahme konstanter Credit als Grenze der Aussagekraft markiert | H 8, G 1 |
| Bewertungsobjekt | Prozessmetriken | plus das P-gegen-Q-Protokoll je Sitzung (alpha_t, Q_mid, P_mid, Luecke, Entscheidung, Gegenfaktum der festen Regel), auch an Tagen ohne Handel | Das einzige Bewertungsobjekt der Abgabe, das keine statistische Power braucht (G 4.5) |

Originalitaet, geprueft in G 2 (RQ5): keine Arbeit setzt Options-Strikes als konformes Vorhersageintervall oder handelt das kalibrierte Intervall gegen seinen Marktpreis; naechster Nachbar ist Bastos (2024, Expert Systems with Applications), der konforme Intervalle um Optionspreise legt, ohne Handelsregel. Historischer Backfill (`docs/conformal_backfill.md`): Abdeckung 0,806 ueber 618 kalibrierte Sitzungen, alpha_t am 1. September 0,218, mittlerer Radius 0,73 implizierte Moves. Was die Historie nicht zeigen kann: ob das Gate Geld verdient, weil keine Optionspreise vorliegen; das wird live je Sitzung aus dem Audit-Log berichtet.

**Nachtrag vom Nachmittag des 2. September (Conformal Risk Control).** Die Abdeckungsvariante kontrolliert, wie oft der Kurs das Intervall verlaesst; die richtige Groesse ist, wie viel wir im Erwartungswert auszahlen, weil die meisten Ausbrueche Teilverluste sind (G 4.3: Gewinnschwelle 75,7 statt 83 Prozent). Conformal Risk Control (Angelopoulos, Bates, Fisch, Lei, Schuster, ICLR 2024) verallgemeinert die Abdeckungsgarantie auf jede monotone, beschraenkte Verlustfunktion; die Auszahlung des Condors ist genau eine solche. Die Strikes werden deshalb ab Donnerstag auf den kleinsten Radius gesetzt, fuer den die erwartete Auszahlung mit endlicher Stichprobe auf hoechstens beta = 10 Prozent der Fluegelbreite zertifiziert ist; die Online-Anpassung (Rolling Risk Control, Feldman, Ringel, Bates, Romano, TMLR 2023) darf den Radius nur enger machen. Gate 31 lautet damit: Credit/Fluegel mindestens 0,10 plus 0,05 Marge, woraus ein erwarteter Gewinn von mindestens 5 Prozent der Fluegelbreite je Paket folgt (Saetze und Beweise in `docs/THEORY.md`). Historisch (618 Sitzungen): realisierte Auszahlungsquote 0,079 gegen die Schranke 0,10, in jedem Jahr darunter (0,070 / 0,079 / 0,090); feste Regel 0,119 / 0,113 / 0,073. Die Abdeckungsvariante bleibt als Gegenfaktum im Protokoll.

---

## 14. Dritte Revision, Abend des 2. September: unabhängiger Literatur-Audit

Ein zweiter Agent hat am 2. September (15:43 bis 18:20 CEST) zwölf Themenberichte, rund 900 Quellenkarten und eine
Zitatprüfung von 35 tragenden Quellen gegen Primärquellen erstellt (Ordner außerhalb des Repos; Urteil in
`VERDICT.md`, Synthese in `STATE_OF_SCIENCE_2026.md`). Was daraus in dieses Repository übernommen wurde:

1. **Vilkov 2026 ist überholt.** Der Autor hat im August 2026 einen Kostenfehler um den Faktor 100 korrigiert; danach
   bleibt keine 0DTE-Struktur netto positiv (Condor-Bucket -0,96 -> -2,67). Alle Vilkov-Sharpe-Zahlen in F1 und in
   Abschnitt 12 sind damit historisch; README, Write-up und Folien zitieren die korrigierte Fassung. Überlebt: der
   Median-VRP von etwa 0,0011 % des Basiswerts ab 10:00 ET. Dew-Becker & Giglio (Chicago Fed WP 2025-17) kommen zum
   selben Schluss für gehandelte Indexoptionen der letzten 15 Jahre.
2. **Die Prämie ist über Nacht.** Muravyev & Ni (JFE 2020): delta-gehedgte S&P-500-Optionsrenditen im Mittel etwa
   -0,7 %/Tag, davon etwa -1 %/Tag von Schluss bis Eröffnung und etwa +0,3 %/Tag intraday, über alle Laufzeiten und
   Moneyness; Papagelis & Dotsis (JFM 2025) und Jones & Shemesh (JF 2018) bestätigen die Richtung. Delphi hält nie über
   Nacht und verzichtet damit per Konstruktion auf den messbaren Teil; das ist jetzt in `docs/THEORY.md` Abschnitt 8
   vorregistriert, mit der Roadmap "1DTE-Übernacht-Condor ab etwa 15:00 ET, kalibriert auf dem
   Schluss-zu-Schluss-Horizont".
3. **Neuheit enger gefasst.** Conformal Decision Theory (Lekeufack et al., ICRA 2024, nicht ICML), Conformal Kelly
   (Ryan 2026), Selective CRC (Xu, Guo & Wei 2025), Cañete (COPA 2023), Wisniewski/Lindsay/Lindsay (COPA 2020) und die
   P-gegen-Q-Ahnen Aït-Sahalia/Wang/Yared 2001, Constantinides/Jackwerth/Perrakis 2009, Faias/Santa-Clara 2017 werden
   als Vorläufer genannt. Was bleibt: niemand setzt Strikes per Conformal Risk Control, fasst die Struktur als verkauftes
   Prognoseintervall auf oder stellt das Zertifikat gegen den Breeden-Litzenberger-Preis desselben Intervalls.
4. **Schärfster Einwand, offen benannt:** Das Zertifikat gilt marginal, das Gate wählt Tage aus (Jin & Ren 2025;
   Gibbs, Cherian & Candès 2025; Xu/Guo/Wei 2025; Zhu et al. 2026). Der exakte Fix (Mondrian auf dem Gate-Ereignis)
   braucht eine historische Credit/Flügel-Reihe, die im Basisplan nicht existiert; Bemerkung (v) zu Satz 3.
5. **Gate 31 zertifiziert Kostendeckung, nicht Gewinn:** mu = 0,05 ist die modellierte Round-trip-Kostenmarge; die
   Formulierung "E[Payoff] >= 5 % der Flügelbreite" wurde überall ersetzt. Credit wird am erwarteten Fill gelesen.
6. **Lean-Vorarbeit existiert** (Ushakov & Berdinsky 2026 in Lean 4; Coelho 2026; Echenim/Guiol/Peltier 2018;
   Coq-Matching; Imandra). Enge Fassung in `lean/README.md`.
7. **Weitere Umformulierungen:** drei Stimmen = Enthaltungsfilter, kein Ensemble (Kim 2026; Bahuguna 2026);
   Determinismus ist eine Assurance-, keine Korrektheitseigenschaft (Thinking Machines 2025: 80 von 1.000
   Temperatur-0-Antworten verschieden); "Level passt online an" ist derzeit ein wirkungsloses Sicherheitsventil;
   Satz-4-Slack 0,224 ist auf Jahresfrist vakuos; Koviazin et al. = IC-AIF 2026, DOI 10.1145/3800973.3801029;
   15:15-Flatten als Liquiditätsregel (Todorov & Zhang; Cboe-VIX1D-Freeze), nicht über Late-Day-Momentum;
   Credit-Floor als Reibungsbudget, kein akademischer Beleg; "66 Einreichungen" -> "50 lesbare am 2. September".
8. **Ausführung:** Alpaca Paper füllt nur marktfähige Limits, keine Warteschlange, keine Preisverbesserung
   (Dokumentation wörtlich geprüft). Folgen und Änderungen datiert in `docs/CONFIG_CHANGES.md`.
9. **Nicht übernommen, mit Grund:** Wechsel des Normalisierers auf Geschäftszeit (bricht die Austauschbarkeit des
   Kalibrierfensters zwei Tage vor Abgabe; als Roadmap notiert); Gate 31 pro Seite (die zweiseitige Verlustfunktion
   ist das, was Satz 3 zertifiziert; die Seitenaufteilung wird protokolliert, nicht erzwungen); Conformal-Mengen
   über das LLM-Regime-Label (Kotte 2026: Unmöglichkeitsresultat für strukturierte LLM-Ausgaben);
   RL-Ausführungsagent (braucht Millisekunden-Orderbuchdaten, die es im Basisplan nicht gibt).
10. **Vom Audit selbst überzogen und deshalb nicht übernommen:** Goetzmann et al. 2007 enthält beides, unendlicher
    Erwartungswert der Stichproben-Sharpe (S. 1505) und endliches Populationsmaximum 1,31; die Koviazin-Zahlen sind aus
    dem PDF bestätigt, nur das Zitierformat war zu ändern; das Vilkov-Paar "0,77 -> -0,20" stand nicht in unserem README
    (dort standen die Tabelle-3-Werte -0,24 -> -0,65 aus F1); die Füllwahrscheinlichkeit je Tick im Audit ist ein Modell,
    kein Messwert; die CNDR/BFLY/WPUT-Zahlen sind Rechnungen des Auditors aus Cboe-Daten und noch nicht unabhängig
    repliziert, wir zitieren sie mit dieser Kennzeichnung.

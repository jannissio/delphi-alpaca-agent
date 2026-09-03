# Configuration changes during the campaign

Every change to a pre-registered parameter after the first live cycle (2026-09-02, 10:00 ET) is listed here
with its date, the evidence that motivated it, and what it does *not* change. The audit log carries the config
hash of every record, so each session can be tied to the exact configuration that produced it.

| Date (CEST) | Parameter | Before | After | Evidence | Effect |
|---|---|---|---|---|---|
| 2026-09-02 17:10 | `sizing.first_live_order_contracts` | 1 (pilot lot) | 0 (off) | Pilot lot filled and closed on 2026-09-02 (+$14) | First order of a session is sized from the budget like every other |
| 2026-09-02 17:40 | `execution.requote_each_rung` | (absent: rungs fixed at the decision) | true | 10:41 ET: three rungs 0.49/0.48/0.47 all cancelled unfilled while the package natural fell 0.47 -> 0.39 in 60 s; Alpaca paper fills only marketable orders | Every rung is priced off quotes pulled at send time; no rung may go below the credit floor the gates approved |
| 2026-09-02 21:30 | `execution.walk_ticks`, `natural_rung_repeats`, `walk_step_interval_s` | [0, 1, 2] + natural, 30 s | [1] + 2 x natural, 20 s | Same evidence; only a rung at or through the live natural filled (entry 0.44 at rung 2, exit through the natural) | Ladder reaches the live natural inside 60 s |
| 2026-09-02 21:30 | `execution.max_leg_spread_ticks`, `risk_limits.max_leg_spread_ticks` | 3 | 5 | 10:00-11:00 ET: most of the 121 rejected evaluations cited a short leg wider than 3 ticks; live chain measurement found 19 of 21 OTM legs one tick wide and the rejections tied to indicative-feed artefacts, while the package round-trip gate (`max_roundtrip_cost_pct_of_credit` 0.25) is the actual cost control | Per-leg check stays as a backstop; the package gate binds. Strike-monotonicity check added to gate 11 |
| 2026-09-02 21:30 | `conformal.credit_reference` | mid | natural | The pilot's only fill (0.44 on a $3 wing) sat below the 0.15 floor evaluated at the mid (0.45); in paper the expected fill is the natural | Gate 31 and the EV bound are read at the expected fill; the mid is logged alongside |

| 2026-09-03 00:40 | competition paper account | PA314NYH4H7G (pilot day) | PA31SEVJV9P9 (brand-new, $100,000, options level 3) | The hackathon requires a fresh, dedicated account for the judged run; after the 2026-09-02 changes the submitted agent differs from the pilot's, so the judged account holds only the submitted agent's trades | The pilot's state is archived under `state/pilot_PA314NYH4H7G_2026-09-02/`; `docs/report_2026-09-02.md` is labelled as the development account |

What did **not** change: the certificate (beta* = 0.10, window 250, clip [0.35, 1.60]), the margin (0.05), the
risk budgets (2 % session, 6 % campaign, $1,000 and 5 contracts per order), the windows, the 15:15 ET flatten,
the LLM menu and the unanimity rule.

"""Static dashboard from the audit log: one self-contained HTML file, no server, no secrets.

    python scripts/dashboard.py [--out docs/dashboard.html]

Order of the page (the audit's D4 item: certificate and ledger front and centre, populated even with zero fills):
status strip, the certificate (from state/conformal.json and today's committed interval), the P-versus-Q ledger
(gate 31), decisions (gate ledger, NO_TRADE reasons), positions and equity, LLM, evidence at T = 3, the rule in one
picture, configuration changes, the archived development pilot, journal, halts. Regenerate after each session;
publish with the repo (scripts/publish_dashboard.py).
"""
from __future__ import annotations

import html
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.core.config import ROOT, STATE_DIR  # noqa: E402


class Raw(str):
    """A table cell that is already HTML (everything else is escaped)."""


def load_jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def esc(x) -> str:
    return html.escape(str(x))


def cell(c) -> str:
    return c if isinstance(c, Raw) else esc(c)


def table(rows: list[list], header: list[str]) -> str:
    h = "".join(f"<th>{esc(c)}</th>" for c in header)
    b = "".join("<tr>" + "".join(f"<td>{cell(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f"<div class='wrap'><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>"


def tile(label: str, value, note: str = "", cls: str = "") -> str:
    return (f"<div class='tile {cls}'><span class='label'>{esc(label)}</span><b>{value if isinstance(value, Raw) else esc(value)}</b>"
            + (f"<span class='note'>{esc(note)}</span>" if note else "") + "</div>")


def tag(ok: bool, text: str) -> Raw:
    return Raw(f"<span class='tag {'ok' if ok else 'no'}'>{esc(text)}</span>")


CSS = """
:root{--bg:#ffffff;--surface:#f6f5f1;--fg:#101010;--muted:#6a6a66;--line:#e4e2dc;--yellow:#FCD72B;--purple:#461D9C;
--ok:#1f7a4d;--okbg:#e6f4ec;--no:#a33a2a;--nobg:#fbe9e5;--mono:Consolas,ui-monospace,SFMono-Regular,Menlo,monospace}
@media (prefers-color-scheme:dark){:root{--bg:#121212;--surface:#1b1b1b;--fg:#ececec;--muted:#a3a39c;--line:#2d2d2d;--purple:#b9a3ff;
--ok:#5ec48f;--okbg:#173225;--no:#e0705c;--nobg:#3a1f1a}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 "Segoe UI",system-ui,Roboto,Helvetica,Arial,sans-serif}
.bar{height:8px;background:var(--yellow)}
main{max-width:1040px;margin:0 auto;padding:24px 20px 64px}
header{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 18px;margin-bottom:4px}
h1{font-size:28px;letter-spacing:-.01em;margin:0}
.sub{color:var(--muted);font-size:14px}
h2{font-size:17px;margin:36px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--line);position:relative}
h2::after{content:"";position:absolute;left:0;bottom:-1px;width:48px;height:3px;background:var(--yellow)}
.claim{font-size:17px;font-weight:600;color:var(--purple);margin:10px 0 14px}
.muted{color:var(--muted);font-size:13.5px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin:12px 0}
.tile{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:10px 12px;min-width:0}
.tile .label{display:block;color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.04em}
.tile b{display:block;font-size:22px;font-weight:650;margin-top:2px;overflow-wrap:anywhere}
.tile .note{display:block;color:var(--muted);font-size:12.5px;margin-top:2px}
.tile.hi{border-color:var(--yellow);box-shadow:inset 4px 0 0 var(--yellow)}
.tile.warn{border-color:var(--no)}
.mono{font-family:var(--mono);font-size:13px}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:6px 0}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top;white-space:nowrap}
td:last-child,th:last-child{white-space:normal}
th{color:var(--muted);font-weight:600;font-size:12.5px;text-transform:uppercase;letter-spacing:.03em}
tbody tr:nth-child(even){background:var(--surface)}
.ok{color:var(--ok)} .no{color:var(--no)}
.tag{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12.5px;font-weight:600}
.tag.ok{background:var(--okbg);color:var(--ok)} .tag.no{background:var(--nobg);color:var(--no)}
.wrap{overflow-x:auto} pre{white-space:pre-wrap;font-size:13px}
.rule{margin:8px 0 0;padding:10px 12px;border-left:4px solid var(--yellow);background:var(--surface);border-radius:0 8px 8px 0}
svg{max-width:100%;height:auto}
a{color:var(--purple)}
footer{margin-top:40px;color:var(--muted);font-size:12.5px;border-top:1px solid var(--line);padding-top:10px}
"""


def pilot_section(archive: Path) -> str:
    """Compact, clearly labelled summary of an archived development run (never mixed into the competition figures)."""
    recs = load_jsonl(archive / "audit.jsonl")
    if not recs:
        return ""
    name = archive.name.replace("pilot_", "")
    account = name.split("_")[0]
    sessions = sorted({r.get("session") for r in recs if isinstance(r.get("session"), str)})  # conformal_interval carries a session dict
    opened = [r for r in recs if r["kind"] == "position_opened"]
    closed = [r for r in recs if r["kind"] == "position_closed"]
    gates = [r for r in recs if r["kind"] == "gates"]
    halts = [r for r in recs if r["kind"] == "halt"]
    pnl = sum(r.get("pnl", 0.0) for r in closed)
    first = sessions[0] if sessions else ""
    out = [f"<h2>What a trade looks like: development pilot {esc(', '.join(sessions))} on account {esc(account)} (not the competition account, not counted above)</h2>",
           "<div class='muted'>One-contract pilot on a separate development account, under the fixed 1.10x strike rule, before the conformal rule, the re-quoting ladder and the "
           "gate at the expected fill went live. It is shown because it exercised the whole path once: regime vote, gates, critic, ladder, fill, exit. "
           "Its lessons are in docs/CONFIG_CHANGES.md; its full report is docs/report_" + esc(first) + ".md. Under the rule that now runs, this day would not have traded either: "
           "the fill was 0.147 of the wing, the gate needs 0.15.</div>",
           "<div class='grid'>" + tile("gate evaluations", len(gates)) + tile("positions opened / closed", f"{len(opened)} / {len(closed)}")
           + tile("realised P&L", f"{pnl:+.2f} USD") + tile("halts", len(halts)) + "</div>"]
    pic = ROOT / "docs" / f"band_price_{first}_pilot.svg"
    if pic.exists():
        out.append("<div class='wrap'>" + pic.read_text(encoding="utf-8") + "</div>")
    # the anatomy: one row per step of the path, straight from the audit log
    steps = []
    for r in recs:
        k, t = r["kind"], r["ts"][11:19]
        if k == "llm_regime":
            d, m = r.get("decision") or {}, r.get("meta") or {}
            steps.append([t, "regime vote", f"{m.get('votes', '?')} calls, unanimous {m.get('unanimous')}: {d.get('vol_regime')} / {d.get('trend')} / {d.get('event_risk')} → {d.get('strategy_family')}, veto {d.get('veto')}"])
        elif k == "gates":
            c, res = r.get("candidate") or {}, r.get("results") or []
            steps.append([t, "gates", f"{sum(1 for x in res if x['passed'])} of {len(res)} passed; condor {c.get('long_put', 0):.0f}/{c.get('short_put', 0):.0f}/{c.get('short_call', 0):.0f}/{c.get('long_call', 0):.0f}, "
                                      f"credit mid {c.get('credit_mid', 0):.2f}, natural {c.get('credit_natural', 0):.2f}, max loss {c.get('max_loss_total', 0):.0f} $"])
        elif k == "llm_critic":
            d = r.get("decision") or {}
            steps.append([t, "critic", f"{d.get('verdict')}: {(d.get('reason') or '')[:110]}"])
        elif k == "order_submitted":
            steps.append([t, "ladder rung " + str(r.get("step")), f"{r.get('tag')}: limit {r.get('price')} (signed {r.get('signed_limit')}), qty {r.get('qty')}"])
        elif k == "open_not_filled":
            res = r.get("result") or {}
            steps.append([t, "ladder exhausted", f"unfilled after {len(res.get('order_ids', []))} rungs, last price {res.get('last_price')}; the natural credit fell faster than the ladder (fixed: every rung is re-quoted now)"])
        elif k == "order_filled":
            steps.append([t, "filled", f"{r.get('tag')}: rung {r.get('step')} at {r.get('avg_price')}"])
        elif k == "position_opened":
            p = r["position"]
            steps.append([t, "position opened", f"{p['contracts']} contract(s), credit {p['entry_credit']:.2f}, max loss {p['max_loss_total']:.0f} $, " +
                          ", ".join(f"{l['side'][0].upper()}{l['strike']:.0f}{l['right'][0].upper()}" for l in p["legs"])])
        elif k == "halt":
            steps.append([t, "halt", (r.get("reason") or "")[:120] + " (a false mismatch: side strings compared case-sensitively; new risk stopped as designed; fixed in cb441a8)"])
        elif k == "flatten_start":
            steps.append([t, "exit", f"{r.get('reason')}: close mid {r.get('close_mid')}, natural {r.get('close_natural')}, ladder {r.get('ladder')}"])
        elif k == "position_closed":
            steps.append([t, "position closed", f"{r.get('reason')}: entry {r['entry_credit']:.2f}, exit {r['exit_debit']:.2f}, P&L {r['pnl']:+.2f} $"])
    if steps:
        out.append("<h3 class='muted'>Anatomy of the trade, from the audit log</h3>" + table(steps, ["UTC", "step", "record"]))
    return "".join(out)


def certificate_section(conf_iv: list[dict], conf_eod: list[dict]) -> str:
    """The certificate, populated from state/conformal.json even when nothing has traded."""
    try:
        st = json.loads((STATE_DIR / "conformal.json").read_text(encoding="utf-8"))
    except Exception as exc:  # cold state: the page must still render
        return f"<h2>The certificate</h2><div class='muted'>state/conformal.json not readable: {esc(str(exc)[:120])}</div>"
    p = st.get("params", {})
    beta_star = float(p.get("beta_target", 0.10))
    margin = float(p.get("margin", 0.05))
    ledger = st.get("ledger", [])
    losses = [float(r.get("loss", 0.0)) for r in ledger]
    ratios = [float(r.get("ratio", 0.0)) for r in ledger if "ratio" in r]
    beta_t = float(st.get("beta_t", beta_star))
    alpha_t = float(st.get("alpha_t", p.get("alpha_target", 0.2)))
    by_year: dict[str, list[float]] = {}
    for r in ledger:
        by_year.setdefault(str(r.get("date", ""))[:4], []).append(float(r.get("ratio", 0.0)))
    years = ", ".join(f"{y}: {sum(v) / len(v):.3f}" for y, v in sorted(by_year.items()) if y)
    last = ledger[-1] if ledger else {}
    today = conf_iv[-1]["session"] if conf_iv else None
    parts = ["<h2>The certificate</h2>",
             "<div class='rule'><b>Trade only if</b> credit / wing at the expected fill &ge; &beta;* + margin = "
             f"{beta_star:.2f} + {margin:.2f} = <b>{beta_star + margin:.2f}</b>, with the short strikes at or beyond the radius certified at &beta;* "
             "(conformal risk control on the buyer's expected payout as a fraction of the wing). The margin is the modelled round-trip cost, "
             "so a passing trade is certified, in expectation and under exchangeability, not to lose after that cost. It is not a profit claim, "
             "and the guarantee is marginal while the gate selects (docs/THEORY.md, Theorem 3 remark v). A closed gate is the mechanism working.</div>",
             "<div class='grid'>",
             tile("certified level β*", f"{beta_star:.2f}", "expected payout / wing, bound by construction", "hi"),
             tile("calibrated sessions", len(ledger), f"{st.get('source', '')[:36]}" if st.get("source") else ""),
             tile("realised payout ratio", f"{(sum(losses) / len(losses)):.3f}" if losses else "-", f"mean over the set; by year {years}" if years else ""),
             tile("mean realised move / implied", f"{(sum(ratios) / len(ratios)):.3f}" if ratios else "-", "score r before the radius is subtracted"),
             tile("online level β_t", f"{beta_t:.3f}", "may only tighten; above β* it has no effect" if beta_t >= beta_star else "tighter than β*: binding"),
             tile("coverage level α_t", f"{alpha_t:.3f}", f"target {float(p.get('alpha_target', 0.2)):.2f}; the coverage track, reported only"),
             tile("calibrated through", st.get("updated_through", "-"), f"last session k {float(last.get('k', 0)):.3f}, {'outside' if last.get('err') else 'inside'}" if last else ""),
             "</div>"]
    if today:
        k = float(today.get("k", 0.0))
        impl = float(today.get("impl_ref_usd", 0.0))
        spot = float(today.get("spot_entry", 0.0))
        rad = k * impl
        parts += ["<div class='grid'>",
                  tile("today's interval committed", today.get("ts", "")[11:16] + " UTC", f"session {today.get('date')}, rule {today.get('rule')}", "hi"),
                  tile("anchor spot", f"{spot:.2f}", f"VIX prev {float(today.get('vix_prev', 0)):.2f} → implied ref move {impl:.2f} $"),
                  tile("certified radius k", f"{k:.3f}", f"k_crc {float(today.get('k_crc', 0)):.3f}, k_cov {float(today.get('k_cov', 0)):.3f}, n {today.get('n')}"),
                  tile("short strikes at or beyond", f"{spot - rad:.2f} / {spot + rad:.2f}", f"radius {rad:.2f} $, wing {float(today.get('wing_usd', 0)):.2f} $"),
                  "</div>"]
    else:
        parts.append("<div class='muted'>Today's interval is committed at the first evaluation inside the entry window (10:15 ET) and appears here with its "
                     "anchor spot, certified radius and strike band. Until then the certificate rests on the calibration set above.</div>")
    if conf_eod:
        rows = [[r["record"]["date"], f"{r['record']['ratio']:.3f}", f"{r['record']['k']:.3f}", f"{r['record'].get('loss', 0):.3f}",
                 Raw(f"{r['record'].get('beta_before', 0):.4f} &rarr; {r['record'].get('beta_after', 0):.4f}"), "outside" if r["record"]["err"] else "inside",
                 Raw(f"{r['record']['alpha_before']:.4f} &rarr; {r['record']['alpha_after']:.4f}")] for r in conf_eod]
        parts.append("<div class='muted'>End-of-day scoring of the committed interval (every session counts, traded or not):</div>")
        parts.append(table(rows, ["session", "realised ratio", "k", "payout ratio", "β update", "coverage", "α update"]))
    return "".join(parts)


def build(recs: list[dict], journal: list[dict], account_id: str = "", pilots: list[Path] = ()) -> str:
    sessions = sorted({r.get("session") for r in recs if isinstance(r.get("session"), str)})  # conformal_interval carries a session dict
    marks = [r for r in recs if r["kind"] == "mark"]
    opened = [r for r in recs if r["kind"] == "position_opened"]
    closed = [r for r in recs if r["kind"] == "position_closed"]
    gates = [r for r in recs if r["kind"] == "gates"]
    no_trade = Counter((r.get("reason") or r.get("msg") or "")[:80] for r in recs if r["kind"] == "no_trade")
    regimes = [r for r in recs if r["kind"] == "llm_regime"]
    critics = [r for r in recs if r["kind"] == "llm_critic"]
    halts = [r for r in recs if r["kind"] == "halt"]
    kills = [r for r in recs if r["kind"] == "kill_switch"]
    evs = [r for r in recs if r["kind"] == "event_vol"]
    chains = [r for r in recs if r["kind"] == "chain"]
    conf_iv = [r for r in recs if r["kind"] == "conformal_interval"]
    conf_led = [r for r in recs if r["kind"] == "conformal"]
    conf_eod = [r for r in recs if r["kind"] == "conformal_eod"]
    beats = [r for r in recs if r["kind"] in ("heartbeat", "no_trade", "halt")]

    gp, gf = Counter(), Counter()
    for g in gates:
        for res in g["results"]:
            (gp if res["passed"] else gf)[res["name"]] += 1
    pnl = sum(r.get("pnl", 0.0) for r in closed)
    slip = sum(r.get("slippage_vs_mid_usd", 0.0) for r in opened)
    rungs = Counter(str(r.get("fill_rung")) for r in opened)
    eq = [(m["ts"][:16], m["equity"], m.get("session_pnl", 0)) for m in marks]
    lat = [c.get("latency_ms", 0) for r in regimes for c in r.get("meta", {}).get("calls", [])]
    fam = Counter(r["decision"]["strategy_family"] for r in regimes if r.get("decision"))
    unanimous = Counter(str(r.get("meta", {}).get("unanimous")) for r in regimes)
    verdicts = Counter(r["decision"]["verdict"] for r in critics if r.get("decision"))

    last = recs[-1] if recs else {}
    last_mark = marks[-1] if marks else {}
    last_beat = beats[-1] if beats else {}
    halted = bool(last_beat.get("halted")) or last_beat.get("kind") == "halt"
    state_msg = last_beat.get("msg") or last_beat.get("reason") or ("no heartbeat yet" if not recs else last.get("kind", "-"))
    open_now = last_mark.get("open_positions", last_beat.get("open_positions", 0))
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # equity sparkline as inline SVG
    svg = ""
    if len(eq) >= 2:
        ys = [e[1] for e in eq]
        lo, hi = min(ys), max(ys)
        span = (hi - lo) or 1.0
        w, h = 720, 120
        pts = " ".join(f"{i / (len(ys) - 1) * w:.1f},{h - (y - lo) / span * (h - 10) - 5:.1f}" for i, y in enumerate(ys))
        svg = (f'<svg viewBox="0 0 {w} {h}" width="100%" height="120" role="img" aria-label="equity marks">'
               f'<polyline fill="none" stroke="currentColor" stroke-width="1.5" points="{pts}"/></svg>'
               f'<div class="muted">equity marks: first {ys[0]:.2f}, last {ys[-1]:.2f}, min {lo:.2f}, max {hi:.2f} over {len(ys)} marks</div>')

    parts = [f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Delphi dashboard</title>
<style>{CSS}</style></head><body><div class="bar"></div><main>
<header><h1>Delphi</h1><span class="sub">0DTE SPY iron condor agent on Alpaca paper, conformal risk control, 31 hard gates</span></header>
<div class="sub">Competition paper account <b>{esc(account_id or 'n/a')}</b>: brand-new, dedicated, $100,000 starting balance, options level 3; only the submitted agent has ever traded on it (from 2026-09-03). The 2026-09-02 pilot ran on a separate development account and is shown at the bottom, labelled.</div>
<div class="claim">We do not claim a statistically detectable edge. We claim a risk process that behaved exactly as specified.</div>
<div class="grid">
{tile("agent state", state_msg[:60], f"last record {esc(last.get('ts', '')[:16])} UTC" if last else "", "warn" if halted else "hi")}
{tile("equity", f"{last_mark['equity']:,.2f} USD" if last_mark else "-", f"session P&L {last_mark.get('session_pnl', 0):+.2f}, campaign {last_mark.get('campaign_pnl', 0):+.2f}" if last_mark else "no mark yet")}
{tile("open positions", open_now, f"opened {len(opened)}, closed {len(closed)}")}
{tile("sessions on this account", len(sessions) or 0, ", ".join(sessions) if sessions else "none yet")}
{tile("code / config", Raw(f"<span class='mono'>{esc(last.get('git', '-'))} / {esc(str(last.get('config', '-'))[:12])}</span>"), f"{len(recs)} audit records; every record carries both hashes")}
{tile("halts / kill events", f"{len(halts)} / {len(kills)}", "halts stop new risk, kills flatten", "warn" if halts or kills else "")}
</div>
"""]
    parts.append(certificate_section(conf_iv, conf_eod))

    # ---- the ledger: P versus Q
    parts.append("<h2>The ledger: P versus Q (gate 31)</h2>")
    parts.append("<div class='muted'>Q = credit / wing at the expected fill, the market's price of the band (Breeden-Litzenberger). P = the empirical payout ratio at the candidate's "
                 "strikes over the calibration set. The gate compares Q with &beta;* + margin; P is shown for the reader, never used to trade. "
                 "One row per candidate strike pair per session; n counts evaluations of that pair.</div>")
    if conf_iv:
        rows = [[r["ts"][:16], r["session"]["date"], r["session"].get("rule"), f"{r['session'].get('beta_t', 0):.4f}", f"{r['session'].get('k_crc', 0):.3f}",
                 f"{r['session']['alpha_t']:.4f}", f"{r['session'].get('k_cov', 0):.3f}", r["session"]["n"], f"{r['session']['k']:.3f}",
                 r["session"]["vix_prev"], f"{r['session']['impl_ref_usd']:.2f}", r["session"]["spot_entry"]] for r in conf_iv]
        parts.append(table(rows, ["committed (UTC)", "session", "rule", "beta_t", "k_crc", "alpha_t", "k_cov", "n", "k used", "VIX prev", "implied ref move $", "anchor spot"]))
    if conf_led:
        agg: dict = {}
        for r in conf_led:
            l, c, cf = r["ledger"], r["candidate"], r.get("counterfactual_fixed") or {}
            key = (r.get("session"), c["short_put"], c["short_call"], bool(l["passes"]))
            a = agg.setdefault(key, {"first": r["ts"][11:16], "last": r["ts"][11:16], "n": 0, "gap": [], "q": [], "p": [], "cf": cf.get("gap")})
            a["last"] = r["ts"][11:16]; a["n"] += 1; a["gap"].append(l["gap"]); a["q"].append(l.get("q_ref", l["q_mid"])); a["p"].append(l.get("beta_empirical", l["p_mid"]))
        rows = [[s, f"{a['first']}-{a['last']}", a["n"], f"{sp:.0f}/{sc:.0f}", f"{sum(a['q']) / a['n']:.3f}", f"{sum(a['p']) / a['n']:.3f}",
                 f"{min(a['gap']):+.3f}..{max(a['gap']):+.3f}", tag(ok, "TRADE" if ok else "NO_TRADE"),
                 "-" if a["cf"] is None else f"{a['cf']:+.3f}"] for (s, sp, sc, ok), a in agg.items()]
        parts.append(table(rows, ["session", "UTC", "n", "shorts", "credit/wing (Q)", "empirical payout at strikes (P)", "gate gap vs beta*", "decision", "fixed-rule gap"]))
    elif conf_iv:
        parts.append("<div class='muted'>Interval committed; no candidate strike pair has reached gate 31 yet.</div>")
    else:
        parts.append("<div class='muted'>No candidate evaluated under the conformal rule yet on this account. The first rows appear in the first entry window (10:15 ET).</div>")
    for s in sessions:
        pic = ROOT / "docs" / f"band_price_{s}.svg"
        if pic.exists():
            parts.append("<div class='wrap'>" + pic.read_text(encoding="utf-8") + "</div>")
            parts.append(f"<div class='muted'>Session {esc(s)}: every evaluation cycle the strategy prices the balanced condor at the configured wing; the red points are what the "
                         "market offered as a fraction of the wing, the black line is the gate. Regenerate: python scripts/band_price.py --session " + esc(s) + ".</div>")

    for archive in pilots:
        parts.append(pilot_section(archive))

    # ---- decisions
    parts.append("<h2>Decisions</h2><div class='grid'>")
    parts.append(tile("gate evaluations / rejections", f"{len(gates)} / {sum(1 for g in gates if not g['passed'])}", "all 31 gates run on every candidate"))
    parts.append(tile("positions opened / closed", f"{len(opened)} / {len(closed)}", f"fill rungs {dict(rungs)}" if rungs else "ladder: mid-1 tick, natural, natural"))
    parts.append(tile("realised P&L (closed)", f"{pnl:+.2f} USD"))
    parts.append(tile("entry slippage vs mid", f"{slip:+.2f} USD"))
    parts.append(tile("LLM decisions unanimous", f"{unanimous.get('True', 0)} / {len(regimes)}", "disagreement is abstention"))
    parts.append(tile("NO_TRADE cycles", sum(no_trade.values()), f"{len(no_trade)} distinct reasons"))
    parts.append("</div>")
    if gp or gf:
        parts.append("<h3 class='muted'>Gate ledger</h3>" + table([[n, gp[n], gf[n]] for n in sorted(set(gp) | set(gf))], ["gate", "passed", "rejected"]))
    else:
        parts.append("<div class='muted'>Gate ledger: no candidate evaluated yet.</div>")
    if no_trade:
        parts.append("<h3 class='muted'>NO_TRADE reasons</h3>" + table([[n, r] for r, n in no_trade.most_common(20)], ["count", "reason"]))

    # ---- positions and equity
    parts.append("<h2>Positions</h2>")
    rows = []
    for r in opened:
        p = r["position"]
        rows.append([p["opened_ts"][:16], p["underlying"], p["contracts"], f"{p['entry_credit']:.2f}",
                     f"{p['max_loss_total']:.0f}", r.get("fill_rung"), f"{r.get('slippage_vs_mid_usd', 0):+.2f}",
                     ", ".join(f"{l['side'][0].upper()}{l['strike']:.0f}{l['right'][0].upper()}" for l in p["legs"])])
    parts.append(table(rows, ["opened (UTC)", "und.", "qty", "credit", "max loss $", "fill rung", "slippage $", "legs"]) if rows else '<div class="muted">none</div>')
    rows = [[r["ts"][:16], r["position_id"], r["reason"], f"{r['entry_credit']:.2f}", f"{r['exit_debit']:.2f}", f"{r['pnl']:+.2f}"] for r in closed]
    if rows:
        parts.append(table(rows, ["closed (UTC)", "id", "reason", "entry", "exit", "P&L $"]))
    parts.append(f"<h2>Equity</h2>{svg or '<div class=muted>fewer than two marks yet</div>'}")

    # ---- LLM
    parts.append("<h2>LLM</h2>")
    parts.append(f"<div class='muted'>regime decisions {len(regimes)} (families {dict(fam)}); critic verdicts {dict(verdicts)}; "
                 f"regime call latency ms min/median/max: {min(lat) if lat else '-'} / {sorted(lat)[len(lat) // 2] if lat else '-'} / {max(lat) if lat else '-'}. "
                 "The models return categories only (regime, family, veto); every number comes from code.</div>")
    rows = []
    for r in regimes[-12:]:
        d, m = r.get("decision") or {}, r.get("meta") or {}
        rows.append([r["ts"][11:16], d.get("vol_regime"), d.get("trend"), d.get("event_risk"), d.get("strategy_family"), d.get("veto"),
                     m.get("entropy_bits", {}).get("strategy_family") if m.get("entropy_bits") else "-", (d.get("rationale") or "")[:140]])
    parts.append(table(rows, ["UTC", "vol", "trend", "event", "family", "veto", "H(family) bits", "rationale"]) if rows else '<div class="muted">no LLM calls yet</div>')
    if evs:
        e = evs[-1]
        parts.append(f"<h2>Term-structure event variance (Dubinsky et al. 2019)</h2><div class='muted'>sigma_event {e.get('sigma_event')} "
                     f"between {e.get('expiry_short')} and {e.get('expiry_long')}; ATM IV {e.get('iv_short')} vs {e.get('iv_long')}</div>")
    if chains:
        c = chains[-1]
        parts.append(f"<div class='muted'>last chain: {c.get('contracts')} contracts, {c.get('quotable')} quotable, feed Greeks {c.get('feed_greeks')}, model Greeks {c.get('model_greeks')}</div>")

    # ---- evidence at T = 3 (docs/THEORY.md section 9) and the rule in one picture
    try:
        from agent.core.evidence import evidence_ceiling, profit_wealth, risk_wealth, sessions_for_alpha
        from scripts.evidence import traded_pairs
        st = json.loads((STATE_DIR / "conformal.json").read_text(encoding="utf-8"))
        beta_star = float(st.get("params", {}).get("beta_target", 0.10))
        losses = [float(r["loss"]) for r in st.get("ledger", []) if "loss" in r]
        risk = risk_wealth(losses, beta_star, 1.0)
        pairs = traded_pairs(STATE_DIR / "audit.jsonl")
        parts.append("<h2>Evidence at T = 3: two e-processes and a ceiling</h2>")
        parts.append(f"<div class='muted'>Risk process (evidence <em>against</em> the certificate, null E[payout ratio | past] &le; beta*): over {len(losses)} "
                     f"calibrated sessions the running maximum is {risk['W_max']:.2f}, anytime-valid p-value {risk['p_anytime']:.2f} "
                     f"(below 0.05 would reject the certificate). Reported, never used to halt.</div>")
        if pairs:
            prof = profit_wealth([(p['g'], p['l']) for p in pairs], 1.0)
            rows = [[p["session"], f"{p['credit']:.2f}", f"{p['wing']:.0f}", f"{p['g']:.3f}", f"{p['l']:.3f}", f"{p['g'] - p['l']:+.3f}"] for p in pairs]
            parts.append(table(rows, ["session", "credit at fill", "wing", "credit/wing g", "payout ratio l", "Y = g - l"]))
            parts.append(f"<div class='muted'>Profit process (evidence <em>for</em> profitability, null E[g - l | past] &le; 0): W_T = {prof['W_T']:.3f}, anytime p {prof['p_anytime']:.2f}.</div>")
        else:
            parts.append("<div class='muted'>Profit process: no traded session with a closed payout ratio yet.</div>")
        parts.append(f"<div class='muted'>Ceiling: T perfect sessions at credit/wing g give at most (1/(1-g))^T; at g = 0.20 three perfect sessions reach "
                     f"{evidence_ceiling(0.20, 3):.2f}, i.e. p &ge; {1 / evidence_ceiling(0.20, 3):.2f}, and p &le; 0.05 needs {sessions_for_alpha(0.20, 0.05)} consecutive perfect packages. "
                     "That is why no Sharpe ratio appears on this page. Details: docs/evidence.md.</div>")
    except Exception as exc:  # the dashboard must render even with a cold state
        parts.append(f"<h2>Evidence at T = 3</h2><div class='muted'>not available: {esc(str(exc)[:120])}</div>")
    svg_path = ROOT / "docs" / "risk_curve.svg"
    if svg_path.exists():
        parts.append("<h2>The rule in one picture</h2><div class='wrap'>" + svg_path.read_text(encoding="utf-8") + "</div>")
        parts.append("<div class='muted'>The buyer's expected payout as a fraction of the wing falls with the radius; where the finite-sample-inflated curve first crosses "
                     "beta* is the certified radius, and the short strikes go there. Regenerate: python scripts/risk_curve.py.</div>")
    parts.append("<h2>Configuration changes since the first live cycle</h2><div class='muted'>Every pre-registered parameter changed after 2026-09-02 10:00 ET, with date, "
                 "evidence and effect: <a href='https://github.com/jannissio/delphi-alpaca-agent/blob/main/docs/CONFIG_CHANGES.md'>docs/CONFIG_CHANGES.md</a>. "
                 "Each audit record carries the config hash that produced it.</div>")
    parts.append("<h2>Journal (last entries)</h2>")
    if not journal:
        parts.append("<div class='muted'>no journal entries yet</div>")
    for j in journal[-8:]:
        parts.append(f"<p><span class='muted'>{esc(j['ts'][:16])} [{esc(j['tier'])}]</span> {esc(j['entry'])}"
                     + (f" <em>Lesson: {esc(j['lesson'])}</em>" if j.get("lesson") else "") + "</p>")
    if halts:
        parts.append("<h2>Halts</h2>" + "".join(f"<p class='no'>{esc(h['ts'][:16])}: {esc(h['reason'])}</p>" for h in halts))
    parts.append("<h2>Not reported, on purpose</h2><p class='muted'>Sharpe ratio, win rate, annualised return, profit factor. With a handful of observations these are noise: "
                 "the minimum track record to certify an annualised Sharpe of 1.0 at 95 % with skew -1.5 and kurtosis 6 is 751 daily observations (Bailey &amp; Lopez de Prado 2014).</p>")
    parts.append(f"<footer>Generated {now_utc} from state/audit.jsonl and state/conformal.json by scripts/dashboard.py. No server, no secrets, no live data: "
                 "everything on this page is a replay of the append-only audit log.</footer>")
    parts.append("</main></body></html>")
    return "".join(parts)


def main() -> None:
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else Path("docs/dashboard.html")
    recs = load_jsonl(STATE_DIR / "audit.jsonl")
    journal = load_jsonl(STATE_DIR / "journal.jsonl")
    import os
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    account_id = os.environ.get("ALPACA_ACCOUNT_ID", "").strip()
    pilots = sorted(p for p in STATE_DIR.glob("pilot_*") if p.is_dir())
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(recs, journal, account_id=account_id, pilots=pilots), encoding="utf-8")
    print("wrote", out, f"({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

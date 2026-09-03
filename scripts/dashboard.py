"""Static dashboard from the audit log: one self-contained HTML file, no server, no secrets.

    python scripts/dashboard.py [--out docs/dashboard.html]

Shows: headline claim, account/equity marks, positions and P&L, the gate ledger, NO_TRADE
reasons, LLM votes / entropy / latency, fill rungs and slippage, the event-variance reading,
and the last journal entries. Regenerate after each session; publish with the repo.
"""
from __future__ import annotations

import html
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.core.config import ROOT, STATE_DIR  # noqa: E402


def load_jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def esc(x) -> str:
    return html.escape(str(x))


def table(rows: list[list], header: list[str]) -> str:
    h = "".join(f"<th>{esc(c)}</th>" for c in header)
    b = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>"


def pilot_section(archive: Path) -> str:
    """Compact, clearly labelled summary of an archived development run (never mixed into the competition figures)."""
    recs = load_jsonl(archive / "audit.jsonl")
    if not recs:
        return ""
    name = archive.name.replace("pilot_", "")
    account = name.split("_")[0]
    sessions = sorted({r.get("session") for r in recs if r.get("session")})
    opened = [r for r in recs if r["kind"] == "position_opened"]
    closed = [r for r in recs if r["kind"] == "position_closed"]
    gates = [r for r in recs if r["kind"] == "gates"]
    halts = [r for r in recs if r["kind"] == "halt"]
    pnl = sum(r.get("pnl", 0.0) for r in closed)
    out = [f"<h2>Development pilot (not the competition account): {esc(account)}, {esc(', '.join(sessions))}</h2>",
           "<div class='muted'>One-contract pilot under the fixed 1.10x strike rule, before the conformal rule, the re-quoting ladder and the "
           "gate at the expected fill went live. Its lessons are in docs/CONFIG_CHANGES.md; its full report is docs/report_" + esc(sessions[0] if sessions else "") + ".md. "
           "Nothing from this run is counted above.</div>",
           f"<div class='grid'><div class='tile'><span class='muted'>gate evaluations</span><b>{len(gates)}</b></div>"
           f"<div class='tile'><span class='muted'>positions opened / closed</span><b>{len(opened)} / {len(closed)}</b></div>"
           f"<div class='tile'><span class='muted'>realised P&amp;L</span><b>{pnl:+.2f} USD</b></div>"
           f"<div class='tile'><span class='muted'>halts</span><b>{len(halts)}</b></div></div>"]
    rows = []
    for r in opened:
        p = r["position"]
        rows.append([p["opened_ts"][:16], p["contracts"], f"{p['entry_credit']:.2f}", f"{p['max_loss_total']:.0f}", r.get("fill_rung"),
                     ", ".join(f"{l['side'][0].upper()}{l['strike']:.0f}{l['right'][0].upper()}" for l in p["legs"])])
    if rows:
        out.append(table(rows, ["opened (UTC)", "qty", "credit", "max loss $", "fill rung", "legs"]))
    rows = [[r["ts"][:16], r["reason"], f"{r['entry_credit']:.2f}", f"{r['exit_debit']:.2f}", f"{r['pnl']:+.2f}"] for r in closed]
    if rows:
        out.append(table(rows, ["closed (UTC)", "reason", "entry", "exit", "P&L $"]))
    if halts:
        out.append("".join(f"<p class='no'>{esc(h['ts'][:16])}: {esc(h['reason'][:160])}</p>" for h in halts))
    return "".join(out)


def build(recs: list[dict], journal: list[dict], account_id: str = "", pilots: list[Path] = ()) -> str:
    sessions = sorted({r.get("session") for r in recs if r.get("session")})
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
<style>
:root{{--bg:#fbfaf7;--fg:#1c1b19;--muted:#6b6862;--line:#e4e1da;--ok:#1f7a4d;--no:#a33a2a;--accent:#2c4c8c}}
@media (prefers-color-scheme:dark){{:root{{--bg:#14161a;--fg:#e8e6e1;--muted:#9a978f;--line:#2b2f36;--ok:#5ec48f;--no:#e0705c;--accent:#8fb0ff}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,Segoe UI,Roboto,sans-serif}}
main{{max-width:1000px;margin:0 auto;padding:28px 20px 60px}}
h1{{font-size:26px;margin:0 0 4px}} h2{{font-size:18px;margin:32px 0 8px;border-bottom:1px solid var(--line);padding-bottom:4px}}
.claim{{font-weight:600;color:var(--accent);margin:6px 0 18px}} .muted{{color:var(--muted);font-size:13px}}
table{{border-collapse:collapse;width:100%;font-size:14px;margin:8px 0}} th,td{{text-align:left;padding:5px 8px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{color:var(--muted);font-weight:600}} .ok{{color:var(--ok)}} .no{{color:var(--no)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:12px 0}}
.tile{{border:1px solid var(--line);border-radius:8px;padding:10px 12px}} .tile b{{display:block;font-size:22px}}
.wrap{{overflow-x:auto}} pre{{white-space:pre-wrap;font-size:13px}}
</style></head><body><main>
<h1>Delphi: 0DTE iron condor agent on Alpaca paper</h1>
<div class="muted">Competition paper account <b>{esc(account_id or 'n/a')}</b>: brand-new, dedicated, $100,000 starting balance, options level 3; only the submitted agent has ever traded on it (from 2026-09-03). The 2026-09-02 pilot ran on a separate development account and is shown at the bottom, labelled.</div>
<div class="claim">We do not claim a statistically detectable edge. We claim a risk process that behaved exactly as specified.</div>
<div class="muted">sessions: {esc(', '.join(sessions) or 'none yet')} | audit records: {len(recs)} | generated from state/audit.jsonl</div>
<div class="grid">
<div class="tile"><span class="muted">positions opened / closed</span><b>{len(opened)} / {len(closed)}</b></div>
<div class="tile"><span class="muted">realised P&amp;L (closed)</span><b>{pnl:+.2f} USD</b></div>
<div class="tile"><span class="muted">entry slippage vs mid</span><b>{slip:+.2f} USD</b></div>
<div class="tile"><span class="muted">gate evaluations / rejections</span><b>{len(gates)} / {sum(1 for g in gates if not g['passed'])}</b></div>
<div class="tile"><span class="muted">halts / kill events</span><b>{len(halts)} / {len(kills)}</b></div>
<div class="tile"><span class="muted">LLM decisions unanimous</span><b>{unanimous.get('True', 0)} / {len(regimes)}</b></div>
</div>
<h2>Equity</h2>{svg or '<div class="muted">no marks yet</div>'}
<h2>Positions</h2>"""]
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
    parts.append("<h2>Gate ledger</h2><div class='wrap'>")
    parts.append(table([[n, gp[n], gf[n]] for n in sorted(set(gp) | set(gf))], ["gate", "passed", "rejected"]) if (gp or gf) else '<div class="muted">no candidate evaluated yet</div>')
    parts.append("</div><h2>NO_TRADE reasons</h2>")
    parts.append(table([[n, r] for r, n in no_trade.most_common(20)], ["count", "reason"]) if no_trade else '<div class="muted">none</div>')
    parts.append("<h2>LLM</h2>")
    parts.append(f"<div class='muted'>regime decisions {len(regimes)} (families {dict(fam)}); critic verdicts {dict(verdicts)}; "
                 f"regime call latency ms min/median/max: {min(lat) if lat else '-'} / {sorted(lat)[len(lat) // 2] if lat else '-'} / {max(lat) if lat else '-'}; fill rungs {dict(rungs) if rungs else '-'}</div>")
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
    parts.append("<h2>Conformal Condor: P versus Q (gate 31)</h2>")
    if conf_iv or conf_led or conf_eod:
        parts.append("<div class='muted'>credit / wing, read at the expected fill, is the market's price of the band (Breeden-Litzenberger); the certified payout is the conformal-risk-control bound "
                     "on the expected payout to the buyer (beta* = 0.10, strikes at or beyond the certified radius); trade iff credit/wing &minus; beta* &ge; margin, where the margin "
                     "is the modelled round-trip cost, so every trade is certified, in expectation and under exchangeability, not to lose after that cost (docs/THEORY.md). "
                     "The certificate is marginal while the gate selects; see Theorem 3, remark v. A closed gate is the mechanism working.</div>")
        rows = [[r["ts"][:16], r["session"]["date"], r["session"].get("rule"), f"{r['session'].get('beta_t', 0):.4f}", f"{r['session'].get('k_crc', 0):.3f}",
                 f"{r['session']['alpha_t']:.4f}", f"{r['session'].get('k_cov', 0):.3f}", r["session"]["n"], f"{r['session']['k']:.3f}",
                 r["session"]["vix_prev"], f"{r['session']['impl_ref_usd']:.2f}", r["session"]["spot_entry"]] for r in conf_iv]
        parts.append(table(rows, ["committed (UTC)", "session", "rule", "beta_t", "k_crc", "alpha_t", "k_cov", "n", "k used", "VIX prev", "implied ref move $", "anchor spot"]) if rows else "")
        agg: dict = {}
        for r in conf_led:
            l, c, cf = r["ledger"], r["candidate"], r.get("counterfactual_fixed") or {}
            key = (r.get("session"), c["short_put"], c["short_call"], bool(l["passes"]))
            a = agg.setdefault(key, {"first": r["ts"][11:16], "last": r["ts"][11:16], "n": 0, "gap": [], "q": [], "p": [], "cf": cf.get("gap")})
            a["last"] = r["ts"][11:16]; a["n"] += 1; a["gap"].append(l["gap"]); a["q"].append(l.get("q_ref", l["q_mid"])); a["p"].append(l.get("beta_empirical", l["p_mid"]))
        rows = [[s, f"{a['first']}-{a['last']}", a["n"], f"{sp:.0f}/{sc:.0f}", f"{sum(a['q']) / a['n']:.3f}", f"{sum(a['p']) / a['n']:.3f}",
                 f"{min(a['gap']):+.3f}..{max(a['gap']):+.3f}", "<span class='ok'>TRADE</span>" if ok else "<span class='no'>NO_TRADE</span>",
                 "-" if a["cf"] is None else f"{a['cf']:+.3f}"] for (s, sp, sc, ok), a in agg.items()]
        parts.append("<div class='wrap'>" + (table(rows, ["session", "UTC", "n", "shorts", "credit/wing (Q)", "empirical payout at strikes (P)", "gate gap vs beta*", "decision", "fixed-rule gap"]) if rows else "<div class='muted'>no candidate evaluated under the conformal rule yet</div>") + "</div>")
        rows = [[r["record"]["date"], f"{r['record']['ratio']:.3f}", f"{r['record']['k']:.3f}", f"{r['record'].get('loss', 0):.3f}",
                 f"{r['record'].get('beta_before', 0):.4f} &rarr; {r['record'].get('beta_after', 0):.4f}", "outside" if r["record"]["err"] else "inside",
                 f"{r['record']['alpha_before']:.4f} &rarr; {r['record']['alpha_after']:.4f}"] for r in conf_eod]
        parts.append(table(rows, ["session", "realised ratio", "k", "payout ratio", "beta update", "coverage", "alpha update"]) if rows else "")
    else:
        parts.append("<div class='muted'>enabled from 2026-09-03; no conformal records yet</div>")
    # ---- evidence at T = 3 (docs/THEORY.md section 9) and the rule in one picture
    try:
        import json as _json
        from agent.core.evidence import evidence_ceiling, profit_wealth, risk_wealth, sessions_for_alpha
        from scripts.evidence import traded_pairs
        st = _json.loads((STATE_DIR / "conformal.json").read_text(encoding="utf-8"))
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
            parts.append("<div class='wrap'>" + table(rows, ["session", "credit at fill", "wing", "credit/wing g", "payout ratio l", "Y = g - l"]) + "</div>")
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
    for archive in pilots:
        parts.append(pilot_section(archive))
    parts.append("<h2>Journal (last entries)</h2>")
    for j in journal[-8:]:
        parts.append(f"<p><span class='muted'>{esc(j['ts'][:16])} [{esc(j['tier'])}]</span> {esc(j['entry'])}"
                     + (f" <em>Lesson: {esc(j['lesson'])}</em>" if j.get("lesson") else "") + "</p>")
    if halts:
        parts.append("<h2>Halts</h2>" + "".join(f"<p class='no'>{esc(h['ts'][:16])}: {esc(h['reason'])}</p>" for h in halts))
    parts.append("<h2>Not reported, on purpose</h2><p class='muted'>Sharpe ratio, win rate, annualised return, profit factor. With a handful of observations these are noise: "
                 "the minimum track record to certify an annualised Sharpe of 1.0 at 95 % with skew -1.5 and kurtosis 6 is 751 daily observations (Bailey &amp; Lopez de Prado 2014).</p>")
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

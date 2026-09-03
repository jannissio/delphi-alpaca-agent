"""Post-session report (gate 30) from the audit log alone: process metrics, not performance claims.

    python scripts/report.py [--session 2026-09-02] [--out docs/report_2026-09-02.md]

Reports: gate evaluations and rejections by gate, NO_TRADE reasons, LLM votes/entropy/latency,
fills with slippage vs mid and the rung that filled, P&L per position, time-to-flat, halts,
kill-switch events. Deliberately absent: Sharpe, win rate, annualised return (see
research/F2 5.3: with T=3 observations the Probabilistic Sharpe Ratio cannot reach 95 % at
any performance level for fat-tailed returns).
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.core.config import STATE_DIR  # noqa: E402


def load(session: str | None) -> list[dict]:
    p = STATE_DIR / "audit.jsonl"
    if not p.exists():
        return []
    recs = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    def belongs(r: dict) -> bool:   # conformal_interval records carry the session dict under "session"; match on its date
        s = r.get("session")
        return session is None or s == session or (isinstance(s, dict) and s.get("date") == session)
    return [r for r in recs if belongs(r)]


def build(recs: list[dict], session: str | None) -> tuple[str, dict]:
    kinds = Counter(r["kind"] for r in recs)
    gates_eval = [r for r in recs if r["kind"] == "gates"]
    gate_fail = Counter()
    gate_pass = Counter()
    for g in gates_eval:
        for res in g["results"]:
            (gate_pass if res["passed"] else gate_fail)[res["name"]] += 1
    no_trade = Counter(r.get("reason", r.get("msg", ""))[:90] for r in recs if r["kind"] == "no_trade")
    regimes = [r for r in recs if r["kind"] == "llm_regime"]
    critics = [r for r in recs if r["kind"] == "llm_critic"]
    opened = [r for r in recs if r["kind"] == "position_opened"]
    closed = [r for r in recs if r["kind"] == "position_closed"]
    halts = [r for r in recs if r["kind"] == "halt"]
    kills = [r for r in recs if r["kind"] in ("kill_switch", "kill_switch_seen")]
    marks = [r for r in recs if r["kind"] == "mark"]
    order_subs = [r for r in recs if r["kind"] == "order_submitted"]
    fills = [r for r in recs if r["kind"] == "order_filled"]
    event_vols = [r for r in recs if r["kind"] == "event_vol"]
    conf_iv = [r for r in recs if r["kind"] == "conformal_interval"]
    conf_led = [r for r in recs if r["kind"] == "conformal"]
    conf_eod = [r for r in recs if r["kind"] == "conformal_eod"]
    conf_err = [r for r in recs if r["kind"] == "conformal_error"]

    pnl = sum(r.get("pnl", 0.0) for r in closed)
    slippage = sum(r.get("slippage_vs_mid_usd", 0.0) for r in opened)
    rungs = Counter(r.get("fill_rung") for r in opened)
    lat = [m["latency_ms"] for r in regimes for m in r.get("meta", {}).get("calls", []) if "latency_ms" in m]
    tokens = sum(m.get("tokens_in", 0) + m.get("tokens_out", 0) for r in regimes for m in r.get("meta", {}).get("calls", []))
    entropies = [r["meta"].get("entropy_bits") for r in regimes if r.get("meta", {}).get("entropy_bits")]
    unanimous = Counter(str(r.get("meta", {}).get("unanimous")) for r in regimes)
    verdicts = Counter(r["decision"]["verdict"] for r in critics if r.get("decision"))
    families = Counter(r["decision"]["strategy_family"] for r in regimes if r.get("decision"))

    lines = [f"# Session report {session or 'all'}", "",
             "**We do not claim a statistically detectable edge. We claim a risk process that behaved exactly as specified.**", "",
             "## Activity",
             f"- audit records: {len(recs)}; cycles with a gate evaluation: {len(gates_eval)}; orders submitted: {len(order_subs)}; package fills: {len(fills)}",
             f"- positions opened: {len(opened)}; closed: {len(closed)}; halts: {len(halts)}; kill-switch events: {len(kills)}",
             f"- realised P&L (closed packages): {pnl:+.2f} USD; entry slippage vs decision mid: {slippage:+.2f} USD",
             f"- fill rung distribution (0 = package mid, last = natural): {dict(rungs) if rungs else 'no fills'}", "",
             "## Gates",
             "| gate | passed | rejected |", "|---|---|---|"]
    for name in sorted(set(gate_pass) | set(gate_fail)):
        lines.append(f"| {name} | {gate_pass[name]} | {gate_fail[name]} |")
    lines += ["", "## NO_TRADE reasons (deduplicated, truncated)"]
    lines += [f"- {n} x {reason}" for reason, n in no_trade.most_common(15)] or ["- none"]
    lines += ["", "## LLM",
              f"- regime calls: {sum(r.get('meta', {}).get('votes', 0) or 0 for r in regimes)} across {len(regimes)} decisions; unanimity: {dict(unanimous)}",
              f"- strategy family votes: {dict(families)}; critic verdicts: {dict(verdicts)}",
              f"- latency ms (min/median/max): {min(lat) if lat else '-'} / {sorted(lat)[len(lat)//2] if lat else '-'} / {max(lat) if lat else '-'}; tokens: {tokens}",
              f"- per-field decision entropy (bits) per decision: {entropies if entropies else 'n/a'}", "",
              "## Positions"]
    for r in opened:
        p = r["position"]
        lines.append(f"- opened {p['opened_ts'][:19]} {p['underlying']} x{p['contracts']} credit {p['entry_credit']:.2f} "
                     f"max loss {p['max_loss_total']:.0f} rung {r.get('fill_rung')} slippage {r.get('slippage_vs_mid_usd', 0):+.2f}")
    for r in closed:
        lines.append(f"- closed {r['ts'][:19]} {r['position_id']} reason '{r['reason']}' exit {r['exit_debit']:.2f} pnl {r['pnl']:+.2f}")
    if event_vols:
        ev = event_vols[-1]
        lines += ["", "## Term-structure event variance (Dubinsky et al. 2019 Eq. 4)",
                  f"- last reading: sigma_event = {ev.get('sigma_event')} between {ev.get('expiry_short')} and {ev.get('expiry_long')} (IV {ev.get('iv_short')} vs {ev.get('iv_long')})"]
    if conf_iv or conf_led or conf_eod or conf_err:
        lines += ["", "## Conformal Condor: P-versus-Q ledger (gate 31)",
                  "Q = credit / wing at the expected fill (the market's price of the band); P = the empirical payout ratio at the candidate's "
                  "strikes, shown for the reader. Rule crc: trade iff Q - beta* >= margin with the short strikes at or beyond the certified radius; "
                  "rule fixed (pilot): Q_mid - P_mid >= margin."]
        for r in conf_iv:
            s = r["session"]
            lines.append(f"- interval committed {r['ts'][:19]} ({s.get('rule')}): beta_t {s.get('beta_t', 0):.4f} -> k_crc {s.get('k_crc', 0):.3f}, "
                         f"alpha_t {s['alpha_t']:.4f} -> k_cov {s.get('k_cov', 0):.3f}, n {s['n']}, chosen k {s['k']:.3f} (clipped {s['clipped']}), "
                         f"VIX prev {s['vix_prev']}, implied ref move {s['impl_ref_usd']:.2f} $, wing {s.get('wing_usd')}, anchor spot {s['spot_entry']}")
        # one row per distinct (strikes, decision), with the evaluation count and the gap range
        agg: dict = {}
        for r in conf_led:
            l, c, cf = r["ledger"], r["candidate"], r.get("counterfactual_fixed") or {}
            key = (c["short_put"], c["short_call"], bool(l["passes"]))
            a = agg.setdefault(key, {"first": r["ts"][11:19], "last": r["ts"][11:19], "n": 0, "gaps": [], "q": [], "p": [],
                                     "credit": [], "cf_gap": cf.get("gap"), "cf_strikes": (cf.get("candidate") or {}).get("short_put")})
            a["last"] = r["ts"][11:19]; a["n"] += 1; a["gaps"].append(l["gap"]); a["q"].append(l.get("q_ref", l["q_mid"]))
            a["p"].append(l.get("beta_empirical", l["p_mid"]))
            a["credit"].append(c["credit_mid"])
        if agg:
            lines += ["", "| UTC first-last | n | shorts | credit mid | credit/wing (Q) | empirical payout at strikes (P) | gate gap vs beta* (min..max) | decision | fixed-rule gap |",
                      "|---|---|---|---|---|---|---|---|---|"]
            for (sp, sc, ok), a in agg.items():
                lines.append(f"| {a['first']}-{a['last']} | {a['n']} | {sp:.0f}/{sc:.0f} | {sum(a['credit']) / a['n']:.3f} | "
                             f"{sum(a['q']) / a['n']:.3f} | {sum(a['p']) / a['n']:.3f} | {min(a['gaps']):+.3f}..{max(a['gaps']):+.3f} | "
                             f"{'TRADE' if ok else 'NO_TRADE'} | {a['cf_gap'] if a['cf_gap'] is None else format(a['cf_gap'], '+.3f')} |")
        for r in conf_eod:
            c = r["record"]
            lines.append(f"- after the close: realised ratio {c['ratio']:.3f} vs k {c['k']:.3f} -> payout ratio {c.get('loss', 0):.3f}, "
                         f"beta {c.get('beta_before', 0):.4f} -> {c.get('beta_after', 0):.4f}; coverage track "
                         f"{'OUTSIDE' if c['err'] else 'inside'}, alpha {c['alpha_before']:.4f} -> {c['alpha_after']:.4f}"
                         f"{' (interval reconstructed at the 10:30 bar)' if c.get('reconstructed') else ''}")
        for r in conf_err[-5:]:
            lines.append(f"- error {r['ts'][:19]}: {r.get('error')}")
    if marks:
        eq = [m["equity"] for m in marks]
        lines += ["", "## Equity marks", f"- first {eq[0]:.2f}, last {eq[-1]:.2f}, min {min(eq):.2f}, max {max(eq):.2f} over {len(eq)} marks"]
    if halts:
        lines += ["", "## Halts"] + [f"- {h['ts'][:19]}: {h['reason']}" for h in halts]
    lines += ["", "## Not reported, on purpose",
              "- Sharpe ratio, win rate, annualised return, profit factor: with a handful of observations these are noise "
              "(Bailey & Lopez de Prado 2014; MinTRL for an annualised Sharpe of 1.0 at skew -1.5 / kurtosis 6 is 751 daily observations)."]
    summary = {"session": session, "records": len(recs), "kinds": dict(kinds), "gate_pass": dict(gate_pass),
               "gate_fail": dict(gate_fail), "no_trade": dict(no_trade), "opened": len(opened), "closed": len(closed),
               "pnl_realized": pnl, "slippage_usd": slippage, "fill_rungs": {str(k): v for k, v in rungs.items()},
               "llm_latency_ms": lat, "critic_verdicts": dict(verdicts), "families": dict(families),
               "unanimity": dict(unanimous), "entropies": entropies,
               "conformal": {"intervals": [r["session"] for r in conf_iv], "evaluations": len(conf_led),
                             "decisions": dict(Counter("TRADE" if r["ledger"]["passes"] else "NO_TRADE" for r in conf_led)),
                             "eod": [r["record"] for r in conf_eod], "errors": len(conf_err)}}
    return "\n".join(lines), summary


def main() -> None:
    session = None
    out = None
    if "--session" in sys.argv:
        session = sys.argv[sys.argv.index("--session") + 1]
    if "--out" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--out") + 1])
    recs = load(session)
    md, summary = build(recs, session)
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md, encoding="utf-8")
        out.with_suffix(".json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
        print(f"wrote {out} and {out.with_suffix('.json')}")
    else:
        print(md)


if __name__ == "__main__":
    main()

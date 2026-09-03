"""What the market offered for the band, all session long, against the gate.

Every evaluation cycle the strategy prices the balanced condor at the configured wing and rejects it when the
credit is below the gated floor (beta* + margin, as a fraction of the wing). Those rejections are in the audit log
as NO_TRADE reasons; candidates that reached gate 31 are in the conformal ledger records; fills are in
position_opened. This script turns them into one picture per session: credit / wing over the day, the gate line,
the entry windows, and any fill. Pure-Python SVG plus a JSON series for the deck's native chart.

    python scripts/band_price.py                                   # today's session from state/audit.jsonl
    python scripts/band_price.py --session 2026-09-03 --audit state/audit.jsonl --out docs/band_price_2026-09-03.svg
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.core.config import ROOT, STATE_DIR  # noqa: E402

ET = ZoneInfo("America/New_York")
PAT = re.compile(r"wing (\d+): credit ([0-9.]+) < ([0-9.]+) \((\d+)% of wing\)")


def load(p: Path) -> list[dict]:
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def et_minutes(ts: str) -> float:
    t = datetime.fromisoformat(ts).astimezone(ET)
    return t.hour * 60 + t.minute + t.second / 60


def series(recs: list[dict], session: str) -> dict:
    """Balanced-condor credit / wing per evaluation (first wing tried), gate floor, candidates at gate 31, fills."""
    offered, floor_pct, wing_used = [], None, None
    for r in recs:
        if r.get("session") != session:
            continue
        if r["kind"] == "no_trade":
            m = PAT.search(r.get("reason") or "")
            if m:
                wing, credit, floor, pct = int(m.group(1)), float(m.group(2)), float(m.group(3)), int(m.group(4))
                if abs(floor - pct / 100.0 * wing) > 1e-6:      # ratio structures carry a scaled floor: not the balanced condor
                    continue
                if wing_used is None:
                    wing_used, floor_pct = wing, pct / 100.0
                if wing == wing_used:
                    offered.append((et_minutes(r["ts"]), credit / wing))
        elif r["kind"] == "conformal":
            l, c = r["ledger"], r["candidate"]
            q = l.get("q_ref", l.get("q_mid"))
            if q is not None:
                offered.append((et_minutes(r["ts"]), float(q)))
        elif r["kind"] == "position_opened":
            p = r["position"]
            wing = abs(float(p["legs"][0]["strike"]) - float(p["legs"][1]["strike"])) or 1.0
            offered.append((et_minutes(r["ts"]), float(p["entry_credit"]) / wing, "fill"))
    offered.sort()
    return {"session": session, "wing": wing_used, "floor": floor_pct, "points": offered}


def svg(s: dict, beta_star: float, margin: float, windows: list[tuple[str, str]], width: int = 860, height: int = 360) -> str:
    pts = [p for p in s["points"] if len(p) == 2]
    fills = [p for p in s["points"] if len(p) == 3]
    floor = s["floor"] if s["floor"] is not None else beta_star + margin
    x0, x1 = 9 * 60 + 30, 16 * 60          # 09:30 .. 16:00 ET
    y_max = max(0.30, max([p[1] for p in pts] + [floor]) * 1.15) if pts else 0.30
    L, R, T, B = 64, 24, 40, 56
    pw, ph = width - L - R, height - T - B

    def X(m: float) -> float:
        return L + pw * (m - x0) / (x1 - x0)

    def Y(v: float) -> float:
        return T + ph * (1 - min(v, y_max) / y_max)

    def hhmm(m: int) -> str:
        return f"{m // 60:02d}:{m % 60:02d}"

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" role="img" '
           f'aria-label="credit over wing offered by the market during the session versus the gate" font-family="Segoe UI,system-ui,sans-serif" font-size="12">',
           f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>']
    for a, b in windows:                       # entry windows as pale bands
        ma, mb = [int(t[:2]) * 60 + int(t[3:5]) for t in (a, b)]
        out.append(f'<rect x="{X(ma):.1f}" y="{T}" width="{X(mb) - X(ma):.1f}" height="{ph}" fill="#FCD72B" opacity="0.18"/>')
        out.append(f'<text x="{X(ma) + 4:.1f}" y="{T + 14}" fill="#6a6a66">entry window {a}-{b} ET</text>')
    for v in [i / 20 for i in range(int(y_max * 20) + 1)]:   # gridlines every 0.05
        out.append(f'<line x1="{L}" y1="{Y(v):.1f}" x2="{width - R}" y2="{Y(v):.1f}" stroke="#e4e2dc" stroke-width="1"/>')
        out.append(f'<text x="{L - 8}" y="{Y(v) + 4:.1f}" text-anchor="end" fill="#6a6a66">{v:.2f}</text>')
    for m in range(x0, x1 + 1, 60):
        out.append(f'<text x="{X(m):.1f}" y="{height - B + 18}" text-anchor="middle" fill="#6a6a66">{hhmm(m)}</text>')
    out.append(f'<line x1="{L}" y1="{Y(beta_star):.1f}" x2="{width - R}" y2="{Y(beta_star):.1f}" stroke="#461D9C" stroke-width="1.2" stroke-dasharray="5 4"/>')
    out.append(f'<text x="{width - R - 4}" y="{Y(beta_star) - 5:.1f}" text-anchor="end" fill="#461D9C">beta* = {beta_star:.2f} (certified payout / wing)</text>')
    out.append(f'<line x1="{L}" y1="{Y(floor):.1f}" x2="{width - R}" y2="{Y(floor):.1f}" stroke="#101010" stroke-width="2"/>')
    out.append(f'<text x="{width - R - 4}" y="{Y(floor) - 5:.1f}" text-anchor="end" fill="#101010" font-weight="600">gate: credit / wing &#8805; beta* + margin = {floor:.2f}</text>')
    if pts:
        out.append('<polyline fill="none" stroke="#a33a2a" stroke-width="1.6" points="' + " ".join(f"{X(m):.1f},{Y(v):.1f}" for m, v in pts) + '"/>')
        for m, v in pts:
            out.append(f'<circle cx="{X(m):.1f}" cy="{Y(v):.1f}" r="2.2" fill="#a33a2a"/>')
        lo, hi = min(v for _, v in pts), max(v for _, v in pts)
        out.append(f'<text x="{L + 4}" y="{height - B - 6}" fill="#a33a2a">offered by the market for the balanced condor at wing {s["wing"]} $: '
                   f'{lo:.3f} to {hi:.3f} of the wing, {len(pts)} evaluations, never at the gate</text>' if not fills else
                   f'<text x="{L + 4}" y="{height - B - 6}" fill="#a33a2a">offered by the market at wing {s["wing"]} $: {lo:.3f} to {hi:.3f} of the wing, {len(pts)} evaluations</text>')
    else:
        out.append(f'<text x="{L + 4}" y="{T + ph / 2:.1f}" fill="#6a6a66">no priced candidate in this session</text>')
    for m, v, _ in fills:
        out.append(f'<circle cx="{X(m):.1f}" cy="{Y(v):.1f}" r="6" fill="#1f7a4d"/>')
        out.append(f'<text x="{X(m) + 9:.1f}" y="{Y(v) + 4:.1f}" fill="#1f7a4d" font-weight="600">filled at {v:.3f}</text>')
    out.append(f'<text x="{L}" y="{T - 16}" fill="#101010" font-size="15" font-weight="600">Session {s["session"]}: what the market paid for the band versus the gate</text>')
    out.append(f'<text x="{width / 2:.0f}" y="{height - 8}" text-anchor="middle" fill="#6a6a66">time (ET); y = credit / wing at the expected fill; the gate opens only above the black line</text>')
    out.append("</svg>")
    return "".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", default=str(STATE_DIR / "audit.jsonl"))
    ap.add_argument("--session", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    recs = load(Path(a.audit))
    session = a.session or (max({r.get("session") for r in recs if r.get("session")}) if recs else date.today().isoformat())
    from agent.core.config import Settings
    strat = Settings().strategy
    conf = strat.get("conformal", {}) or {}
    beta_star = float(conf.get("beta_target", 0.10))
    margin = float(conf.get("margin", 0.05))
    windows = [(str(w[0])[:5], str(w[1])[:5]) for w in (strat.get("entry_windows_et", {}) or {}).get(session, [])]
    s = series(recs, session)
    out = Path(a.out) if a.out else ROOT / "docs" / f"band_price_{session}.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg(s, beta_star, margin, windows), encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps({**s, "beta_star": beta_star, "margin": margin, "windows": windows,
                                                     "points": [[round(m, 2), round(v, 4)] + list(p[2:]) for p in s["points"] for m, v in [p[:2]]]},
                                                    indent=1), encoding="utf-8")
    print("wrote", out, "and", out.with_suffix(".json"), f"({len(s['points'])} points, wing {s['wing']}, floor {s['floor']})")


if __name__ == "__main__":
    main()

"""The picture that makes the rule legible: the empirical payout-ratio curve R_n(k) over the trailing calibration
window, its finite-sample inflation n/(n+1) R_n(k) + 1/(n+1), the pre-registered level beta*, and the certified
radius k_hat where the inflated curve first crosses beta*. Pure-Python SVG, no plotting dependency.

    python scripts/risk_curve.py                       # -> docs/risk_curve.svg from state/conformal.json
    python scripts/risk_curve.py --state s.json --out f.svg [--omega 0.64] [--beta 0.10]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.core.config import ROOT, STATE_DIR  # noqa: E402
from agent.core.conformal import ConformalParams, crc_certified, crc_radius, crc_risk  # noqa: E402


def svg_curve(scores: list[float], omega: float, beta: float, k_max: float = 1.6, width: int = 860, height: int = 440) -> str:
    n = len(scores)
    ks = [i * k_max / 320 for i in range(321)]
    raw = [crc_risk(scores, k, omega) for k in ks]
    inf = [crc_certified(scores, k, omega) for k in ks]
    k_hat = crc_radius(scores, omega, beta)
    y_max = max(0.5, min(1.0, max(inf[:20]) * 1.05))
    L, R, T, B = 70, 30, 30, 60          # margins
    pw, ph = width - L - R, height - T - B

    def X(k: float) -> float:
        return L + pw * k / k_max

    def Y(v: float) -> float:
        return T + ph * (1 - min(v, y_max) / y_max)

    def path(vals: list[float]) -> str:
        return "M " + " L ".join(f"{X(k):.1f},{Y(v):.1f}" for k, v in zip(ks, vals))

    ticks_x = [i / 4 for i in range(int(k_max * 4) + 1)]
    ticks_y = [i / 10 for i in range(int(y_max * 10) + 1)]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13">',
             f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
             f'<text x="{L}" y="18" font-size="15" font-weight="600">Payout ratio of the condor buyer vs. radius of the interval (trailing {n} sessions, wing = {omega:.2f} implied moves)</text>']
    for t in ticks_y:
        parts.append(f'<line x1="{L}" y1="{Y(t):.1f}" x2="{width - R}" y2="{Y(t):.1f}" stroke="#e5e7eb"/>')
        parts.append(f'<text x="{L - 8}" y="{Y(t) + 4:.1f}" text-anchor="end" fill="#374151">{t:.1f}</text>')
    for t in ticks_x:
        parts.append(f'<line x1="{X(t):.1f}" y1="{T}" x2="{X(t):.1f}" y2="{height - B}" stroke="#f3f4f6"/>')
        parts.append(f'<text x="{X(t):.1f}" y="{height - B + 18}" text-anchor="middle" fill="#374151">{t:.2f}</text>')
    parts.append(f'<text x="{L + pw / 2:.1f}" y="{height - 14}" text-anchor="middle" fill="#111827">short-strike distance k, in implied moves (|close / entry - 1| / VIX-implied E|move|)</text>')
    parts.append(f'<text transform="translate(16,{T + ph / 2:.1f}) rotate(-90)" text-anchor="middle" fill="#111827">expected payout / wing</text>')
    # beta* line
    parts.append(f'<line x1="{L}" y1="{Y(beta):.1f}" x2="{width - R}" y2="{Y(beta):.1f}" stroke="#b91c1c" stroke-dasharray="6 4" stroke-width="1.5"/>')
    parts.append(f'<text x="{width - R - 4}" y="{Y(beta) - 6:.1f}" text-anchor="end" fill="#b91c1c">beta* = {beta:.2f} (pre-registered)</text>')
    # curves
    parts.append(f'<path d="{path(raw)}" fill="none" stroke="#2563eb" stroke-width="2"/>')
    parts.append(f'<path d="{path(inf)}" fill="none" stroke="#111827" stroke-width="2.2"/>')
    # k_hat marker
    parts.append(f'<line x1="{X(k_hat):.1f}" y1="{T}" x2="{X(k_hat):.1f}" y2="{height - B}" stroke="#059669" stroke-width="1.5" stroke-dasharray="3 3"/>')
    parts.append(f'<circle cx="{X(k_hat):.1f}" cy="{Y(beta):.1f}" r="5" fill="#059669"/>')
    parts.append(f'<text x="{X(k_hat) + 8:.1f}" y="{T + 16}" fill="#059669" font-weight="600">k_hat = {k_hat:.3f}: smallest radius certified at beta*</text>')
    parts.append(f'<text x="{X(k_hat) + 8:.1f}" y="{T + 32}" fill="#065f46">short strikes at spot +- k_hat x implied move (rounded outward)</text>')
    # legend
    lx, ly = L + 12, T + ph - 46
    parts.append(f'<rect x="{lx - 6}" y="{ly - 14}" width="330" height="52" fill="#ffffff" fill-opacity="0.9" stroke="#e5e7eb"/>')
    parts.append(f'<line x1="{lx}" y1="{ly}" x2="{lx + 26}" y2="{ly}" stroke="#2563eb" stroke-width="2"/><text x="{lx + 32}" y="{ly + 4}">R_n(k): empirical payout ratio of the calibration set</text>')
    parts.append(f'<line x1="{lx}" y1="{ly + 20}" x2="{lx + 26}" y2="{ly + 20}" stroke="#111827" stroke-width="2.2"/><text x="{lx + 32}" y="{ly + 24}">n/(n+1) R_n(k) + 1/(n+1): the certified curve (Theorem 3)</text>')
    parts.append('</svg>')
    return "\n".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default=str(STATE_DIR / "conformal.json"))
    ap.add_argument("--out", default=str(ROOT / "docs" / "risk_curve.svg"))
    ap.add_argument("--omega", type=float, default=None, help="wing / implied move; default: the last ledger record's omega")
    ap.add_argument("--beta", type=float, default=None)
    args = ap.parse_args()
    st = json.loads(Path(args.state).read_text(encoding="utf-8"))
    p = ConformalParams.from_config(st.get("params"))
    scores = st["scores"][-p.window:]
    omega = args.omega if args.omega is not None else float(st["ledger"][-1]["omega"])
    beta = args.beta if args.beta is not None else p.beta_target
    svg = svg_curve(scores, omega, beta, k_max=p.k_max)
    Path(args.out).write_text(svg, encoding="utf-8")
    print(f"wrote {args.out}: n={len(scores)} omega={omega:.3f} beta*={beta} k_hat={crc_radius(scores, omega, beta):.4f}")


if __name__ == "__main__":
    main()

"""Conformal Condor: calibrated short strikes and the P-versus-Q coverage gate (gate 31).

An iron condor's short strikes are a prediction interval for the session close. This module
builds that interval by split conformal prediction on the nonconformity score

    r = |close / p_entry - 1| * 100 / impl_move_ref_pct

where impl_move_ref_pct = VIX_prev / 100 / sqrt(252) * sqrt(2 / pi) * 100 is the VIX-implied expected
absolute daily move in percent of spot. It is the same quantity as ``impl_move_cc`` in
``scripts/history_data.py``, so the live score and the historical calibration set share one unit.
Adaptive conformal inference (Gibbs & Candes 2021, NeurIPS) moves the miscoverage level alpha_t after
every session, traded or not, with the fixed, pre-registered step gamma.

The market's price of the same interval is read off the quote. For a vertical spread of width w the
credit divided by w is, to first order in w, the risk-neutral probability of finishing beyond the
midpoint of the spread (Breeden & Litzenberger 1978, digital limit). The physical counterpart is the
conformal p-value of the same midpoint distance in the calibration set. To the same order the expected
payoff of one package is

    E_P[payoff] ~= w * (Q_mid - P_mid)

so the coverage gate trades only when Q_mid - P_mid >= margin. The margin (5 probability points at a
0.5 % wing, about $20 per contract) is the modelled round-trip cost of four legs, not a tuning knob.
Evidence and the refutation of the width-changing variant: research/G_conformal_condor.md.

Pure functions plus a small JSON-backed state. No network, no LLM.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Mapping, Optional, Sequence

from agent.core.models import CondorCandidate

SQRT_2_OVER_PI = math.sqrt(2.0 / math.pi)


# --------------------------------------------------------------------------- units
def impl_move_ref_pct(vix_prev: float) -> float:
    """VIX-implied expected absolute daily move, in percent of spot (== history impl_move_cc)."""
    return vix_prev / 100.0 / math.sqrt(252.0) * SQRT_2_OVER_PI * 100.0


def realized_ratio(p_entry: float, p_close: float, impl_pct: float) -> float:
    """Nonconformity score of one session: absolute move from the entry price in implied-move units."""
    if p_entry <= 0 or impl_pct <= 0:
        raise ValueError("entry price and implied move must be positive")
    return abs(p_close / p_entry - 1.0) * 100.0 / impl_pct


# --------------------------------------------------------------------------- conformal arithmetic
def conformal_quantile(scores: Sequence[float], alpha: float) -> tuple[float, float]:
    """Split-conformal radius at miscoverage alpha: the ceil((n+1)(1-alpha))/n empirical quantile
    (method 'higher'). Returns (k, level). With alpha <= 1/(n+1) the level is 1 and k is the maximum."""
    n = len(scores)
    if n == 0:
        raise ValueError("no calibration scores")
    level = min(1.0, math.ceil((n + 1) * (1.0 - alpha)) / n)
    srt = sorted(scores)
    idx = min(n - 1, max(0, math.ceil(level * n) - 1))
    return float(srt[idx]), level


def p_outside(scores: Sequence[float], k: float) -> float:
    """Conformal p-value that a new session's score exceeds k: (1 + #{r_i > k}) / (n + 1)."""
    n = len(scores)
    if n == 0:
        raise ValueError("no calibration scores")
    return (1 + sum(1 for r in scores if r > k)) / (n + 1)


def aci_update(alpha: float, err: int, alpha_target: float, gamma: float,
               lo: float = 0.02, hi: float = 0.40) -> float:
    """Gibbs-Candes adaptive conformal inference step: alpha_{t+1} = alpha_t + gamma (alpha* - err_t)."""
    return min(hi, max(lo, alpha + gamma * (alpha_target - err)))


def expected_payout_outside(scores: Sequence[float], k: float, impl_usd: float, wing_usd: float) -> Optional[float]:
    """E[X | r > k] where X = min((r - k) * impl_usd, wing_usd) is the gross payout on the breached side,
    from the calibration set. None when no score lies outside."""
    xs = [min((r - k) * impl_usd, wing_usd) for r in scores if r > k]
    if not xs:
        return None
    return sum(xs) / len(xs)


# --------------------------------------------------------------------------- parameters and state
@dataclass(frozen=True)
class ConformalParams:
    enabled: bool = True
    alpha_target: float = 0.20      # 80 % coverage interval
    gamma: float = 0.005            # ACI step, pre-registered (research/G)
    window: int = 250               # trailing calibration scores
    k_min: float = 0.35             # tradability clip on the radius, in implied-move units
    k_max: float = 1.60
    margin: float = 0.05            # probability points of cushion in the coverage gate
    horizon: str = "ratio_1030"     # history column used for the back-fill
    min_scores: int = 50            # below this the interval is not defined (state is 'cold')
    alpha_lo: float = 0.02
    alpha_hi: float = 0.40

    @classmethod
    def from_config(cls, cfg: Optional[Mapping]) -> "ConformalParams":
        cfg = dict(cfg or {})
        allowed = {k: cfg[k] for k in cls.__dataclass_fields__ if k in cfg}
        return cls(**allowed)


@dataclass
class Interval:
    k_raw: float
    k: float
    clipped: bool
    level: float
    n: int
    alpha_t: float


@dataclass
class ConformalState:
    alpha_t: float
    scores: list[float] = field(default_factory=list)
    ledger: list[dict] = field(default_factory=list)        # one record per calibrated session
    session: Optional[dict] = None                           # today's committed interval
    updated_through: str = ""                                # last session date folded into the scores
    source: str = ""
    params: dict = field(default_factory=dict)

    # persistence -------------------------------------------------------------
    @classmethod
    def load(cls, path: Path) -> "ConformalState":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(alpha_t=float(raw["alpha_t"]), scores=[float(x) for x in raw.get("scores", [])],
                   ledger=list(raw.get("ledger", [])), session=raw.get("session"),
                   updated_through=str(raw.get("updated_through", "")), source=str(raw.get("source", "")),
                   params=dict(raw.get("params", {})))

    def save(self, path: Path) -> None:
        path = Path(path)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(asdict(self), indent=1), encoding="utf-8")
        tmp.replace(path)

    # interval ----------------------------------------------------------------
    def window_scores(self, p: ConformalParams) -> list[float]:
        return self.scores[-p.window:]

    def interval(self, p: ConformalParams, alpha: Optional[float] = None) -> Interval:
        scores = self.window_scores(p)
        if len(scores) < p.min_scores:
            raise ValueError(f"conformal state cold: {len(scores)} scores < {p.min_scores}")
        a = self.alpha_t if alpha is None else alpha
        k_raw, level = conformal_quantile(scores, a)
        k = min(p.k_max, max(p.k_min, k_raw))
        return Interval(k_raw=k_raw, k=k, clipped=(k != k_raw), level=level, n=len(scores), alpha_t=a)


def open_session(st: ConformalState, p: ConformalParams, day: date, ts: datetime, spot_entry: float,
                 vix_prev: float, reconstructed: bool = False) -> dict:
    """Commit today's interval: radius k from the current alpha_t and scores, anchored at spot_entry.
    Called once per session (first evaluation inside the entry window, or reconstructed at 10:30 from bars)."""
    iv = st.interval(p)
    impl_pct = impl_move_ref_pct(vix_prev)
    sess = {
        "date": day.isoformat(), "ts": ts.isoformat(), "spot_entry": float(spot_entry), "vix_prev": float(vix_prev),
        "impl_ref_pct": impl_pct, "impl_ref_usd": impl_pct / 100.0 * spot_entry,
        "alpha_t": iv.alpha_t, "n": iv.n, "level": iv.level, "k_raw": iv.k_raw, "k": iv.k, "clipped": iv.clipped,
        "reconstructed": reconstructed,
    }
    st.session = sess
    return sess


def eod_update(st: ConformalState, p: ConformalParams, close: float, day: date) -> dict:
    """After the close: score the committed interval, move alpha_t, append the score. Every session counts,
    traded or not, because calibration is a property of the forecast and not of the trade."""
    sess = st.session
    if not sess or sess.get("date") != day.isoformat():
        raise ValueError("no committed interval for this session")
    ratio = realized_ratio(sess["spot_entry"], close, sess["impl_ref_pct"])
    err = 1 if ratio > sess["k"] else 0
    alpha_before = st.alpha_t
    st.alpha_t = aci_update(st.alpha_t, err, p.alpha_target, p.gamma, p.alpha_lo, p.alpha_hi)
    st.scores.append(ratio)
    st.scores = st.scores[-max(p.window, 400):]
    rec = {"date": day.isoformat(), "k": sess["k"], "alpha_before": alpha_before, "ratio": ratio, "err": err,
           "alpha_after": st.alpha_t, "close": close, "spot_entry": sess["spot_entry"],
           "reconstructed": bool(sess.get("reconstructed", False))}
    st.ledger.append(rec)
    st.ledger = st.ledger[-1000:]
    st.updated_through = day.isoformat()
    st.session = None
    return rec


def backfill(rows: Sequence[tuple[str, float]], p: ConformalParams, alpha0: Optional[float] = None,
             source: str = "") -> ConformalState:
    """Replay ACI through a dated history of scores so the agent starts calibrated, not cold.
    rows: (date_iso, ratio) in chronological order. Deterministic."""
    st = ConformalState(alpha_t=p.alpha_target if alpha0 is None else alpha0, source=source, params=asdict(p))
    for d, ratio in rows:
        if len(st.scores) >= p.min_scores:
            iv = st.interval(p)
            err = 1 if ratio > iv.k else 0
            a0 = st.alpha_t
            st.alpha_t = aci_update(st.alpha_t, err, p.alpha_target, p.gamma, p.alpha_lo, p.alpha_hi)
            st.ledger.append({"date": d, "k": iv.k, "k_raw": iv.k_raw, "alpha_before": a0, "ratio": ratio, "err": err,
                              "alpha_after": st.alpha_t, "reconstructed": True})
        st.scores.append(float(ratio))
        st.updated_through = d
    st.scores = st.scores[-max(p.window, 400):]
    return st


def coverage_stats(ledger: Sequence[Mapping], since: str = "") -> dict:
    recs = [r for r in ledger if r["date"] >= since]
    if not recs:
        return {"n": 0}
    cov = 1.0 - sum(r["err"] for r in recs) / len(recs)
    ks = [r["k"] for r in recs]
    k_mean = sum(ks) / len(ks)
    by_year: dict[str, dict] = {}
    for r in recs:
        y = r["date"][:4]
        b = by_year.setdefault(y, {"n": 0, "err": 0, "k_sum": 0.0})
        b["n"] += 1
        b["err"] += r["err"]
        b["k_sum"] += r["k"]
    return {"n": len(recs), "coverage": cov, "k_mean": k_mean,
            "k_sd": (sum((k - k_mean) ** 2 for k in ks) / max(1, len(ks) - 1)) ** 0.5,
            "alpha_last": recs[-1]["alpha_after"],
            "by_year": {y: {"n": b["n"], "coverage": 1 - b["err"] / b["n"], "k_mean": b["k_sum"] / b["n"]}
                        for y, b in sorted(by_year.items())}}


# --------------------------------------------------------------------------- the ledger for one candidate
def kelly_exhibit(credit_usd: float, wing_usd: float, p_inside: float, n: int,
                  payout_outside_usd: Optional[float]) -> dict:
    """Kelly for a condor, per research/G section 4.3. An exhibit: it demonstrates that the 2 % cap binds
    (or that Kelly is negative); it never sets a size."""
    L = wing_usd - credit_usd
    b = credit_usd / L if L > 0 else float("inf")
    f_two = p_inside - (1.0 - p_inside) / b if b > 0 else float("-inf")
    out: dict = {"b": b, "p_inside": p_inside, "break_even_two_state": 1.0 / (1.0 + b) if b > 0 else None,
                 "f_two_state": f_two}
    lbar = (payout_outside_usd - credit_usd) if payout_outside_usd is not None else None
    if lbar is not None and lbar > 0:
        f_three = (p_inside * credit_usd - (1 - p_inside) * lbar) / (credit_usd * lbar / (credit_usd + lbar))
        out["break_even_three_state"] = lbar / (credit_usd + lbar)
    else:
        f_three = f_two
        out["break_even_three_state"] = None
    out["loss_given_outside_usd"] = lbar
    se_p = math.sqrt(max(p_inside * (1 - p_inside), 1e-9) / max(n, 1))
    if f_three > 0 and b > 0:
        f_shrunk = f_three * max(0.0, 1.0 - 2.0 * se_p * (1.0 + b) / b / f_three)
    else:
        f_shrunk = 0.0
    out.update({"f_three_state": f_three, "se_p": se_p, "f_shrunk": f_shrunk, "f_quarter": f_shrunk / 4.0,
                "f_used": min(f_shrunk / 4.0, 0.02), "binding_constraint": "cap" if f_shrunk / 4.0 >= 0.02 else "kelly"})
    return out


def ledger_for_candidate(cand: CondorCandidate, st: ConformalState, p: ConformalParams, session: Mapping) -> dict:
    """The P-versus-Q ledger for one candidate: what the market pays for the interval (Q, from the quote)
    against what the calibration says it is worth (P, from the scores). Everything the coverage gate and
    the write-up need, reproducible from the audit record alone."""
    scores = st.window_scores(p)
    impl_usd = float(session["impl_ref_usd"])
    spot = cand.spot
    d_call = cand.short_call.quote.strike - spot
    d_put = spot - cand.short_put.quote.strike
    d_short = 0.5 * (d_call + d_put)
    w = cand.wing_width
    ratio = max(cand.short_call.ratio, cand.short_put.ratio)
    k_eff = d_short / impl_usd
    k_mid = (d_short + 0.5 * w) / impl_usd
    p_short = p_outside(scores, k_eff)
    p_mid = p_outside(scores, k_mid)
    credit_1 = cand.credit_mid / ratio                      # credit per 1:1 package, $/share
    q_mid = credit_1 / w
    q_call = (cand.short_call.quote.mid - cand.long_call.quote.mid) / w
    q_put = (cand.short_put.quote.mid - cand.long_put.quote.mid) / w
    warnings: list[str] = []
    # Quote sanity: credit/wing is the average digital probability across the spread, so it must lie between
    # |delta| of the bought wing and |delta| of the short strike (near expiry |delta| ~ digital). Outside that
    # band the quote is stale, crossed or the Greeks are wrong; the gate rejects only on non-positive credit.
    for name, q_side, short, long in (("call", q_call, cand.short_call, cand.long_call),
                                      ("put", q_put, cand.short_put, cand.long_put)):
        ds, dl = short.quote.delta, long.quote.delta
        if ds is not None and dl is not None and not (abs(dl) - 0.05 <= q_side <= abs(ds) + 0.05):
            warnings.append(f"{name} side: credit/wing {q_side:.3f} outside the delta band [{abs(dl):.3f}, {abs(ds):.3f}]")
    if q_call <= 0 or q_put <= 0:
        warnings.append("a spread has non-positive mid credit (stale or crossed quote)")
    gap = q_mid - p_mid
    strict_gap = q_mid - p_short
    payout_out = expected_payout_outside(scores, k_eff, impl_usd, w)
    ev_digital = 100.0 * ratio * w * gap
    ev_hist = 100.0 * ratio * (credit_1 - p_short * payout_out) if payout_out is not None else None
    kelly = kelly_exhibit(credit_1 * 100.0, w * 100.0, 1.0 - p_short, len(scores),
                          payout_out * 100.0 if payout_out is not None else None)
    return {
        "rule": "Q_mid - P_mid >= margin (digital limit at the spread midpoint)",
        "alpha_target": p.alpha_target, "alpha_t": float(session["alpha_t"]), "gamma": p.gamma, "n_calibration": len(scores),
        "impl_ref_pct": float(session["impl_ref_pct"]), "impl_ref_usd": impl_usd, "vix_prev": float(session["vix_prev"]),
        "k_conformal": float(session["k"]), "k_clipped": bool(session["clipped"]), "k_effective": k_eff, "k_mid": k_mid,
        "short_distance_usd": d_short, "wing_usd": w, "ratio": ratio,
        "rounding_error_pp": p_short - p_outside(scores, float(session["k"])),
        "p_short": p_short, "p_mid": p_mid, "q_mid": q_mid, "q_call": q_call, "q_put": q_put,
        "delta_short_call": cand.short_call.quote.delta, "delta_short_put": cand.short_put.quote.delta,
        "gap": gap, "strict_gap": strict_gap, "margin": p.margin, "passes": gap >= p.margin - 1e-12,
        "ev_digital_usd_per_package": ev_digital, "ev_hist_usd_per_package": ev_hist,
        "expected_payout_outside_usd": payout_out * 100.0 if payout_out is not None else None,
        "break_even_p_inside": (1.0 - credit_1 / payout_out) if payout_out else None,
        "kelly": kelly, "warnings": warnings,
    }

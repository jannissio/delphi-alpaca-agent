"""Conformal Risk Control Condor: calibrated short strikes and the P-versus-Q gate (gate 31).

An iron condor's short strikes are a prediction interval for the session close, and its payout to the
buyer is a monotone, bounded loss of the interval's radius. Two calibration tracks share one state:

* **Coverage track** (split conformal + adaptive conformal inference, Gibbs & Candes 2021): radius k_cov
  such that the close leaves the interval with probability alpha_t; the miscoverage indicator is the loss.
* **Risk track** (conformal risk control, Angelopoulos, Bates, Fisch, Lei & Schuster, ICLR 2024; online
  version Rolling Risk Control, Feldman, Ringel, Bates & Romano, TMLR 2023): radius k_crc such that the
  *expected payout to the buyer*, in units of the wing, is at most beta_t. The loss is
      loss(r, k) = min((r - k)^+, omega) / omega in [0, 1],
  non-increasing in k and bounded, with omega = wing / implied move. The coverage track is the special
  case loss = 1{r > k}. Both use the nonconformity score

      r = |close / p_entry - 1| * 100 / impl_move_ref_pct,

  where impl_move_ref_pct = VIX_prev / 100 / sqrt(252) * sqrt(2/pi) * 100 is the VIX-implied expected
  absolute daily move in percent of spot, identical to ``impl_move_cc`` in ``scripts/history_data.py``.

The market's price of the same interval is read off the quote: credit / wing (Breeden & Litzenberger 1978,
digital limit; exactly the integral of the risk-neutral survival function across the wing band). The
expected payoff of one package is credit - E[payout], so the gate

      credit / wing  >=  beta_cert(k_eff) + margin

implies E_P[payoff] >= margin * wing under exchangeability of the scores (docs/THEORY.md, Theorem 3).
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


# --------------------------------------------------------------------------- coverage arithmetic
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


def online_update(level: float, loss: float, target: float, gamma: float, lo: float, hi: float) -> float:
    """One step of adaptive conformal inference / Rolling Risk Control: level += gamma (target - loss).
    A loss above target tightens the level, below target loosens it; clipped to [lo, hi]."""
    return min(hi, max(lo, level + gamma * (target - loss)))


def aci_update(alpha: float, err: int, alpha_target: float, gamma: float,
               lo: float = 0.02, hi: float = 0.40) -> float:
    """Gibbs-Candes adaptive conformal inference step (coverage track)."""
    return online_update(alpha, float(err), alpha_target, gamma, lo, hi)


# --------------------------------------------------------------------------- risk-control arithmetic
def crc_loss(r: float, k: float, omega: float) -> float:
    """Payout to the condor buyer in units of the wing: min((r - k)^+, omega) / omega, in [0, 1],
    non-increasing in k (docs/THEORY.md, Lemma 1)."""
    if omega <= 0:
        raise ValueError("wing in implied-move units must be positive")
    return min(max(r - k, 0.0), omega) / omega


def crc_risk(scores: Sequence[float], k: float, omega: float) -> float:
    """Empirical risk R_hat_n(k): mean payout ratio over the calibration scores."""
    if not scores:
        raise ValueError("no calibration scores")
    return sum(crc_loss(r, k, omega) for r in scores) / len(scores)


def crc_certified(scores: Sequence[float], k: float, omega: float) -> float:
    """Finite-sample certified risk at radius k: n/(n+1) R_hat_n(k) + 1/(n+1). Conformal risk control
    guarantees E[loss(r_{n+1}, k)] <= this value for any k chosen as the CRC threshold (Angelopoulos et al.
    2024, Theorem 1, with B = 1)."""
    n = len(scores)
    return n / (n + 1) * crc_risk(scores, k, omega) + 1.0 / (n + 1)


def crc_radius(scores: Sequence[float], omega: float, beta: float, tol: float = 1e-6) -> float:
    """Smallest radius whose certified risk is at most beta: k_hat = inf{k : n/(n+1) R_hat(k) + 1/(n+1) <= beta}.
    The certified risk is continuous and non-increasing in k, so bisection is exact up to tol."""
    n = len(scores)
    if n == 0:
        raise ValueError("no calibration scores")
    if beta < 1.0 / (n + 1):
        raise ValueError(f"beta {beta} below the 1/(n+1) floor of conformal risk control with n={n}")
    hi = max(scores)
    if crc_certified(scores, 0.0, omega) <= beta:
        return 0.0
    lo = 0.0
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if crc_certified(scores, mid, omega) <= beta:
            hi = mid
        else:
            lo = mid
    return hi


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
    rule: str = "crc"               # "crc" (risk track sets the strikes and the gate) or "coverage"
    alpha_target: float = 0.20      # coverage track: 80 % interval
    beta_target: float = 0.10       # risk track: expected payout <= 10 % of the wing
    gamma: float = 0.005            # online step for both tracks; fixed, not fitted
    window: int = 250               # trailing calibration scores
    k_min: float = 0.35             # tradability clip on the radius, in implied-move units
    k_max: float = 1.60
    margin: float = 0.05            # probability points / wing fraction of cushion in the gate
    credit_reference: str = "natural"   # gate 31 reads credit/wing at the expected fill ("natural") or at the "mid"
    horizon: str = "ratio_1030"     # history column used for the back-fill
    min_scores: int = 50            # below this the interval is not defined (state is 'cold')
    alpha_lo: float = 0.02
    alpha_hi: float = 0.40
    beta_lo: float = 0.02
    beta_hi: float = 0.30
    wing_pct_of_spot: float = 0.005  # default wing for omega when the caller passes none

    @classmethod
    def from_config(cls, cfg: Optional[Mapping]) -> "ConformalParams":
        cfg = dict(cfg or {})
        allowed = {k: cfg[k] for k in cls.__dataclass_fields__ if k in cfg}
        p = cls(**allowed)
        if p.rule not in ("crc", "coverage"):
            raise ValueError(f"conformal.rule must be 'crc' or 'coverage', got {p.rule!r}")
        if p.credit_reference not in ("mid", "natural"):
            raise ValueError(f"conformal.credit_reference must be 'mid' or 'natural', got {p.credit_reference!r}")
        return p


@dataclass
class ConformalState:
    alpha_t: float
    beta_t: float = 0.10
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
        return cls(alpha_t=float(raw["alpha_t"]), beta_t=float(raw.get("beta_t", 0.10)),
                   scores=[float(x) for x in raw.get("scores", [])],
                   ledger=list(raw.get("ledger", [])), session=raw.get("session"),
                   updated_through=str(raw.get("updated_through", "")), source=str(raw.get("source", "")),
                   params=dict(raw.get("params", {})))

    def save(self, path: Path) -> None:
        path = Path(path)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(asdict(self), indent=1), encoding="utf-8")
        tmp.replace(path)

    # radii -------------------------------------------------------------------
    def window_scores(self, p: ConformalParams) -> list[float]:
        return self.scores[-p.window:]

    def radii(self, p: ConformalParams, omega: float) -> dict:
        """Both tracks' radii from the current levels and scores. Raises when the state is cold."""
        scores = self.window_scores(p)
        if len(scores) < p.min_scores:
            raise ValueError(f"conformal state cold: {len(scores)} scores < {p.min_scores}")
        k_cov_raw, level = conformal_quantile(scores, self.alpha_t)
        # Risk track: the radius certified at the pre-registered level beta* gives the per-session bound
        # (Theorem 3); the online level beta_t may only tighten it (Theorem 4, one-sided long-run bound).
        k_crc_fixed = crc_radius(scores, omega, p.beta_target)
        k_crc_adaptive = crc_radius(scores, omega, self.beta_t)
        k_crc_raw = max(k_crc_fixed, k_crc_adaptive)
        clip = lambda k: min(p.k_max, max(p.k_min, k))  # noqa: E731
        k_cov, k_crc = clip(k_cov_raw), clip(k_crc_raw)
        k = k_crc if p.rule == "crc" else k_cov
        return {"n": len(scores), "omega": omega, "alpha_t": self.alpha_t, "beta_t": self.beta_t, "beta_star": p.beta_target,
                "level": level, "k_cov_raw": k_cov_raw, "k_cov": k_cov, "k_crc_fixed": k_crc_fixed,
                "k_crc_adaptive": k_crc_adaptive, "k_crc_raw": k_crc_raw, "k_crc": k_crc, "k": k,
                "clipped": (k != (k_crc_raw if p.rule == "crc" else k_cov_raw)), "rule": p.rule,
                "certified_at_k_crc_fixed": crc_certified(scores, k_crc_fixed, omega),
                "risk_hat_at_k": crc_risk(scores, k, omega), "empirical_risk_at_k": crc_certified(scores, k, omega)}


def open_session(st: ConformalState, p: ConformalParams, day: date, ts: datetime, spot_entry: float,
                 vix_prev: float, wing_usd: Optional[float] = None, reconstructed: bool = False) -> dict:
    """Commit today's interval: radii from the current levels and scores, anchored at spot_entry, for the
    wing the strategy will use. Called once per session (first evaluation inside the entry window, or
    reconstructed at 10:30 from bars)."""
    impl_pct = impl_move_ref_pct(vix_prev)
    impl_usd = impl_pct / 100.0 * spot_entry
    if wing_usd is None:
        wing_usd = max(3.0, p.wing_pct_of_spot * spot_entry)
    rad = st.radii(p, wing_usd / impl_usd)
    sess = {"date": day.isoformat(), "ts": ts.isoformat(), "spot_entry": float(spot_entry), "vix_prev": float(vix_prev),
            "impl_ref_pct": impl_pct, "impl_ref_usd": impl_usd, "wing_usd": float(wing_usd),
            "reconstructed": reconstructed, **rad}
    st.session = sess
    return sess


def eod_update(st: ConformalState, p: ConformalParams, close: float, day: date) -> dict:
    """After the close: score the committed interval on both tracks, move alpha_t and beta_t, append the
    score. Every session counts, traded or not: calibration is a property of the forecast, not of the trade."""
    sess = st.session
    if not sess or sess.get("date") != day.isoformat():
        raise ValueError("no committed interval for this session")
    ratio = realized_ratio(sess["spot_entry"], close, sess["impl_ref_pct"])
    err = 1 if ratio > sess["k_cov"] else 0
    loss = crc_loss(ratio, sess["k_crc"], sess["omega"])
    a0, b0 = st.alpha_t, st.beta_t
    st.alpha_t = aci_update(st.alpha_t, err, p.alpha_target, p.gamma, p.alpha_lo, p.alpha_hi)
    st.beta_t = online_update(st.beta_t, loss, p.beta_target, p.gamma, p.beta_lo, p.beta_hi)
    st.scores.append(ratio)
    st.scores = st.scores[-max(p.window, 400):]
    rec = {"date": day.isoformat(), "rule": sess.get("rule", p.rule), "k": sess["k"], "k_cov": sess["k_cov"], "k_crc": sess["k_crc"],
           "omega": sess["omega"], "ratio": ratio, "err": err, "loss": loss, "alpha_before": a0, "alpha_after": st.alpha_t,
           "beta_before": b0, "beta_after": st.beta_t, "close": close, "spot_entry": sess["spot_entry"],
           "reconstructed": bool(sess.get("reconstructed", False))}
    st.ledger.append(rec)
    st.ledger = st.ledger[-1000:]
    st.updated_through = day.isoformat()
    st.session = None
    return rec


def backfill(rows: Sequence[tuple], p: ConformalParams, alpha0: Optional[float] = None,
             beta0: Optional[float] = None, source: str = "") -> ConformalState:
    """Replay both online tracks through a dated history so the agent starts calibrated, not cold.
    rows: (date_iso, ratio, omega) in chronological order, omega = wing / implied move of that session.
    Deterministic."""
    st = ConformalState(alpha_t=p.alpha_target if alpha0 is None else alpha0,
                        beta_t=p.beta_target if beta0 is None else beta0, source=source, params=asdict(p))
    for row in rows:
        d, ratio, omega = row[0], float(row[1]), float(row[2])
        if len(st.scores) >= p.min_scores:
            rad = st.radii(p, omega)
            err = 1 if ratio > rad["k_cov"] else 0
            loss = crc_loss(ratio, rad["k_crc"], omega)
            a0, b0 = st.alpha_t, st.beta_t
            st.alpha_t = aci_update(st.alpha_t, err, p.alpha_target, p.gamma, p.alpha_lo, p.alpha_hi)
            st.beta_t = online_update(st.beta_t, loss, p.beta_target, p.gamma, p.beta_lo, p.beta_hi)
            st.ledger.append({"date": d, "rule": p.rule, "k": rad["k"], "k_cov": rad["k_cov"], "k_crc": rad["k_crc"],
                              "omega": omega, "ratio": ratio, "err": err, "loss": loss, "alpha_before": a0,
                              "alpha_after": st.alpha_t, "beta_before": b0, "beta_after": st.beta_t, "reconstructed": True})
        st.scores.append(ratio)
        st.updated_through = d
    st.scores = st.scores[-max(p.window, 400):]
    return st


def coverage_stats(ledger: Sequence[Mapping], since: str = "") -> dict:
    """Coverage and realised risk of both tracks, overall and by year."""
    recs = [r for r in ledger if r["date"] >= since]
    if not recs:
        return {"n": 0}

    def agg(rs):
        n = len(rs)
        kc = [r["k_cov"] for r in rs]
        kr = [r.get("k_crc", r["k"]) for r in rs]
        return {"n": n, "coverage": 1 - sum(r["err"] for r in rs) / n, "k_cov_mean": sum(kc) / n,
                "realized_risk": sum(r.get("loss", 0.0) for r in rs) / n, "k_crc_mean": sum(kr) / n}

    out = agg(recs)
    ks = [r["k_cov"] for r in recs]
    m = sum(ks) / len(ks)
    out["k_cov_sd"] = (sum((k - m) ** 2 for k in ks) / max(1, len(ks) - 1)) ** 0.5
    out["alpha_last"] = recs[-1]["alpha_after"]
    out["beta_last"] = recs[-1].get("beta_after")
    years = sorted({r["date"][:4] for r in recs})
    out["by_year"] = {y: agg([r for r in recs if r["date"][:4] == y]) for y in years}
    return out


# --------------------------------------------------------------------------- the ledger for one candidate
def kelly_exhibit(credit_usd: float, wing_usd: float, p_inside: float, n: int,
                  payout_outside_usd: Optional[float]) -> dict:
    """Kelly for a condor, per research/G section 4.3 and docs/THEORY.md Lemma 5. An exhibit: it shows that
    the 2 % cap binds (or that Kelly is negative); it never sets a size."""
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
    out["se_f_two_state"] = (1.0 + b) / b * se_p if b > 0 else None      # d f*/d p = (1+b)/b
    if f_three > 0 and b > 0:
        f_shrunk = f_three * max(0.0, 1.0 - 2.0 * se_p * (1.0 + b) / b / f_three)
    else:
        f_shrunk = 0.0
    out.update({"f_three_state": f_three, "se_p": se_p, "f_shrunk": f_shrunk, "f_quarter": f_shrunk / 4.0,
                "f_used": min(f_shrunk / 4.0, 0.02), "binding_constraint": "cap" if f_shrunk / 4.0 >= 0.02 else "kelly"})
    return out


def ledger_for_candidate(cand: CondorCandidate, st: ConformalState, p: ConformalParams, session: Mapping) -> dict:
    """The P-versus-Q ledger for one candidate: what the market pays for the interval (Q, from the quote)
    against what the calibration certifies it costs (P, from the scores). Everything gate 31 and the
    write-up need, reproducible from the audit record alone."""
    scores = st.window_scores(p)
    impl_usd = float(session["impl_ref_usd"])
    spot = cand.spot
    d_call = cand.short_call.quote.strike - spot
    d_put = spot - cand.short_put.quote.strike
    d_short = 0.5 * (d_call + d_put)
    w = cand.wing_width
    ratio = max(cand.short_call.ratio, cand.short_put.ratio)
    omega = w / impl_usd
    k_eff = min(d_call, d_put) / impl_usd          # the nearer short strike bounds the payout from above
    k_mid = (d_short + 0.5 * w) / impl_usd
    p_short = p_outside(scores, k_eff)
    p_mid = p_outside(scores, k_mid)
    credit_1 = cand.credit_mid / ratio                      # credit per 1:1 package at the mid, $/share
    credit_1_nat = cand.credit_natural / ratio              # ... and at the natural (sell at bid, buy at ask)
    q_mid = credit_1 / w                                    # = credit / wing: the market's price of the band, at the mid
    q_nat = credit_1_nat / w                                # the same price at the expected fill (paper fills only marketable orders)
    credit_1_ref, q_ref = (credit_1_nat, q_nat) if p.credit_reference == "natural" else (credit_1, q_mid)
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
    # risk track at the effective strikes: the certificate beta* holds only if the nearer short strike sits at or
    # beyond the radius certified at beta* (rounding outward keeps it; a delta-band shift inward would break it)
    risk_hat = crc_risk(scores, k_eff, omega)
    beta_empirical = crc_certified(scores, k_eff, omega)
    # The session committed omega for the default wing; the strategy may have narrowed the wing (smaller omega,
    # larger payout per breach), so the radius certified at beta* is re-derived for the wing actually traded and
    # the stricter of the two is binding. A k_max clip that binds means the certificate is void, not clipped.
    beta_star = float(session.get("beta_star", p.beta_target))
    k_cert_session = float(session.get("k_crc_fixed", session["k_crc"]))
    try:
        k_cert_wing = crc_radius(scores, omega, beta_star)
    except ValueError:
        k_cert_wing = float("inf")
    k_cert = max(k_cert_session, k_cert_wing)
    certified_ok = k_eff >= k_cert - 1e-9
    if not certified_ok:
        warnings.append(f"short strike inside the certified radius: k_eff {k_eff:.3f} < k_crc_fixed {k_cert:.3f}"
                        f" (session {k_cert_session:.3f}, at this wing {k_cert_wing:.3f})")
    beta_certified = beta_star if certified_ok else None
    # every gap is read at the credit reference (mid or expected fill); q_mid and q_nat are both reported
    gap_crc = (q_ref - beta_certified) if beta_certified is not None else float("-inf")
    gap_empirical = q_ref - beta_empirical
    gap_cov = q_ref - p_mid
    strict_gap = q_ref - p_short
    gate_gap = gap_crc if p.rule == "crc" else gap_cov
    payout_out = expected_payout_outside(scores, k_eff, impl_usd, w)
    kelly = kelly_exhibit(credit_1_ref * 100.0, w * 100.0, 1.0 - p_short, len(scores),
                          payout_out * 100.0 if payout_out is not None else None)
    return {
        "rule": p.rule,
        "rule_text": ("credit/wing - beta* >= margin, strikes at or beyond the radius certified at beta* (conformal risk control)" if p.rule == "crc"
                      else "Q_mid - P_mid >= margin (digital limit at the spread midpoint)"),
        "alpha_target": p.alpha_target, "alpha_t": float(session["alpha_t"]), "beta_target": p.beta_target,
        "beta_t": float(session["beta_t"]), "gamma": p.gamma, "n_calibration": len(scores),
        "impl_ref_pct": float(session["impl_ref_pct"]), "impl_ref_usd": impl_usd, "vix_prev": float(session["vix_prev"]),
        "k_conformal": float(session["k"]), "k_cov": float(session["k_cov"]), "k_crc": float(session["k_crc"]),
        "k_clipped": bool(session["clipped"]), "k_effective": k_eff, "k_mid": k_mid, "omega": omega,
        "short_distance_usd": d_short, "wing_usd": w, "ratio": ratio,
        "rounding_error_pp": p_short - p_outside(scores, float(session["k"])),
        "p_short": p_short, "p_mid": p_mid, "q_mid": q_mid, "q_nat": q_nat, "q_ref": q_ref, "credit_reference": p.credit_reference,
        "q_call": q_call, "q_put": q_put,
        "delta_short_call": cand.short_call.quote.delta, "delta_short_put": cand.short_put.quote.delta,
        "risk_hat": risk_hat, "beta_empirical": beta_empirical, "beta_certified": beta_certified,
        "k_crc_fixed": k_cert, "k_crc_fixed_session": k_cert_session, "k_crc_fixed_at_wing": k_cert_wing,
        "certified_ok": certified_ok,
        "gap_crc": gap_crc, "gap_empirical": gap_empirical, "gap_cov": gap_cov, "gap": gate_gap, "strict_gap": strict_gap,
        "margin": p.margin, "passes": gate_gap >= p.margin - 1e-12,
        "ev_lower_bound_usd_per_package": (100.0 * ratio * (credit_1_ref - beta_certified * w)) if beta_certified is not None else None,
        "ev_empirical_usd_per_package": 100.0 * ratio * (credit_1_ref - beta_empirical * w),
        "ev_digital_usd_per_package": 100.0 * ratio * w * gap_cov,
        "ev_hist_usd_per_package": (100.0 * ratio * (credit_1 - p_short * payout_out)) if payout_out is not None else None,
        "expected_payout_outside_usd": payout_out * 100.0 if payout_out is not None else None,
        "break_even_p_inside": (1.0 - credit_1 / payout_out) if payout_out else None,
        "kelly": kelly, "warnings": warnings,
    }

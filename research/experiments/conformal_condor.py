"""Conformal Condor prototype.

Research only. Does not touch agent/. Writes tables to stdout and to
research/experiments/conformal_condor_out.md

Idea under test
---------------
An iron condor is a short prediction interval for the session's close.
  - Physical side P: build the interval by split conformal / CQR on the
    nonconformity score  r = |move| / impl_move_cc  (conformalising the RATIO
    makes the interval scale with implied vol), with adaptive conformal
    inference (ACI) updating alpha online.
  - Risk-neutral side Q: for a vertical spread of width w, credit/w is (to
    first order in w) the risk-neutral probability of finishing beyond the
    short strike (Breeden-Litzenberger digital approximation).  For the condor
    therefore   Q(outside) ~= credit / wing.
  - Rule: sell the interval only when the calibrated physical outside
    probability alpha is below the market's Q(outside) = credit/wing by a
    margin.

Because we have no option-price history on the basic Alpaca plan, Q is
modelled here as a driftless normal whose scale is the VIX-implied move,
calibrated so that at the baseline width it reproduces the one live-observed
credit (17 % of the wing, chain of 2026-09-02).  This is stated as a
limitation, not hidden.
"""
from __future__ import annotations

import math
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.stats import norm
from sklearn.ensemble import GradientBoostingRegressor

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "state" / "history" / "daily.csv"
OUT = Path(__file__).resolve().parent / "conformal_condor_out.md"

WING_PCT = 0.50          # wing width, % of spot          (report convention)
CREDIT_RATIO = 0.17      # credit / wing observed live    (report convention)
K_BASE = 0.70            # baseline short distance in units of impl_move_cc
SPOT = 762.0
ALPHA = 0.20             # target outside probability -> 80 % coverage
GAMMA_ACI = 0.005
K_MIN, K_MAX = 0.35, 1.60   # tradability clip on the conformal width
CREDIT_FLOOR = 0.20         # design gate from research/F1: credit >= 20 % of wing
SQRT_PI_2 = math.sqrt(math.pi / 2.0)   # sigma = E|X| * sqrt(pi/2) for a normal

FEATURES = ["vix_prev", "slope_prev", "rv5_over_vix", "rv20_over_vix",
            "gap", "absret_prev", "dow_0", "dow_1", "dow_2", "dow_3",
            "is_first_friday", "is_third_friday"]


# ---------------------------------------------------------------- payoff ----
def condor_pnl(abs_move, short_pct, credit):
    """P&L in % of spot. Short at +-short_pct, wing WING_PCT wide."""
    loss = np.clip(np.asarray(abs_move) - np.asarray(short_pct), 0.0, WING_PCT)
    return np.asarray(credit) - loss


def _put_value(dist, s):
    """E[(K - S)^+] for S ~ N(0, s) in % move units, K a distance `dist` below."""
    z = np.asarray(dist, dtype=float) / np.asarray(s, dtype=float)
    return s * norm.pdf(z) - dist * norm.cdf(-z)


def bs_condor_credit(short_pct, sigma_pct, wing=WING_PCT):
    """Model credit of the condor under a driftless normal of sd sigma_pct."""
    short_pct = np.asarray(short_pct, dtype=float)
    sigma_pct = np.asarray(sigma_pct, dtype=float)
    return 2.0 * (_put_value(short_pct, sigma_pct)
                  - _put_value(short_pct + wing, sigma_pct))


def calibrate_theta(median_impl):
    """theta = sd of the remaining-horizon move / sd of the full close-close day.

    Chosen so the model credit at the baseline width equals the live 17 % of wing.
    """
    def f(theta):
        s = theta * SQRT_PI_2 * median_impl
        return float(bs_condor_credit(K_BASE * median_impl, s)) - CREDIT_RATIO * WING_PCT
    return brentq(f, 0.05, 3.0)


# ------------------------------------------------------------ conformal ----
def conf_quantile(scores, alpha):
    """Split-conformal (1-alpha) quantile with the finite-sample correction."""
    scores = np.asarray(scores, dtype=float)
    n = len(scores)
    if n == 0:
        return float("nan")
    lvl = min(1.0, math.ceil((n + 1) * (1.0 - alpha)) / n)
    return float(np.quantile(scores, lvl, method="higher"))


def run_split_conformal(ratio, window, alpha, aci=False, gamma=GAMMA_ACI):
    """Rolling split conformal on the ratio score. Returns k_t (NaN before warm-up)."""
    n = len(ratio)
    k = np.full(n, np.nan)
    a_t = alpha
    for t in range(window, n):
        cal = ratio[t - window:t]
        a_use = min(max(a_t, 1e-3), 0.5)
        k[t] = conf_quantile(cal, a_use)
        if aci:
            err = 1.0 if ratio[t] > k[t] else 0.0
            a_t = a_t + gamma * (alpha - err)
    return k


def run_cqr(X, ratio, window, alpha, aci=False, gamma=GAMMA_ACI, refit_every=25,
            train_extra=250, seed=0):  # noqa: PLR0913
    """CQR: quantile GBM for the conditional (1-alpha) quantile of the ratio,
    conformalised on the trailing `window` residuals E_i = r_i - qhat_i."""
    n = len(ratio)
    k = np.full(n, np.nan)
    qhat = np.full(n, np.nan)
    a_t = alpha
    model = None
    start = window + train_extra
    for t in range(start, n):
        if model is None or (t - start) % refit_every == 0:
            tr0 = max(0, t - window - train_extra)
            model = GradientBoostingRegressor(
                loss="quantile", alpha=1.0 - alpha, n_estimators=150,
                max_depth=2, learning_rate=0.05, subsample=0.9,
                random_state=seed)
            model.fit(X[tr0:t - window], ratio[tr0:t - window])
            qhat[tr0:t + 1] = model.predict(X[tr0:t + 1])
        else:
            qhat[t] = model.predict(X[t:t + 1])[0]
        resid = ratio[t - window:t] - qhat[t - window:t]
        a_use = min(max(a_t, 1e-3), 0.5)
        k[t] = max(0.05, qhat[t] + conf_quantile(resid, a_use))
        if aci:
            err = 1.0 if ratio[t] > k[t] else 0.0
            a_t = a_t + gamma * (alpha - err)
    return k


# ------------------------------------------------------------- reporting ----
def summarise(df, kcol, label, theta, gate=None):
    d = df.dropna(subset=[kcol]).copy()
    if gate is not None:
        d = d[gate.reindex(d.index).fillna(False)]
    if len(d) == 0:
        return None
    short = (d[kcol] * d["impl_move_cc"]).values
    sigma = (theta * SQRT_PI_2 * d["impl_move_cc"]).values
    cred_fix = np.full(len(d), CREDIT_RATIO * WING_PCT)
    cred_bs = bs_condor_credit(short, sigma)
    inside = (d["abs_move"].values <= short).astype(float)
    pnl_fix = condor_pnl(d["abs_move"].values, short, cred_fix)
    pnl_bs = condor_pnl(d["abs_move"].values, short, cred_bs)
    q_out = cred_bs / WING_PCT           # Breeden-Litzenberger digital approx
    return {
        "method": label, "n": int(len(d)),
        "coverage": round(float(inside.mean()), 3),
        "mean_k": round(float(d[kcol].mean()), 3),
        "sd_k": round(float(d[kcol].std()), 3),
        "credit_bs_pct": round(float(cred_bs.mean()), 4),
        "Q_outside": round(float(q_out.mean()), 3),
        "P_outside": round(float(1 - inside.mean()), 3),
        "PQ_gap_pp": round(float((q_out.mean() - (1 - inside.mean())) * 100), 1),
        "pnl_fix_pct": round(float(pnl_fix.mean()), 4),
        "pnl_bs_pct": round(float(pnl_bs.mean()), 4),
        "pnl_bs_usd": round(float(pnl_bs.mean() / 100 * SPOT * 100), 2),
        "loss_share": round(float((pnl_bs < 0).mean()), 3),
        "worst_pct": round(float(pnl_bs.min()), 3),
        "t_stat": round(float(pnl_bs.mean() / (pnl_bs.std() / math.sqrt(len(d)))), 2),
        "_pnl_bs": pnl_bs, "_pnl_fix": pnl_fix, "_idx": d.index, "_inside": inside,
    }


def by_year(res):
    d = pd.DataFrame({"pnl": res["_pnl_bs"], "inside": res["_inside"]}, index=res["_idx"])
    return [{"year": int(y), "n": len(g), "cov": round(float(g["inside"].mean()), 3),
             "pnl_pct": round(float(g["pnl"].mean()), 4)}
            for y, g in d.groupby(d.index.year)]


def main():
    df = pd.read_csv(CSV, parse_dates=["date"]).set_index("date")
    for i in range(4):
        df[f"dow_{i}"] = (df["dow"] == i).astype(float)
    theta = calibrate_theta(float(df["impl_move_cc"].median()))
    k_q = theta * SQRT_PI_2 * norm.ppf(1 - ALPHA / 2)

    L = []
    L.append("# Conformal Condor - experiment output\n")
    L.append(f"Target outside probability alpha = {ALPHA}; wing {WING_PCT} % of spot; "
             f"baseline k = {K_BASE}; ACI gamma = {GAMMA_ACI}.\n")
    L.append(f"Calibrated horizon factor theta = {theta:.3f} (sd of the remaining-horizon "
             f"move / sd of the full VIX day) so that the model credit at the baseline "
             f"width equals the live 17 % of wing.\n")
    L.append(f"Risk-neutral width for alpha = {ALPHA}: k_Q = {k_q:.3f} impl_move units "
             f"(the market's own 80 % interval). Baseline k = {K_BASE}.\n")

    horizons = {
        "A_1030_close (2024-)": dict(col="ret_1030_close", window=125, extra=125),
        "B_open_close (2018-)": dict(col="ret_oc", window=250, extra=250),
    }
    store = {}
    for hname, cfg in horizons.items():
        d = df.dropna(subset=[cfg["col"], "impl_move_cc"] + FEATURES).copy()
        d["abs_move"] = d[cfg["col"]].abs() * 100.0
        d["ratio"] = d["abs_move"] / d["impl_move_cc"]
        X = d[FEATURES].values
        r = d["ratio"].values
        W = cfg["window"]

        d["k_base"] = K_BASE
        d["k_scr"] = run_split_conformal(r, W, ALPHA, aci=False)
        d["k_scr_aci"] = run_split_conformal(r, W, ALPHA, aci=True)
        d["k_cqr"] = run_cqr(X, r, W, ALPHA, aci=False, train_extra=cfg["extra"])
        d["k_cqr_aci"] = run_cqr(X, r, W, ALPHA, aci=True, train_extra=cfg["extra"])

        for c_ in ("k_scr", "k_scr_aci", "k_cqr", "k_cqr_aci"):
            d[c_] = d[c_].clip(K_MIN, K_MAX)

        common = d[["k_scr", "k_cqr_aci"]].notna().all(axis=1)
        de = d[common].copy()
        store[hname] = de

        rows, keep = [], {}
        for col, lab in [("k_base", "baseline k=0.70"), ("k_scr", "split conformal"),
                         ("k_scr_aci", "split conformal + ACI"), ("k_cqr", "CQR"),
                         ("k_cqr_aci", "CQR + ACI")]:
            s = summarise(de, col, lab, theta)
            if s:
                rows.append(s)
                keep[lab] = s
        for col, lab in [("k_scr_aci", "split conformal + ACI, PQ-gated"),
                         ("k_cqr_aci", "CQR + ACI, PQ-gated")]:
            gate = de[col] <= k_q
            s = summarise(de, col, lab, theta, gate=gate)
            if s:
                s["gate_rate"] = round(float(gate.mean()), 3)
                rows.append(s)
                keep[lab] = s
        # design's own credit gate: model credit >= 20 % of the wing
        sig = theta * SQRT_PI_2 * de["impl_move_cc"]
        for col, lab in [("k_base", "baseline, credit-gated"),
                         ("k_cqr_aci", "CQR + ACI, credit-gated")]:
            cred = pd.Series(bs_condor_credit((de[col] * de["impl_move_cc"]).values, sig.values),
                             index=de.index)
            gate = cred >= CREDIT_FLOOR * WING_PCT
            s = summarise(de, col, lab, theta, gate=gate)
            if s:
                s["gate_rate"] = round(float(gate.mean()), 3)
                rows.append(s)
                keep[lab] = s

        L.append(f"\n## {hname}\n")
        L.append(f"Evaluation sample: {de.index.min().date()} to {de.index.max().date()}, "
                 f"n = {len(de)} (common to all methods).\n")
        L.append("| method | n | coverage | mean k | sd k | model credit % | Q(out) | P(out) | "
                 "Q-P pp | P&L % fixed credit | P&L % model credit | $/contract | loss share | "
                 "worst % | t |")
        L.append("|" + "---|" * 15)
        for s in rows:
            L.append(f"| {s['method']} | {s['n']} | {s['coverage']} | {s['mean_k']} | {s['sd_k']} | "
                     f"{s['credit_bs_pct']} | {s['Q_outside']} | {s['P_outside']} | {s['PQ_gap_pp']} | "
                     f"{s['pnl_fix_pct']} | {s['pnl_bs_pct']} | {s['pnl_bs_usd']} | {s['loss_share']} | "
                     f"{s['worst_pct']} | {s['t_stat']} |")
        gates = [s for s in rows if "gate_rate" in s]
        if gates:
            L.append("\nGate hit rate (share of sessions traded): "
                     + ", ".join(f"{s['method']} {s['gate_rate']}" for s in gates) + "\n")

        L.append(f"\n### {hname}: coverage and P&L (model credit) by year\n")
        labs = ["baseline k=0.70", "split conformal + ACI", "CQR + ACI"]
        yr = {lab: by_year(keep[lab]) for lab in labs}
        years = sorted({y["year"] for lab in labs for y in yr[lab]})
        L.append("| year | " + " | ".join(f"{l} cov / P&L%" for l in labs) + " |")
        L.append("|" + "---|" * (len(labs) + 1))
        for y in years:
            cells = []
            for lab in labs:
                rec = [x for x in yr[lab] if x["year"] == y]
                cells.append(f"{rec[0]['cov']} / {rec[0]['pnl_pct']}" if rec else "-")
            L.append(f"| {y} | " + " | ".join(cells) + " |")

        # ---- break-even analysis for the baseline rule, by regime bucket ----
        L.append(f"\n### {hname}: empirical coverage vs break-even inside probability "
                 f"(baseline k = {K_BASE}, fixed credit {CREDIT_RATIO:.0%} of wing)\n")
        base = de.copy()
        base["short"] = K_BASE * base["impl_move_cc"]
        base["inside"] = (base["abs_move"] <= base["short"]).astype(float)
        base["loss"] = np.clip(base["abs_move"] - base["short"], 0, WING_PCT)
        c = CREDIT_RATIO * WING_PCT
        L.append("| bucket | n | coverage P | Q(inside)=1-c/w | E[loss|outside] % | "
                 "break-even P* | P - P* pp | mean P&L % |")
        L.append("|" + "---|" * 8)

        def bucket_rows(keycol, edges, names):
            b = pd.cut(base[keycol], edges, labels=names)
            for nm, g in base.groupby(b, observed=True):
                if len(g) < 25:
                    continue
                out = g[g["inside"] == 0]
                el = float(out["loss"].mean()) if len(out) else 0.0
                pstar = el / (c + el) if (c + el) > 0 else float("nan")
                cov = float(g["inside"].mean())
                pnl = float((c - g["loss"]).mean())
                L.append(f"| {keycol} {nm} | {len(g)} | {round(cov,3)} | {round(1-CREDIT_RATIO,3)} | "
                         f"{round(el,3)} | {round(pstar,3)} | {round((cov-pstar)*100,1)} | "
                         f"{round(pnl,4)} |")

        bucket_rows("slope_prev", [0, 0.85, 0.95, 1.0, 9], ["<0.85", "0.85-0.95", "0.95-1.00", ">=1.00"])
        bucket_rows("vix_prev", [0, 15, 21, 99], ["<15", "15-21", ">21"])
        allout = base[base["inside"] == 0]
        el = float(allout["loss"].mean())
        pstar = el / (c + el)
        cov = float(base["inside"].mean())
        L.append(f"| ALL | {len(base)} | {round(cov,3)} | {round(1-CREDIT_RATIO,3)} | "
                 f"{round(el,3)} | {round(pstar,3)} | {round((cov-pstar)*100,1)} | "
                 f"{round(float((c-base['loss']).mean()),4)} |")

        # ---- coverage of the conformal interval, split by regime -----------
        L.append(f"\n### {hname}: conditional coverage of the CQR+ACI interval by regime\n")
        cq = de.dropna(subset=["k_cqr_aci"]).copy()
        cq["short"] = cq["k_cqr_aci"] * cq["impl_move_cc"]
        cq["inside"] = (cq["abs_move"] <= cq["short"]).astype(float)
        cq["ins_base"] = (cq["abs_move"] <= K_BASE * cq["impl_move_cc"]).astype(float)
        L.append("| bucket | n | conformal coverage | baseline coverage | mean k conformal |")
        L.append("|" + "---|" * 5)
        for keycol, edges, names in [("slope_prev", [0, 0.85, 0.95, 1.0, 9],
                                      ["<0.85", "0.85-0.95", "0.95-1.00", ">=1.00"]),
                                     ("vix_prev", [0, 15, 21, 99], ["<15", "15-21", ">21"])]:
            b = pd.cut(cq[keycol], edges, labels=names)
            for nm, g in cq.groupby(b, observed=True):
                if len(g) < 25:
                    continue
                L.append(f"| {keycol} {nm} | {len(g)} | {round(float(g['inside'].mean()),3)} | "
                         f"{round(float(g['ins_base'].mean()),3)} | "
                         f"{round(float(g['k_cqr_aci'].mean()),3)} |")

        # ---- longest sample the model-free split conformal allows -----------
        dl = d.dropna(subset=["k_scr_aci"]).copy()
        L.append(f"\n### {hname}: split conformal on the longest available sample "
                 f"({dl.index.min().date()} to {dl.index.max().date()}, n = {len(dl)})\n")
        L.append("| method | n | coverage | mean k | P&L % fixed credit | P&L % model credit | t |")
        L.append("|" + "---|" * 7)
        for col, lab in [("k_base", "baseline k=0.70"), ("k_scr", "split conformal"),
                         ("k_scr_aci", "split conformal + ACI")]:
            s = summarise(dl, col, lab, theta)
            L.append(f"| {s['method']} | {s['n']} | {s['coverage']} | {s['mean_k']} | "
                     f"{s['pnl_fix_pct']} | {s['pnl_bs_pct']} | {s['t_stat']} |")

    # ---- theta sensitivity: the model-credit level is a calibration choice ----
    L.append("\n## Sensitivity of the model-credit P&L to the horizon factor theta\n")
    L.append("theta is the one free parameter of the modelled risk-neutral measure. "
             "It was calibrated to a single live chain. The table shows that the LEVEL "
             "of the model-credit P&L is a function of theta; the RANKING of the methods "
             "is much less sensitive.\n")
    L.append("| horizon | theta | k_Q | baseline P&L % | split conf + ACI P&L % | CQR + ACI P&L % |")
    L.append("|" + "---|" * 6)
    for hname, de in store.items():
        for th in (0.50, 0.556, 0.60, 0.65, 0.70):
            kq = th * SQRT_PI_2 * norm.ppf(1 - ALPHA / 2)
            vals = [summarise(de, c, c, th)["pnl_bs_pct"]
                    for c in ("k_base", "k_scr_aci", "k_cqr_aci")]
            L.append(f"| {hname} | {th} | {round(kq,3)} | " + " | ".join(str(v) for v in vals) + " |")

    # ---- empirical Kelly on the realised P&L distribution ----
    L.append("\n## Empirical Kelly on the realised P&L distribution (model credit)\n")
    L.append("f* maximises E[log(1 + f * pnl / maxloss)] over the realised sample. "
             "It is an in-sample upper bound, reported to show the order of magnitude only.\n")
    L.append("| horizon | method | mean P&L % | full Kelly f* | 1/4 Kelly | max loss used |")
    L.append("|" + "---|" * 6)
    for hname, de in store.items():
        for col, lab in [("k_base", "baseline k=0.70"), ("k_scr_aci", "split conformal + ACI"),
                         ("k_cqr_aci", "CQR + ACI")]:
            s = summarise(de, col, lab, theta)
            x = s["_pnl_bs"]
            maxloss = float(-x.min())
            grid = np.linspace(0.0, 1.0, 201)
            util = [np.mean(np.log1p(np.clip(f * x / maxloss, -0.999, None))) for f in grid]
            fstar = float(grid[int(np.argmax(util))])
            L.append(f"| {hname} | {lab} | {s['pnl_bs_pct']} | {round(fstar,3)} | "
                     f"{round(fstar/4,3)} | {round(maxloss,3)} % of spot |")

    # ---- Kelly numbers ----
    L.append("\n## Kelly fraction for the condor (two-state approximation)\n")
    L.append("f* = (p*b - (1-p)) / b with b = c/L, c = credit, L = max loss = wing - credit.\n")
    L.append("| b = c/L | p | full Kelly f* | half Kelly | quarter Kelly |")
    L.append("|---|---|---|---|---|")
    for b in (0.15, 0.2, 0.25, 0.3, 0.41):
        for p in (0.75, 0.80, 0.85):
            f = (p * b - (1 - p)) / b
            L.append(f"| {b} | {p} | {round(f,3)} | {round(f/2,3)} | {round(f/4,3)} |")

    txt = "\n".join(L)
    OUT.write_text(txt, encoding="utf-8")
    print(txt)


if __name__ == "__main__":
    main()

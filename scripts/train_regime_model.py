"""Train the regime model on the historical dataset and back-test the condor rule.

What the model is: a small logistic regression (plus a gradient-boosting cross-check) that maps
regime features known at the morning entry (VIX level, term-structure slope, realised-vs-implied
volatility, overnight gap, calendar flags) to the probability that the index finishes the session
inside the condor's short strikes. It is validated with expanding-window, year-by-year splits and
compared with the unconditional base rate. Its only use in the agent is to SHRINK the size or
to set it to zero (monotone authority), never to pick a direction.

What the back-test is: the P&L of our live geometry on every historical session, three horizons:
  * 10:30 -> close, 2024-2026 (the exact horizon, 668 sessions)
  * open  -> close, 2018-2026 (proxy, 1,534 sessions)
  * close -> close, 1990-2026 (decades, overnight included; only for regime features)
plus a random-entry Monte Carlo giving the null distribution of a 2.5-session campaign.

Assumptions stated in the output: short distance = 1.10 x the straddle-implied remaining move,
proxied by 0.70 x the VIX-implied full-day expected |move| (calibrated on the live chain on
2026-09-02: straddle 0.52 % vs VIX-implied 0.82 %); wing = 0.5 % of spot; credit = 17 % of the
wing (live chain 0.67/4.00). Options history is not available on the basic plan, so credit is
an assumption, not data.

    python scripts/train_regime_model.py            # writes config/regime_model.json, docs/regime_model_report.md
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.core.config import ROOT, STATE_DIR  # noqa: E402

HIST = STATE_DIR / "history"
K_SHORT = 0.70          # short distance as a multiple of the VIX-implied full-day E|move|
WING_PCT = 0.50         # wing width in % of spot
CREDIT_RATIO = 0.17     # credit as a share of the wing (live chain 2026-09-02)
SPOT = 762.0


def condor_pnl_pct(abs_move_pct: pd.Series, short_pct: pd.Series) -> pd.Series:
    """P&L in % of spot for one package: credit minus the loss beyond the short, capped at the wing."""
    credit = CREDIT_RATIO * WING_PCT
    loss = (abs_move_pct - short_pct).clip(lower=0.0).clip(upper=WING_PCT)
    return credit - loss


def dow_dummies(df: pd.DataFrame) -> pd.DataFrame:
    for d in range(5):
        df[f"dow_{d}"] = (df["dow"] == d).astype(int)
    return df


def expanding_cv(df: pd.DataFrame, features: list[str], target: str, first_test_year: int) -> dict:
    """Train on all years < y, test on year y; pooled out-of-sample predictions."""
    years = sorted(df.index.year.unique())
    test_years = [y for y in years if y >= first_test_year]
    oos = pd.Series(index=df.index, dtype=float)
    oos_gb = pd.Series(index=df.index, dtype=float)
    for y in test_years:
        tr = df[df.index.year < y]
        te = df[df.index.year == y]
        if len(tr) < 200 or len(te) == 0:
            continue
        mu, sd = tr[features].mean(), tr[features].std().replace(0, 1.0)
        lr = LogisticRegression(C=1.0, max_iter=2000)
        lr.fit(((tr[features] - mu) / sd).values, tr[target].values)
        oos.loc[te.index] = lr.predict_proba(((te[features] - mu) / sd).values)[:, 1]
        gb = HistGradientBoostingClassifier(max_depth=3, max_iter=150, learning_rate=0.05, min_samples_leaf=40)
        gb.fit(tr[features].values, tr[target].values)
        oos_gb.loc[te.index] = gb.predict_proba(te[features].values)[:, 1]
    mask = oos.notna()
    y = df.loc[mask, target].values
    base = df.loc[df.index.year < first_test_year, target].mean()
    out = {"n_oos": int(mask.sum()), "test_years": f"{test_years[0]}-{test_years[-1]}", "base_rate_train": round(float(base), 4),
           "oos_rate": round(float(y.mean()), 4)}
    for name, p in (("logit", oos[mask].values), ("gbm", oos_gb[mask].values)):
        p = np.clip(p, 1e-6, 1 - 1e-6)
        out[name] = {
            "brier": round(float(brier_score_loss(y, p)), 5),
            "brier_base": round(float(brier_score_loss(y, np.full_like(p, base))), 5),
            "logloss": round(float(log_loss(y, p)), 5),
            "logloss_base": round(float(log_loss(y, np.full_like(p, base))), 5),
            "auc": round(float(roc_auc_score(y, p)), 4) if len(set(y)) > 1 else None,
        }
    # final logit fit on everything (the model the agent uses), with standardisation params
    mu, sd = df[features].mean(), df[features].std().replace(0, 1.0)
    lr = LogisticRegression(C=1.0, max_iter=2000).fit(((df[features] - mu) / sd).values, df[target].values)
    out["model"] = {"features": features, "mean": {f: float(mu[f]) for f in features}, "std": {f: float(sd[f]) for f in features},
                    "coef": {f: float(c) for f, c in zip(features, lr.coef_[0])}, "intercept": float(lr.intercept_[0]),
                    "base_rate": float(df[target].mean()), "n": int(len(df))}
    out["_oos"] = oos[mask]
    return out


def bucket_table(df: pd.DataFrame, oos: pd.Series, pnl_col: str, target: str) -> list[dict]:
    """Out-of-sample predicted probability terciles vs realised inside-rate and condor P&L."""
    d = df.loc[oos.index].copy()
    d["p"] = oos.values
    d["bucket"] = pd.qcut(d["p"], 3, labels=["low", "mid", "high"])
    rows = []
    for b, g in d.groupby("bucket", observed=True):
        rows.append({"bucket": str(b), "n": int(len(g)), "p_pred_mean": round(float(g["p"].mean()), 3),
                     "inside_rate": round(float(g[target].mean()), 3),
                     "pnl_pct_mean": round(float(g[pnl_col].mean()), 4), "pnl_pct_median": round(float(g[pnl_col].median()), 4),
                     "pnl_usd_mean_per_contract": round(float(g[pnl_col].mean() / 100 * SPOT * 100), 2),
                     "loss_share": round(float((g[pnl_col] < 0).mean()), 3)})
    return rows


def monte_carlo(pnl: pd.Series, sessions: float = 2.5, contracts_per_session: float = 2.0, n: int = 20000, seed: int = 7) -> dict:
    """Random-entry null: sample sessions with replacement, sum P&L in USD for a 2.5-session campaign."""
    rng = np.random.default_rng(seed)
    usd = (pnl.dropna().values / 100.0) * SPOT * 100.0 * contracts_per_session
    k = int(round(sessions))
    sims = usd[rng.integers(0, len(usd), size=(n, k))].sum(axis=1)
    q = np.percentile(sims, [1, 5, 25, 50, 75, 95, 99])
    return {"n_sessions_sampled": int(len(usd)), "campaign_sessions": k, "contracts_per_session": contracts_per_session,
            "mean_usd": round(float(sims.mean()), 2), "percentiles_usd": {str(p): round(float(v), 2) for p, v in zip([1, 5, 25, 50, 75, 95, 99], q)},
            "prob_negative": round(float((sims < 0).mean()), 3), "_sims": sims}


def main() -> None:
    df = pd.read_csv(HIST / "daily.csv", parse_dates=["date"]).set_index("date").sort_index()
    df = dow_dummies(df)
    df["short_pct"] = K_SHORT * df["impl_move_cc"]
    df["vix1d_over_vix"] = df["vix1d_prev"] / df["vix_prev"]
    df["vix9d_over_vix"] = df["vix9d_prev"] / df["vix_prev"]
    report: dict = {"generated": datetime.now(tz=timezone.utc).isoformat(), "assumptions": {
        "short_multiple_of_vix_implied_day_move": K_SHORT, "wing_pct": WING_PCT, "credit_ratio_of_wing": CREDIT_RATIO, "spot": SPOT}}

    # ---- horizon A: 10:30 -> close (exact) ----
    a = df.dropna(subset=["ret_1030_close", "vix_prev", "slope_prev", "rv5_over_vix", "rv20_over_vix", "gap", "absret_prev"]).copy()
    a["abs_move"] = a["ret_1030_close"].abs() * 100
    a["inside"] = (a["abs_move"] <= a["short_pct"]).astype(int)
    a["pnl"] = condor_pnl_pct(a["abs_move"], a["short_pct"])
    # ---- horizon B: open -> close (proxy, 2018-) ----
    b = df.dropna(subset=["ret_oc", "vix_prev", "slope_prev", "rv5_over_vix", "rv20_over_vix", "gap", "absret_prev"]).copy()
    b["abs_move"] = b["ret_oc"].abs() * 100
    b["inside"] = (b["abs_move"] <= b["short_pct"]).astype(int)
    b["pnl"] = condor_pnl_pct(b["abs_move"], b["short_pct"])
    # ---- horizon C: close -> close (decades, full-day condor at 1.10x) ----
    c = df.dropna(subset=["ret_cc", "vix_prev", "slope_prev", "rv5_over_vix", "rv20_over_vix", "absret_prev"]).copy()
    c["abs_move"] = c["ret_cc"].abs() * 100
    c["short_cc"] = 1.10 * c["impl_move_cc"]
    c["inside"] = (c["abs_move"] <= c["short_cc"]).astype(int)
    c["pnl"] = condor_pnl_pct(c["abs_move"], c["short_cc"])

    feats_full = ["vix_prev", "slope_prev", "rv5_over_vix", "rv20_over_vix", "gap", "absret_prev",
                  "is_first_friday", "is_third_friday", "dow_0", "dow_1", "dow_2", "dow_3"]
    feats_nogap = [f for f in feats_full if f != "gap"]

    res = {}
    res["A_1030_close"] = expanding_cv(a, feats_full, "inside", first_test_year=2025)
    res["B_open_close"] = expanding_cv(b, feats_full, "inside", first_test_year=2021)
    res["C_close_close"] = expanding_cv(c, feats_nogap, "inside", first_test_year=2012)
    buckets = {"A_1030_close": bucket_table(a, res["A_1030_close"]["_oos"], "pnl", "inside"),
               "B_open_close": bucket_table(b, res["B_open_close"]["_oos"], "pnl", "inside"),
               "C_close_close": bucket_table(c, res["C_close_close"]["_oos"], "pnl", "inside")}

    # unconditional back-test stats per horizon
    def stats(x: pd.DataFrame, label: str) -> dict:
        p = x["pnl"]
        return {"horizon": label, "n": int(len(x)), "inside_rate": round(float(x["inside"].mean()), 3),
                "pnl_pct_mean": round(float(p.mean()), 4), "pnl_pct_median": round(float(p.median()), 4),
                "pnl_usd_mean_per_contract": round(float(p.mean() / 100 * SPOT * 100), 2),
                "pnl_usd_p05_per_contract": round(float(p.quantile(0.05) / 100 * SPOT * 100), 2),
                "loss_share": round(float((p < 0).mean()), 3), "worst_pct": round(float(p.min()), 4),
                "by_year_mean_pct": {int(y): round(float(g["pnl"].mean()), 4) for y, g in x.groupby(x.index.year)}}
    report["backtest"] = [stats(a, "10:30->close 2024-2026"), stats(b, "open->close 2018-2026"), stats(c, "close->close 1990-2026 (1.10x, overnight incl.)")]
    # by-regime slices on horizon B (largest sample with the exact features)
    b["slope_bucket"] = pd.cut(b["slope_prev"], [0, 0.85, 0.95, 1.0, 9], labels=["<0.85", "0.85-0.95", "0.95-1.00", ">=1.00"])
    b["vix_bucket"] = pd.cut(b["vix_prev"], [0, 15, 21, 100], labels=["<15", "15-21", ">21"])
    report["by_slope_B"] = [{"slope": str(k), "n": int(len(g)), "pnl_pct_mean": round(float(g["pnl"].mean()), 4), "inside_rate": round(float(g["inside"].mean()), 3)}
                            for k, g in b.groupby("slope_bucket", observed=True)]
    report["by_vix_B"] = [{"vix": str(k), "n": int(len(g)), "pnl_pct_mean": round(float(g["pnl"].mean()), 4), "inside_rate": round(float(g["inside"].mean()), 3)}
                          for k, g in b.groupby("vix_bucket", observed=True)]
    mc_a = monte_carlo(a["pnl"])
    mc_b = monte_carlo(b["pnl"])
    report["monte_carlo"] = {"A_1030_close": {k: v for k, v in mc_a.items() if k != "_sims"},
                             "B_open_close": {k: v for k, v in mc_b.items() if k != "_sims"}}
    np.save(STATE_DIR / "mc_null_A.npy", mc_a["_sims"])
    np.save(STATE_DIR / "mc_null_B.npy", mc_b["_sims"])

    report["cv"] = {k: {kk: vv for kk, vv in v.items() if kk not in ("_oos", "model")} for k, v in res.items()}
    report["buckets"] = buckets

    # ---- choose the deployed model: B (largest sample with the gap feature and the intraday horizon) ----
    chosen = "B_open_close"
    model = res[chosen]["model"]
    bk = buckets[chosen]
    # thresholds: p below the low-tercile edge -> half size; below the 10th percentile of OOS p -> no trade
    oos_p = res[chosen]["_oos"]
    p_half = float(oos_p.quantile(1 / 3))
    p_zero = float(oos_p.quantile(0.10))
    low_bucket_negative = bk[0]["pnl_pct_mean"] < 0
    deployed = {
        "name": chosen, "trained_at": report["generated"], "horizon": "SPY open->close, IEX daily bars 2018-11..2026-09",
        "target": f"|move| <= {K_SHORT} x VIX-implied full-day E|move| (our 1.10x straddle geometry)",
        "features": model["features"], "mean": model["mean"], "std": model["std"], "coef": model["coef"],
        "intercept": model["intercept"], "base_rate": model["base_rate"], "n": model["n"],
        "thresholds": {"p_half": round(p_half, 4), "p_zero": round(p_zero, 4)},
        "rule": "multiplier 1.0 if p >= p_half; 0.5 if p_zero <= p < p_half; 0.0 if p < p_zero. Never above 1.0.",
        "use_taper": bool(low_bucket_negative),
        "cv": report["cv"][chosen], "buckets": bk,
        "assumptions": report["assumptions"],
    }
    (ROOT / "config" / "regime_model.json").write_text(json.dumps(deployed, indent=2), encoding="utf-8")

    # ---- markdown report ----
    L = ["# Regime model and historical benchmark", "",
         f"Generated {report['generated'][:19]} UTC from `state/history/daily.csv`. Assumptions: short distance {K_SHORT} x VIX-implied full-day E|move| "
         f"(= 1.10 x the straddle-implied remaining move measured live), wing {WING_PCT} % of spot, credit {CREDIT_RATIO:.0%} of wing (live chain 2026-09-02), "
         f"spot {SPOT:.0f}. Options history is not available on the basic plan; the credit is an assumption, the moves are data.", "",
         "## Unconditional back-test of the condor rule", "",
         "| horizon | n | inside rate | mean P&L % | median P&L % | mean $/contract | P05 $/contract | loss share | worst % |", "|---|---|---|---|---|---|---|---|---|"]
    for s in report["backtest"]:
        L.append(f"| {s['horizon']} | {s['n']} | {s['inside_rate']} | {s['pnl_pct_mean']} | {s['pnl_pct_median']} | {s['pnl_usd_mean_per_contract']} | {s['pnl_usd_p05_per_contract']} | {s['loss_share']} | {s['worst_pct']} |")
    L += ["", "By year (mean P&L % per session), 10:30->close: " + ", ".join(f"{y}: {v}" for y, v in report["backtest"][0]["by_year_mean_pct"].items()),
          "By year, open->close: " + ", ".join(f"{y}: {v}" for y, v in report["backtest"][1]["by_year_mean_pct"].items()), "",
          "## By regime (open->close, 2018-2026)", "", "| VIX/VIX3M slope | n | mean P&L % | inside rate |", "|---|---|---|---|"]
    L += [f"| {r['slope']} | {r['n']} | {r['pnl_pct_mean']} | {r['inside_rate']} |" for r in report["by_slope_B"]]
    L += ["", "| VIX level | n | mean P&L % | inside rate |", "|---|---|---|---|"]
    L += [f"| {r['vix']} | {r['n']} | {r['pnl_pct_mean']} | {r['inside_rate']} |" for r in report["by_vix_B"]]
    L += ["", "## Regime model: expanding-window out-of-sample validation", "",
          "| dataset | OOS years | n OOS | base rate | logit Brier (base) | logit AUC | GBM Brier | GBM AUC |", "|---|---|---|---|---|---|---|---|"]
    for k, v in report["cv"].items():
        L.append(f"| {k} | {v['test_years']} | {v['n_oos']} | {v['base_rate_train']} | {v['logit']['brier']} ({v['logit']['brier_base']}) | {v['logit']['auc']} | {v['gbm']['brier']} | {v['gbm']['auc']} |")
    L += ["", "## Predicted-probability terciles (out of sample) vs realised", ""]
    for k, rows in buckets.items():
        L += [f"**{k}**", "", "| bucket | n | mean p | inside rate | mean P&L % | median P&L % | mean $/contract | loss share |", "|---|---|---|---|---|---|---|---|"]
        L += [f"| {r['bucket']} | {r['n']} | {r['p_pred_mean']} | {r['inside_rate']} | {r['pnl_pct_mean']} | {r['pnl_pct_median']} | {r['pnl_usd_mean_per_contract']} | {r['loss_share']} |" for r in rows]
        L.append("")
    L += ["## Random-entry Monte Carlo null (2.5-session campaign, 2 contracts per session)", ""]
    for k, m in report["monte_carlo"].items():
        L.append(f"- {k}: mean {m['mean_usd']} USD, P05 {m['percentiles_usd']['5']}, median {m['percentiles_usd']['50']}, P95 {m['percentiles_usd']['95']}, P(negative) {m['prob_negative']}")
    L += ["", "## Deployed model", "", f"`config/regime_model.json`: {chosen}, logistic regression on {', '.join(model['features'])}; "
          f"thresholds p_half {p_half:.3f}, p_zero {p_zero:.3f}; taper enabled: {low_bucket_negative}. "
          "Coefficients (standardised): " + ", ".join(f"{f} {c:+.3f}" for f, c in model["coef"].items()) + ".", "",
          "Reading guide: the model is used only to shrink size. If the low-probability tercile has no worse P&L than the others out of sample, "
          "the taper is disabled and the report says so. No Sharpe ratios are computed: with 2.5 sessions the Probabilistic Sharpe Ratio cannot reach 95 % (research/F2)."]
    (ROOT / "docs" / "regime_model_report.md").write_text("\n".join(L), encoding="utf-8")
    (STATE_DIR / "regime_model_full_report.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()

"""Controlled model comparison for the regime model (research agent H).

Reuses the exact feature/target/payoff definitions of scripts/train_regime_model.py and the same
expanding-window, year-by-year out-of-sample protocol, and compares:

    base    constant base rate of the training window
    logit   logistic regression, C=1, standardised   (the currently deployed model)
    xgb     XGBoost, depth 3, strong regularisation
    lgbm    LightGBM, num_leaves 8, strong regularisation
    hgb     sklearn HistGradientBoosting (the cross-check already in the repo)
    tabpfn  TabPFN v2 classifier (CPU, if installed)
    tabicl  TabICL classifier      (CPU, if installed)
    ens     0.5 * logit + 0.5 * xgb

Metrics per horizon: Brier, log loss, AUC, calibration slope/intercept, tercile condor P&L,
paired bootstrap CI for the Brier difference against the logit, seed stability for the tree
models, and a "purged" variant that drops the PURGE sessions immediately before each test year
from the training set.

    python research/experiments/model_comparison.py            # writes model_comparison_results.md

Writes nothing outside research/experiments/.
"""
from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import torch
    torch.set_num_threads(8)
except Exception:
    pass
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
HIST = ROOT / "state" / "history"
OUT = Path(__file__).resolve().parent

# --- payoff geometry, identical to scripts/train_regime_model.py -------------------------------
K_SHORT = 0.70
WING_PCT = 0.50
CREDIT_RATIO = 0.17
SPOT = 762.0
PURGE = 5              # sessions dropped before each test year in the purged variant
TFM_MAX_TRAIN = 1200   # training-window cap for the tabular foundation models (CPU budget)
SEEDS = [0, 1, 2, 3, 4]

FEATS_FULL = ["vix_prev", "slope_prev", "rv5_over_vix", "rv20_over_vix", "gap", "absret_prev",
              "is_first_friday", "is_third_friday", "dow_0", "dow_1", "dow_2", "dow_3"]
FEATS_NOGAP = [f for f in FEATS_FULL if f != "gap"]


def condor_pnl_pct(abs_move_pct: pd.Series, short_pct: pd.Series) -> pd.Series:
    credit = CREDIT_RATIO * WING_PCT
    loss = (abs_move_pct - short_pct).clip(lower=0.0).clip(upper=WING_PCT)
    return credit - loss


def load() -> dict:
    df = pd.read_csv(HIST / "daily.csv", parse_dates=["date"]).set_index("date").sort_index()
    for d in range(5):
        df[f"dow_{d}"] = (df["dow"] == d).astype(int)
    df["short_pct"] = K_SHORT * df["impl_move_cc"]

    need = ["vix_prev", "slope_prev", "rv5_over_vix", "rv20_over_vix", "gap", "absret_prev"]
    a = df.dropna(subset=["ret_1030_close"] + need).copy()
    a["abs_move"] = a["ret_1030_close"].abs() * 100
    a["inside"] = (a["abs_move"] <= a["short_pct"]).astype(int)
    a["pnl"] = condor_pnl_pct(a["abs_move"], a["short_pct"])

    b = df.dropna(subset=["ret_oc"] + need).copy()
    b["abs_move"] = b["ret_oc"].abs() * 100
    b["inside"] = (b["abs_move"] <= b["short_pct"]).astype(int)
    b["pnl"] = condor_pnl_pct(b["abs_move"], b["short_pct"])

    c = df.dropna(subset=["ret_cc", "vix_prev", "slope_prev", "rv5_over_vix", "rv20_over_vix", "absret_prev"]).copy()
    c["abs_move"] = c["ret_cc"].abs() * 100
    c["short_cc"] = 1.10 * c["impl_move_cc"]
    c["inside"] = (c["abs_move"] <= c["short_cc"]).astype(int)
    c["pnl"] = condor_pnl_pct(c["abs_move"], c["short_cc"])

    return {"A_1030_close": (a, FEATS_FULL, 2025),
            "B_open_close": (b, FEATS_FULL, 2021),
            "C_close_close": (c, FEATS_NOGAP, 2012)}


# --- model factories -----------------------------------------------------------------------
def fit_logit(Xtr, ytr, Xte, seed=0):
    mu, sd = Xtr.mean(0), Xtr.std(0)
    sd = np.where(sd == 0, 1.0, sd)
    lr = LogisticRegression(C=1.0, max_iter=2000)
    lr.fit((Xtr - mu) / sd, ytr)
    return lr.predict_proba((Xte - mu) / sd)[:, 1]


def fit_xgb(Xtr, ytr, Xte, seed=0):
    from xgboost import XGBClassifier
    m = XGBClassifier(max_depth=3, n_estimators=200, learning_rate=0.03, subsample=0.8,
                      colsample_bytree=0.8, min_child_weight=20, reg_lambda=5.0, reg_alpha=0.5,
                      random_state=seed, n_jobs=4, eval_metric="logloss", tree_method="hist")
    m.fit(Xtr, ytr)
    return m.predict_proba(Xte)[:, 1]


def fit_lgbm(Xtr, ytr, Xte, seed=0):
    from lightgbm import LGBMClassifier
    m = LGBMClassifier(num_leaves=8, max_depth=3, n_estimators=200, learning_rate=0.03,
                       min_child_samples=40, subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
                       reg_lambda=5.0, random_state=seed, n_jobs=4, verbose=-1)
    m.fit(Xtr, ytr)
    return m.predict_proba(Xte)[:, 1]


def fit_hgb(Xtr, ytr, Xte, seed=0):
    from sklearn.ensemble import HistGradientBoostingClassifier
    m = HistGradientBoostingClassifier(max_depth=3, max_iter=150, learning_rate=0.05,
                                       min_samples_leaf=40, random_state=seed)
    m.fit(Xtr, ytr)
    return m.predict_proba(Xte)[:, 1]


_TFM_CACHE: dict = {}


def fit_tabpfn(Xtr, ytr, Xte, seed=0):
    from tabpfn import TabPFNClassifier
    if "tabpfn" not in _TFM_CACHE:
        _TFM_CACHE["tabpfn"] = TabPFNClassifier(device="cpu", n_estimators=2, random_state=seed,
                                                ignore_pretraining_limits=True)
    m = _TFM_CACHE["tabpfn"]
    Xtr, ytr = Xtr[-TFM_MAX_TRAIN:], ytr[-TFM_MAX_TRAIN:]
    m.fit(Xtr, ytr)
    return m.predict_proba(Xte)[:, 1]


def fit_tabicl(Xtr, ytr, Xte, seed=0):
    from tabicl import TabICLClassifier
    if "tabicl" not in _TFM_CACHE:
        _TFM_CACHE["tabicl"] = TabICLClassifier(device="cpu", random_state=seed)
    m = _TFM_CACHE["tabicl"]
    Xtr, ytr = Xtr[-TFM_MAX_TRAIN:], ytr[-TFM_MAX_TRAIN:]
    m.fit(Xtr, ytr)
    return m.predict_proba(Xte)[:, 1]


MODELS = {"logit": fit_logit, "xgb": fit_xgb, "lgbm": fit_lgbm, "hgb": fit_hgb,
          "tabpfn": fit_tabpfn, "tabicl": fit_tabicl}


def available() -> list[str]:
    out = []
    for name in MODELS:
        if name == "logit":
            out.append(name)
            continue
        mod = {"xgb": "xgboost", "lgbm": "lightgbm", "hgb": "sklearn",
               "tabpfn": "tabpfn", "tabicl": "tabicl"}[name]
        try:
            __import__(mod)
            out.append(name)
        except Exception:
            pass
    return out


# --- CV ------------------------------------------------------------------------------------
def expanding_cv(df: pd.DataFrame, feats: list[str], first_test_year: int, model: str,
                 seed: int = 0, purge: int = 0) -> tuple[pd.Series, float]:
    """Train on all sessions in years < y (optionally dropping the last `purge` before y), test on y."""
    years = sorted(df.index.year.unique())
    test_years = [y for y in years if y >= first_test_year]
    oos = pd.Series(index=df.index, dtype=float)
    fn = MODELS[model]
    t0 = time.perf_counter()
    for y in test_years:
        tr = df[df.index.year < y]
        te = df[df.index.year == y]
        if len(tr) < 200 or len(te) == 0:
            continue
        if purge:
            tr = tr.iloc[:-purge] if len(tr) > purge + 200 else tr
        oos.loc[te.index] = fn(tr[feats].values.astype(float), tr["inside"].values,
                               te[feats].values.astype(float), seed=seed)
    return oos[oos.notna()], time.perf_counter() - t0


def calibration(y: np.ndarray, p: np.ndarray) -> tuple[float, float]:
    """Cox calibration: logistic regression of y on logit(p). Perfect = intercept 0, slope 1."""
    p = np.clip(p, 1e-6, 1 - 1e-6)
    z = np.log(p / (1 - p)).reshape(-1, 1)
    if len(set(y)) < 2 or z.std() < 1e-9:
        return float("nan"), float("nan")
    lr = LogisticRegression(C=1e6, max_iter=2000).fit(z, y)
    return float(lr.intercept_[0]), float(lr.coef_[0][0])


def metrics(y: np.ndarray, p: np.ndarray) -> dict:
    p = np.clip(p, 1e-6, 1 - 1e-6)
    icept, slope = calibration(y, p)
    return {"brier": brier_score_loss(y, p), "logloss": log_loss(y, p),
            "auc": roc_auc_score(y, p) if len(set(y)) > 1 else float("nan"),
            "cal_intercept": icept, "cal_slope": slope}


def paired_brier_ci(y: np.ndarray, p_a: np.ndarray, p_b: np.ndarray, years: np.ndarray,
                    n: int = 2000, seed: int = 11) -> tuple[float, float, float]:
    """Block (by year) paired bootstrap of Brier(a) - Brier(b). Negative = a better."""
    d = (p_a - y) ** 2 - (p_b - y) ** 2
    rng = np.random.default_rng(seed)
    uy = np.unique(years)
    blocks = [d[years == u] for u in uy]
    draws = np.empty(n)
    for i in range(n):
        idx = rng.integers(0, len(blocks), len(blocks))
        draws[i] = np.concatenate([blocks[j] for j in idx]).mean()
    return float(d.mean()), float(np.percentile(draws, 5)), float(np.percentile(draws, 95))


def terciles(df: pd.DataFrame, oos: pd.Series) -> list[dict]:
    d = df.loc[oos.index].copy()
    d["p"] = oos.values
    try:
        d["bucket"] = pd.qcut(d["p"], 3, labels=["low", "mid", "high"], duplicates="drop")
    except ValueError:
        return []
    rows = []
    for bkt, g in d.groupby("bucket", observed=True):
        rows.append({"bucket": str(bkt), "n": len(g), "p_mean": g["p"].mean(),
                     "inside": g["inside"].mean(), "pnl_pct": g["pnl"].mean(),
                     "usd": g["pnl"].mean() / 100 * SPOT * 100, "loss_share": (g["pnl"] < 0).mean()})
    return rows


def fmt(x, n=4):
    return "n/a" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{n}f}"


def main() -> None:
    data = load()
    avail = available()
    print("available models:", avail)
    L: list[str] = ["# Model comparison: regime model on the condor inside-probability",
                    "",
                    f"Generated by `research/experiments/model_comparison.py`. Geometry identical to "
                    f"`scripts/train_regime_model.py` (short = {K_SHORT} x VIX-implied full-day E|move|, "
                    f"wing {WING_PCT}% of spot, credit {CREDIT_RATIO:.0%} of wing, spot {SPOT:.0f}). "
                    f"Expanding-window yearly CV, pooled out-of-sample predictions. "
                    f"Purged variant drops the {PURGE} sessions before each test year. "
                    f"Tabular foundation models capped at {TFM_MAX_TRAIN} most recent training rows (CPU).",
                    ""]
    dump: dict = {}

    for hz, (df, feats, fty) in data.items():
        L += [f"## {hz}", ""]
        preds: dict[str, pd.Series] = {}
        times: dict[str, float] = {}
        for m in avail:
            try:
                oos, dt = expanding_cv(df, feats, fty, m, seed=0, purge=0)
                preds[m], times[m] = oos, dt
                print(f"  {hz} {m}: {dt:.1f}s n={len(oos)}")
            except Exception as e:  # noqa: BLE001
                print(f"  {hz} {m}: FAILED {type(e).__name__}: {e}")
        if "logit" in preds and "xgb" in preds:
            preds["ens_logit_xgb"] = (preds["logit"] + preds["xgb"]) / 2
            times["ens_logit_xgb"] = times.get("logit", 0) + times.get("xgb", 0)

        idx = preds["logit"].index
        y = df.loc[idx, "inside"].values
        years = idx.year.values
        base = float(df[df.index.year < fty]["inside"].mean())

        rows = [("base_rate", np.full(len(y), base), 0.0)]
        rows += [(m, preds[m].reindex(idx).values, times[m]) for m in preds]

        L += [f"n out of sample = {len(y)} ({idx.year.min()}-{idx.year.max()}), "
              f"training base rate = {base:.4f}, realised inside rate = {y.mean():.4f}", "",
              "| model | Brier | log loss | AUC | cal. intercept | cal. slope | dBrier vs logit [90% block-boot CI] | fit+predict s |",
              "|---|---|---|---|---|---|---|---|"]
        mrec = {}
        for name, p, dt in rows:
            mm = metrics(y, p)
            mrec[name] = mm
            if name == "logit":
                dstr = "-"
            else:
                d, lo, hi = paired_brier_ci(y, np.clip(p, 1e-6, 1 - 1e-6),
                                            np.clip(preds["logit"].reindex(idx).values, 1e-6, 1 - 1e-6), years)
                dstr = f"{d:+.5f} [{lo:+.5f}, {hi:+.5f}]"
            L.append(f"| {name} | {fmt(mm['brier'], 5)} | {fmt(mm['logloss'], 5)} | {fmt(mm['auc'])} | "
                     f"{fmt(mm['cal_intercept'], 3)} | {fmt(mm['cal_slope'], 3)} | {dstr} | {dt:.1f} |")
        L.append("")

        # terciles
        L += ["### Predicted-probability terciles (out of sample) vs realised condor P&L", "",
              "| model | bucket | n | mean p | inside rate | mean P&L % | mean $/contract | loss share |",
              "|---|---|---|---|---|---|---|---|"]
        for m in preds:
            for r in terciles(df, preds[m]):
                L.append(f"| {m} | {r['bucket']} | {r['n']} | {r['p_mean']:.3f} | {r['inside']:.3f} | "
                         f"{r['pnl_pct']:.4f} | {r['usd']:.2f} | {r['loss_share']:.3f} |")
        L.append("")

        # purged variant
        L += [f"### Purged variant (drop {PURGE} sessions before each test year)", "",
              "| model | Brier | AUC | dBrier vs unpurged same model |", "|---|---|---|---|"]
        purge_models = ("logit", "xgb", "lgbm") if hz == "C_close_close" else ("logit", "xgb", "lgbm", "tabpfn", "tabicl")
        for m in [x for x in purge_models if x in preds]:
            try:
                oosp, _ = expanding_cv(df, feats, fty, m, seed=0, purge=PURGE)
                pp = oosp.reindex(idx).values
                mp = metrics(y, pp)
                L.append(f"| {m} | {fmt(mp['brier'], 5)} | {fmt(mp['auc'])} | "
                         f"{mp['brier'] - mrec[m]['brier']:+.5f} |")
            except Exception as e:  # noqa: BLE001
                L.append(f"| {m} | failed: {type(e).__name__} | | |")
        L.append("")

        # seed stability for the tree models
        tree = [m for m in ("xgb", "lgbm", "hgb") if m in preds]
        if tree:
            L += ["### Seed stability (tree models, seeds " + ", ".join(map(str, SEEDS)) + ")", "",
                  "| model | Brier mean | Brier sd | Brier min-max | AUC mean | AUC sd |", "|---|---|---|---|---|---|"]
            for m in tree:
                bs, aucs = [], []
                for s in SEEDS:
                    o, _ = expanding_cv(df, feats, fty, m, seed=s)
                    mm = metrics(y, o.reindex(idx).values)
                    bs.append(mm["brier"])
                    aucs.append(mm["auc"])
                L.append(f"| {m} | {np.mean(bs):.5f} | {np.std(bs):.5f} | {min(bs):.5f}-{max(bs):.5f} | "
                         f"{np.mean(aucs):.4f} | {np.std(aucs):.4f} |")
            L.append("")

        (OUT / "model_comparison_results.md").write_text("\n".join(L), encoding="utf-8")
        dump[hz] = {"n_oos": len(y), "base": base, "metrics": {k: {kk: float(vv) for kk, vv in v.items()} for k, v in mrec.items()},
                    "times": times}

    (OUT / "model_comparison_results.md").write_text("\n".join(L), encoding="utf-8")
    (OUT / "model_comparison_results.json").write_text(json.dumps(dump, indent=2), encoding="utf-8")
    print("\nwritten:", OUT / "model_comparison_results.md")


if __name__ == "__main__":
    sys.exit(main())

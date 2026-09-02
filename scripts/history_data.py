"""Download and assemble the historical dataset for the regime model and the benchmark.

Sources (all free, no login):
  * Cboe daily histories: SPX (1975-), VIX (1990-), VIX3M (2009-), VIX9D (2011-), VIX1D (2022-)
  * Alpaca IEX: SPY daily OHLC (2018-11-) and 30-minute bars (2024-09-) for open->close and
    10:30->close moves, i.e. the exact horizon of a 0DTE condor entered in the morning window.

Output: state/history/daily.csv (one row per session, features known BEFORE the entry) and
state/history/intraday.csv (sessions with a 10:30 ET price). Nothing here touches the agent.

    python scripts/history_data.py
"""
from __future__ import annotations

import csv
import io
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.core.config import STATE_DIR, Settings  # noqa: E402

HIST = STATE_DIR / "history"
HEADERS = {"User-Agent": "Mozilla/5.0 (delphi-options-agent; hackathon research)"}
CBOE = "https://cdn.cboe.com/api/global/us_indices/daily_prices/{sym}_History.csv"


def cboe_series(sym: str) -> pd.Series:
    r = requests.get(CBOE.format(sym=sym), headers=HEADERS, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = [c.strip().lower() for c in df.columns]
    date_col = "date"
    val_col = "close" if "close" in df.columns else df.columns[-1]
    s = pd.Series(df[val_col].astype(float).values, index=pd.to_datetime(df[date_col]), name=sym.lower())
    s = s[~s.index.duplicated(keep="last")].sort_index()
    (HIST / f"{sym}.csv").write_text(s.to_csv(), encoding="utf-8")
    return s


def alpaca_bars(settings: Settings, timeframe, start: datetime, chunk_days: int = 3650) -> pd.DataFrame:
    from alpaca.data.enums import DataFeed
    from alpaca.data.historical.stock import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    c = StockHistoricalDataClient(settings.alpaca_key, settings.alpaca_secret)
    rows = []
    t0 = start
    end = datetime.now(tz=timezone.utc)
    while t0 < end:
        t1 = min(t0 + timedelta(days=chunk_days), end)
        req = StockBarsRequest(symbol_or_symbols="SPY", timeframe=timeframe, start=t0, end=t1, feed=DataFeed.IEX, limit=10000)
        bars = c.get_stock_bars(req).data.get("SPY", [])
        rows += [(b.timestamp, float(b.open), float(b.high), float(b.low), float(b.close), float(b.volume)) for b in bars]
        t0 = t1
    df = pd.DataFrame(rows, columns=["ts", "open", "high", "low", "close", "volume"]).drop_duplicates("ts").set_index("ts").sort_index()
    return df


def build() -> None:
    HIST.mkdir(parents=True, exist_ok=True)
    s = Settings()
    print("downloading Cboe histories ...")
    spx = cboe_series("SPX")
    vix = cboe_series("VIX")
    vix3m = cboe_series("VIX3M")
    vix9d = cboe_series("VIX9D")
    vix1d = cboe_series("VIX1D")
    print(f"  SPX {spx.index.min().date()}..{spx.index.max().date()} ({len(spx)}), VIX {len(vix)}, VIX3M {len(vix3m)}, VIX9D {len(vix9d)}, VIX1D {len(vix1d)}")

    from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
    print("downloading Alpaca IEX SPY daily bars ...")
    spy_d = alpaca_bars(s, TimeFrame.Day, datetime(2016, 1, 1, tzinfo=timezone.utc))
    spy_d.index = pd.to_datetime(spy_d.index).tz_convert("America/New_York").normalize().tz_localize(None)
    spy_d = spy_d[~spy_d.index.duplicated(keep="last")]
    spy_d.to_csv(HIST / "SPY_daily.csv")
    print(f"  SPY daily {spy_d.index.min().date()}..{spy_d.index.max().date()} ({len(spy_d)})")

    print("downloading Alpaca IEX SPY 30-minute bars ...")
    spy_30 = alpaca_bars(s, TimeFrame(30, TimeFrameUnit.Minute), datetime(2024, 1, 1, tzinfo=timezone.utc), chunk_days=200)
    spy_30.index = pd.to_datetime(spy_30.index).tz_convert("America/New_York")
    spy_30.to_csv(HIST / "SPY_30min.csv")
    print(f"  SPY 30-min bars {len(spy_30)}")

    # ---------------- daily table: everything a decision at 10:00 ET could know ----------------
    df = pd.DataFrame({"spx": spx})
    df["vix"] = vix
    df["vix3m"] = vix3m
    df["vix9d"] = vix9d
    df["vix1d"] = vix1d
    df = df.dropna(subset=["spx", "vix"])
    df["ret_cc"] = df["spx"].pct_change()                      # close-to-close (available for decades)
    df["vix_prev"] = df["vix"].shift(1)                        # known at the open
    df["vix3m_prev"] = df["vix3m"].shift(1)
    df["vix9d_prev"] = df["vix9d"].shift(1)
    df["vix1d_prev"] = df["vix1d"].shift(1)
    df["slope_prev"] = df["vix_prev"] / df["vix3m_prev"]
    df["rv5"] = df["ret_cc"].rolling(5).std().shift(1) * (252 ** 0.5) * 100
    df["rv20"] = df["ret_cc"].rolling(20).std().shift(1) * (252 ** 0.5) * 100
    df["rv5_over_vix"] = df["rv5"] / df["vix_prev"]
    df["rv20_over_vix"] = df["rv20"] / df["vix_prev"]
    df["absret_prev"] = df["ret_cc"].abs().shift(1) * 100
    df["dow"] = df.index.dayofweek
    df["month"] = df.index.month
    df["is_first_friday"] = ((df.index.dayofweek == 4) & (df.index.day <= 7)).astype(int)       # NFP proxy
    df["is_third_friday"] = ((df.index.dayofweek == 4) & (df.index.day >= 15) & (df.index.day <= 21)).astype(int)  # opex
    # implied expected |move| for one day from the prior VIX close: sigma_d * sqrt(2/pi)
    df["impl_move_cc"] = df["vix_prev"] / 100 / (252 ** 0.5) * (2 / 3.141592653589793) ** 0.5 * 100   # in %
    df["ratio_cc"] = df["ret_cc"].abs() * 100 / df["impl_move_cc"]

    # SPY open->close (intraday) since 2018 from Alpaca
    d = spy_d.copy()
    d["ret_oc"] = d["close"] / d["open"] - 1
    d["gap"] = d["open"] / d["close"].shift(1) - 1
    df = df.join(d[["open", "close", "ret_oc", "gap"]].rename(columns={"open": "spy_open", "close": "spy_close"}), how="left")
    df["ratio_oc"] = df["ret_oc"].abs() * 100 / df["impl_move_cc"]

    # 10:30 -> close from 30-minute bars (bar timestamps are bar starts; the 10:00 bar closes at 10:30)
    intra = spy_30.copy()
    intra["date"] = intra.index.normalize().tz_localize(None)
    intra["hhmm"] = intra.index.strftime("%H:%M")
    p1030 = intra[intra["hhmm"] == "10:00"].groupby("date")["close"].last()
    p1230 = intra[intra["hhmm"] == "12:00"].groupby("date")["close"].last()
    pclose = intra.groupby("date")["close"].last()
    hi = intra[intra["hhmm"] >= "10:30"].groupby("date")["high"].max()
    lo = intra[intra["hhmm"] >= "10:30"].groupby("date")["low"].min()
    it = pd.DataFrame({"p1030": p1030, "p1230": p1230, "pclose": pclose, "hi_after_1030": hi, "lo_after_1030": lo}).dropna(subset=["p1030", "pclose"])
    it["ret_1030_close"] = it["pclose"] / it["p1030"] - 1
    it["ret_1230_close"] = it["pclose"] / it["p1230"] - 1
    it["max_excursion_1030"] = ((it["hi_after_1030"] / it["p1030"] - 1).abs()).combine((it["lo_after_1030"] / it["p1030"] - 1).abs(), max)
    df = df.join(it, how="left")
    df["ratio_1030"] = df["ret_1030_close"].abs() * 100 / df["impl_move_cc"]

    df.index.name = "date"
    df.to_csv(HIST / "daily.csv")
    it.index.name = "date"
    it.to_csv(HIST / "intraday.csv")
    print(f"daily.csv rows {len(df)}, with open->close {df['ret_oc'].notna().sum()}, with 10:30->close {df['ret_1030_close'].notna().sum()}")
    print("median realised/implied ratio: close-to-close", round(df["ratio_cc"].median(), 3),
          "| open-to-close", round(df["ratio_oc"].median(), 3), "| 10:30-to-close", round(df["ratio_1030"].median(), 3))


if __name__ == "__main__":
    build()

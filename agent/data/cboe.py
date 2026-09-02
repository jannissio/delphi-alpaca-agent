"""Volatility term structure from Cboe delayed quotes (no login, ~15 min delay).

Used by the regime gate (VIX/VIX3M slope, Johnson 2017) and to place the VIX level in its
long-run tercile (asymmetry neutralisation). Alpaca does not distribute index levels.
"""
from __future__ import annotations

import csv
import io
import logging
from datetime import datetime, timezone
from typing import Optional

import requests

log = logging.getLogger(__name__)

QUOTE_URL = "https://cdn.cboe.com/api/global/delayed_quotes/quotes/{sym}.json"
HIST_URL = "https://cdn.cboe.com/api/global/us_indices/daily_prices/{sym}_History.csv"
HEADERS = {"User-Agent": "Mozilla/5.0 (delphi-options-agent; hackathon paper trading)"}


def _quote(sym: str, timeout: float = 10.0) -> Optional[dict]:
    try:
        r = requests.get(QUOTE_URL.format(sym=sym), headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r.json().get("data", {})
    except Exception as exc:  # network errors are a NO_TRADE condition, not a crash
        log.warning("cboe quote %s failed: %s", sym, exc)
        return None


def fetch_term_structure() -> Optional[dict]:
    """Return {vix, vix3m, vix1d, ts} or None if any leg is missing."""
    v = _quote("_VIX")
    v3 = _quote("_VIX3M")
    v1 = _quote("_VIX1D")
    if not v or not v3:
        return None
    vix = float(v.get("current_price") or 0)
    vix3m = float(v3.get("current_price") or 0)
    if vix <= 0 or vix3m <= 0:
        return None
    return {
        "vix": vix,
        "vix3m": vix3m,
        "vix1d": float(v1.get("current_price")) if v1 and v1.get("current_price") else None,
        "ts": datetime.now(tz=timezone.utc),
        "last_trade_time": v.get("last_trade_time"),
        "source": "cboe_delayed_json",
    }


def vix_history_closes(years: int = 10, sym: str = "VIX") -> list[float]:
    """Daily index closes (VIX, VIX3M, VIX1D) for tercile estimation. Falls back to [] on failure."""
    try:
        r = requests.get(HIST_URL.format(sym=sym), headers=HEADERS, timeout=20)
        r.raise_for_status()
        rows = list(csv.reader(io.StringIO(r.text)))
        closes = []
        cutoff_year = datetime.now().year - years
        for row in rows[1:]:
            try:
                d = datetime.strptime(row[0], "%m/%d/%Y")
                if d.year >= cutoff_year:
                    closes.append(float(row[4]))
            except (ValueError, IndexError):
                continue
        return closes
    except Exception as exc:
        log.warning("cboe history failed: %s", exc)
        return []


def vix_terciles(closes: list[float]) -> tuple[float, float]:
    """(lower, upper) tercile breakpoints; default to (15, 21) if no data."""
    if len(closes) < 100:
        return 15.0, 21.0
    s = sorted(closes)
    return s[len(s) // 3], s[2 * len(s) // 3]


def vix1d_top_tercile_threshold(lookback_sessions: int = 60) -> Optional[float]:
    """Upper tercile of VIX1D closes over the trailing window (F1 E-V12 implied-variance taper proxy)."""
    closes = vix_history_closes(years=2, sym="VIX1D")
    if len(closes) < 20:
        return None
    window = sorted(closes[-lookback_sessions:])
    return window[2 * len(window) // 3]

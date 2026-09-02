"""Time helpers. Everything the agent decides on is in America/New_York."""
from __future__ import annotations

from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")


def now_et() -> datetime:
    return datetime.now(tz=ET)


def to_et(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(ET)


def parse_hhmm(s: str) -> time:
    h, m = s.split(":")
    return time(int(h), int(m))


def at_et(d: date, hhmm: str) -> datetime:
    return datetime.combine(d, parse_hhmm(hhmm), tzinfo=ET)


def in_window(now: datetime, start_hhmm: str, end_hhmm: str) -> bool:
    now = to_et(now)
    return at_et(now.date(), start_hhmm) <= now < at_et(now.date(), end_hhmm)


def in_any_window(now: datetime, windows: list[list[str]]) -> bool:
    return any(in_window(now, w[0], w[1]) for w in windows)


def seconds_until(now: datetime, d: date, hhmm: str) -> float:
    return (at_et(d, hhmm) - to_et(now)).total_seconds()


def is_friday(d: date) -> bool:
    return d.weekday() == 4


def age_seconds(ts: datetime, now: datetime | None = None) -> float:
    now = now or datetime.now(tz=UTC)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=UTC)
    return (now.astimezone(UTC) - ts.astimezone(UTC)).total_seconds()


def market_minutes_remaining(now: datetime, close_hhmm: str = "16:00") -> float:
    now = to_et(now)
    return max(0.0, (at_et(now.date(), close_hhmm) - now).total_seconds() / 60.0)


def next_weekday(d: date) -> date:
    n = d + timedelta(days=1)
    while n.weekday() >= 5:
        n += timedelta(days=1)
    return n

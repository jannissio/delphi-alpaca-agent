"""Scheduled-event calendar (config/calendar.yaml) -> event flags and pause windows.

The LLM sees the same events in its prompt and returns an EVENT_RISK enum, but the
deterministic flags here are what gate_event_veto and gate_time_window act on.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Mapping

from agent.core.clock import at_et, to_et
from agent.core.models import EventRisk


@dataclass(frozen=True)
class EventFlags:
    no_trade_day: bool
    market_closed: bool
    in_pause_window: bool
    pause_reason: str
    next_major_minutes: float | None     # minutes until the next scheduled_major event today
    deterministic_event_risk: EventRisk
    events_today: tuple[str, ...]


def events_on(cal: Mapping, d: date) -> list[Mapping]:
    return [e for e in cal["events"] if e["date"] == d.isoformat()]


def flags_for(cal: Mapping, now: datetime) -> EventFlags:
    now = to_et(now)
    today = now.date()
    todays = events_on(cal, today)
    no_trade = any(e.get("no_trade_day") for e in todays)
    closed = any(e.get("market_closed") for e in todays)

    in_pause, reason = False, ""
    for e in todays:
        pw = e.get("pause_window_et")
        if pw and at_et(today, pw[0]) <= now < at_et(today, pw[1]):
            in_pause, reason = True, f"pause window for {e['name']}"
            break

    next_major = None
    severity = EventRisk.NONE
    for e in todays:
        t = at_et(today, e["time"])
        mins = (t - now).total_seconds() / 60.0
        sev = e.get("severity", "scheduled_minor")
        if sev == "scheduled_major" and mins > 0 and (next_major is None or mins < next_major):
            next_major = mins
        if sev == "scheduled_major" and -30 <= mins <= 90:
            severity = EventRisk.SCHEDULED_MAJOR
        elif sev == "scheduled_minor" and severity == EventRisk.NONE and -15 <= mins <= 30:
            severity = EventRisk.SCHEDULED_MINOR

    return EventFlags(
        no_trade_day=no_trade,
        market_closed=closed,
        in_pause_window=in_pause,
        pause_reason=reason,
        next_major_minutes=next_major,
        deterministic_event_risk=severity,
        events_today=tuple(f"{e['time']} ET {e['name']} [{e.get('severity')}]" for e in todays),
    )


def upcoming_for_prompt(cal: Mapping, now: datetime, horizon_days: int = 2) -> list[str]:
    now = to_et(now)
    out = []
    for e in cal["events"]:
        d = date.fromisoformat(e["date"])
        if now.date() <= d <= now.date() + timedelta(days=horizon_days):
            out.append(f"{e['date']} {e['time']} ET: {e['name']} ({e.get('severity')})")
    return out


def ex_dividend_block(cal: Mapping, symbol: str, today: date, sessions: int) -> bool:
    exd = cal.get("ex_dividend", {}).get(symbol)
    if not exd:
        return False
    d = date.fromisoformat(exd)
    delta = (d - today).days
    return 0 <= delta <= sessions + 2   # calendar days, generous on purpose

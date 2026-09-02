"""End-of-session update of the Conformal Condor state, for when the agent was not running at 16:10 ET.

Scores the committed interval of the session (or reconstructs it at the 10:30 ET bar exactly as the
history does), moves alpha_t by one ACI step, appends the score, and prints the record. Idempotent:
a session already folded in is skipped.

    python scripts/conformal_update.py [--date 2026-09-03] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.core import conformal as conf  # noqa: E402
from agent.core.clock import now_et  # noqa: E402
from agent.core.config import STATE_DIR, Settings  # noqa: E402
from agent.core.strategy import wing_width_for  # noqa: E402
from agent.data import cboe  # noqa: E402
from agent.data.alpaca_data import AlpacaData  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=now_et().date().isoformat())
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    day = date.fromisoformat(args.date)

    s = Settings()
    s.require_alpaca()
    p = conf.ConformalParams.from_config(s.strategy.get("conformal"))
    path = STATE_DIR / "conformal.json"
    st = conf.ConformalState.load(path)
    if st.updated_through >= day.isoformat():
        print(f"already updated through {st.updated_through}; nothing to do")
        return
    d = AlpacaData(s.alpaca_key, s.alpaca_secret, paper=True)
    bars = d.intraday_bars(s.enabled_underlyings()[0], 30, day)
    if not bars or bars[-1]["et"] < "15:30":
        raise SystemExit(f"session {day} incomplete: {len(bars)} bars, last {bars[-1]['et'] if bars else None}")
    close = bars[-1]["close"]
    if st.session and st.session.get("date") == day.isoformat():
        print("using the interval committed by the agent:", json.dumps(st.session))
    else:
        p_entry = next(b["close"] for b in bars if b["et"] == "10:00")
        vix_prev = cboe.closes_before("VIX", day, 1)[-1]
        und = s.enabled_underlyings()[0]
        wing = wing_width_for(p_entry, s.strategy["structure"], float(s.underlying_cfg(und)["strike_increment"]))
        sess = conf.open_session(st, p, day, datetime.now(tz=timezone.utc), p_entry, vix_prev, wing_usd=wing, reconstructed=True)
        print("reconstructed the interval at the 10:30 bar:", json.dumps(sess))
    rec = conf.eod_update(st, p, close, day)
    print(json.dumps(rec, indent=1))
    if args.dry_run:
        print("dry run: state not written")
        return
    st.save(path)
    print(f"saved {path}: alpha_t {st.alpha_t:.4f}, scores {len(st.scores)}, updated through {st.updated_through}")


if __name__ == "__main__":
    main()

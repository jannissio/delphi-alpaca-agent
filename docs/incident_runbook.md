# Incident runbook (gate 26)

Written before the first live cycle. Kill first, diagnose second. Never edit code while a
position is open.

## 1. Anything looks wrong (unexpected order, position, error loop, unknown state)

1. `python scripts/kill.py --flatten`
   Cancels every open order (< 5 s), writes `state/KILL`, closes every package with escalating
   limit orders. The running agent sees the flag on its next cycle and halts.
2. Confirm with a second, independent path: `bash scripts/status.sh` (Alpaca CLI) or the Alpaca
   dashboard. Positions must be zero.
3. Only then read `state/audit.jsonl` (last 200 lines) and `logs/`.

## 2. Agent process died

* Positions are protected by the broker-side rules (defined risk, day orders) and by the
  flatten script. Run `python scripts/flatten_now.py` if any package is open and it is past
  15:00 ET, otherwise restart the agent: it reloads `state/book.json` and reconciles against
  the broker before doing anything else.

## 3. Reconciliation mismatch (`recon_position_mismatch` / `recon_order_mismatch` in the audit log)

* The agent has already halted new risk. Compare `state/book.json` with `alpaca positions list`.
* If the broker shows a leg the book does not, close that leg with a limit order in the
  dashboard, then `python scripts/kill.py --clear` and restart.

## 4. Data feed down (Cboe or Alpaca data)

* The loop logs `no_trade` with the reason and keeps running; existing packages are still
  marked with Alpaca snapshots. Nothing to do unless it persists past 14:30 ET, then flatten.

## 5. LLM provider down

* Regime returns None -> gate 18 rejects -> no new risk. Existing packages are managed by code
  alone (take-profit, flatten deadline). Nothing to do.

## 6. Re-enable after a halt

* Fix the cause, `python scripts/kill.py --clear`, restart `python -m agent.main`. The
  session counters (fills, orders) persist in `state/session_<date>.json`, so the throttle
  and budget gates keep counting.

## Contacts and limits

* Paper account only (`ALPACA_PAPER_TRADE=true` is enforced at start-up).
* Session max loss 2 % ($2,000), campaign 6 % ($6,000), per order $1,000 / 5 contracts.

## 7. Planned restart with new code (Thursday 2026-09-03, before 09:30 ET / 15:30 CEST)

The config is read once at start-up, so the new logic (conformal risk control, gate 31, full size) only
goes live with a restart. Do it while the book is flat, in this order:

1. Flat and idle: `bash scripts/status.sh` shows no positions and no open orders; the audit log tail shows
   `heartbeat ... market closed`.
2. Stop the old process: `python scripts/kill.py` (cancel-all + flag), then `Stop-Process -Id <pid>`
   (pid from `Get-CimInstance Win32_Process -Filter "Name='python.exe'"`), then `python scripts/kill.py --clear`.
3. Yesterday's close must be in the conformal state: `state/conformal.json` has `updated_through` = the
   previous session. If not: `python scripts/conformal_update.py --date <previous session>`.
4. `python -m pytest -q` and `python scripts/reproduce.py` both green on the commit that will run.
5. `python scripts/preflight.py --at 10:20`: read the interval line (n >= 50 scores), the sizing line
   (`config pilot OFF`), and the P-vs-Q decision. Stale pre-market quotes are expected; the live loop
   re-reads the chain every cycle.
6. Start: `powershell -ExecutionPolicy Bypass -File scripts/run_agent_detached.ps1`; note the pid.
7. Verify within a minute: the audit log has a new `startup` record whose `git` hash is the new commit,
   then `heartbeat` lines; `python scripts/watch_audit.py` for the session.

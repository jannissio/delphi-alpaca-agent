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

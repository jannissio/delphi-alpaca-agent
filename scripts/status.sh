#!/usr/bin/env bash
# Monitoring / reconciliation snapshot via the Alpaca CLI (JSON output appended to logs/cli_status.jsonl).
# Runs from cron-like loops (`watch -n 60 scripts/status.sh`) independently of the Python agent, so a
# second, independent code path (gate 22) sees the same account. Requires `alpaca` on PATH and the
# ALPACA_API_KEY / ALPACA_SECRET_KEY env vars (see SETUP.md). Paper endpoint is the CLI default.
set -u
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
if ! command -v alpaca >/dev/null 2>&1; then
  echo "{\"ts\":\"$ts\",\"error\":\"alpaca CLI not on PATH\"}" | tee -a logs/cli_status.jsonl
  exit 0
fi
acct=$(alpaca account get --json 2>/dev/null | tr -d '\n')
pos=$(alpaca positions list --json 2>/dev/null | tr -d '\n')
ords=$(alpaca orders list --status open --json 2>/dev/null | tr -d '\n')
clk=$(alpaca clock --json 2>/dev/null | tr -d '\n')
echo "{\"ts\":\"$ts\",\"account\":${acct:-null},\"positions\":${pos:-null},\"open_orders\":${ords:-null},\"clock\":${clk:-null}}" >> logs/cli_status.jsonl
alpaca account get --jq '{equity: .equity, cash: .cash, options_bp: .options_buying_power, level: .options_trading_level}' 2>/dev/null
alpaca positions list --jq '.[] | {symbol, qty, side, unrealized_pl}' 2>/dev/null

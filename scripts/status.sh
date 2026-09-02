#!/usr/bin/env bash
# Monitoring / reconciliation snapshot via the Alpaca CLI (JSON output appended to logs/cli_status.jsonl).
# Runs from cron-like loops (`watch -n 60 scripts/status.sh`) independently of the Python agent, so a
# second, independent code path (gate 22) sees the same account. Requires `alpaca` on PATH and the
# ALPACA_API_KEY / ALPACA_SECRET_KEY env vars (see SETUP.md). Paper endpoint is the CLI default.
set -u
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
# credentials from .env (the CLI reads ALPACA_API_KEY / ALPACA_SECRET_KEY; paper is its default).
# Tolerant parser: ignores comments, strips CR and whitespace around '='.
if [ -f .env ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    line="${line%%$'\r'}"
    case "$line" in ''|\#*) continue ;; esac
    key="${line%%=*}"; val="${line#*=}"
    key="$(echo "$key" | sed -E 's/^[[:space:]]+|[[:space:]]+$//g')"
    val="$(echo "$val" | sed -E 's/^[[:space:]]+|[[:space:]]+$//g; s/[[:space:]]+#.*$//')"
    [ -n "$key" ] && export "$key=$val"
  done < .env
fi
export ALPACA_QUIET=1
if ! command -v alpaca >/dev/null 2>&1; then
  if [ -x /c/tools/alpaca/alpaca.exe ]; then PATH="$PATH:/c/tools/alpaca"; else
    echo "{\"ts\":\"$ts\",\"error\":\"alpaca CLI not on PATH\"}" | tee -a logs/cli_status.jsonl
    exit 0
  fi
fi
acct=$(alpaca account get 2>/dev/null | tr -d '\n')
pos=$(alpaca position list 2>/dev/null | tr -d '\n')
ords=$(alpaca order list --status open 2>/dev/null | tr -d '\n')
clk=$(alpaca clock 2>/dev/null | tr -d '\n')
echo "{\"ts\":\"$ts\",\"account\":${acct:-null},\"positions\":${pos:-null},\"open_orders\":${ords:-null},\"clock\":${clk:-null}}" >> logs/cli_status.jsonl
alpaca account get --jq '{equity: .equity, cash: .cash, options_bp: .options_buying_power, level: .options_trading_level}' 2>/dev/null
alpaca position list --jq '.[] | {symbol, qty, side, unrealized_pl}' 2>/dev/null
alpaca order list --status open --jq '.[] | {id, status, order_class, limit_price, legs: (.legs // [] | length)}' 2>/dev/null

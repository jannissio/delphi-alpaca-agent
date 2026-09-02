#!/usr/bin/env bash
# Start the live paper loop with logs on disk. Usage: bash scripts/run_agent.sh [--dry-run]
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
if [ "${1:-}" = "--dry-run" ]; then export AGENT_DRY_RUN=true; fi
export PYTHONIOENCODING=utf-8
stamp=$(date -u +%Y%m%dT%H%M%SZ)
echo "starting agent (dry_run=${AGENT_DRY_RUN:-false}) -> logs/agent_${stamp}.log"
exec ./.venv/Scripts/python.exe -m agent.main 2>&1 | tee -a "logs/agent_${stamp}.log"

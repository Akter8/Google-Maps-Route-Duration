#!/usr/bin/env bash
# Run one traffic collection safely from cron or an interactive shell.
set -Eeuo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/traffic-collector"
STATE_DIR="${TRAFFIC_COLLECTOR_STATE_DIR:-${XDG_STATE_HOME:-$HOME/.local/state}/traffic-collector}"
ENV_FILE="${TRAFFIC_COLLECTOR_ENV_FILE:-$CONFIG_DIR/collector.env}"
LOG_FILE="${TRAFFIC_COLLECTOR_LOG_FILE:-$STATE_DIR/collector.log}"
LOCK_FILE="${TRAFFIC_COLLECTOR_LOCK_FILE:-$STATE_DIR/collector.lock}"
PYTHON_BIN="${TRAFFIC_COLLECTOR_PYTHON:-$PROJECT_DIR/.venv/bin/python}"

if [[ ! -r "$ENV_FILE" ]]; then
  echo "Configuration file not found or unreadable: $ENV_FILE" >&2
  exit 2
fi
if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python executable not found: $PYTHON_BIN. Create .venv and install requirements first." >&2
  exit 2
fi

mkdir -p "$STATE_DIR"
chmod 700 "$STATE_DIR"

# collector.env is an owner-only shell environment file. Do not put commands in it.
# shellcheck disable=SC1090
set -a
source "$ENV_FILE"
set +a

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "$(date --iso-8601=seconds) skipped: another collector run is active" >> "$LOG_FILE"
  exit 0
fi

cd "$PROJECT_DIR"
"$PYTHON_BIN" -m src.collector "$@" >> "$LOG_FILE" 2>&1

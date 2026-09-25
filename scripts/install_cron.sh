#!/usr/bin/env bash
# Install or replace this user's traffic-collector crontab block.
set -Eeuo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNER="$PROJECT_DIR/scripts/run_collector.sh"
BEGIN="# BEGIN traffic-collector"
END="# END traffic-collector"

if [[ ! -x "$RUNNER" ]]; then
  echo "Make the runner executable first: chmod +x $RUNNER" >&2
  exit 2
fi

existing="$(crontab -l 2>/dev/null || true)"
filtered="$(printf '%s\n' "$existing" | sed "/^${BEGIN}$/,/^${END}$/d")"
{
  printf '%s\n' "$filtered"
  printf '%s\n' "$BEGIN"
  printf '%s\n' 'CRON_TZ=America/Los_Angeles'
  printf '%s\n' "0,30 5-6 * * 1-5 /bin/bash $RUNNER"
  printf '%s\n' "*/15 7-9 * * 1-5 /bin/bash $RUNNER"
  printf '%s\n' "0,30 10-14 * * 1-5 /bin/bash $RUNNER"
  printf '%s\n' "*/15 15-18 * * 1-5 /bin/bash $RUNNER"
  printf '%s\n' "0,30 19-21 * * 1-5 /bin/bash $RUNNER"
  printf '%s\n' "$END"
} | crontab -

echo "Installed local weekday traffic-collector schedule (America/Los_Angeles)."
crontab -l

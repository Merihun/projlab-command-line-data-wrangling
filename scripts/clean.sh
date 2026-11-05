#!/usr/bin/env bash
# Clean one order export.
# Usage: scripts/clean.sh IN OUT
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 IN OUT" >&2
  exit 2
fi

tr -d '\r' < "$1" | sed 's/[[:space:]]*$//' | grep -v '^$' | awk '!seen[$0]++' > "$2"

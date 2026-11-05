#!/usr/bin/env bash
# Split a cleaned export into valid and rejected rows. Both files keep the header.
# Usage: scripts/split_valid.sh IN GOOD BAD
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "usage: $0 IN GOOD BAD" >&2
  exit 2
fi

awk -F, -v good="$2" -v bad="$3" '
  # the rules of the next two instructions go here
    NR == 1 { print > good; print > bad; next }
    NF == 7 && $5 ~ /^[1-9][0-9]*$/ && $6 ~ /^[0-9]+\.[0-9][0-9]$/ { print > good; next }
  { print > bad }
' "$1"
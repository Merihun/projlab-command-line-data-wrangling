#!/usr/bin/env bash
# Orders and revenue per day from valid order files, cancelled orders left out: "date,orders,revenue".
# Usage: scripts/daily_revenue.sh FILE...
set -euo pipefail

awk -F, '
  FNR == 1 { next }
  $7 != "cancelled" { day = substr($2, 1, 10); orders[day]++; revenue[day] += $5 * $6 }
  END { for (d in orders) printf "%s,%d,%.2f\n", d, orders[d], revenue[d] }
' "$@" | sort
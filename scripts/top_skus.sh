#!/usr/bin/env bash
set -euo pipefail

tail -q -n +2 incoming/orders/*.csv | cut -d, -f4 | sort | uniq -c | sort -rn | head -n 5
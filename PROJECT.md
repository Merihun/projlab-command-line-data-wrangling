# Command Line Data Wrangling: what this starter gives you

You start on the command line, the way most data engineering starts: files land on a Linux machine and
someone has to inspect, clean, check, add up and move them, every night, without breaking anything when the
job runs twice. You will do all of it with the shell tools every Linux server has.

| Provided | What it is |
|----------|------------|
| `fernhill_files/` | Makes the files you work on. You do not change it. |
| `answers/explore.txt` | Your answers for the first step. |
| `bin/`, `scripts/`, `ops/` | Empty: your scripts go here, step by step. |
| `Makefile` | `make data` recreates the files, `make lint` runs shellcheck, `make check` runs the project's checks. |

## Make the files

Inside the workspace (VS Code: Terminal → New Terminal; Docker lab: `docker compose exec workspace bash`):

    python -m fernhill_files generate

It writes, in this folder:

| Path | What it is |
|------|------------|
| `incoming/orders/orders_YYYYMMDD.csv` | Fourteen nightly order exports, 1 to 14 September 2026. Columns: `order_id,order_ts,customer_id,sku,quantity,unit_price,status`. |
| `incoming/customers.csv` | 400 customers: `customer_id,name,country`. |
| `app-logs/loader-YYYYMMDD.log` | What the old loader wrote each night: INFO, WARN and ERROR lines. |

Every copy of the project gets exactly the same files. Run the command again whenever you want them back as
they were (for example after archiving some in step 9).

## What is wrong with the files

Real exports are messy, and these are messy on purpose, one problem per file so you meet each one:

- `orders_20260903.csv` was exported on Windows: every line ends in a carriage return (`\r\n`).
- `orders_20260906.csv` has five lines twice: the export ran twice into one file.
- `orders_20260909.csv` has spaces at the end of lines and two blank lines at the end.
- `orders_20260911.csv` has five rows that are not valid orders.

A row is a **valid order** when it has exactly 7 fields, the quantity is a whole number of at least 1, and
the price has two decimals (`12.50`, not `12.5`). **Revenue** is quantity × unit price, summed over orders
whose status is not `cancelled`.

## What you will have at the end

- `scripts/*.sh`: small tools that each do one thing (count, clean, split, add up, join, archive).
- `bin/nightly.sh YYYY-MM-DD`: one command that loads a day into `warehouse/date=YYYY-MM-DD/`, keeps
  `warehouse/daily_revenue.csv` up to date, logs to `logs/nightly.log`, and can run again safely.
- `ops/crontab.txt`: the schedule.

`incoming/`, `app-logs/`, `warehouse/`, `archive/` and `logs/` are in `.gitignore`: they are rebuilt from the
generator and your scripts, so only your scripts and answers go into git.

## The shell in the lab

The workspace runs Debian Linux with GNU bash 5, coreutils, `sed`, `grep`, `find`, `tar`, `sha256sum`,
`join`, `flock` and `mawk` as `awk`. Stick to plain POSIX awk (no `gawk`-only functions such as `asort`).
If you also try commands on a Mac, some flags differ (`sed -i`, `date -d`): the lab is the reference.

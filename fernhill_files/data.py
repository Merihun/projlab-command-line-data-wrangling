"""The files, from fixed seeds: every copy of the project gets the same bytes."""

from __future__ import annotations

import random
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

DAYS = [date(2026, 9, 1) + timedelta(days=i) for i in range(14)]
HEADER = "order_id,order_ts,customer_id,sku,quantity,unit_price,status"
CUSTOMERS = 400
COUNTRIES = ("GB", "GB", "GB", "IE", "FR", "DE", "NL", "ES")
# The five best sellers, with clearly different shares so "the top five" has one answer.
TOP_SKUS = ("SKU-1042", "SKU-1007", "SKU-1113", "SKU-1088", "SKU-1150")
TOP_WEIGHTS = (14, 11, 9, 7, 5)
OTHER_SKUS = tuple(f"SKU-{n}" for n in range(1001, 1161) if f"SKU-{n}" not in TOP_SKUS)

# The problems, one per file, so each step meets one.
CRLF_DAY = date(2026, 9, 3)  # exported from a Windows machine
DUPLICATE_DAY = date(2026, 9, 6)  # the export job ran twice into one file
TRAILING_DAY = date(2026, 9, 9)  # trailing spaces and blank lines at the end
MALFORMED_DAY = date(2026, 9, 11)  # five rows that are not valid orders
DUPLICATES = 5


def _rng(*parts: object) -> random.Random:
    return random.Random(":".join(["fernhill-files-v1", *map(str, parts)]))


def customers() -> list[str]:
    r = _rng("customers")
    given = ("Ada", "Ben", "Chloe", "Dev", "Elin", "Farid", "Grace", "Hugo", "Isla", "Jamal", "Kira", "Leo")
    family = ("Abbott", "Bose", "Clarke", "Dlamini", "Evans", "Fraser", "Gupta", "Hart", "Ito", "Jones")
    rows = ["customer_id,name,country"]
    for i in range(1, CUSTOMERS + 1):
        rows.append(f"{5000 + i},{r.choice(given)} {r.choice(family)},{r.choice(COUNTRIES)}")
    return rows


def orders(day: date) -> list[str]:
    """The valid orders of one day, as CSV lines without the header, in the order the shop wrote them."""
    r = _rng("orders", day)
    lines = []
    seconds = sorted(r.sample(range(86400), 180 + r.randint(0, 60)))
    for i, s in enumerate(seconds, start=1):
        sku = r.choices(TOP_SKUS, TOP_WEIGHTS)[0] if r.random() < 0.3 else r.choice(OTHER_SKUS)
        price = Decimal(r.randint(450, 12000)) / 100
        status = r.choices(("paid", "shipped", "cancelled"), (60, 32, 8))[0]
        ts = f"{day.isoformat()}T{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}Z"
        lines.append(f"FH{day:%m%d}{i:04d},{ts},{5001 + r.randrange(CUSTOMERS)},{sku},{r.randint(1, 5)},{price:.2f},{status}")
    return lines


def raw_file(day: date) -> bytes:
    """The order export exactly as it lands, problems included."""
    lines = [HEADER, *orders(day)]
    if day == DUPLICATE_DAY:
        r = _rng("duplicates")
        for line in r.sample(lines[1:], DUPLICATES):
            lines.insert(r.randint(len(lines) // 2, len(lines)), line)
    if day == MALFORMED_DAY:
        r = _rng("malformed")
        bad = [
            f"FH{day:%m%d}9001,{day}T23:58:10Z,5012,SKU-1007,2",  # the last two fields are missing
            f"FH{day:%m%d}9002,{day}T23:58:44Z,5100,SKU-1042,two,19.99,paid",  # quantity is a word
            f"FH{day:%m%d}9003,{day}T23:59:02Z,5233,SKU-1113,0,7.50,paid",  # nobody orders zero
            f"FH{day:%m%d}9004,{day}T23:59:30Z,5301,SKU-1088,1,12.5,paid",  # a price without two decimals
            f"FH{day:%m%d}9005,{day}T23:59:41Z,5050,SKU-1150,1,9.99,paid,gift",  # one field too many
        ]
        for line in bad:
            lines.insert(r.randint(1, len(lines)), line)
    if day == TRAILING_DAY:
        r = _rng("trailing")
        lines = [line + " " * r.choice((0, 0, 1, 3)) for line in lines] + ["", ""]
    text = "\r\n".join(lines) + "\r\n" if day == CRLF_DAY else "\n".join(lines) + "\n"
    return text.encode()


def loader_log(day: date) -> list[str]:
    """What the old loader wrote for a day: INFO lines, a few WARN, and ERROR on some nights."""
    r = _rng("log", day)
    out = [f"{day}T01:30:0{r.randint(0, 9)}Z INFO  start load of orders_{day:%Y%m%d}.csv"]
    for _ in range(r.randint(6, 14)):
        out.append(f"{day}T01:3{r.randint(0, 9)}:{r.randint(10, 59)}Z INFO  batch committed rows={r.randint(20, 60)}")
    for _ in range(r.randint(0, 3)):
        out.append(f"{day}T01:4{r.randint(0, 9)}:{r.randint(10, 59)}Z WARN  slow statement took {r.randint(3, 9)}.{r.randint(0, 9)}s")
    if day.day % 4 == 2:
        out.append(f"{day}T01:5{r.randint(0, 9)}:{r.randint(10, 59)}Z ERROR connection reset by peer")
    if day == MALFORMED_DAY:
        out.append(f"{day}T01:59:59Z ERROR could not parse 5 rows")
    out.append(f"{day}T01:59:59Z INFO  done")
    return out


def generate(root: Path) -> dict[str, int]:
    """Write ``incoming/`` and ``app-logs/`` under ``root``, replacing what is there."""
    orders_dir, logs_dir = root / "incoming" / "orders", root / "app-logs"
    for folder in (orders_dir, logs_dir):
        folder.mkdir(parents=True, exist_ok=True)
        for old in folder.iterdir():
            if old.is_file():
                old.unlink()
    for day in DAYS:
        (orders_dir / f"orders_{day:%Y%m%d}.csv").write_bytes(raw_file(day))
        (logs_dir / f"loader-{day:%Y%m%d}.log").write_text("\n".join(loader_log(day)) + "\n")
    (root / "incoming" / "customers.csv").write_text("\n".join(customers()) + "\n")
    return {"order_files": len(DAYS), "log_files": len(DAYS)}


# ---------------------------------------------------------------- what the files hold, for checking answers


def clean_lines(day: date) -> list[str]:
    """The export after cleaning: no carriage returns or trailing spaces, no blank lines, each line once."""
    seen, out = set(), []
    for line in raw_file(day).decode().split("\n"):
        line = line.replace("\r", "").rstrip(" \t")
        if line and line not in seen:
            seen.add(line)
            out.append(line)
    return out


def is_valid(line: str) -> bool:
    import re

    fields = line.split(",")
    return (
        len(fields) == 7
        and re.fullmatch(r"[1-9][0-9]*", fields[4]) is not None
        and re.fullmatch(r"[0-9]+\.[0-9][0-9]", fields[5]) is not None
    )


def daily_revenue(day: date) -> tuple[int, Decimal]:
    """``(orders, revenue)`` of a day's valid, not cancelled orders."""
    count, total = 0, Decimal(0)
    for line in clean_lines(day)[1:]:
        if is_valid(line):
            f = line.split(",")
            if f[6] != "cancelled":
                count += 1
                total += int(f[4]) * Decimal(f[5])
    return count, total

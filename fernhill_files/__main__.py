"""python -m fernhill_files generate    write incoming/ and app-logs/ (again) in this folder"""

import sys
from pathlib import Path

from . import data


def main(argv: list[str]) -> int:
    if argv[:1] != ["generate"]:
        print(__doc__)
        return 2
    counts = data.generate(Path.cwd())
    print(f"Wrote {counts['order_files']} order files to incoming/orders, incoming/customers.csv, and {counts['log_files']} logs to app-logs/")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

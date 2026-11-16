"""Command-line entry point for ERA5 extraction."""
import argparse
import logging
import sys
from datetime import date

from stormtrace.extract.extract import extract_all


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract ERA5 daily weather.")
    parser.add_argument("--city", help="One city name, e.g. Kochi. Default: all six.")
    parser.add_argument("--start-date", type=date.fromisoformat, help="YYYY-MM-DD")
    parser.add_argument("--end-date", type=date.fromisoformat, help="YYYY-MM-DD")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    succeeded, failed = extract_all(args.city, args.start_date, args.end_date)

    print(f"\nSucceeded: {len(succeeded)}")
    for name, path in succeeded:
        print(f"  {name}: {path.name}")
    print(f"Failed: {len(failed)}")
    for name, reason in failed:
        print(f"  {name}: {reason}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
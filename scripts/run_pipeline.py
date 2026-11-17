"""Main command: run the complete STORMTRACE pipeline."""
import argparse
import sys
from datetime import datetime, timezone

from stormtrace.logging_setup import setup_logging
from stormtrace.pipeline import run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the STORMTRACE pipeline.")
    parser.add_argument("--mode", choices=["incremental", "backfill"], default="incremental",
                        help="incremental (default): recent days only. backfill: full history.")
    parser.add_argument("--city", help="One city, e.g. Kochi. Default: all six.")
    args = parser.parse_args()

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = setup_logging(run_id)
    try:
        summary = run_pipeline(args.mode, args.city, run_id)
    except Exception as exc:
        print(f"\nPIPELINE FAILED: {exc}")
        print(f"Full details: {log_path}")
        return 1

    print("\nPIPELINE SUCCESS")
    print(f"  mode: {summary['mode']}  city: {summary['city']}  end date: {summary['end_date']}")
    print(f"  raw files read: {summary['raw_files_read']}")
    print(f"  rows sent: {summary['load']['rows_sent']}")
    print(f"  rows before: {summary['load']['rows_before']}  after: {summary['load']['rows_after']}")
    print(f"  NaN rows in database: {summary['verification']['nan_rows']}")
    for c in summary["verification"]["per_city"]:
        print(f"  city {c['city_id']}: {c['days']} days, {c['first']} to {c['last']}, gaps {c['gaps']}")
    print(f"  log: {log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
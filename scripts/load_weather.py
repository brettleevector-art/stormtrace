"""Load data/processed/weather_daily.csv into PostgreSQL."""
import logging
import sys

import pandas as pd

from stormtrace import config
from stormtrace.load.database import DatabaseError
from stormtrace.load.load_data import load_all
from stormtrace.validation.quality_checks import critical_failures, run_checks


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    csv_path = config.PROCESSED_DIR / "weather_daily.csv"
    if not csv_path.exists():
        print("weather_daily.csv not found. Run transform_weather.py first.")
        return 1

    df = pd.read_csv(csv_path)
    failures = critical_failures(run_checks(df))
    if failures:
        print("Refusing to load. Critical data quality failures:")
        for f in failures:
            print(f"  {f.name}: {f.detail}")
        return 1

    try:
        result = load_all(df)
    except DatabaseError as exc:
        print(exc)
        return 1

    print("\nLoad complete:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
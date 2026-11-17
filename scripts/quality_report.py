"""Run quality checks on data/processed/weather_daily.csv and write a report."""
import sys

import pandas as pd

from stormtrace import config
from stormtrace.validation.quality_checks import build_report, critical_failures, run_checks


def main() -> int:
    csv_path = config.PROCESSED_DIR / "weather_daily.csv"
    if not csv_path.exists():
        print("weather_daily.csv not found. Run transform_weather.py first.")
        return 1

    df = pd.read_csv(csv_path)
    results = run_checks(df, start_date=config.START_DATE, end_date=config.safe_end_date())
    report = build_report(df, results)
    print(report)

    out = config.PROCESSED_DIR / "quality_report.txt"
    out.write_text(report, encoding="utf-8")
    print(f"\nReport saved to {out}")
    return 1 if critical_failures(results) else 0


if __name__ == "__main__":
    sys.exit(main())
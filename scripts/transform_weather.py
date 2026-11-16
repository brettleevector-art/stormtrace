"""Combine all raw files into data/processed/weather_daily.csv."""
import sys

import pandas as pd

from stormtrace import config
from stormtrace.transform.clean import clean
from stormtrace.transform.transform import transform_file


def main() -> int:
    files = sorted(config.RAW_DIR.glob("*.json"))
    if not files:
        print("No raw files found in data/raw/. Run extract_weather.py first.")
        return 1

    print(f"Reading {len(files)} raw files...")
    combined = pd.concat([transform_file(f) for f in files], ignore_index=True)
    cleaned, report = clean(combined)

    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = config.PROCESSED_DIR / "weather_daily.csv"
    cleaned.to_csv(out, index=False)

    print("\nCleaning report:")
    for key, value in report.items():
        print(f"  {key}: {value}")

    print(f"\nWrote {out}  shape={cleaned.shape}")
    print("\nPer city:")
    print(cleaned.groupby("city")["date"].agg(["count", "min", "max"]).to_string())
    print("\nMissing values per column:")
    print(cleaned.isna().sum().to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
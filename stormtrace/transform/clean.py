"""Clean combined daily data. Missing values stay missing, never zero."""
import pandas as pd

from stormtrace.transform.transform import OUTPUT_COLUMNS

NON_NEGATIVE = ["precipitation_mm", "rain_mm", "precipitation_hours", "sunshine_hours"]

CORE_WEATHER_COLUMNS = [
    "temperature_max", "temperature_min", "temperature_mean",
    "precipitation_mm", "rain_mm", "weather_code",
    "wind_speed_max", "wind_direction", "sunshine_hours",
]


def clean(df: pd.DataFrame):
    """Return (clean_df, report). The report counts every fix so nothing is hidden."""
    df = df.copy()
    report = {}

    # 1. Invalid dates
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    report["invalid_dates_dropped"] = int(df["date"].isna().sum())
    df = df.dropna(subset=["date"])

    # 2. Remove records without usable core weather measurements
    unusable = df[CORE_WEATHER_COLUMNS].isna().all(axis=1)
    report["unusable_rows_dropped"] = int(unusable.sum())
    df = df.loc[~unusable]

    # 3. Duplicate city/date: keep the most recently extracted usable row
    df = df.sort_values(["city_id", "date", "extracted_at"])
    duplicated = df.duplicated(["city_id", "date"], keep="last")
    report["duplicates_removed"] = int(duplicated.sum())
    df = df[~duplicated]

    # 3. Hours of precipitation are meaningless when the rainfall total is missing
    orphan_hours = df["precipitation_mm"].isna() & df["precipitation_hours"].notna()
    report["precip_hours_set_missing"] = int(orphan_hours.sum())
    df.loc[orphan_hours, "precipitation_hours"] = float("nan")

    # 4. Impossible values become missing (never zero)
    for column in NON_NEGATIVE:
        bad = df[column] < 0
        report[f"{column}_negative_set_missing"] = int(bad.sum())
        df.loc[bad, column] = float("nan")

    bad_direction = (df["wind_direction"] < 0) | (df["wind_direction"] > 360)
    report["wind_direction_out_of_range_set_missing"] = int(bad_direction.sum())
    df.loc[bad_direction, "wind_direction"] = float("nan")

    # 5. Temperature ordering: counted and reported, not altered
    both = df[["temperature_min", "temperature_mean", "temperature_max"]].notna().all(axis=1)
    order_ok = (df["temperature_min"] <= df["temperature_mean"]) & (
        df["temperature_mean"] <= df["temperature_max"]
    )
    report["temperature_order_violations"] = int((both & ~order_ok).sum())

    df = df[OUTPUT_COLUMNS].sort_values(["city_id", "date"]).reset_index(drop=True)
    return df, report
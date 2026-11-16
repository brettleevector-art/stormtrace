"""Turn one raw ERA5 JSON file into a standardized daily DataFrame."""
import json
from pathlib import Path

import pandas as pd

COLUMN_MAP = {
    "temperature_2m_max": "temperature_max",
    "temperature_2m_min": "temperature_min",
    "temperature_2m_mean": "temperature_mean",
    "precipitation_sum": "precipitation_mm",
    "rain_sum": "rain_mm",
    "precipitation_hours": "precipitation_hours",
    "weather_code": "weather_code",
    "wind_speed_10m_max": "wind_speed_max",
    "wind_direction_10m_dominant": "wind_direction",
}

OUTPUT_COLUMNS = [
    "city_id", "city", "date",
    "temperature_max", "temperature_min", "temperature_mean",
    "precipitation_mm", "rain_mm", "precipitation_hours",
    "weather_code", "wind_speed_max", "wind_direction", "sunshine_hours",
]


def transform_file(path) -> pd.DataFrame:
    """Read one raw file and return one row per date, with project column names."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    meta = payload["meta"]
    daily = payload["response"]["daily"]

    expected_keys = ["time", "sunshine_duration", *COLUMN_MAP]
    count = len(daily["time"])
    for key in expected_keys:
        if key not in daily:
            raise ValueError(f"{path}: missing variable '{key}'")
        if len(daily[key]) != count:
            raise ValueError(f"{path}: '{key}' has {len(daily[key])} values, expected {count}")

    df = pd.DataFrame({key: daily[key] for key in expected_keys})
    df = df.rename(columns={"time": "date", **COLUMN_MAP})
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # The API gives sunshine in seconds. Convert to hours.
    df["sunshine_hours"] = pd.to_numeric(df["sunshine_duration"], errors="coerce") / 3600
    df = df.drop(columns=["sunshine_duration"])

    for column in COLUMN_MAP.values():
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df["weather_code"] = df["weather_code"].astype("Int64")

    df["city_id"] = meta["city_id"]
    df["city"] = meta["city"]
    df["extracted_at"] = meta["extracted_at"]   # used later to pick the newest duplicate
    return df[[*OUTPUT_COLUMNS, "extracted_at"]]
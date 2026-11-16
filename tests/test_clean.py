import pandas as pd

from stormtrace.transform.clean import clean
from stormtrace.transform.transform import OUTPUT_COLUMNS


def row(**overrides):
    base = {
        "city_id": 1, "city": "Kochi", "date": "2024-01-01",
        "temperature_max": 30.0, "temperature_min": 24.0, "temperature_mean": 27.0,
        "precipitation_mm": 1.0, "rain_mm": 1.0, "precipitation_hours": 2.0,
        "weather_code": 61, "wind_speed_max": 12.0, "wind_direction": 90.0,
        "sunshine_hours": 5.0, "extracted_at": "2026-11-16T10:00:00+00:00",
    }
    base.update(overrides)
    return base


def test_duplicate_keeps_newest_extraction():
    df = pd.DataFrame([
        row(temperature_mean=20.0, extracted_at="2026-11-01T00:00:00+00:00"),
        row(temperature_mean=27.0, extracted_at="2026-11-16T00:00:00+00:00"),
    ])
    cleaned, report = clean(df)
    assert len(cleaned) == 1
    assert cleaned["temperature_mean"].iloc[0] == 27.0
    assert report["duplicates_removed"] == 1


def test_precip_hours_missing_when_total_missing():
    df = pd.DataFrame([row(precipitation_mm=float("nan"), precipitation_hours=2.0)])
    cleaned, report = clean(df)
    assert pd.isna(cleaned["precipitation_hours"].iloc[0])
    assert report["precip_hours_set_missing"] == 1


def test_negative_rain_becomes_missing_not_zero():
    df = pd.DataFrame([row(rain_mm=-5.0)])
    cleaned, _ = clean(df)
    assert pd.isna(cleaned["rain_mm"].iloc[0])


def test_output_columns_and_no_extracted_at():
    cleaned, _ = clean(pd.DataFrame([row()]))
    assert list(cleaned.columns) == OUTPUT_COLUMNS
import json

import pytest

from stormtrace.transform.transform import OUTPUT_COLUMNS, transform_file


def make_payload(days=3, break_length=False):
    daily = {
        "time": [f"2024-01-0{i + 1}" for i in range(days)],
        "temperature_2m_max": [30.0] * days,
        "temperature_2m_min": [24.0] * days,
        "temperature_2m_mean": [27.0] * days,
        "precipitation_sum": [0.0] * days,
        "rain_sum": [0.0] * days,
        "precipitation_hours": [0.0] * days,
        "weather_code": [3] * days,
        "wind_speed_10m_max": [12.0] * days,
        "wind_direction_10m_dominant": [90] * days,
        "sunshine_duration": [36000.0] * days,
    }
    if break_length:
        daily["rain_sum"] = daily["rain_sum"][:-1]
    return {
        "meta": {"city_id": 1, "city": "Kochi", "extracted_at": "2026-11-16T10:00:00+00:00"},
        "response": {"daily": daily},
    }


def write(tmp_path, payload):
    path = tmp_path / "raw.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_columns_and_rows(tmp_path):
    df = transform_file(write(tmp_path, make_payload(3)))
    assert list(df.columns) == [*OUTPUT_COLUMNS, "extracted_at"]
    assert len(df) == 3
    assert set(df["city"]) == {"Kochi"}


def test_sunshine_seconds_become_hours(tmp_path):
    df = transform_file(write(tmp_path, make_payload(3)))
    assert df["sunshine_hours"].iloc[0] == pytest.approx(10.0)


def test_length_mismatch_raises(tmp_path):
    with pytest.raises(ValueError, match="rain_sum"):
        transform_file(write(tmp_path, make_payload(3, break_length=True)))




import pandas as pd

from stormtrace.transform.clean import clean, CORE_WEATHER_COLUMNS


def test_unusable_newer_record_does_not_replace_older_valid_record(tmp_path):
    valid = transform_file(write(tmp_path, make_payload(3)))
    valid["extracted_at"] = "2026-11-16T10:00:00+00:00"

    unusable = valid.iloc[[2]].copy()
    unusable[CORE_WEATHER_COLUMNS] = float("nan")
    unusable["precipitation_hours"] = 0.0
    unusable["extracted_at"] = "2026-11-17T07:18:21+00:00"

    combined = pd.concat([valid, unusable], ignore_index=True)
    cleaned, report = clean(combined)

    final_day = cleaned[cleaned["date"] == pd.Timestamp("2024-01-03")]

    assert len(final_day) == 1
    assert final_day.iloc[0]["temperature_mean"] == 27.0
    assert report["unusable_rows_dropped"] == 1
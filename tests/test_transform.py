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
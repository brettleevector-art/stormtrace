import datetime

import pandas as pd

from stormtrace.load.load_data import FACT_COLUMNS, to_records


def make_df():
    return pd.DataFrame({
        "city_id": [1, 1],
        "city": ["Kochi", "Kochi"],
        "date": ["2024-01-01", "2024-01-02"],
        "temperature_max": [30.0, float("nan")],
        "temperature_min": [24.0, float("nan")],
        "temperature_mean": [27.0, float("nan")],
        "precipitation_mm": [0.0, float("nan")],
        "rain_mm": [0.0, float("nan")],
        "precipitation_hours": [0.0, float("nan")],
        "weather_code": pd.array([3, None], dtype="Int64"),
        "wind_speed_max": [12.0, float("nan")],
        "wind_direction": [90.0, float("nan")],
        "sunshine_hours": [10.0, float("nan")],
    })


def test_missing_values_become_none_not_nan():
    records = to_records(make_df())
    assert len(records[0]) == len(FACT_COLUMNS)
    assert all(value is None for value in records[1][2:])


def test_values_are_plain_python_types():
    first = to_records(make_df())[0]
    assert type(first[0]) is int
    assert type(first[1]) is datetime.date
    assert type(first[2]) is float
    assert type(first[8]) is int


def test_zero_stays_zero():
    first = to_records(make_df())[0]
    assert first[5] == 0.0
from datetime import date

import pandas as pd

from stormtrace.validation.quality_checks import run_checks


def row(**overrides):
    base = {
        "city_id": 1, "city": "Kochi", "date": "2024-01-01",
        "temperature_max": 30.0, "temperature_min": 24.0, "temperature_mean": 27.0,
        "precipitation_mm": 1.0, "rain_mm": 1.0, "precipitation_hours": 2.0,
        "weather_code": 61, "wind_speed_max": 12.0, "wind_direction": 90.0,
        "sunshine_hours": 5.0,
    }
    base.update(overrides)
    return base


def good_df(days=3):
    return pd.DataFrame([row(date=f"2024-01-{i + 1:02d}") for i in range(days)])


def by_name(results):
    return {r.name: r for r in results}


def test_clean_data_passes_everything():
    results = run_checks(good_df(), expected_city_ids={1})
    assert all(r.passed for r in results)


def test_missing_column_fails():
    df = good_df().drop(columns=["rain_mm"])
    assert not by_name(run_checks(df))["required_columns"].passed


def test_duplicates_detected():
    df = pd.concat([good_df(1), good_df(1)], ignore_index=True)
    assert not by_name(run_checks(df, expected_city_ids={1}))["duplicate_city_date"].passed


def test_temperature_order_violation():
    df = good_df()
    df.loc[0, "temperature_min"] = 40.0
    assert not by_name(run_checks(df, expected_city_ids={1}))["temperature_order"].passed


def test_negative_rain_detected():
    df = good_df()
    df.loc[0, "rain_mm"] = -1.0
    assert not by_name(run_checks(df, expected_city_ids={1}))["no_negative_values"].passed


def test_wind_direction_out_of_range():
    df = good_df()
    df.loc[0, "wind_direction"] = 400.0
    assert not by_name(run_checks(df, expected_city_ids={1}))["wind_direction_range"].passed


def test_unexpected_city_set():
    assert not by_name(run_checks(good_df()))["city_ids"].passed


def test_date_gap_is_a_warning():
    df = pd.DataFrame([row(date="2024-01-01"), row(date="2024-01-03")])
    result = by_name(run_checks(df, expected_city_ids={1}))["date_gaps"]
    assert not result.passed
    assert result.severity == "warning"


def test_high_missingness_is_a_warning():
    df = good_df(10)
    df.loc[0:4, "rain_mm"] = float("nan")
    result = by_name(run_checks(df, expected_city_ids={1}))["missingness"]
    assert not result.passed
    assert result.severity == "warning"


def test_date_outside_range():
    results = run_checks(
        good_df(), start_date=date(2024, 1, 2), end_date=date(2024, 1, 3), expected_city_ids={1}
    )
    assert not by_name(results)["date_range"].passed
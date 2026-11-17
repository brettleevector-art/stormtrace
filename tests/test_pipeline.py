from datetime import date

from stormtrace import config
from stormtrace.pipeline import build_incremental_plan

CITIES = [{"city_id": 1, "city": "Kochi"}, {"city_id": 2, "city": "Kottayam"}]


def test_no_history_starts_at_project_start():
    plan = build_incremental_plan(CITIES, {})
    assert [start for _, start in plan] == [config.START_DATE, config.START_DATE]


def test_history_starts_60_days_before_latest():
    plan = build_incremental_plan(CITIES, {1: date(2026, 11, 12)})
    assert plan[0][1] == date(2026, 9, 13)
    assert plan[1][1] == config.START_DATE


def test_start_never_before_project_start():
    plan = build_incremental_plan(CITIES, {1: date(2020, 1, 10)})
    assert plan[0][1] == config.START_DATE
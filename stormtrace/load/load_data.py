"""Load cities and daily weather into PostgreSQL. Safe to rerun (upsert)."""
import logging

import pandas as pd

from stormtrace import config
from stormtrace.load.database import get_connection
from stormtrace.transform.transform import OUTPUT_COLUMNS

log = logging.getLogger(__name__)

FACT_COLUMNS = [c for c in OUTPUT_COLUMNS if c != "city"]
KEY_COLUMNS = ["city_id", "date"]
UPDATE_COLUMNS = [c for c in FACT_COLUMNS if c not in KEY_COLUMNS]

UPSERT_DAILY_SQL = (
    f"INSERT INTO fact_daily_weather ({', '.join(FACT_COLUMNS)}) "
    f"VALUES ({', '.join(['%s'] * len(FACT_COLUMNS))}) "
    "ON CONFLICT (city_id, date) DO UPDATE SET "
    + ", ".join(f"{c} = EXCLUDED.{c}" for c in UPDATE_COLUMNS)
    + ", loaded_at = now()"
)

UPSERT_CITY_SQL = (
    "INSERT INTO dim_city (city_id, city, state, country, latitude, longitude) "
    "VALUES (%(city_id)s, %(city)s, %(state)s, %(country)s, %(latitude)s, %(longitude)s) "
    "ON CONFLICT (city_id) DO UPDATE SET city = EXCLUDED.city, state = EXCLUDED.state, "
    "country = EXCLUDED.country, latitude = EXCLUDED.latitude, longitude = EXCLUDED.longitude"
)


def to_records(df: pd.DataFrame) -> list[tuple]:
    """Convert a DataFrame to plain Python tuples with NaN/NA replaced by None.

    PostgreSQL stores a pandas NaN as a real 'NaN' value, not NULL, and one NaN
    makes AVG() return NaN. So every missing value must become None here.
    """
    df = df[FACT_COLUMNS].copy()
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["weather_code"] = df["weather_code"].astype("Int64")
    df = df.astype(object).where(df.notna(), None)
    return list(df.itertuples(index=False, name=None))


def upsert_cities(conn, cities) -> int:
    with conn.cursor() as cur:
        cur.executemany(UPSERT_CITY_SQL, cities)
    return len(cities)


def upsert_daily(conn, df: pd.DataFrame) -> int:
    records = to_records(df)
    with conn.cursor() as cur:
        cur.executemany(UPSERT_DAILY_SQL, records)
    return len(records)


def count_rows(conn, table: str) -> int:
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        return cur.fetchone()[0]


def load_all(df: pd.DataFrame) -> dict:
    """Load everything in one transaction. Nothing is saved if anything fails."""
    with get_connection() as conn:
        before = count_rows(conn, "fact_daily_weather")
        cities = upsert_cities(conn, config.load_cities())
        sent = upsert_daily(conn, df)
        after = count_rows(conn, "fact_daily_weather")
    log.info("Loaded %s cities, sent %s rows, table %s -> %s", cities, sent, before, after)
    return {"cities": cities, "rows_sent": sent, "rows_before": before, "rows_after": after}
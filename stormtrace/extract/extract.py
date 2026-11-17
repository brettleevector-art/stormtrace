"""Extract raw ERA5 data for each city and save it as JSON."""
import json
import logging
import time
from datetime import datetime, timezone

from stormtrace import config
from stormtrace.extract.api_client import ExtractionError, fetch_daily_weather

log = logging.getLogger(__name__)

PAUSE_BETWEEN_CITIES_SECONDS = 30


def extract_city(city, start_date, end_date, run_id):
    """Fetch one city and write data/raw/<city>_<start>_<end>_<run_id>.json."""
    response = fetch_daily_weather(
        city["latitude"], city["longitude"],
        start_date.isoformat(), end_date.isoformat(),
    )
    payload = {
        "meta": {
            "run_id": run_id,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "city_id": city["city_id"],
            "city": city["city"],
            "requested_latitude": city["latitude"],
            "requested_longitude": city["longitude"],
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "model": config.MODEL,
        },
        "response": response,
    }
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    name = f"{city['city'].lower()}_{start_date}_{end_date}_{run_id}.json"
    path = config.RAW_DIR / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    log.info("Saved %s", path)
    return path


def extract_all(city_name=None, start_date=None, end_date=None):
    """Extract one or all cities. Returns (succeeded, failed) lists."""
    cities = config.load_cities()
    if city_name:
        cities = [c for c in cities if c["city"].lower() == city_name.lower()]
        if not cities:
            raise ValueError(f"Unknown city: {city_name}")

    start_date = start_date or config.START_DATE
    end_date = end_date or config.safe_end_date()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log.info("Run %s: %s cities, %s to %s", run_id, len(cities), start_date, end_date)

    succeeded, failed = [], []
    for index, city in enumerate(cities):
        if index > 0:
            log.info("Waiting %s s to respect API limits", PAUSE_BETWEEN_CITIES_SECONDS)
            time.sleep(PAUSE_BETWEEN_CITIES_SECONDS)
        try:
            path = extract_city(city, start_date, end_date, run_id)
            succeeded.append((city["city"], path))
        except ExtractionError as exc:
            log.error("%s failed: %s", city["city"], exc)
            failed.append((city["city"], str(exc)))
    return succeeded, failed




def extract_plan(plan, end_date, pause_seconds=PAUSE_BETWEEN_CITIES_SECONDS):
    """Extract a list of (city, start_date) pairs. Returns (succeeded, failed)."""
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log.info("Run %s: %s cities, up to %s", run_id, len(plan), end_date)

    succeeded, failed = [], []
    for index, (city, start_date) in enumerate(plan):
        if index > 0:
            time.sleep(pause_seconds)
        try:
            path = extract_city(city, start_date, end_date, run_id)
            succeeded.append((city["city"], path))
        except ExtractionError as exc:
            log.error("%s failed: %s", city["city"], exc)
            failed.append((city["city"], str(exc)))
    return succeeded, failed    
"""Open-Meteo Historical Weather API client with retry handling."""
import logging
import time

import requests

from stormtrace import config

log = logging.getLogger(__name__)

MAX_RETRIES = 5
RATE_LIMIT_WAIT_SECONDS = 60


class ExtractionError(Exception):
    """Raised when the API request cannot be completed."""


def fetch_daily_weather(latitude, longitude, start_date, end_date, session=None):
    """Request daily ERA5 data for one location. Dates are 'YYYY-MM-DD' strings."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ",".join(config.DAILY_VARIABLES),
        "timezone": config.TIMEZONE,
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
        "models": config.MODEL,
    }
    http = session or requests
    last_problem = "unknown error"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = http.get(config.API_URL, params=params, timeout=60)
        except (requests.ConnectionError, requests.Timeout) as exc:
            last_problem = f"connection problem: {exc}"
            log.warning("Attempt %s failed: %s", attempt, last_problem)
            time.sleep(2 ** attempt)
            continue

        if response.status_code == 429:
            last_problem = "rate limited (HTTP 429)"
            log.warning("Rate limited. Waiting %s seconds.", RATE_LIMIT_WAIT_SECONDS)
            time.sleep(RATE_LIMIT_WAIT_SECONDS)
        elif response.status_code >= 500:
            last_problem = f"server error (HTTP {response.status_code})"
            log.warning("Attempt %s: %s", attempt, last_problem)
            time.sleep(2 ** attempt)
        elif response.status_code == 400:
            reason = response.json().get("reason", "no reason given")
            raise ExtractionError(f"Invalid request: {reason}")
        elif response.ok:
            return response.json()
        else:
            raise ExtractionError(f"Unexpected HTTP {response.status_code}")

    raise ExtractionError(f"Gave up after {MAX_RETRIES} attempts: {last_problem}")
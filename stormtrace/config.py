"""Project configuration, paths and API settings."""
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

CITIES_FILE = PROJECT_ROOT / "config" / "cities.json"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
LOGS_DIR = PROJECT_ROOT / "logs"

API_URL = "https://archive-api.open-meteo.com/v1/archive"
MODEL = "era5"
TIMEZONE = "Asia/Kolkata"
START_DATE = date(2020, 1, 1)
ERA5_DELAY_DAYS = 5

DAILY_VARIABLES = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "rain_sum",
    "precipitation_hours",
    "weather_code",
    "wind_speed_10m_max",
    "wind_direction_10m_dominant",
    "sunshine_duration",
]


def load_cities() -> list[dict]:
    """Return the list of city dictionaries from config/cities.json."""
    with open(CITIES_FILE, encoding="utf-8") as f:
        return json.load(f)["cities"]


def safe_end_date() -> date:
    """Latest date ERA5 should have: today in India minus 5 days."""
    today_india = datetime.now(ZoneInfo(TIMEZONE)).date()
    return today_india - timedelta(days=ERA5_DELAY_DAYS)
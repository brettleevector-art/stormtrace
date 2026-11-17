"""Build the processed daily dataset from all raw files (reusable by the pipeline)."""
import pandas as pd

from stormtrace import config
from stormtrace.transform.clean import clean
from stormtrace.transform.transform import transform_file


def build_daily_dataset():
    """Read every raw file, combine, clean. Returns (clean_df, cleaning_report, file_count)."""
    files = sorted(config.RAW_DIR.glob("*.json"))
    if not files:
        raise FileNotFoundError("No raw files in data/raw/. Run extraction first.")
    combined = pd.concat([transform_file(f) for f in files], ignore_index=True)
    cleaned, report = clean(combined)
    return cleaned, report, len(files)


def write_processed_csv(df):
    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = config.PROCESSED_DIR / "weather_daily.csv"
    df.to_csv(path, index=False)
    return path
"""Data quality checks for the combined daily weather DataFrame."""
from dataclasses import dataclass

import pandas as pd

from stormtrace.transform.transform import OUTPUT_COLUMNS

CRITICAL = "critical"
WARNING = "warning"

EXPECTED_CITY_IDS = {1, 2, 3, 4, 5, 6}
VALUE_COLUMNS = [c for c in OUTPUT_COLUMNS if c not in ("city_id", "city", "date")]
NON_NEGATIVE = ["precipitation_mm", "rain_mm", "precipitation_hours", "sunshine_hours"]
MISSING_WARNING_PCT = 1.0


@dataclass
class CheckResult:
    name: str
    passed: bool
    severity: str
    detail: str


def run_checks(df, start_date=None, end_date=None, expected_city_ids=None):
    """Run every check and return a list of CheckResult. Nothing is fixed or hidden."""
    expected = set(expected_city_ids or EXPECTED_CITY_IDS)
    results = []

    missing_cols = [c for c in OUTPUT_COLUMNS if c not in df.columns]
    results.append(CheckResult(
        "required_columns", not missing_cols, CRITICAL,
        "all present" if not missing_cols else f"missing: {missing_cols}",
    ))
    if missing_cols:
        return results

    results.append(CheckResult("has_rows", len(df) > 0, CRITICAL, f"{len(df)} rows"))
    if len(df) == 0:
        return results

    dates = pd.to_datetime(df["date"], errors="coerce")
    bad_dates = int(dates.isna().sum())
    results.append(CheckResult("valid_dates", bad_dates == 0, CRITICAL, f"{bad_dates} invalid dates"))

    found = set(df["city_id"].dropna().unique())
    results.append(CheckResult(
        "city_ids", found == expected, CRITICAL,
        f"found {sorted(found)}, expected {sorted(expected)}",
    ))

    dupes = int(df.duplicated(["city_id", "date"]).sum())
    results.append(CheckResult("duplicate_city_date", dupes == 0, CRITICAL, f"{dupes} duplicates"))

    both = df[["temperature_min", "temperature_mean", "temperature_max"]].notna().all(axis=1)
    ordered = (df["temperature_min"] <= df["temperature_mean"]) & (
        df["temperature_mean"] <= df["temperature_max"]
    )
    bad_order = int((both & ~ordered).sum())
    results.append(CheckResult("temperature_order", bad_order == 0, CRITICAL, f"{bad_order} violations"))

    negatives = {c: int((df[c] < 0).sum()) for c in NON_NEGATIVE}
    negatives = {c: n for c, n in negatives.items() if n > 0}
    results.append(CheckResult(
        "no_negative_values", not negatives, CRITICAL,
        "none" if not negatives else f"negative values: {negatives}",
    ))

    bad_wind = int(((df["wind_direction"] < 0) | (df["wind_direction"] > 360)).sum())
    results.append(CheckResult("wind_direction_range", bad_wind == 0, CRITICAL, f"{bad_wind} outside 0-360"))

    if start_date is not None and end_date is not None:
        outside = int(((dates < pd.Timestamp(start_date)) | (dates > pd.Timestamp(end_date))).sum())
        results.append(CheckResult("date_range", outside == 0, WARNING, f"{outside} rows outside {start_date} to {end_date}"))
    else:
        results.append(CheckResult("date_range", True, WARNING, "no range supplied"))

    work = df.assign(_date=dates).dropna(subset=["_date"])
    gaps = {}
    for city_id, group in work.groupby("city_id"):
        span = (group["_date"].max() - group["_date"].min()).days + 1
        missing_days = span - group["_date"].nunique()
        if missing_days > 0:
            gaps[city_id] = missing_days
    results.append(CheckResult(
        "date_gaps", not gaps, WARNING,
        "no gaps" if not gaps else f"missing days per city_id: {gaps}",
    ))

    missing = df[VALUE_COLUMNS].isna().sum()
    worst_pct = float(missing.max() / len(df) * 100)
    listed = ", ".join(f"{c}={n}" for c, n in missing.items() if n > 0) or "no missing values"
    results.append(CheckResult(
        "missingness", worst_pct <= MISSING_WARNING_PCT, WARNING,
        f"worst column {worst_pct:.2f}% missing; {listed}",
    ))
    return results


def build_report(df, results):
    """Return a plain-text quality report."""
    dates = pd.to_datetime(df["date"], errors="coerce")
    per_city = df.assign(date=dates).groupby("city")["date"].agg(["count", "min", "max"])
    lines = [
        "STORMTRACE DATA QUALITY REPORT",
        "==============================",
        f"Total records: {len(df)}",
        "",
        "Per city:",
        per_city.to_string(),
        "",
        "Missing values per variable:",
        df[VALUE_COLUMNS].isna().sum().to_string(),
        "",
        f"Duplicate city/date rows: {int(df.duplicated(['city_id', 'date']).sum())}",
        "",
        "Checks:",
    ]
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        lines.append(f"  [{status}] ({r.severity}) {r.name}: {r.detail}")
    failures = [r for r in results if not r.passed and r.severity == CRITICAL]
    lines += ["", f"Critical failures: {len(failures)}"]
    return "\n".join(lines)


def critical_failures(results):
    return [r for r in results if not r.passed and r.severity == CRITICAL]
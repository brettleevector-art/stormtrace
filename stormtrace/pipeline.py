"""Run the whole pipeline: extract -> transform -> validate -> load -> verify."""
import json
import logging
from datetime import datetime, timedelta, timezone

from stormtrace import config
from stormtrace.extract.extract import extract_all, extract_plan
from stormtrace.load.database import get_connection
from stormtrace.load.load_data import load_all
from stormtrace.transform.build import build_daily_dataset, write_processed_csv
from stormtrace.validation.quality_checks import critical_failures, run_checks

log = logging.getLogger(__name__)

OVERLAP_DAYS = 60  # recent ERA5 values are preliminary, so re-request the last 60 days
INCREMENTAL_PAUSE_SECONDS = 5


class PipelineError(Exception):
    """Raised when a stage fails and the run must stop."""


def select_cities(city_name=None):
    cities = config.load_cities()
    if city_name:
        cities = [c for c in cities if c["city"].lower() == city_name.lower()]
        if not cities:
            raise PipelineError(f"Unknown city: {city_name}")
    return cities


def build_incremental_plan(cities, latest_dates, overlap_days=OVERLAP_DAYS):
    """Return [(city, start_date)]: last stored date minus the overlap, or the project start."""
    plan = []
    for city in cities:
        last = latest_dates.get(city["city_id"])
        if last is None:
            start = config.START_DATE
        else:
            start = max(config.START_DATE, last - timedelta(days=overlap_days))
        plan.append((city, start))
    return plan


def latest_dates():
    """Latest date stored per city_id in the database."""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT city_id, MAX(date) FROM fact_daily_weather GROUP BY city_id")
        return {row[0]: row[1] for row in cur.fetchall()}


def stage_extract(mode, city_name, end_date):
    if mode == "backfill":
        log.info("Extract (backfill): full range from %s", config.START_DATE)
        succeeded, failed = extract_all(city_name, config.START_DATE, end_date)
    else:
        log.info("Extract (incremental): last stored date minus %s days", OVERLAP_DAYS)
        plan = build_incremental_plan(select_cities(city_name), latest_dates())
        for city, start in plan:
            log.info("  %s: from %s", city["city"], start)
        succeeded, failed = extract_plan(plan, end_date, INCREMENTAL_PAUSE_SECONDS)
    if failed:
        raise PipelineError(f"Extraction failed for: {failed}")
    return succeeded


def verify_database():
    """Check the stored data. Raises if any NaN value reached the database."""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM fact_daily_weather")
        total = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(*) FROM fact_daily_weather WHERE temperature_mean = 'NaN' "
            "OR precipitation_mm = 'NaN' OR rain_mm = 'NaN' OR sunshine_hours = 'NaN'"
        )
        nan_rows = cur.fetchone()[0]
        cur.execute(
            "SELECT city_id, COUNT(*), MIN(date), MAX(date), MAX(date) - MIN(date) + 1 "
            "FROM fact_daily_weather GROUP BY city_id ORDER BY city_id"
        )
        per_city = [
            {"city_id": r[0], "days": r[1], "first": r[2].isoformat(),
             "last": r[3].isoformat(), "gaps": r[4] - r[1]}
            for r in cur.fetchall()
        ]
    if nan_rows:
        raise PipelineError(f"{nan_rows} rows contain NaN values")
    if any(c["gaps"] for c in per_city):
        log.warning("Date gaps found in database: %s", [c for c in per_city if c["gaps"]])
    return {"total_rows": total, "nan_rows": nan_rows, "per_city": per_city}


def write_summary(summary, run_id):
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    path = config.LOGS_DIR / f"run_summary_{run_id}.json"
    path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return path


def run_pipeline(mode="incremental", city=None, run_id=None):
    run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    end_date = config.safe_end_date()
    summary = {
        "run_id": run_id, "mode": mode, "city": city or "all",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "end_date": end_date.isoformat(), "status": "failed",
    }
    log.info("Pipeline start: mode=%s city=%s end_date=%s", mode, city or "all", end_date)
    try:
        extracted = stage_extract(mode, city, end_date)
        log.info("Extract done: %s files", len(extracted))

        df, clean_report, raw_files = build_daily_dataset()
        log.info("Transform done: %s rows from %s raw files; cleaning: %s", len(df), raw_files, clean_report)

        checks = run_checks(df, start_date=config.START_DATE, end_date=end_date)
        for check in checks:
            log.info("Check %s %s (%s): %s", "PASS" if check.passed else "FAIL",
                     check.name, check.severity, check.detail)
        failures = critical_failures(checks)
        if failures:
            raise PipelineError("Critical data quality failures: " + "; ".join(f.name for f in failures))

        csv_path = write_processed_csv(df)
        log.info("Saved %s", csv_path)

        load_result = load_all(df)
        log.info("Load done: %s", load_result)

        verification = verify_database()
        log.info("Verification done: %s rows, %s NaN rows", verification["total_rows"], verification["nan_rows"])

        summary.update(status="success", raw_files_read=raw_files, cleaning=clean_report,
                       load=load_result, verification=verification)
        log.info("Pipeline finished: success")
    except Exception as exc:
        log.exception("Pipeline failed")
        summary["error"] = str(exc)
        raise
    finally:
        summary["finished_at"] = datetime.now(timezone.utc).isoformat()
        log.info("Run summary: %s", write_summary(summary, run_id))
    return summary
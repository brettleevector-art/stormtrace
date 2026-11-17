"""Logging setup: every run writes to the console and to logs/pipeline_<run_id>.log."""
import logging
import os

from stormtrace import config


def setup_logging(run_id: str):
    """Configure logging and return the path of this run's log file."""
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = config.LOGS_DIR / f"pipeline_{run_id}.log"
    level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    root = logging.getLogger()
    root.setLevel(level)
    for handler in list(root.handlers):
        root.removeHandler(handler)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root.addHandler(console)
    root.addHandler(file_handler)
    return log_path
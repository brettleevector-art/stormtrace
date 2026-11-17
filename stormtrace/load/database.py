"""PostgreSQL connection helper. Credentials come from .env."""
import os

import psycopg

from stormtrace import config  # noqa: F401  (importing config loads .env)


class DatabaseError(Exception):
    """Raised when the database cannot be reached."""


def get_connection():
    """Open a connection. Use it as `with get_connection() as conn:`.

    The block commits if it finishes cleanly, rolls back on any error,
    and always closes the connection.
    """
    try:
        return psycopg.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            sslmode=os.getenv("DB_SSLMODE", "prefer"),
            connect_timeout=10,
        )
    except psycopg.OperationalError as exc:
        raise DatabaseError(
            "Could not connect to PostgreSQL. Is it running? "
            "Start it with: wsl.exe -d Ubuntu -u root -- service postgresql start. "
            f"Details: {exc}"
        ) from exc
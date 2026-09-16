"""PostgreSQL access with a CSV fallback for easy local use."""

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def get_database_url() -> str | None:
    """Return the configured SQLAlchemy PostgreSQL URL, if one exists."""
    return os.getenv("DATABASE_URL")


def load_transactions(csv_path: Path) -> tuple[pd.DataFrame, str, str | None]:
    """Load transactions from PostgreSQL, falling back to the packaged CSV."""
    database_url = get_database_url()
    if database_url:
        try:
            engine = create_engine(database_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
            with engine.connect() as connection:
                frame = pd.read_sql_query(
                    text("SELECT * FROM transactions ORDER BY date, product_id"),
                    connection,
                    parse_dates=["date"],
                )
            if not frame.empty:
                return frame, "PostgreSQL", None
            warning = "PostgreSQL is connected, but the transactions table is empty. Loaded the CSV instead."
        except (SQLAlchemyError, OSError):
            warning = "PostgreSQL could not be reached. Loaded the CSV instead."
    else:
        warning = None

    frame = pd.read_csv(csv_path, parse_dates=["date"])
    return frame, "CSV", warning


def database_healthcheck(database_url: str) -> bool:
    """Return True when PostgreSQL accepts a simple query."""
    try:
        engine = create_engine(database_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
        with engine.connect() as connection:
            return connection.execute(text("SELECT 1")).scalar_one() == 1
    except (SQLAlchemyError, OSError):
        return False


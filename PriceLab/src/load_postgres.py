"""Create the PriceLab PostgreSQL schema and load the packaged retail data."""

import argparse
import os
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "pricelab_transactions.csv"
SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema.sql"


def load_database(database_url: str) -> int:
    frame = pd.read_csv(DATA_PATH, parse_dates=["date"])
    engine = create_engine(database_url, pool_pre_ping=True)
    statements = [statement.strip() for statement in SCHEMA_PATH.read_text().split(";") if statement.strip()]

    for attempt in range(15):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            break
        except OperationalError:
            if attempt == 14:
                raise
            time.sleep(1)

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
        connection.execute(text("TRUNCATE TABLE transactions"))
        frame.to_sql(
            "transactions",
            connection,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=500,
        )
        loaded_rows = connection.execute(text("SELECT COUNT(*) FROM transactions")).scalar_one()

    return int(loaded_rows)


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    parser = argparse.ArgumentParser(description="Load PriceLab data into PostgreSQL")
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL"))
    args = parser.parse_args()
    if not args.database_url:
        raise SystemExit("DATABASE_URL is missing. Copy .env.example to .env first.")
    row_count = load_database(args.database_url)
    print(f"PostgreSQL is ready: loaded {row_count:,} rows into transactions.")


if __name__ == "__main__":
    main()

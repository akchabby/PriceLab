# PostgreSQL setup on a Mac

The easiest option is Docker Desktop because it creates the database without changing your Mac's system configuration.

## Before you start

- Install and open **Docker Desktop** if you do not already have it.
- Open Terminal in the unzipped PriceLab folder.
- Activate the PriceLab virtual environment:

```bash
source .venv/bin/activate
```

If `.venv` does not exist yet, follow `START_HERE.md` first.

## Start PostgreSQL

Run these commands one at a time:

```bash
cp .env.example .env
docker compose up -d
python3 -m src.load_postgres
streamlit run app.py
```

Open the PriceLab sidebar. You should see a green message that says:

> Data source: PostgreSQL

The loader creates the schema, loads 4,368 rows, and verifies the final row count.

## Verify the database yourself

```bash
docker compose exec postgres psql -U pricelab -d pricelab -c "SELECT COUNT(*) FROM transactions;"
```

Expected result: `4368`.

Try a business query:

```bash
docker compose exec postgres psql -U pricelab -d pricelab -c "SELECT product_name, ROUND(SUM(gross_profit), 2) AS profit FROM transactions GROUP BY product_name ORDER BY profit DESC;"
```

The complete portfolio queries are in `sql/pricing_analysis.sql`.

## Stop and restart the database

Stop PostgreSQL without deleting the data:

```bash
docker compose stop
```

Restart it later:

```bash
docker compose start
```

## Common issue: port 5432 is already being used

If Docker reports that port `5432` is unavailable:

1. Open `docker-compose.yml` and change `5432:5432` to `5433:5432`.
2. Open `.env` and change `localhost:5432` to `localhost:5433`.
3. Run `docker compose up -d` again.

## How the fallback works

PriceLab tries PostgreSQL whenever `DATABASE_URL` exists. If the database is stopped or unavailable, the dashboard safely loads the packaged CSV and shows a warning. This lets you keep demonstrating the app even when PostgreSQL is not running.


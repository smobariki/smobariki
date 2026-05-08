install:
	pip install -e .[dev]

db-up:
	docker compose up -d

db-down:
	docker compose down -v

migrate:
	edgar-etl init-db

sync-cik:
	edgar-etl sync-cik-map

ingest-sample:
	edgar-etl ingest-company --ticker AAPL

ingest-watchlist:
	edgar-etl ingest-watchlist

scheduler:
	edgar-etl run-scheduler

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

qlik-views:
	echo "Qlik views are created by Alembic migration"

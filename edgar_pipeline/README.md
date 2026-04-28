# EDGAR -> PostgreSQL -> Qlik Sense SaaS MVP

This project provides an hourly automated ingestion and transformation pipeline for SEC EDGAR filings (8-K, Form 4, SC 13D/G and amendments), persists raw + parsed data in PostgreSQL, and triggers Qlik reloads only when new filings are inserted.

## Architecture

1. Python ingestion orchestrator (`app/main.py`)
2. SEC API client with user-agent, rate limiting, retries (`app/sec_client.py`)
3. Layered PostgreSQL schemas (`sql/*.sql`)
4. Rule-based filing parsers (`app/parsers/*.py`)
5. Qlik reload trigger (`app/qlik/reload.py`)

## Supported forms

- 8-K / 8-K/A
- Form 4 / 4/A
- SC 13D / SC 13D/A
- SC 13G / SC 13G/A

## Environment variables

- `DATABASE_URL`
- `SEC_USER_AGENT`
- `SEC_CONTACT_EMAIL`
- `QLIK_TENANT_URL`
- `QLIK_API_KEY`
- `QLIK_APP_ID`
- `RUN_MODE`
- `LOG_LEVEL`

## Run locally

```bash
cd edgar_pipeline
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

## Run tests

```bash
cd edgar_pipeline
pytest
```

## Deploy

- Build container with `Dockerfile`
- Schedule hourly with cron, ECS scheduled task, Cloud Run job, or Container Apps job
- Default MVP recommendation: AWS RDS PostgreSQL + lightweight VM/container runner

## Notes

- No historical backfill (starts collection at deployment time)
- Deduplication uses accession number
- Amendments are stored as separate filings (`is_amendment=true`)
- Parser errors are logged and do not stop the full run
- Qlik reload is skipped when no new filings are inserted

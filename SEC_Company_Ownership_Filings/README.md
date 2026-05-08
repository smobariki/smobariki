# SEC_Company_Ownership_Filings

Phase 1 MVP local ETL for SEC Forms 3/4/5 into PostgreSQL with Qlik-friendly views.

## Setup
1. `cp .env.example .env`
2. Use existing local PostgreSQL by editing only `DATABASE_URL`, or optional Docker:
   - `docker compose up -d`
3. `pip install -e .[dev]`
4. `edgar-etl init-db`

## Commands
- `edgar-etl sync-cik-map`
- `edgar-etl ingest-company --ticker AAPL`
- `edgar-etl ingest-company --cik 0000320193`
- `edgar-etl ingest-watchlist`
- `edgar-etl ingest-latest` (Phase 3 target)
- `edgar-etl run-scheduler` (Phase 3 target)

## Using the database with Qlik Sense Desktop
Use PostgreSQL connector (or ODBC PostgreSQL driver) to connect to the DB in `DATABASE_URL`.
Load these views first:
- `vw_latest_insider_transactions` (Phase 1 target)
- `vw_form4_transactions` (Phase 1 target)
- `vw_reporting_owner_activity` (Phase 1 target)
- `vw_company_filing_history` (available)
- `vw_beneficial_ownership_summary` (Phase 2 target)

Example SQL:
```sql
SELECT * FROM vw_company_filing_history WHERE ticker='AAPL' ORDER BY filing_date DESC LIMIT 100;
```
Refresh Qlik model after each ETL run by reloading the app script.

## SEC Fair Access
Set `SEC_USER_AGENT`, keep request rate <= 10 rps unless force override is enabled.

## Limitations
This commit provides core scaffolding + parser/tests for Phase 1 MVP and marks Phase 2/3 features clearly.

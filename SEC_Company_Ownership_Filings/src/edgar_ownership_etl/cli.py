import typer
from alembic import command
from alembic.config import Config
from sqlalchemy import text, select

from edgar_ownership_etl.db.models import Issuer
from edgar_ownership_etl.db.session import SessionLocal, engine
from edgar_ownership_etl.orchestration.pipeline import ingest_company as ingest_company_pipeline
from edgar_ownership_etl.sec.cik import normalize_cik
from edgar_ownership_etl.sec.client import SecClient

app = typer.Typer()


def _dedupe_issuer_rows(payload: dict) -> dict[str, dict]:
    grouped: dict[str, dict] = {}
    for row in payload.values():
        cik = normalize_cik(str(row["cik_str"]))
        ticker = (row.get("ticker", "") or "").upper()
        name = row.get("title", "")
        if cik not in grouped:
            grouped[cik] = {"cik": cik, "ticker": ticker or None, "name": name}
            continue
        current = grouped[cik]
        current_ticker = current.get("ticker") or ""
        if ticker and (not current_ticker or ticker < current_ticker):
            current["ticker"] = ticker
        if not current.get("name") and name:
            current["name"] = name
    return grouped


@app.command("init-db")
def init_db() -> None:
    command.upgrade(Config("alembic.ini"), "head")
    with engine.begin() as conn:
        conn.execute(text("select 1"))
    typer.echo("Database initialized")


@app.command("sync-cik-map")
def sync_cik_map() -> None:
    client = SecClient()
    payload = client.get("https://www.sec.gov/files/company_tickers.json").json()
    inserted = 0
    updated = 0
    deduped = _dedupe_issuer_rows(payload)
    with SessionLocal() as session:
        for row in deduped.values():
            cik = row["cik"]
            ticker = row["ticker"]
            name = row["name"]
            existing = session.scalar(select(Issuer).where(Issuer.cik == cik))
            if existing:
                existing.ticker = ticker
                existing.name = name
                updated += 1
            else:
                session.add(Issuer(cik=cik, ticker=ticker, name=name))
                inserted += 1
        session.commit()
    typer.echo(f"sync-cik-map complete: inserted={inserted} updated={updated}")


@app.command("ingest-company")
def ingest_company(ticker: str = "", cik: str = "") -> None:
    if not ticker and not cik:
        raise typer.BadParameter("Provide --ticker or --cik")
    with SessionLocal() as session:
        summary = ingest_company_pipeline(session, ticker=ticker or None, cik=cik or None)
    typer.echo(
        f"filings_seen={summary.filings_seen} filings_skipped_existing={summary.filings_skipped_existing} "
        f"filings_processed={summary.filings_processed} filings_failed={summary.filings_failed} rows_loaded={summary.rows_loaded}"
    )


@app.command("ingest-watchlist")
def ingest_watchlist() -> None:
    from edgar_ownership_etl.config import settings

    tickers = [t.strip() for t in settings.watchlist_tickers.split(",") if t.strip()]
    ciks = [c.strip() for c in settings.watchlist_ciks.split(",") if c.strip()]
    failures = 0
    with SessionLocal() as session:
        for ticker in tickers:
            try:
                ingest_company_pipeline(session, ticker=ticker)
            except Exception:
                failures += 1
        for cik in ciks:
            try:
                ingest_company_pipeline(session, cik=cik)
            except Exception:
                failures += 1
    typer.echo(f"ingest-watchlist complete failures={failures}")


@app.command("ingest-latest")
def ingest_latest() -> None:
    ingest_watchlist()


@app.command("run-scheduler")
def run_scheduler() -> None:
    raise NotImplementedError("Phase 3 feature")

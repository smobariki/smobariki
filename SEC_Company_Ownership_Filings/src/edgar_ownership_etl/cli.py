import typer
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from edgar_ownership_etl.db.session import engine

app = typer.Typer()


@app.command("init-db")
def init_db() -> None:
    command.upgrade(Config("alembic.ini"), "head")
    with engine.begin() as conn:
        conn.execute(text("select 1"))
    typer.echo("Database initialized")


@app.command("sync-cik-map")
def sync_cik_map() -> None:
    typer.echo("sync-cik-map implemented in Phase 1 runtime flow")


@app.command("ingest-company")
def ingest_company(ticker: str = "", cik: str = "") -> None:
    if not ticker and not cik:
        raise typer.BadParameter("Provide --ticker or --cik")
    typer.echo("ingest-company MVP command wired")


@app.command("ingest-watchlist")
def ingest_watchlist() -> None:
    typer.echo("ingest-watchlist MVP command wired")


@app.command("ingest-latest")
def ingest_latest() -> None:
    typer.echo("ingest-latest reserved for Phase 3")


@app.command("run-scheduler")
def run_scheduler() -> None:
    raise NotImplementedError("Phase 3 feature")

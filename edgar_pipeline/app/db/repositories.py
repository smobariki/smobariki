from __future__ import annotations

from datetime import datetime
from typing import Iterable

from app.db.models import FilingRecord


def create_ingestion_run(conn) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO raw.ingestion_runs(started_at, status)
            VALUES (NOW(), 'running') RETURNING run_id
            """
        )
        return cur.fetchone()[0]


def complete_ingestion_run(
    conn,
    run_id: int,
    status: str,
    filings_found_count: int,
    filings_inserted_count: int,
    filings_failed_count: int,
    error_message: str | None = None,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE raw.ingestion_runs
            SET completed_at = NOW(),
                status = %s,
                filings_found_count = %s,
                filings_inserted_count = %s,
                filings_failed_count = %s,
                error_message = %s
            WHERE run_id = %s
            """,
            (
                status,
                filings_found_count,
                filings_inserted_count,
                filings_failed_count,
                error_message,
                run_id,
            ),
        )


def accession_exists(conn, accession_number: str) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM raw.sec_filings WHERE accession_number = %s",
            (accession_number,),
        )
        return cur.fetchone() is not None


def insert_filing(conn, filing: FilingRecord) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO raw.sec_filings(
                accession_number, cik, ticker, company_name, form_type,
                filing_date, report_date, acceptance_datetime,
                primary_document, primary_document_url, filing_detail_url, filing_index_url,
                is_amendment, amendment_parent_accession_number,
                raw_metadata_json, raw_html, raw_xml, raw_text,
                content_sha256, fetched_at
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s, %s,
                %s, NOW()
            ) RETURNING filing_id
            """,
            (
                filing.accession_number,
                filing.cik,
                filing.ticker,
                filing.company_name,
                filing.form_type,
                filing.filing_date,
                filing.report_date,
                filing.acceptance_datetime,
                filing.primary_document,
                filing.primary_document_url,
                filing.filing_detail_url,
                filing.filing_index_url,
                filing.is_amendment,
                filing.amendment_parent_accession_number,
                filing.raw_metadata_json,
                filing.raw_html,
                filing.raw_xml,
                filing.raw_text,
                filing.content_sha256,
            ),
        )
        return cur.fetchone()[0]


def upsert_company_universe(conn, companies: Iterable[dict]) -> None:
    with conn.cursor() as cur:
        for c in companies:
            cur.execute(
                """
                INSERT INTO raw.company_universe(cik, ticker, company_name, exchange, source, is_active, last_seen_at)
                VALUES (%s,%s,%s,%s,%s,TRUE,NOW())
                ON CONFLICT (cik)
                DO UPDATE SET ticker=EXCLUDED.ticker, company_name=EXCLUDED.company_name,
                              exchange=EXCLUDED.exchange, source=EXCLUDED.source,
                              is_active=TRUE, last_seen_at=NOW(), updated_at=NOW()
                """,
                (c["cik"], c.get("ticker"), c["company_name"], c.get("exchange"), c.get("source", "sec")),
            )


def get_last_successful_run_timestamp(conn) -> datetime | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT completed_at
            FROM raw.ingestion_runs
            WHERE status='success'
            ORDER BY completed_at DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()
        return row[0] if row else None


def insert_qlik_reload(conn, run_id: int, reload_id: str, status: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO raw.qlik_reload_log(run_id, reload_id, status, requested_at)
            VALUES (%s, %s, %s, NOW())
            """,
            (run_id, reload_id, status),
        )

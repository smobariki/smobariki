from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select

from edgar_ownership_etl.db.models import Issuer, SourceFiling
from edgar_ownership_etl.extract.filing_document_extractor import select_ownership_document
from edgar_ownership_etl.extract.submissions_extractor import fetch_company_filings
from edgar_ownership_etl.load.loader import load_ownership_filing
from edgar_ownership_etl.orchestration.watermarks import should_process_accession, upsert_watermark
from edgar_ownership_etl.sec.cik import normalize_cik
from edgar_ownership_etl.sec.client import SecClient
from edgar_ownership_etl.transform.ownership_xml_parser import parse_ownership_xml


@dataclass
class IngestSummary:
    filings_seen: int = 0
    filings_skipped_existing: int = 0
    filings_processed: int = 0
    filings_failed: int = 0
    rows_loaded: int = 0


def resolve_cik(session, ticker: str | None, cik: str | None) -> str:
    if cik:
        return normalize_cik(cik)
    issuer = session.scalar(select(Issuer).where(Issuer.ticker == ticker.upper()))
    if not issuer:
        raise ValueError(f"Unknown ticker: {ticker}. Run sync-cik-map first.")
    return normalize_cik(issuer.cik)


def _record_failure(session, filing, resolved_cik: str, error: str) -> None:
    with session.begin():
        sf = session.scalar(select(SourceFiling).where(SourceFiling.accession_number == filing.accession_number))
        if not sf:
            sf = SourceFiling(accession_number=filing.accession_number, cik=resolved_cik, form_type=filing.form_type, filing_date=filing.filing_date, report_date=filing.report_date, acceptance_datetime=filing.acceptance_datetime, filing_detail_url=filing.filing_detail_url, archive_base_url=filing.archive_base_url, is_amendment=filing.is_amendment)
            session.add(sf)
        sf.parse_status = "failed"
        sf.parse_error = error


def ingest_company(session, ticker: str | None = None, cik: str | None = None) -> IngestSummary:
    resolved_cik = resolve_cik(session, ticker, cik)
    summary = IngestSummary()
    client = SecClient()
    filings = fetch_company_filings(client, resolved_cik)
    summary.filings_seen = len(filings)
    known = set(session.scalars(select(SourceFiling.accession_number).where(SourceFiling.cik == resolved_cik)).all())

    for filing in filings:
        if not should_process_accession(filing.accession_number, known):
            summary.filings_skipped_existing += 1
            continue
        try:
            with session.begin():
                doc_name, xml_text = select_ownership_document(client, filing.archive_base_url, filing.primary_document)
                parsed = parse_ownership_xml(xml_text)
                summary.rows_loaded += load_ownership_filing(session, filing, doc_name, f"{filing.archive_base_url}/{doc_name}", "application/xml", xml_text, parsed)
                upsert_watermark(session, resolved_cik, filing.accession_number, filing.filing_date, filing.acceptance_datetime)
                known.add(filing.accession_number)
                summary.filings_processed += 1
        except Exception as exc:
            summary.filings_failed += 1
            session.rollback()
            try:
                _record_failure(session, filing, resolved_cik, str(exc))
            except Exception:
                session.rollback()

    return summary

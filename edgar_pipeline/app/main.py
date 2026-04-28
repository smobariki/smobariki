from __future__ import annotations

import logging
from datetime import datetime

from dotenv import load_dotenv

from app.company_universe import refresh_company_universe
from app.config import load_settings
from app.db.connection import get_conn
from app.db.models import FilingRecord
from app.db.repositories import (
    accession_exists,
    complete_ingestion_run,
    create_ingestion_run,
    get_last_successful_run_timestamp,
    insert_filing,
    insert_qlik_reload,
    upsert_company_universe,
)
from app.filing_discovery import discover_recent_filings
from app.filing_fetcher import fetch_filing_content
from app.parsers.eightk import classify_eightk_events, parse_eightk_sections
from app.parsers.form4 import parse_form4
from app.parsers.sc13 import parse_sc13_text
from app.qlik.reload import trigger_qlik_reload
from app.transforms.refresh_views import refresh_views
from app.utils.hashing import sha256_text
from app.utils.logging import configure_logging
from app.sec_client import SECClient

logger = logging.getLogger(__name__)


def _safe_iso_datetime(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def run() -> None:
    load_dotenv()
    settings = load_settings()
    configure_logging(settings.log_level)

    sec_client = SECClient(settings.full_user_agent, per_second=settings.sec_rate_limit_per_second)

    with get_conn(settings.database_url) as conn:
        run_id = create_ingestion_run(conn)
        found = inserted = failed = 0
        try:
            companies = refresh_company_universe(sec_client)
            upsert_company_universe(conn, companies)
            last_success = get_last_successful_run_timestamp(conn)

            for company in companies[:200]:  # MVP guardrail
                cik = company["cik"]
                filings = discover_recent_filings(sec_client, cik=cik, since=last_success)
                for filing in filings:
                    found += 1
                    if accession_exists(conn, filing["accession_number"]):
                        continue
                    try:
                        content = fetch_filing_content(sec_client, filing)
                        combined_text = "\n".join(filter(None, [content.get("raw_html"), content.get("raw_xml"), content.get("raw_text")]))
                        filing_record = FilingRecord(
                            accession_number=filing["accession_number"],
                            cik=filing["cik"],
                            ticker=company.get("ticker"),
                            company_name=company["company_name"],
                            form_type=filing["form_type"],
                            filing_date=(datetime.fromisoformat(filing["filing_date"]).date() if filing.get("filing_date") else None),
                            report_date=(datetime.fromisoformat(filing["report_date"]).date() if filing.get("report_date") else None),
                            acceptance_datetime=_safe_iso_datetime(filing.get("acceptance_datetime")),
                            primary_document=filing.get("primary_document"),
                            primary_document_url=filing.get("primary_document_url"),
                            filing_detail_url=filing.get("filing_index_url"),
                            filing_index_url=filing.get("filing_index_url"),
                            is_amendment=filing["form_type"].endswith("/A"),
                            amendment_parent_accession_number=None,
                            raw_metadata_json=filing.get("raw_metadata_json", {}),
                            raw_html=content.get("raw_html"),
                            raw_xml=content.get("raw_xml"),
                            raw_text=content.get("raw_text"),
                            content_sha256=sha256_text(combined_text),
                        )
                        filing_id = insert_filing(conn, filing_record)

                        form = filing["form_type"]
                        if form in {"8-K", "8-K/A"}:
                            _insert_8k(conn, filing_id, content.get("raw_text"))
                        elif form in {"4", "4/A"}:
                            _insert_form4(conn, filing_id, content.get("raw_xml") or content.get("raw_text"))
                        else:
                            _insert_sc13(conn, filing_id, content.get("raw_text"))
                        inserted += 1
                    except Exception:
                        failed += 1
                        logger.exception("failed_processing_filing", extra={"accession": filing["accession_number"]})

            refresh_views(conn)

            if inserted > 0:
                reload_id, reload_status = trigger_qlik_reload(
                    settings.qlik_tenant_url,
                    settings.qlik_api_key,
                    settings.qlik_app_id,
                )
                insert_qlik_reload(conn, run_id, reload_id, reload_status)

            complete_ingestion_run(conn, run_id, "success", found, inserted, failed)
        except Exception as exc:
            complete_ingestion_run(conn, run_id, "failed", found, inserted, failed, str(exc))
            raise


def _insert_8k(conn, filing_id: int, text: str | None) -> None:
    sections = parse_eightk_sections(text)
    events = classify_eightk_events(text)
    with conn.cursor() as cur:
        for s in sections:
            cur.execute(
                "INSERT INTO parsed.eightk_items(filing_id,item_number,item_description,section_text,parsed_at) VALUES (%s,%s,%s,%s,NOW())",
                (filing_id, s["item_number"], s["item_description"], s["section_text"]),
            )
        for e in events:
            cur.execute(
                "INSERT INTO parsed.eightk_event_tags(filing_id,event_category,event_keyword,confidence_method,matched_text,created_at) VALUES (%s,%s,%s,%s,%s,NOW())",
                (filing_id, e["event_category"], e["event_keyword"], e["confidence_method"], e["matched_text"]),
            )


def _insert_form4(conn, filing_id: int, xml_text: str | None) -> None:
    parsed = parse_form4(xml_text)
    with conn.cursor() as cur:
        for o in parsed["owners"]:
            cur.execute(
                """INSERT INTO parsed.form4_reporting_owners(
                    filing_id,owner_cik,owner_name,is_director,is_officer,officer_title,is_ten_percent_owner,is_other,other_text)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (filing_id, o["owner_cik"], o["owner_name"], o["is_director"], o["is_officer"], o["officer_title"], o["is_ten_percent_owner"], o["is_other"], o["other_text"]),
            )
        for t in parsed["non_derivative"]:
            cur.execute(
                "INSERT INTO parsed.form4_non_derivative_transactions(filing_id,owner_cik,security_title,transaction_date,transaction_code) VALUES (%s,%s,%s,%s,%s)",
                (filing_id, None, t["security_title"], t["transaction_date"], t["transaction_code"]),
            )
        for t in parsed["derivative"]:
            cur.execute(
                "INSERT INTO parsed.form4_derivative_transactions(filing_id,owner_cik,security_title,transaction_date,transaction_code) VALUES (%s,%s,%s,%s,%s)",
                (filing_id, None, t["security_title"], t["transaction_date"], t["transaction_code"]),
            )
        for f in parsed["footnotes"]:
            cur.execute(
                "INSERT INTO parsed.form4_footnotes(filing_id,footnote_id,footnote_text) VALUES (%s,%s,%s)",
                (filing_id, f["footnote_id"], f["footnote_text"]),
            )


def _insert_sc13(conn, filing_id: int, text: str | None) -> None:
    parsed = parse_sc13_text(text)
    with conn.cursor() as cur:
        for s in parsed["sections"]:
            cur.execute(
                "INSERT INTO parsed.sc13_sections(filing_id,section_name,section_text) VALUES (%s,%s,%s)",
                (filing_id, s["section_name"], s["section_text"]),
            )
        for s in parsed["signals"]:
            cur.execute(
                "INSERT INTO parsed.sc13_signals(filing_id,signal_category,signal_keyword,matched_text,confidence_method,created_at) VALUES (%s,%s,%s,%s,%s,NOW())",
                (filing_id, s["signal_category"], s["signal_keyword"], s["matched_text"], s["confidence_method"]),
            )


if __name__ == "__main__":
    run()

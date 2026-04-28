from dataclasses import dataclass
from datetime import datetime, date
from typing import Any


@dataclass
class FilingRecord:
    accession_number: str
    cik: str
    ticker: str | None
    company_name: str
    form_type: str
    filing_date: date | None
    report_date: date | None
    acceptance_datetime: datetime | None
    primary_document: str | None
    primary_document_url: str | None
    filing_detail_url: str | None
    filing_index_url: str | None
    is_amendment: bool
    amendment_parent_accession_number: str | None
    raw_metadata_json: dict[str, Any]
    raw_html: str | None
    raw_xml: str | None
    raw_text: str | None
    content_sha256: str

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from edgar_ownership_etl.sec.urls import archive_base_url

SUPPORTED_OWNERSHIP_FORMS = {"3", "3/A", "4", "4/A", "5", "5/A"}


@dataclass
class FilingCandidate:
    accession_number: str
    cik: str
    form_type: str
    filing_date: date | None
    report_date: date | None
    acceptance_datetime: datetime | None
    primary_document: str | None
    primary_doc_description: str | None
    filing_detail_url: str
    archive_base_url: str
    is_amendment: bool


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")


def parse_recent_filings(submissions_payload: dict[str, Any], cik: str) -> list[FilingCandidate]:
    recent = submissions_payload.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    out: list[FilingCandidate] = []
    for i, form in enumerate(forms):
        if form not in SUPPORTED_OWNERSHIP_FORMS:
            continue
        accession = recent.get("accessionNumber", [None])[i]
        if not accession:
            continue
        archive = archive_base_url(cik, accession)
        out.append(
            FilingCandidate(
                accession_number=accession,
                cik=cik,
                form_type=form,
                filing_date=_parse_date(recent.get("filingDate", [None])[i]),
                report_date=_parse_date(recent.get("reportDate", [None])[i]),
                acceptance_datetime=_parse_dt(recent.get("acceptanceDateTime", [None])[i]),
                primary_document=recent.get("primaryDocument", [None])[i],
                primary_doc_description=recent.get("primaryDocDescription", [None])[i],
                filing_detail_url=f"{archive}/{accession}-index.html",
                archive_base_url=archive,
                is_amendment=form.endswith("/A"),
            )
        )
    return out

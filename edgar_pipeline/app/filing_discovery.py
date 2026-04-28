from __future__ import annotations

from datetime import datetime

from app.sec_client import SECClient

TARGET_FORMS = {"8-K", "8-K/A", "4", "4/A", "SC 13D", "SC 13D/A", "SC 13G", "SC 13G/A"}


def discover_recent_filings(sec_client: SECClient, cik: str, since: datetime | None = None) -> list[dict]:
    submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    payload = sec_client.get_json(submissions_url)
    recent = payload.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accession_numbers = recent.get("accessionNumber", [])
    filing_dates = recent.get("filingDate", [])
    report_dates = recent.get("reportDate", [])
    primary_docs = recent.get("primaryDocument", [])
    acceptance_datetimes = recent.get("acceptanceDateTime", [])

    results = []
    for idx, form in enumerate(forms):
        if form not in TARGET_FORMS:
            continue
        filing_date = datetime.fromisoformat(filing_dates[idx]) if filing_dates[idx] else None
        if since and filing_date and filing_date < since:
            continue
        accession = accession_numbers[idx]
        accession_plain = accession.replace("-", "")
        filing_index_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_plain}/{accession}-index.html"
        primary_doc = primary_docs[idx] if idx < len(primary_docs) else None
        primary_doc_url = (
            f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_plain}/{primary_doc}"
            if primary_doc
            else None
        )
        results.append(
            {
                "accession_number": accession,
                "cik": cik,
                "form_type": form,
                "filing_date": filing_dates[idx] if idx < len(filing_dates) else None,
                "report_date": report_dates[idx] if idx < len(report_dates) else None,
                "acceptance_datetime": acceptance_datetimes[idx] if idx < len(acceptance_datetimes) else None,
                "primary_document": primary_doc,
                "primary_document_url": primary_doc_url,
                "filing_index_url": filing_index_url,
                "raw_metadata_json": payload,
            }
        )
    return results

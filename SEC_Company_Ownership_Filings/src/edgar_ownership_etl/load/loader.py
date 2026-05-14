from __future__ import annotations

from hashlib import sha256
from sqlalchemy import select

from edgar_ownership_etl.db.models import (
    DerivativeHolding,
    DerivativeTransaction,
    NonDerivativeHolding,
    NonDerivativeTransaction,
    OwnerSignature,
    OwnershipFootnote,
    OwnershipSubmission,
    OwnershipSubmissionReportingOwner,
    RawDocument,
    ReportingOwner,
    SourceFiling,
)


def _dedupe_items(items: list[dict], key_fields: tuple[str, ...]) -> list[dict]:
    seen = set()
    out = []
    for item in items:
        key = tuple(item.get(k) for k in key_fields)
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def load_ownership_filing(session, filing, document_name: str, document_url: str, content_type: str | None, raw_text: str, parsed: dict) -> int:
    rows = 0
    sf = session.scalar(select(SourceFiling).where(SourceFiling.accession_number == filing.accession_number))
    if not sf:
        sf = SourceFiling(accession_number=filing.accession_number, cik=filing.cik, form_type=filing.form_type, filing_date=filing.filing_date, report_date=filing.report_date, acceptance_datetime=filing.acceptance_datetime, filing_detail_url=filing.filing_detail_url, archive_base_url=filing.archive_base_url, is_amendment=filing.is_amendment, parse_status="parsed")
        session.add(sf)
        session.flush()
        rows += 1

    digest = sha256(raw_text.encode()).hexdigest()
    rd = session.scalar(select(RawDocument).where(RawDocument.source_filing_id == sf.id, RawDocument.document_name == document_name))
    if not rd:
        session.add(RawDocument(source_filing_id=sf.id, document_name=document_name, document_url=document_url, content_type=content_type, content_sha256=digest, raw_text=raw_text))
        rows += 1

    sub = session.scalar(select(OwnershipSubmission).where(OwnershipSubmission.source_filing_id == sf.id))
    if not sub:
        sub = OwnershipSubmission(source_filing_id=sf.id, accession_number=sf.accession_number, document_type=parsed["document_type"], issuer_cik=parsed["issuer_cik"])
        session.add(sub)
        session.flush()
        rows += 1

    for owner in _dedupe_items(parsed.get("reporting_owners", []), ("rpt_owner_cik", "owner_name")):
        ro = session.scalar(select(ReportingOwner).where(ReportingOwner.rpt_owner_cik == owner["rpt_owner_cik"], ReportingOwner.owner_name == owner["owner_name"]))
        if not ro:
            ro = ReportingOwner(**owner)
            session.add(ro)
            session.flush()
            rows += 1
        else:
            for field in ["is_director", "is_officer", "officer_title", "is_ten_percent_owner", "is_other", "other_text"]:
                val = owner.get(field)
                if val is not None:
                    setattr(ro, field, val)
        link = session.scalar(select(OwnershipSubmissionReportingOwner).where(OwnershipSubmissionReportingOwner.ownership_submission_id == sub.id, OwnershipSubmissionReportingOwner.reporting_owner_id == ro.id))
        if not link:
            session.add(OwnershipSubmissionReportingOwner(ownership_submission_id=sub.id, reporting_owner_id=ro.id))
            rows += 1

    def add_unique(model, items):
        nonlocal rows
        deduped = _dedupe_items(items, ("source_row_hash",))
        hashes = [x["source_row_hash"] for x in deduped if x.get("source_row_hash")]
        existing = set(session.scalars(select(model.source_row_hash).where(model.ownership_submission_id == sub.id, model.source_row_hash.in_(hashes))).all()) if hashes else set()
        for item in deduped:
            h = item.get("source_row_hash")
            if h in existing:
                continue
            session.add(model(ownership_submission_id=sub.id, **item))
            existing.add(h)
            rows += 1

    add_unique(NonDerivativeTransaction, parsed.get("non_derivative_transactions", []))
    add_unique(DerivativeTransaction, parsed.get("derivative_transactions", []))
    add_unique(NonDerivativeHolding, parsed.get("non_derivative_holdings", []))
    add_unique(DerivativeHolding, parsed.get("derivative_holdings", []))

    for footnote in _dedupe_items(parsed.get("footnotes", []), ("footnote_id",)):
        exists = session.scalar(select(OwnershipFootnote).where(OwnershipFootnote.ownership_submission_id == sub.id, OwnershipFootnote.footnote_id == footnote["footnote_id"]))
        if not exists:
            session.add(OwnershipFootnote(ownership_submission_id=sub.id, **footnote))
            rows += 1
    for sig in _dedupe_items(parsed.get("signatures", []), ("signature_name", "signature_date")):
        exists = session.scalar(select(OwnerSignature).where(OwnerSignature.ownership_submission_id == sub.id, OwnerSignature.signature_name == sig["signature_name"], OwnerSignature.signature_date == sig["signature_date"]))
        if not exists:
            session.add(OwnerSignature(ownership_submission_id=sub.id, **sig))
            rows += 1

    return rows

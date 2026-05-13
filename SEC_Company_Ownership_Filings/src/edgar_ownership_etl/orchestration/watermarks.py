from edgar_ownership_etl.db.models import EtlWatermark


def should_process_accession(accession: str, known_accessions: set[str]) -> bool:
    return accession not in known_accessions


def upsert_watermark(session, cik: str, last_accession_number: str | None, last_filing_date=None, last_acceptance_datetime=None):
    wm = session.query(EtlWatermark).filter_by(scope="cik", scope_value=cik).one_or_none()
    if wm is None:
        wm = EtlWatermark(scope="cik", scope_value=cik)
        session.add(wm)
    wm.last_accession_number = last_accession_number
    wm.last_filing_date = last_filing_date
    wm.last_acceptance_datetime = last_acceptance_datetime

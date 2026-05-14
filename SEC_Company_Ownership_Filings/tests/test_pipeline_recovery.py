from datetime import date
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session

from edgar_ownership_etl.db.models import Base, Issuer, SourceFiling
from edgar_ownership_etl.orchestration import pipeline
from edgar_ownership_etl.sec.filings import FilingCandidate


class DummyClient:
    pass


def test_pipeline_rolls_back_and_continues(monkeypatch):
    engine = create_engine('sqlite+pysqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(Issuer(cik='0000320193', ticker='AAPL', name='Apple'))
        session.commit()

        filings = [
            FilingCandidate('acc1', '0000320193', '4', date(2024, 1, 1), None, None, 'a.xml', None, 'u1', 'u1', False),
            FilingCandidate('acc2', '0000320193', '4', date(2024, 1, 2), None, None, 'b.xml', None, 'u2', 'u2', False),
        ]
        monkeypatch.setattr(pipeline, 'SecClient', DummyClient)
        monkeypatch.setattr(pipeline, 'fetch_company_filings', lambda c, cik: filings)
        monkeypatch.setattr(pipeline, 'select_ownership_document', lambda c, base, doc: ('x.xml', '<ownershipDocument/>'))
        monkeypatch.setattr(pipeline, 'parse_ownership_xml', lambda x: {'document_type': '4', 'issuer_cik': '0000320193'})

        state = {'n': 0}

        def fake_load(session, filing, *args, **kwargs):
            state['n'] += 1
            if filing.accession_number == 'acc1':
                raise ValueError('boom')
            sf = SourceFiling(accession_number=filing.accession_number, cik=filing.cik, form_type=filing.form_type, filing_date=filing.filing_date, report_date=filing.report_date, acceptance_datetime=filing.acceptance_datetime, filing_detail_url=filing.filing_detail_url, archive_base_url=filing.archive_base_url, is_amendment=False, parse_status='parsed')
            session.add(sf)
            return 1

        monkeypatch.setattr(pipeline, 'load_ownership_filing', fake_load)
        monkeypatch.setattr(pipeline, 'upsert_watermark', lambda *a, **k: None)

        summary = pipeline.ingest_company(session, ticker='AAPL')
        assert summary.filings_failed == 1
        assert summary.filings_processed == 1
        assert session.scalar(select(func.count()).select_from(SourceFiling)) >= 2

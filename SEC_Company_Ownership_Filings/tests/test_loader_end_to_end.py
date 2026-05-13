from pathlib import Path

from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session

from edgar_ownership_etl.db.models import Base, NonDerivativeTransaction, OwnershipSubmission, RawDocument, ReportingOwner
from edgar_ownership_etl.load.loader import load_ownership_filing
from edgar_ownership_etl.sec.filings import FilingCandidate
from edgar_ownership_etl.transform.ownership_xml_parser import parse_ownership_xml


def test_loader_inserts_and_is_idempotent():
    engine = create_engine('sqlite+pysqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)
    xml = Path('tests/fixtures/sample_form4.xml').read_text()
    parsed = parse_ownership_xml(xml)
    filing = FilingCandidate('0001-01-01', '0000320193', '4', None, None, None, 'x.xml', None, 'u', 'u', False)

    with Session(engine) as s:
        rows1 = load_ownership_filing(s, filing, 'x.xml', 'u/x.xml', 'application/xml', xml, parsed)
        s.commit()
        rows2 = load_ownership_filing(s, filing, 'x.xml', 'u/x.xml', 'application/xml', xml, parsed)
        s.commit()
        assert rows1 > 0
        assert rows2 == 0
        assert s.scalar(select(func.count()).select_from(RawDocument)) == 1
        assert s.scalar(select(func.count()).select_from(OwnershipSubmission)) == 1
        assert s.scalar(select(func.count()).select_from(ReportingOwner)) >= 0
        assert s.scalar(select(func.count()).select_from(NonDerivativeTransaction)) == 1
        tx = s.scalar(select(NonDerivativeTransaction))
        assert str(tx.transaction_shares) == '100.0000000000'
        assert str(tx.transaction_price_per_share) == '150.2500000000'
        assert tx.transaction_code == 'P'

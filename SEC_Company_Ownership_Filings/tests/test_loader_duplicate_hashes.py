from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session

from edgar_ownership_etl.db.models import Base, NonDerivativeTransaction
from edgar_ownership_etl.load.loader import load_ownership_filing
from edgar_ownership_etl.sec.filings import FilingCandidate


def test_duplicate_hash_rows_in_same_batch_do_not_crash_or_duplicate():
    engine = create_engine('sqlite+pysqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)
    filing = FilingCandidate('0001-01-01', '0000320193', '4', None, None, None, 'x.xml', None, 'u', 'u', False)
    parsed = {
        'document_type': '4', 'issuer_cik': '0000320193', 'reporting_owners': [],
        'non_derivative_transactions': [
            {'security_title': 'Common Stock', 'transaction_date': None, 'transaction_code': 'S', 'transaction_shares': 0, 'transaction_price_per_share': 0, 'source_row_hash': 'abc'},
            {'security_title': 'Common Stock', 'transaction_date': None, 'transaction_code': 'S', 'transaction_shares': 0, 'transaction_price_per_share': 0, 'source_row_hash': 'abc'},
        ],
        'derivative_transactions': [], 'non_derivative_holdings': [], 'derivative_holdings': [], 'footnotes': [], 'signatures': [],
    }
    with Session(engine) as session:
        load_ownership_filing(session, filing, 'x.xml', 'u/x.xml', 'application/xml', '<ownershipDocument/>', parsed)
        session.commit()
        load_ownership_filing(session, filing, 'x.xml', 'u/x.xml', 'application/xml', '<ownershipDocument/>', parsed)
        session.commit()
        assert session.scalar(select(func.count()).select_from(NonDerivativeTransaction)) == 1

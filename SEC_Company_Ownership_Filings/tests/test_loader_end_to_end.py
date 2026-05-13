from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session

from edgar_ownership_etl.db.models import Base, RawDocument, OwnershipSubmission, ReportingOwner, NonDerivativeTransaction
from edgar_ownership_etl.load.loader import load_ownership_filing
from edgar_ownership_etl.sec.filings import FilingCandidate
from edgar_ownership_etl.transform.ownership_xml_parser import parse_ownership_xml


XML = """<ownershipDocument><documentType>4</documentType><issuer><issuerCik>0000320193</issuerCik></issuer><reportingOwner><reportingOwnerId><rptOwnerCik>0001</rptOwnerCik><rptOwnerName>Jane Doe</rptOwnerName></reportingOwnerId><reportingOwnerRelationship><isDirector>1</isDirector></reportingOwnerRelationship></reportingOwner><nonDerivativeTable><nonDerivativeTransaction><securityTitle><value>Common</value></securityTitle><transactionDate><value>2024-01-01</value></transactionDate><transactionCoding><transactionCode>P</transactionCode></transactionCoding><transactionAmounts><transactionShares><value>10</value></transactionShares><transactionPricePerShare><value>1.1</value></transactionPricePerShare></transactionAmounts></nonDerivativeTransaction></nonDerivativeTable></ownershipDocument>"""


def test_loader_inserts_and_is_idempotent():
    engine = create_engine('sqlite+pysqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)
    parsed = parse_ownership_xml(XML)
    filing = FilingCandidate('0001-01-01', '0000320193', '4', None, None, None, 'x.xml', None, 'u', 'u', False)

    with Session(engine) as s:
        rows1 = load_ownership_filing(s, filing, 'x.xml', 'u/x.xml', 'application/xml', XML, parsed)
        s.commit()
        rows2 = load_ownership_filing(s, filing, 'x.xml', 'u/x.xml', 'application/xml', XML, parsed)
        s.commit()
        assert rows1 > 0
        assert rows2 == 0
        assert s.scalar(select(func.count()).select_from(RawDocument)) == 1
        assert s.scalar(select(func.count()).select_from(OwnershipSubmission)) == 1
        assert s.scalar(select(func.count()).select_from(ReportingOwner)) == 1
        assert s.scalar(select(func.count()).select_from(NonDerivativeTransaction)) == 1

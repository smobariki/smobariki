from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from edgar_ownership_etl.db.models import Base, ReportingOwner
from edgar_ownership_etl.load.loader import load_ownership_filing
from edgar_ownership_etl.sec.filings import FilingCandidate
from edgar_ownership_etl.transform.ownership_xml_parser import parse_ownership_xml


def test_loader_persists_reporting_owner_relationship_fields():
    xml = """<ownershipDocument><documentType>4</documentType><issuer><issuerCik>0000320193</issuerCik></issuer><reportingOwner><reportingOwnerId><rptOwnerCik>0001</rptOwnerCik><rptOwnerName>Jane Doe</rptOwnerName></reportingOwnerId><reportingOwnerRelationship><isDirector>1</isDirector><isOfficer>1</isOfficer><officerTitle>CFO</officerTitle><isTenPercentOwner>0</isTenPercentOwner><isOther>1</isOther><otherText>Trustee</otherText></reportingOwnerRelationship></reportingOwner></ownershipDocument>"""
    parsed = parse_ownership_xml(xml)
    filing = FilingCandidate('0009-01-01', '0000320193', '4', None, None, None, 'x.xml', None, 'u', 'u', False)
    engine = create_engine('sqlite+pysqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        load_ownership_filing(session, filing, 'x.xml', 'u/x.xml', 'application/xml', xml, parsed)
        session.commit()
        owner = session.scalar(select(ReportingOwner))
        assert owner.is_director is True
        assert owner.is_officer is True
        assert owner.officer_title == 'CFO'
        assert owner.is_ten_percent_owner is False
        assert owner.is_other is True
        assert owner.other_text == 'Trustee'

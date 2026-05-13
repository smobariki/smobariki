from pathlib import Path
from decimal import Decimal

from edgar_ownership_etl.transform.ownership_xml_parser import parse_ownership_xml


def test_parse_form4_fixture_numeric_values():
    parsed = parse_ownership_xml(Path('tests/fixtures/sample_form4.xml').read_text())
    row = parsed['non_derivative_transactions'][0]
    assert parsed['document_type'] == '4'
    assert row['transaction_code'] == 'P'
    assert row['transaction_date'].isoformat() == '2024-01-01'
    assert row['transaction_shares'] == Decimal('100')
    assert row['transaction_price_per_share'] == Decimal('150.25')


def test_missing_numeric_fields_remain_none():
    xml = '<ownershipDocument><documentType>4</documentType><issuer><issuerCik>1</issuerCik></issuer><nonDerivativeTable><nonDerivativeTransaction><securityTitle><value>Common</value></securityTitle></nonDerivativeTransaction></nonDerivativeTable></ownershipDocument>'
    parsed = parse_ownership_xml(xml)
    row = parsed['non_derivative_transactions'][0]
    assert row['transaction_shares'] is None
    assert row['transaction_price_per_share'] is None

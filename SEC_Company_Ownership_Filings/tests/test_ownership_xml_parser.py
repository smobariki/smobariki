from pathlib import Path
from edgar_ownership_etl.transform.ownership_xml_parser import parse_ownership_xml

def test_parse_form4_fixture():
    parsed = parse_ownership_xml(Path('tests/fixtures/sample_form4.xml').read_text())
    assert parsed['document_type'] == '4'
    assert parsed['non_derivative_transactions'][0]['transaction_code'] == 'P'

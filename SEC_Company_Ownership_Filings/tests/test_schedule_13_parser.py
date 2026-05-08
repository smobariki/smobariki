from pathlib import Path
from edgar_ownership_etl.transform.schedule_13_parser import parse_schedule_13

def test_schedule_fallback_splits_items():
    out = parse_schedule_13(Path('tests/fixtures/sample_schedule13d.html').read_text())
    assert out['source_parse_method'] == 'text_fallback'

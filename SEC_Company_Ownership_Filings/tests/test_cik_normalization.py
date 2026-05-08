import pytest
from edgar_ownership_etl.sec.cik import normalize_cik

def test_normalize_cik():
    assert normalize_cik('320193') == '0000320193'
    with pytest.raises(ValueError):
        normalize_cik('abc')

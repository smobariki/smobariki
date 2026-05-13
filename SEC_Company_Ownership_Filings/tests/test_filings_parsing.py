from edgar_ownership_etl.sec.filings import parse_recent_filings


def test_parse_recent_filings_filters_supported_forms():
    payload = {
        "filings": {"recent": {
            "form": ["4", "10-K"],
            "accessionNumber": ["0001-01-01", "0002-01-01"],
            "filingDate": ["2024-01-01", "2024-01-02"],
            "reportDate": ["2023-12-31", "2023-12-31"],
            "acceptanceDateTime": ["2024-01-01T01:02:03.000Z", "2024-01-02T01:02:03.000Z"],
            "primaryDocument": ["x.xml", "y.htm"],
            "primaryDocDescription": ["OWN", "ANNUAL"],
        }}
    }
    out = parse_recent_filings(payload, "0000320193")
    assert len(out) == 1
    assert out[0].form_type == "4"

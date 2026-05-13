from edgar_ownership_etl.sec.client import SecClient
from edgar_ownership_etl.sec.filings import FilingCandidate, parse_recent_filings
from edgar_ownership_etl.sec.urls import submissions_url


def fetch_company_filings(client: SecClient, cik: str) -> list[FilingCandidate]:
    resp = client.get(submissions_url(cik))
    return parse_recent_filings(resp.json(), cik)

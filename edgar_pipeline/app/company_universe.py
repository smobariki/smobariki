from __future__ import annotations

from app.sec_client import SECClient


def refresh_company_universe(sec_client: SECClient) -> list[dict]:
    url = "https://www.sec.gov/files/company_tickers_exchange.json"
    payload = sec_client.get_json(url)
    companies = []
    for row in payload.get("data", []):
        if not row:
            continue
        cik = str(row[0]).zfill(10)
        ticker = row[2]
        company_name = row[1]
        exchange = row[3]
        companies.append(
            {
                "cik": cik,
                "ticker": ticker,
                "company_name": company_name,
                "exchange": exchange,
                "source": "sec_company_tickers_exchange",
            }
        )
    return companies

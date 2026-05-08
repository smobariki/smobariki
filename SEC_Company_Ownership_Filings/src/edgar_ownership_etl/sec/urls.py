from edgar_ownership_etl.sec.cik import cik_for_archive, normalize_cik


def submissions_url(cik: str) -> str:
    return f"https://data.sec.gov/submissions/CIK{normalize_cik(cik)}.json"


def archive_base_url(cik: str, accession: str) -> str:
    return f"https://www.sec.gov/Archives/edgar/data/{cik_for_archive(cik)}/{accession.replace('-', '')}"

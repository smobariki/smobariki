from pathlib import Path


def test_qlik_views_declared_in_migration():
    content = Path('alembic/versions/0001_initial.py').read_text()
    for view in [
        'vw_latest_insider_transactions',
        'vw_form4_transactions',
        'vw_reporting_owner_activity',
        'vw_company_filing_history',
    ]:
        assert view in content

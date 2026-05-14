from pathlib import Path


def test_qlik_views_declared_in_migration():
    content = Path('alembic/versions/0001_initial.py').read_text()
    for view in [
        'vw_latest_insider_transactions',
        'vw_form4_transactions',
        'vw_reporting_owner_activity',
        'vw_company_filing_history',
        'fact_ownership_transactions',
        'dim_issuer',
        'dim_form_type',
        'dim_transaction_code',
        'dim_reporting_owner',
        'dim_filing',
    ]:
        assert view in content


def test_fact_ownership_transactions_columns_declared():
    content = Path('alembic/versions/0001_initial.py').read_text()
    for col in [
        'transaction_shares',
        'transaction_price_per_share',
        'transaction_value',
        'form_type',
        'issuer_cik',
        'owner_name',
        'transaction_code',
    ]:
        assert col in content

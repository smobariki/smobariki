from pathlib import Path

from edgar_ownership_etl.db.models import Base


MODEL_FILE = Path('src/edgar_ownership_etl/db/models.py')


def test_required_table_mappings_exist_once():
    keys = list(Base.metadata.tables.keys())
    assert len(keys) == len(set(keys))

    required = {
        'non_derivative_transactions',
        'derivative_transactions',
        'non_derivative_holdings',
        'derivative_holdings',
        'raw_documents',
        'ownership_submissions',
        'reporting_owners',
        'source_filings',
        'etl_watermarks',
    }
    for name in required:
        assert keys.count(name) == 1


def test_single_occurrence_of_transaction_holding_models_in_file():
    content = MODEL_FILE.read_text()
    assert content.count('class NonDerivativeTransaction') == 1
    assert content.count('__tablename__ = "non_derivative_transactions"') == 1
    assert content.count('class DerivativeTransaction') == 1
    assert content.count('__tablename__ = "derivative_transactions"') == 1
    assert content.count('class NonDerivativeHolding') == 1
    assert content.count('__tablename__ = "non_derivative_holdings"') == 1
    assert content.count('class DerivativeHolding') == 1
    assert content.count('__tablename__ = "derivative_holdings"') == 1

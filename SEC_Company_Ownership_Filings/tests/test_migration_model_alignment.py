from pathlib import Path

from edgar_ownership_etl.db.models import (
    DerivativeHolding,
    DerivativeTransaction,
    NonDerivativeHolding,
    NonDerivativeTransaction,
)


def _model_columns(model):
    return {c.name for c in model.__table__.columns}


def test_model_columns_for_transaction_holding_tables():
    assert _model_columns(NonDerivativeTransaction) >= {
        'id', 'ownership_submission_id', 'transaction_date', 'transaction_code',
        'transaction_shares', 'transaction_price_per_share', 'security_title',
        'equity_swap_involved', 'transaction_acquired_disposed_code',
        'shares_owned_following_transaction', 'direct_or_indirect_ownership',
        'nature_of_ownership', 'source_row_hash',
    }
    assert _model_columns(DerivativeTransaction) >= {
        'id', 'ownership_submission_id', 'transaction_date', 'transaction_code',
        'transaction_shares', 'transaction_price_per_share', 'security_title',
        'equity_swap_involved', 'transaction_acquired_disposed_code',
        'shares_owned_following_transaction', 'direct_or_indirect_ownership',
        'nature_of_ownership', 'source_row_hash',
    }
    assert _model_columns(NonDerivativeHolding) >= {
        'id', 'ownership_submission_id', 'security_title', 'equity_swap_involved',
        'transaction_acquired_disposed_code', 'shares_owned_following_transaction',
        'direct_or_indirect_ownership', 'nature_of_ownership', 'source_row_hash',
    }
    assert _model_columns(DerivativeHolding) >= {
        'id', 'ownership_submission_id', 'security_title', 'equity_swap_involved',
        'transaction_acquired_disposed_code', 'shares_owned_following_transaction',
        'direct_or_indirect_ownership', 'nature_of_ownership', 'source_row_hash',
    }


def test_migration_contains_equity_swap_columns():
    content = Path('alembic/versions/0001_initial.py').read_text()
    assert "create_table('non_derivative_transactions'" in content
    assert "create_table('derivative_transactions'" in content
    assert "create_table('non_derivative_holdings'" in content
    assert "create_table('derivative_holdings'" in content
    assert content.count("equity_swap_involved") >= 4

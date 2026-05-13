from edgar_ownership_etl.db.models import Base, DerivativeTransaction


def test_derivative_transaction_single_mapping():
    assert DerivativeTransaction.__tablename__ == 'derivative_transactions'
    assert list(Base.metadata.tables.keys()).count('derivative_transactions') == 1


def test_no_duplicate_table_mappings():
    names = [t.name for t in Base.metadata.sorted_tables]
    assert len(names) == len(set(names))

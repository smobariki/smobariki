from edgar_ownership_etl.db.models import Base


def test_table_names_are_unique_and_derivative_exists():
    assert len(Base.metadata.tables) == len(set(Base.metadata.tables.keys()))
    assert 'derivative_transactions' in Base.metadata.tables

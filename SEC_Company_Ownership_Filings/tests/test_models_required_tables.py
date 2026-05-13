from edgar_ownership_etl.db.models import (
    Base,
    DerivativeHolding,
    DerivativeTransaction,
    EtlWatermark,
    NonDerivativeHolding,
    NonDerivativeTransaction,
    OwnershipSubmission,
    RawDocument,
    ReportingOwner,
    SourceFiling,
)


def test_required_table_mappings_exist_once():
    assert DerivativeHolding.__tablename__ == 'derivative_holdings'
    assert DerivativeTransaction.__tablename__ == 'derivative_transactions'
    assert NonDerivativeHolding.__tablename__ == 'non_derivative_holdings'
    assert NonDerivativeTransaction.__tablename__ == 'non_derivative_transactions'
    assert SourceFiling.__tablename__ == 'source_filings'
    assert RawDocument.__tablename__ == 'raw_documents'
    assert OwnershipSubmission.__tablename__ == 'ownership_submissions'
    assert ReportingOwner.__tablename__ == 'reporting_owners'
    assert EtlWatermark.__tablename__ == 'etl_watermarks'

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
    keys = list(Base.metadata.tables.keys())
    assert len(keys) == len(set(keys))
    for name in required:
        assert keys.count(name) == 1

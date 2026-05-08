from edgar_ownership_etl.orchestration.watermarks import should_process_accession

def test_unseen_accession_processed():
    assert should_process_accession('x', {'y'})

from edgar_ownership_etl.load.upserts import dedupe_new_transactions

class S:
    def scalar(self, *_):
        return None

def test_dedupe_keeps_new():
    rows=[{'source_row_hash':'a'}]
    assert len(dedupe_new_transactions(S(), 'id', rows)) == 1

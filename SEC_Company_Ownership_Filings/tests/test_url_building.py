from edgar_ownership_etl.sec.urls import submissions_url

def test_submissions_url():
    assert submissions_url('320193').endswith('CIK0000320193.json')

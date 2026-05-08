import pytest
from edgar_ownership_etl.sec.client import SecClient, SecClientError

class Resp:
    status_code = 429
    def raise_for_status(self):
        return None

class Client:
    def get(self, _):
        return Resp()

def test_retryable_status_raises():
    c = SecClient()
    c.client = Client()
    with pytest.raises(SecClientError):
        c.get.__wrapped__(c, 'http://x')

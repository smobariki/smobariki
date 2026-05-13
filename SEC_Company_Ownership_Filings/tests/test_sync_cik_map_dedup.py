from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker

from edgar_ownership_etl.cli import sync_cik_map
from edgar_ownership_etl.db.models import Base, Issuer


class _Resp:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class _SecClient:
    def __init__(self, payload):
        self.payload = payload

    def get(self, _):
        return _Resp(self.payload)


def test_sync_cik_map_dedup_duplicate_cik(monkeypatch):
    payload = {
        "0": {"cik_str": 1652044, "ticker": "GOOG", "title": "Alphabet Inc."},
        "1": {"cik_str": 1652044, "ticker": "GOOGL", "title": "Alphabet Inc."},
    }

    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, future=True)

    monkeypatch.setattr("edgar_ownership_etl.cli.SessionLocal", TestingSessionLocal)
    monkeypatch.setattr("edgar_ownership_etl.cli.SecClient", lambda: _SecClient(payload))

    sync_cik_map()
    sync_cik_map()

    with TestingSessionLocal() as session:
        assert session.scalar(select(func.count()).select_from(Issuer)) == 1
        issuer = session.scalar(select(Issuer).where(Issuer.cik == "0001652044"))
        assert issuer is not None
        assert issuer.ticker in {"GOOG", "GOOGL"}

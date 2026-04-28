from contextlib import contextmanager
import psycopg


@contextmanager
def get_conn(database_url: str):
    conn = psycopg.connect(database_url)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

from __future__ import annotations


def refresh_views(conn) -> None:
    with conn.cursor() as cur:
        cur.execute("REFRESH MATERIALIZED VIEW analytics.mv_daily_filing_kpis")

from sqlalchemy import select
from edgar_ownership_etl.db.models import NonDerivativeTransaction


def dedupe_new_transactions(session, submission_id, rows):
    out = []
    for row in rows:
        exists = session.scalar(select(NonDerivativeTransaction.id).where(
            NonDerivativeTransaction.ownership_submission_id == submission_id,
            NonDerivativeTransaction.source_row_hash == row["source_row_hash"],
        ))
        if not exists:
            out.append(row)
    return out

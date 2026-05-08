import hashlib
import json
from datetime import date
from decimal import Decimal


def _normalize(v):
    if isinstance(v, str):
        return v.strip()
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, Decimal):
        return format(v.normalize(), "f")
    return v


def row_hash(payload: dict) -> str:
    normalized = {k.lower(): _normalize(v) for k, v in payload.items()}
    blob = json.dumps(normalized, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()

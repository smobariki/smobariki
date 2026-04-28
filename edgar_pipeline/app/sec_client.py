from __future__ import annotations

import logging
import time
from typing import Any

import requests

from app.utils.rate_limit import SimpleRateLimiter

logger = logging.getLogger(__name__)


class SECClient:
    def __init__(self, user_agent: str, per_second: float = 5.0, timeout: int = 30):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"})
        self.timeout = timeout
        self.rate_limiter = SimpleRateLimiter(per_second=per_second)

    def get_json(self, url: str, retries: int = 3) -> dict[str, Any]:
        return self._request(url, "json", retries=retries)

    def get_text(self, url: str, retries: int = 3) -> str:
        return self._request(url, "text", retries=retries)

    def _request(self, url: str, mode: str, retries: int = 3):
        for attempt in range(1, retries + 1):
            try:
                self.rate_limiter.wait()
                r = self.session.get(url, timeout=self.timeout)
                r.raise_for_status()
                return r.json() if mode == "json" else r.text
            except Exception as exc:
                logger.warning("SEC request failed", extra={"url": url, "attempt": attempt, "error": str(exc)})
                if attempt == retries:
                    raise
                time.sleep(2 ** (attempt - 1))

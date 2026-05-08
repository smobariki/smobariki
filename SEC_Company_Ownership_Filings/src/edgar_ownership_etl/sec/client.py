import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from edgar_ownership_etl.config import settings
from edgar_ownership_etl.sec.rate_limiter import RateLimiter


class SecClientError(Exception):
    pass


class SecClient:
    def __init__(self) -> None:
        self.client = httpx.Client(headers={"User-Agent": settings.sec_user_agent}, timeout=30)
        self.limiter = RateLimiter(settings.sec_requests_per_second)

    @retry(stop=stop_after_attempt(4), wait=wait_exponential(min=1, max=8), retry=retry_if_exception_type(SecClientError))
    def get(self, url: str) -> httpx.Response:
        self.limiter.wait()
        resp = self.client.get(url)
        if resp.status_code in {429,500,502,503,504}:
            raise SecClientError(f"Retryable status {resp.status_code}")
        resp.raise_for_status()
        return resp

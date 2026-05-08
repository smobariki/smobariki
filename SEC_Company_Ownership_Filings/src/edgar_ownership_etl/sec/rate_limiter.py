import threading
import time


class RateLimiter:
    def __init__(self, rps: int) -> None:
        self.period = 1.0 / max(rps, 1)
        self.lock = threading.Lock()
        self.last = 0.0

    def wait(self) -> None:
        with self.lock:
            now = time.monotonic()
            elapsed = now - self.last
            if elapsed < self.period:
                time.sleep(self.period - elapsed)
            self.last = time.monotonic()

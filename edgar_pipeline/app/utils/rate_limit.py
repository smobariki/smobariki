import threading
import time


class SimpleRateLimiter:
    def __init__(self, per_second: float = 5.0):
        self.interval = 1.0 / per_second
        self._lock = threading.Lock()
        self._next_allowed = 0.0

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            if now < self._next_allowed:
                time.sleep(self._next_allowed - now)
            self._next_allowed = time.monotonic() + self.interval

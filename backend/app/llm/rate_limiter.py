import threading
import time

from app.llm.errors import RetryableProviderError


class TokenBucket:
    def __init__(self, capacity: int, fill_rate: float):
        self.capacity = float(capacity)
        self._tokens = float(capacity)
        self.fill_rate = fill_rate
        self.last_update = time.time()
        self._lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        with self._lock:
            now = time.time()
            elapsed = now - self.last_update
            self._tokens = min(self.capacity, self._tokens + elapsed * self.fill_rate)
            self.last_update = now

            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False


class ProviderRateLimiter:
    def __init__(self, provider_name: str, max_concurrent: int, rpm: int):
        self.provider_name = provider_name
        self._semaphore = threading.BoundedSemaphore(max_concurrent)
        self._bucket = TokenBucket(capacity=rpm, fill_rate=rpm / 60.0)

    def __enter__(self):
        if not self._semaphore.acquire(blocking=False):
            raise RetryableProviderError(f"{self.provider_name} concurrency limit reached")

        if not self._bucket.consume():
            self._semaphore.release()
            raise RetryableProviderError(f"{self.provider_name} rate limit (RPM) reached")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._semaphore.release()

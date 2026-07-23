"""
=========================================================
NPAT - Rate Limiter
=========================================================

Token Bucket rate limiter.

Protects providers from exceeding API limits.

Version:
1.0.0
=========================================================
"""

from __future__ import annotations

import time

from threading import RLock

from services.exceptions import RateLimitExceededException


class RateLimiter:

    def __init__(
        self,
        capacity: int,
        refill_rate: float,
    ) -> None:

        if capacity <= 0:
            raise ValueError("capacity must be greater than zero.")

        if refill_rate <= 0:
            raise ValueError("refill_rate must be greater than zero.")

        self.capacity = capacity

        self.tokens = float(capacity)

        self.refill_rate = refill_rate

        self.last_refill = time.monotonic()

        self._lock = RLock()

    def _refill(self) -> None:

        now = time.monotonic()

        elapsed = now - self.last_refill

        if elapsed <= 0:
            return

        new_tokens = elapsed * self.refill_rate

        self.tokens = min(
            self.capacity,
            self.tokens + new_tokens,
        )

        self.last_refill = now
        
    def acquire(self) -> None:

        with self._lock:

            self._refill()

            if self.tokens >= 1:

                self.tokens -= 1

                return

            raise RateLimitExceededException(
                message="Rate limit exceeded."
        )
    
    def reset(self) -> None:

        with self._lock:

            self.tokens = float(self.capacity)

            self.last_refill = time.monotonic()
            
    def stats(self) -> dict[str, float]:

        with self._lock:

            self._refill()

            return {
                "capacity": float(self.capacity),
                "tokens": round(self.tokens, 2),
                "refill_rate": self.refill_rate,
            }
"""
=========================================================
NPAT - Circuit Breaker
=========================================================

Protects external providers from repeated failures.

Version:
1.0.0
=========================================================
"""

from __future__ import annotations

import time

from enum import Enum
from threading import RLock
from typing import Any, Callable

from services.exceptions import CircuitOpenException

class CircuitState(Enum):

    CLOSED = "CLOSED"

    OPEN = "OPEN"

    HALF_OPEN = "HALF_OPEN"
    
class CircuitBreaker:

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        success_threshold: int = 2,
     ):

        self.name = name

        self.failure_threshold = failure_threshold

        self.recovery_timeout = recovery_timeout

        self.success_threshold = success_threshold

        self.state = CircuitState.CLOSED

        self.failure_count = 0

        self.success_count = 0

        self.last_failure_time = 0.0

        self._lock = RLock()

    def _open(self) -> None:

        self.state = CircuitState.OPEN

        self.last_failure_time = time.time()
        
        self.success_count = 0


    def _close(self) -> None:

        self.state = CircuitState.CLOSED

        self.failure_count = 0

        self.success_count = 0


    def _half_open(self) -> None:

        self.state = CircuitState.HALF_OPEN

        self.success_count = 0
    
    def before_request(self) -> None:

        with self._lock:

            if self.state == CircuitState.CLOSED:

             return

            if self.state == CircuitState.OPEN:

                elapsed = time.time() - self.last_failure_time

                if elapsed >= self.recovery_timeout:

                    self._half_open()

                    return

                raise CircuitOpenException(

                    message=f"Circuit '{self.name}' is OPEN.",

                    provider=self.name,

                )

            if self.state == CircuitState.HALF_OPEN:

                return
        
    def record_success(self) -> None:

        with self._lock:

            if self.state == CircuitState.HALF_OPEN:

                self.success_count += 1

                if self.success_count >= self.success_threshold:

                    self._close()

            elif self.state == CircuitState.CLOSED:

                self.failure_count = 0
            
    def record_failure(self) -> None:

        with self._lock:

            if self.state == CircuitState.HALF_OPEN:
            
                self.failure_count = self.failure_threshold

                self._open()

                return
            
            self.failure_count += 1

            if self.failure_count >= self.failure_threshold:

                self._open()

    def reset(self) -> None:

        with self._lock:

            self._close()

            self.last_failure_time = 0.0
        
        
    def stats(self) -> dict[str, Any]:

        with self._lock:

            remaining_timeout = 0.0

            if self.state == CircuitState.OPEN:

                remaining_timeout = max(
                    0.0,
                    self.recovery_timeout
                    - (time.time() - self.last_failure_time),
                )

            return {

                "name": self.name,

                "state": self.state.value,

                "failure_count": self.failure_count,

                "success_count": self.success_count,

                "failure_threshold": self.failure_threshold,

                "success_threshold": self.success_threshold,

                "remaining_timeout": round(
                    remaining_timeout,
                    2,
                ),
            }
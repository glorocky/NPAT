"""
=========================================================
NPAT - Telemetry
=========================================================

Collects execution metrics for services.

Features
--------
✓ Thread Safe
✓ Context Manager
✓ Manual Start/Stop
✓ Success/Failure Tracking
✓ Execution Time Statistics

Version:
1.0.0
=========================================================
"""

from __future__ import annotations

import time
import threading

from contextlib import contextmanager
from dataclasses import dataclass, asdict
from typing import Dict, Optional


@dataclass(slots=True)
class TelemetryStats:
    requests: int = 0
    success: int = 0
    failures: int = 0
    active: int = 0

    total_time: float = 0.0
    average_time: float = 0.0
    minimum_time: float = 0.0
    maximum_time: float = 0.0
    last_execution_time: float = 0.0

    success_rate: float = 0.0


class Telemetry:

    def __init__(self):

        self._lock = threading.RLock()

        self._stats = TelemetryStats()

        self._start_time: Optional[float] = None

    # --------------------------------------------------

    def start(self) -> None:

        with self._lock:

            self._start_time = time.perf_counter()

            self._stats.active += 1

    # --------------------------------------------------

    def stop(self, success: bool = True) -> float:

        with self._lock:

            if self._start_time is None:
                raise RuntimeError("Telemetry.start() was not called.")

            elapsed = time.perf_counter() - self._start_time

            self._stats.requests += 1

            self._stats.active -= 1

            self._stats.total_time += elapsed

            self._stats.last_execution_time = elapsed

            if self._stats.minimum_time == 0:
                self._stats.minimum_time = elapsed
            else:
                self._stats.minimum_time = min(
                    self._stats.minimum_time,
                    elapsed,
                )

            self._stats.maximum_time = max(
                self._stats.maximum_time,
                elapsed,
            )

            self._stats.average_time = (
                self._stats.total_time
                / self._stats.requests
            )

            if success:
                self._stats.success += 1
            else:
                self._stats.failures += 1

            self._stats.success_rate = (
                self._stats.success
                / self._stats.requests
            ) * 100

            self._start_time = None

            return elapsed

    # --------------------------------------------------

    @contextmanager
    def track(self):

        self.start()

        try:

            yield

        except Exception:

            self.stop(success=False)

            raise

        else:

            self.stop(success=True)

    # --------------------------------------------------

    def reset(self):

        with self._lock:

            self._stats = TelemetryStats()

            self._start_time = None

    # --------------------------------------------------

    def stats(self) -> Dict:

        with self._lock:

            return asdict(self._stats)


telemetry = Telemetry()
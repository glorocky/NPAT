"""
=========================================================
NPAT - Health Manager
=========================================================

Tracks the health of NPAT services and providers.

Features
--------
✓ Thread Safe
✓ Service Registration
✓ Health Monitoring
✓ Warning Support
✓ Summary Report

Version:
1.0.0
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from threading import RLock
from typing import Dict


# ==========================================================
# Health Status
# ==========================================================

class HealthStatus(Enum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


# ==========================================================
# Health Record
# ==========================================================

@dataclass(slots=True)
class HealthRecord:
    name: str
    status: HealthStatus = HealthStatus.UNKNOWN
    message: str = ""
    response_time: float = 0.0
    last_checked: datetime | None = None
    checks: int = 0
    failures: int = 0


# ==========================================================
# Health Manager
# ==========================================================

class HealthManager:

    def __init__(self):

        self._services: Dict[str, HealthRecord] = {}

        self._lock = RLock()

    # -----------------------------------------------------

    def register(self, name: str) -> None:

        with self._lock:

            if name not in self._services:

                self._services[name] = HealthRecord(name=name)

    # -----------------------------------------------------

    def unregister(self, name: str) -> None:

        with self._lock:

            self._services.pop(name, None)

    # -----------------------------------------------------

    def _get_record(self, name: str) -> HealthRecord:

        record = self._services.get(name)

        if record is None:

            raise ValueError(
                f"Service '{name}' is not registered."
            )

        return record

    # -----------------------------------------------------

    def _update(
        self,
        name: str,
        status: HealthStatus,
        message: str = "",
        response_time: float = 0.0,
    ) -> None:

        with self._lock:

            record = self._get_record(name)

            record.status = status
            record.message = message
            record.response_time = response_time
            record.last_checked = datetime.now()
            record.checks += 1

            if status == HealthStatus.UNHEALTHY:
                record.failures += 1

    # -----------------------------------------------------

    def set_healthy(
        self,
        name: str,
        response_time: float = 0.0,
    ) -> None:

        self._update(
            name=name,
            status=HealthStatus.HEALTHY,
            response_time=response_time,
        )

    # -----------------------------------------------------

    def set_warning(
        self,
        name: str,
        message: str,
        response_time: float = 0.0,
    ) -> None:

        self._update(
            name=name,
            status=HealthStatus.WARNING,
            message=message,
            response_time=response_time,
        )

    # -----------------------------------------------------

    def set_unhealthy(
        self,
        name: str,
        message: str,
    ) -> None:

        self._update(
            name=name,
            status=HealthStatus.UNHEALTHY,
            message=message,
        )

    # -----------------------------------------------------

    def get(self, name: str) -> HealthRecord:

        with self._lock:

            return self._get_record(name)

    # -----------------------------------------------------

    def is_healthy(self, name: str) -> bool:

        with self._lock:

            return (
                self._get_record(name).status
                == HealthStatus.HEALTHY
            )

    # -----------------------------------------------------

    def summary(self) -> Dict[str, int | str]:

        with self._lock:

            healthy = 0
            warning = 0
            unhealthy = 0
            unknown = 0

            for record in self._services.values():

                if record.status == HealthStatus.HEALTHY:
                    healthy += 1

                elif record.status == HealthStatus.WARNING:
                    warning += 1

                elif record.status == HealthStatus.UNHEALTHY:
                    unhealthy += 1

                else:
                    unknown += 1

            if unhealthy:
                overall = HealthStatus.UNHEALTHY.value

            elif warning:
                overall = HealthStatus.WARNING.value

            elif unknown:
                overall = HealthStatus.UNKNOWN.value

            else:
                overall = HealthStatus.HEALTHY.value

            return {
                "overall": overall,
                "services": len(self._services),
                "healthy": healthy,
                "warning": warning,
                "unhealthy": unhealthy,
                "unknown": unknown,
            }

    # -----------------------------------------------------

    def reset(self) -> None:

        with self._lock:

            self._services.clear()


# ==========================================================
# Global Health Manager
# ==========================================================

health = HealthManager()
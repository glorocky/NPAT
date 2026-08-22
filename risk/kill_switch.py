from __future__ import annotations

from dataclasses import dataclass


@dataclass
class KillSwitch:
    """Explicit paper-only emergency gate for NPAT."""
    enabled: bool = False
    reason: str = ""

    def activate(self, reason: str = "Manual emergency stop") -> None:
        self.enabled = True
        self.reason = reason

    def reset(self) -> None:
        self.enabled = False
        self.reason = ""

    def allow(self) -> bool:
        return not self.enabled

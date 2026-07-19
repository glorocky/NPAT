"""
=========================================================
NPAT - Core Data Models
=========================================================

Purpose
-------
Central data models used across the NPAT application.

These dataclasses provide strongly typed objects instead
of dictionaries, making the code safer, easier to read,
and easier to maintain.

Author : Rocky Chopra
Version: 1.0.0
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


# =========================================================
# Quote
# =========================================================

@dataclass(frozen=True)
class Quote:
    """Live market quote."""

    symbol: str
    exchange: str
    last_price: float
    open: float
    high: float
    low: float
    previous_close: float
    volume: int = 0
    timestamp: Optional[datetime] = None


# =========================================================
# Historical Candle
# =========================================================

@dataclass(frozen=True)
class HistoricalCandle:
    """Represents one OHLCV candle."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


# =========================================================
# Option Data
# =========================================================

@dataclass(frozen=True)
class OptionData:
    """Single option strike data."""

    strike: float

    call_oi: int = 0
    put_oi: int = 0

    call_change_oi: int = 0
    put_change_oi: int = 0

    call_volume: int = 0
    put_volume: int = 0

    call_iv: float = 0.0
    put_iv: float = 0.0

    call_ltp: float = 0.0
    put_ltp: float = 0.0


# =========================================================
# Market Snapshot
# =========================================================

@dataclass(frozen=True)
class MarketSnapshot:
    """
    Complete market snapshot used by the analytics engine.
    """

    symbol: str

    spot_price: float

    expiry: str

    atm_strike: int

    pcr: float = 0.0

    max_pain: Optional[int] = None

    support: List[int] = field(default_factory=list)

    resistance: List[int] = field(default_factory=list)

    options: List[OptionData] = field(default_factory=list)

    timestamp: Optional[datetime] = None
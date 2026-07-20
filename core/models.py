"""
=========================================================
NPAT - Core Data Models
=========================================================

Purpose
-------
Central strongly-typed data models used throughout NPAT.

These dataclasses replace dictionaries across the application,
providing type safety, IDE auto-completion, easier debugging,
and cleaner architecture.

Author : Rocky Chopra
Version: 2.0.0
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


# =========================================================
# Quote
# =========================================================

@dataclass(frozen=True)
class Quote:
    """
    Represents a live market quote.
    """

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
    """
    Represents one historical OHLCV candle.
    """

    timestamp: datetime

    open: float
    high: float
    low: float
    close: float

    volume: int


# =========================================================
# Option Chain Strike
# =========================================================

@dataclass(frozen=True)
class OptionData:
    """
    Represents one option strike.

    Contains both Call and Put information for a strike.
    """

    strike_price: float

    expiry: str

    underlying_price: float

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
    Complete analytical market snapshot.

    Generated from the live option chain and used by
    the analytics engine.
    """

    symbol: str

    exchange: str = "NSE"

    spot_price: float = 0.0

    expiry: str = ""

    atm_strike: int = 0

    pcr: float = 0.0

    max_pain: Optional[int] = None

    support: List[tuple[int, int]] = field(default_factory=list)

    resistance: List[tuple[int, int]] = field(default_factory=list)

    total_call_oi: int = 0

    total_put_oi: int = 0

    option_chain: List[OptionData] = field(default_factory=list)

    timestamp: datetime = field(default_factory=datetime.now)
"""
=========================================================
NPAT Paper Trading
Enums
=========================================================

Common enumerations used throughout the
Paper Trading Engine.

These enums define the lifecycle of trades,
orders and AI-generated decisions while
remaining broker-independent.

=========================================================
"""

from enum import Enum


# =========================================================
# Trade Side
# =========================================================

class TradeSide(str, Enum):
    """
    Direction of the trade.
    """

    BUY = "BUY"
    SELL = "SELL"


# =========================================================
# Trade Status
# =========================================================

class TradeStatus(str, Enum):
    """
    Current lifecycle state of a paper trade.
    """

    PENDING = "PENDING"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


# =========================================================
# Exit Reason
# =========================================================

class ExitReason(str, Enum):
    """
    Reason for closing a trade.
    """

    TARGET = "TARGET"
    STOPLOSS = "STOPLOSS"
    MANUAL = "MANUAL"
    AI = "AI"
    MARKET_CLOSE = "MARKET_CLOSE"


# =========================================================
# Order Type
# =========================================================

class OrderType(str, Enum):
    """
    Type of order placed.
    """

    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


# =========================================================
# Trade Source
# =========================================================

class TradeSource(str, Enum):
    """
    Origin of the trading decision.
    """

    AI = "AI"
    MANUAL = "MANUAL"


# =========================================================
# Position State
# =========================================================

class PositionState(str, Enum):
    """
    Current state of the position.
    """

    FLAT = "FLAT"
    LONG = "LONG"
    SHORT = "SHORT"


# =========================================================
# Risk Status
# =========================================================

class RiskStatus(str, Enum):
    """
    Current risk state of the trade.
    """

    SAFE = "SAFE"
    WARNING = "WARNING"
    DANGER = "DANGER"


# =========================================================
# AI Recommendation
# =========================================================

class AIRecommendation(str, Enum):
    """
    AI recommendation for an open trade.
    """

    HOLD = "HOLD"
    EXIT = "EXIT"
    BOOK_PROFIT = "BOOK_PROFIT"
    TRAIL_STOP = "TRAIL_STOP"
"""
=========================================================
NPAT Paper Trading
Models
=========================================================

Core data models used by the Paper Trading Engine.

These models are intentionally broker-independent so
they can later be reused by the Live Trading Engine.

=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from paper_trading.enums import (
    AIRecommendation,
    ExitReason,
    OrderType,
    PositionState,
    TradeSide,
    TradeSource,
    TradeStatus,
)


# =========================================================
# Paper Trade
# =========================================================

@dataclass(slots=True)
class PaperTrade:
    """
    Represents one complete paper trade.

    A PaperTrade progresses through the lifecycle:

        PENDING
            ↓
        OPEN
            ↓
        CLOSED

    It contains all information required for:

    • Dashboard
    • Paper Broker
    • Trade Journal
    • Performance Analytics
    • Future Live Trading
    """

    # -----------------------------------------------------
    # Identity
    # -----------------------------------------------------

    trade_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    symbol: str = ""
    exchange: str = "NSE"

    # Persist exact derivative contract identity for option positions.
    underlying_symbol: str = ""
    expiry: str = ""
    strike_price: int = 0
    option_type: str = ""
    trading_symbol: str = ""
    lot_size: int = 0

    # -----------------------------------------------------
    # Trade Details
    # -----------------------------------------------------

    side: TradeSide = TradeSide.BUY

    order_type: OrderType = OrderType.MARKET

    source: TradeSource = TradeSource.AI

    quantity: int = 0

    # -----------------------------------------------------
    # Prices
    # -----------------------------------------------------

    entry_price: float = 0.0

    current_price: float = 0.0

    exit_price: float = 0.0

    # -----------------------------------------------------
    # Risk Management
    # -----------------------------------------------------

    stop_loss: float = 0.0

    target: float = 0.0

    # -----------------------------------------------------
    # Time
    # -----------------------------------------------------

    entry_time: datetime = field(
    default_factory=lambda: datetime.now(timezone.utc)
    )
    exit_time: datetime | None = None

    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------

    status: TradeStatus = TradeStatus.PENDING

    exit_reason: ExitReason | None = None

    # -----------------------------------------------------
    # P&L
    # -----------------------------------------------------

    unrealized_pnl: float = 0.0

    realized_pnl: float = 0.0

    # -----------------------------------------------------
    # AI
    # -----------------------------------------------------

    ai_confidence: float = 0.0

    ai_recommendation: AIRecommendation = (
        AIRecommendation.HOLD
    )

    ai_reason: str = ""

    # -----------------------------------------------------
    # Notes
    # -----------------------------------------------------

    notes: str = ""


@dataclass(frozen=True, slots=True)
class OptionPaperOrderPreview:
    """A reviewable AI option paper order; it is not an order itself."""

    underlying_symbol: str
    exchange: str
    expiry: str
    strike_price: int
    option_type: str
    trading_symbol: str
    entry_price: float
    lot_size: int
    quantity: int
    stop_loss: float
    target: float
    risk_reward: float
    
# =========================================================
# Position
# =========================================================

@dataclass(slots=True)
class Position:
    """
    Represents the current live position derived
    from an open paper trade.

    Used for:

    • MTM
    • Risk
    • Dashboard
    """

    trade_id: str

    symbol: str

    quantity: int

    average_price: float

    current_price: float

    market_value: float

    unrealized_pnl: float

    state: PositionState = PositionState.FLAT
    
# =========================================================
# Trade Event
# =========================================================

@dataclass(slots=True)
class TradeEvent:
    """
    Represents one event in a trade lifecycle.
    """

    trade_id: str

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    event: str = ""

    description: str = ""

# =========================================================
# Trade Result
# =========================================================

@dataclass(slots=True)
class TradeResult:
    """
    Represents the final outcome of a completed paper trade.

    Used by:
    • Trade Journal
    • Performance Analytics
    • Dashboard History
    """

    trade_id: str

    symbol: str

    entry_price: float

    exit_price: float

    quantity: int

    gross_pnl: float

    net_pnl: float

    return_pct: float

    duration_minutes: float

    exit_reason: ExitReason

    won: bool
    
# =========================================================
# Trade Statistics
# =========================================================

@dataclass(slots=True)
class TradeStatistics:
    """
    Aggregate trading performance statistics.

    Generated by Performance Analytics.
    """

    total_trades: int = 0

    winning_trades: int = 0

    losing_trades: int = 0
    
    breakeven_trades: int = 0

    win_rate: float = 0.0

    gross_profit: float = 0.0

    gross_loss: float = 0.0

    net_profit: float = 0.0

    average_profit: float = 0.0

    average_loss: float = 0.0

    largest_win: float = 0.0

    largest_loss: float = 0.0

    profit_factor: float = 0.0

    expectancy: float = 0.0

    max_drawdown: float = 0.0

# =========================================================
# Dashboard Summary
# =========================================================

@dataclass(slots=True)
class DashboardSummary:
    """
    Summary displayed on the Paper Trading Dashboard..
    """

    account_balance: float = 0.0

    available_cash: float = 0.0

    open_positions: int = 0

    open_trades: int = 0

    closed_trades: int = 0

    today_pnl: float = 0.0

    total_pnl: float = 0.0

    win_rate: float = 0.0

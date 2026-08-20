"""
=========================================================
NPAT Paper Trading
Position Manager
=========================================================

Performs all position-level calculations for the
Paper Trading Engine.

This module is intentionally stateless.

Responsibilities:
    • Market Value
    • Unrealized P&L
    • Position Construction

=========================================================
"""

from __future__ import annotations

from paper_trading.enums import (
    ExitReason,
    PositionState,
    TradeSide,
    TradeStatus,
)

from paper_trading.models import (
    PaperTrade,
    Position,
)


# =========================================================
# Position Manager
# =========================================================

class PositionManager:
    """
    Stateless utility class for position calculations.
    """

    # =====================================================
    # Market Value
    # =====================================================

    @staticmethod
    def calculate_market_value(
        quantity: int,
        current_price: float,
    ) -> float:
        """
        Calculate current market value.
        """

        return quantity * current_price

    # =====================================================
    # Unrealized P&L
    # =====================================================

    @staticmethod
    def calculate_unrealized_pnl(
        trade: PaperTrade,
    ) -> float:
        """
        Calculate unrealized profit/loss.
        """

        if trade.side == TradeSide.BUY:

            return (
                trade.current_price
                - trade.entry_price
            ) * trade.quantity

        return (
            trade.entry_price
            - trade.current_price
        ) * trade.quantity
        
    # =====================================================
    # Check Stop Loss / Target
    # =====================================================

    @staticmethod
    def check_exit_condition(
        trade: PaperTrade,
    ) -> ExitReason | None:
        """
        Check whether an open trade has reached
        its Stop Loss or Target.
        """

        if trade.status != TradeStatus.OPEN:
            return None

        price = trade.current_price

        # BUY position
        if trade.side == TradeSide.BUY:

            if (
                trade.stop_loss > 0
                and price <= trade.stop_loss
            ):
                return ExitReason.STOPLOSS

            if (
                trade.target > 0
                and price >= trade.target
            ):
                return ExitReason.TARGET

        # SELL position
        else:

            if (
                trade.stop_loss > 0
                and price >= trade.stop_loss
            ):
                return ExitReason.STOPLOSS

            if (
                trade.target > 0
                and price <= trade.target
            ):
                return ExitReason.TARGET

        return None

    # =====================================================
    # Position
    # =====================================================

    @staticmethod
    def calculate_position(
        trade: PaperTrade,
    ) -> Position:
        """
        Build a Position object from a PaperTrade.
        """

        market_value = (
            PositionManager.calculate_market_value(
                trade.quantity,
                trade.current_price,
            )
        )

        unrealized = (
            PositionManager.calculate_unrealized_pnl(
                trade
            )
        )

        state = (
            PositionState.LONG
            if trade.side == TradeSide.BUY
            else PositionState.SHORT
        )

        return Position(
            trade_id=trade.trade_id,
            symbol=trade.symbol,
            quantity=trade.quantity,
            average_price=trade.entry_price,
            current_price=trade.current_price,
            market_value=market_value,
            unrealized_pnl=unrealized,
            state=state,
        )
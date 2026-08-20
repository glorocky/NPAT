"""
=========================================================
NPAT Paper Trading
Paper Broker
=========================================================

Simulates broker order execution for paper trading.

Responsibilities:
    • Place Paper Orders
    • Close Paper Orders
    • Modify Orders

No external broker APIs are used.

=========================================================
"""

from __future__ import annotations

from datetime import datetime, timezone

from paper_trading.enums import (
    TradeSide,
    TradeSource,
    TradeStatus,
)

from paper_trading.models import (
    PaperTrade,
    TradeEvent,
)

from paper_trading.storage import (
    PaperTradeStorage,
)
from paper_trading.enums import (
    TradeSide,
    TradeSource,
    TradeStatus,
    ExitReason,
)
from paper_trading.position_manager import (
    PositionManager,
)


# =========================================================
# Paper Broker
# =========================================================

class PaperBroker:
    """
    Simulates a broker for paper trading.
    """

    def __init__(
        self,
        storage: PaperTradeStorage,
    ):

        self.storage = storage
    # =====================================================
    # Place Order
    # =====================================================

    def place_order(
        self,
        symbol: str,
        side: TradeSide,
        quantity: int,
        price: float,
        stop_loss: float = 0.0,
        target: float = 0.0,
        source: TradeSource = TradeSource.AI,
    ) -> PaperTrade:
        """
        Create and save a paper trade.
        """

        trade = PaperTrade(
            symbol=symbol,
            side=side,
            quantity=quantity,
            entry_price=price,
            current_price=price,
            stop_loss=stop_loss,
            target=target,
            source=source,
            status=TradeStatus.OPEN,
        )

        self.storage.save_trade(trade)
        
        return trade
    
    # =====================================================
    # Update Market Price
    # =====================================================

    def update_market_price(
        self,
        trade_id: str,
        price: float,
    ) -> PaperTrade:
        """
        Update the current market price of an open trade.

        Automatically closes the trade when
        Stop Loss or Target is reached.
        """

        trade = self.storage.get_trade(
            trade_id,
        )

        if trade is None:
            raise ValueError(
                f"Trade not found: {trade_id}"
            )

        if trade.status != TradeStatus.OPEN:
            raise ValueError(
                f"Trade is not OPEN: {trade_id}"
            )

        trade.current_price = price

        trade.unrealized_pnl = (
            PositionManager.calculate_unrealized_pnl(
            trade
            )
        )

        exit_reason = (
            PositionManager.check_exit_condition(
                trade
            )
        )

        if exit_reason is not None:
            return self.close_order(
                trade_id=trade.trade_id,
                price=price,
                exit_reason=exit_reason,
            )

        self.storage._flush()

        return trade
        
    
    # =====================================================
    # Close Order
    # =====================================================

    def close_order(
        self,
        trade_id: str,
        price: float,
        exit_reason: ExitReason = ExitReason.MANUAL,
    ) -> PaperTrade:
        """
        Close an existing paper trade.
        """

        trade = self.storage.get_trade(
            trade_id,
        )

        if trade is None:
            raise ValueError(
                f"Trade not found: {trade_id}"
            )

        if trade.status != TradeStatus.OPEN:
            raise ValueError(
                f"Trade is not OPEN: {trade_id}"
            )

        trade.current_price = price
        trade.exit_price = price
        trade.exit_time = datetime.now(timezone.utc)
        trade.exit_reason = exit_reason
        trade.status = TradeStatus.CLOSED

        if trade.side == TradeSide.BUY:
            trade.realized_pnl = (
                price - trade.entry_price
            ) * trade.quantity

        else:
            trade.realized_pnl = (
                trade.entry_price - price
            ) * trade.quantity

        trade.unrealized_pnl = 0.0

        self.storage._flush()
        
        self.storage.save_event(
        TradeEvent(
            trade_id=trade.trade_id,
            event="TRADE_CLOSED",
            description=(
            f"Trade closed at "
            f"₹{price:,.2f}. "
            f"Reason: {exit_reason.value}. "
            f"Realized P&L: "
            f"₹{trade.realized_pnl:,.2f}."
                ),
            )
        )

        return trade
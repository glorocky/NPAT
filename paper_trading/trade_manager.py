"""
=========================================================
NPAT Paper Trading
Trade Manager
=========================================================

Coordinates all paper trading operations.

Responsibilities:
    • Open Trades
    • Close Trades
    • Query Trades

Delegates execution to:
    • PaperBroker
    • PaperTradeStorage

=========================================================
"""
from __future__ import annotations

from paper_trading.enums import (
    TradeSide,
    TradeSource,
)

from paper_trading.models import (
    PaperTrade,
)

from paper_trading.paper_broker import (
    PaperBroker,
)

from paper_trading.storage import (
    PaperTradeStorage,
)

from paper_trading.enums import (
    TradeSide,
    TradeSource,
    ExitReason,
)

# =========================================================
# Trade Manager
# =========================================================

class TradeManager:
    """
    Coordinates paper trading operations.
    """

    def __init__(
        self,
        broker: PaperBroker,
        storage: PaperTradeStorage,
    ):

        self.broker = broker
        self.storage = storage
    # =====================================================
    # Open Trade
    # =====================================================

    def open_trade(
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
        Open a new paper trade.
        """

        return self.broker.place_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            stop_loss=stop_loss,
            target=target,
            source=source,
        )
        
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
        """

        return self.broker.update_market_price(
            trade_id=trade_id,
            price=price,
        )
    
    # =====================================================
    # Get Trade
    # =====================================================

    def get_trade(
        self,
        trade_id: str,
    ) -> PaperTrade | None:
        """
        Return one trade.
        """

        return self.storage.get_trade(
            trade_id,
        )
    # =====================================================
    # Open Trades
    # =====================================================

    def get_open_trades(
        self,
    ) -> list[PaperTrade]:
        """
        Return all open trades.
        """

        return self.storage.get_open_trades()
    
    # =====================================================
    # Close Trade
    # =====================================================

    def close_trade(
        self,
        trade_id: str,
        price: float,
        exit_reason: ExitReason = ExitReason.MANUAL,
    ) -> PaperTrade:
        """
        Close an existing paper trade.
        """

        return self.broker.close_order(
            trade_id=trade_id,
            price=price,
            exit_reason=exit_reason,
        )
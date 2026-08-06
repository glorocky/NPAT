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
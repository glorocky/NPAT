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

from paper_trading.enums import (
    TradeSide,
    TradeSource,
    TradeStatus,
)

from paper_trading.models import (
    PaperTrade,
)

from paper_trading.storage import (
    PaperTradeStorage,
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
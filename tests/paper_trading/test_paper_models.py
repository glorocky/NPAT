from paper_trading.models import PaperTrade
from datetime import datetime, timezone
from paper_trading.enums import (
    TradeSide,
    TradeStatus,
)

from paper_trading.models import (
    PaperTrade,
    Position,
    TradeEvent,
    TradeResult,
    TradeStatistics,
)
from paper_trading.enums import PositionState

from paper_trading.enums import (
    ExitReason,
    PositionState,
    TradeSide,
    TradeStatus,
)


def test_default_trade():

    trade = PaperTrade()

    assert trade.status == TradeStatus.PENDING
    assert trade.side == TradeSide.BUY
    assert trade.quantity == 0


def test_trade_symbol():

    trade = PaperTrade(
        symbol="NIFTY",
        quantity=50,
    )

    assert trade.symbol == "NIFTY"
    assert trade.quantity == 50


def test_trade_id_created():

    trade = PaperTrade()

    assert trade.trade_id != ""
    

def test_position_defaults():

    position = Position(
        trade_id="1",
        symbol="NIFTY",
        quantity=50,
        average_price=25000,
        current_price=25000,
        market_value=1250000,
        unrealized_pnl=0,
    )

    assert position.state == PositionState.FLAT
    
    
def test_trade_event():

    event = TradeEvent(
        trade_id="1",
        event="TRADE_OPENED",
    )

    assert event.event == "TRADE_OPENED"
    
def test_trade_result():

    result = TradeResult(
        trade_id="1",
        symbol="NIFTY",
        entry_price=25000,
        exit_price=25100,
        quantity=50,
        gross_pnl=5000,
        net_pnl=4950,
        return_pct=0.40,
        duration_minutes=18,
        exit_reason=ExitReason.TARGET,
        won=True,
    )

    assert result.won is True
    assert result.net_pnl == 4950
    
def test_trade_statistics_defaults():

    stats = TradeStatistics()

    assert stats.total_trades == 0
    assert stats.net_profit == 0
    assert stats.win_rate == 0.0
    

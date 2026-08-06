from paper_trading.enums import (
    PositionState,
    TradeSide,
)

from paper_trading.models import (
    PaperTrade,
)

from paper_trading.position_manager import (
    PositionManager,
)


def test_market_value():

    value = PositionManager.calculate_market_value(
        quantity=50,
        current_price=25000,
    )

    assert value == 1250000


def test_unrealized_pnl():

    trade = PaperTrade(
        side=TradeSide.BUY,
        quantity=50,
        entry_price=25000,
        current_price=25100,
    )

    pnl = PositionManager.calculate_unrealized_pnl(
        trade
    )

    assert pnl == 5000


def test_position_creation():

    trade = PaperTrade(
        symbol="NIFTY",
        side=TradeSide.BUY,
        quantity=50,
        entry_price=25000,
        current_price=25100,
    )

    position = PositionManager.calculate_position(
        trade
    )

    assert position.state == PositionState.LONG

    assert position.market_value == 1255000

    assert position.unrealized_pnl == 5000
from paper_trading.enums import (
    TradeSide,
    TradeStatus,
    ExitReason,
    OrderType,
    TradeSource,
    PositionState,
    RiskStatus,
    AIRecommendation,
)


def test_trade_side():

    assert TradeSide.BUY.value == "BUY"
    assert TradeSide.SELL.value == "SELL"


def test_trade_status():

    assert TradeStatus.OPEN.value == "OPEN"
    assert TradeStatus.CLOSED.value == "CLOSED"
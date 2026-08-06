from paper_trading.models import (
    PaperTrade,
)

from paper_trading.performance import (
    PerformanceEngine,
)

def test_total_trades():

    trades = [
        PaperTrade(),
        PaperTrade(),
        PaperTrade(),
    ]

    assert (
        PerformanceEngine.calculate_total_trades(
            trades
        )
        == 3
    )
    
def test_winning_trades():

    trades = [
        PaperTrade(realized_pnl=100),
        PaperTrade(realized_pnl=-50),
        PaperTrade(realized_pnl=25),
    ]

    assert (
        PerformanceEngine.calculate_winning_trades(
            trades
        )
        == 2
    )
def test_losing_trades():

    trades = [
        PaperTrade(realized_pnl=100),
        PaperTrade(realized_pnl=-50),
        PaperTrade(realized_pnl=-20),
    ]

    assert (
        PerformanceEngine.calculate_losing_trades(
            trades
        )
        == 2
    )

def test_win_rate():

    trades = [
        PaperTrade(realized_pnl=100),
        PaperTrade(realized_pnl=-50),
    ]

    assert (
        PerformanceEngine.calculate_win_rate(
            trades
        )
        == 50.0
    )
def test_statistics():

    trades = [
        PaperTrade(realized_pnl=100),
        PaperTrade(realized_pnl=-50),
    ]

    stats = (
        PerformanceEngine.calculate_statistics(
            trades
        )
    )

    assert stats.total_trades == 2

    assert stats.winning_trades == 1

    assert stats.losing_trades == 1
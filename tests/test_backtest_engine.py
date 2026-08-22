from types import SimpleNamespace
from backtesting.engine import BacktestEngine


def test_backtest_basic_round_trip():
    candles = [SimpleNamespace(close=x) for x in [100, 102, 105, 103]]
    result = BacktestEngine.run(candles, lambda c: "BUY" if c.close == 100 else ("EXIT" if c.close == 105 else "HOLD"))
    assert result.net_pnl == 5
    assert result.win_rate == 100

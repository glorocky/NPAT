from types import SimpleNamespace
from strategies.trade_planner import TradePlanner


def option(strike, put=10, call=10):
    return SimpleNamespace(strike_price=strike, put_ltp=put, call_ltp=call,
                           put_trading_symbol=f"P{strike}", call_trading_symbol=f"C{strike}", expiry="2026-08-27")


def test_bull_future_gets_protective_put():
    f = SimpleNamespace(symbol="NIFTY", trading_symbol="NIFTY-FUT", futures_price=25000,
                        spot_price=24980, price_change_pct=1.0, positioning="LONG_BUILDUP")
    plan = TradePlanner.build_future_plan(f, [option(24900), option(25000), option(25100)])
    assert plan.action == "BUY FUTURE"
    assert plan.hedge is not None
    assert plan.hedge.option_type == "PE"


def test_bear_future_gets_protective_call():
    f = SimpleNamespace(symbol="NIFTY", trading_symbol="NIFTY-FUT", futures_price=25000,
                        spot_price=25000, price_change_pct=-1.0, positioning="SHORT_BUILDUP")
    plan = TradePlanner.build_future_plan(f, [option(24900), option(25000), option(25100)])
    assert plan.action == "SELL FUTURE"
    assert plan.hedge is not None
    assert plan.hedge.option_type == "CE"

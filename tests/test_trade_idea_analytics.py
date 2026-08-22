from core.models import Quote, FuturesAnalysis
from analytics.trade_idea_analytics import TradeIdeaAnalytics


def test_stock_positive_momentum_can_generate_buy():
    quote = Quote(
        symbol="RELIANCE", exchange="NSE", last_price=1020,
        open=1000, high=1025, low=995, previous_close=1000,
    )
    score, signal, reasons = TradeIdeaAnalytics.stock_score(quote, 40)
    assert score > 0
    assert signal in {"BUY", "STRONG_BUY"}
    assert reasons


def test_stock_negative_momentum_can_generate_sell():
    quote = Quote(
        symbol="RELIANCE", exchange="NSE", last_price=980,
        open=1000, high=1005, low=975, previous_close=1000,
    )
    score, signal, _ = TradeIdeaAnalytics.stock_score(quote, -40)
    assert score < 0
    assert signal in {"SELL", "STRONG_SELL"}


def test_future_positioning_influences_direction():
    future = FuturesAnalysis(
        symbol="NIFTY", exchange="NSE", trading_symbol="NIFTY-FUT", expiry="2026-09-29",
        spot_price=100, futures_price=102, basis=2, basis_pct=2,
        previous_price=100, price_change=2, price_change_pct=2,
        previous_oi=1000, current_oi=1100, oi_change=100, oi_change_pct=10,
        positioning="LONG_BUILDUP", volume=10000,
        total_buy_quantity=6000, total_sell_quantity=4000,
        quantity_imbalance=2000, quantity_imbalance_pct=20,
        lot_size=65,
    )
    score, signal, _ = TradeIdeaAnalytics.future_score(future, 20)
    assert score > 20
    assert signal in {"BUY", "STRONG_BUY"}

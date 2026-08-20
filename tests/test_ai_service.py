"""Contract tests for the current AI service output."""

from types import SimpleNamespace

from core.models import (
    ForwardPremiumAnalysis, FuturesAnalysis, GreeksSummary, MarketRegimeAnalysis,
    MarketSnapshot, OptionData,
)
from services.ai_service import AIService


def _dashboard():
    regime = MarketRegimeAnalysis(
        regime="STRONG_BULLISH", regime_score=66.8712, futures_score=80.0,
        breadth_score=70.0759, sector_score=66.1613, volatility_score=20.0,
        bullish_sectors=14, bearish_sectors=0, neutral_sectors=1,
        strongest_sector="Consumer Services", weakest_sector="Oil Gas", confidence=93.0806,
        reasons=("futures", "breadth", "sector", "volatility"),
    )
    option = OptionData(
        strike_price=24000, expiry="2026-08-25", underlying_price=24000.0,
        call_ltp=104.0, call_iv=17.0, call_volume=1_000, call_oi=1_000,
        put_ltp=102.0, put_iv=16.0, put_volume=1_000, put_oi=1_000,
    )
    market = MarketSnapshot(
        symbol="NIFTY", exchange="NSE", expiry="2026-08-25", spot_price=24000.0,
        atm_strike=24000, option_chain=[option],
    )
    futures = FuturesAnalysis(
        symbol="NIFTY", exchange="NSE", trading_symbol="NIFTY26AUGFUT", expiry="2026-08-25",
        spot_price=24000.0, futures_price=24030.0, basis=30.0, basis_pct=0.125,
        previous_price=23950.0, price_change=80.0, price_change_pct=0.334,
        previous_oi=100000, current_oi=110000, oi_change=10000, oi_change_pct=10.0,
        positioning="LONG_BUILDUP", volume=500000, total_buy_quantity=600000,
        total_sell_quantity=400000, quantity_imbalance=200000, quantity_imbalance_pct=20.0,
        lot_size=65,
    )
    greeks = GreeksSummary(
        symbol="NIFTY", expiry="2026-08-25", spot_price=24000.0, atm_strike=24000,
        atm_call_delta=0.60, atm_put_delta=-0.40, delta_balance=0.20,
        atm_call_iv=17.0, atm_put_iv=16.0, iv_skew=-1.0, highest_gamma_strike=24000,
        highest_gamma=0.015, total_call_theta=-20.0, total_put_theta=-20.0,
        total_theta=-40.0, total_call_vega=2.5, total_put_vega=2.5, total_vega=5.0,
    )
    premiums = [
        ForwardPremiumAnalysis("NIFTY", "2026-08-25", 24000, "CE", 24000.0, 24010.0,
            104.0, 100.0, 100.0, 4.0, 4.0, 4.0, 4.0, 17.0, 0.01, "ATM"),
        ForwardPremiumAnalysis("NIFTY", "2026-08-25", 24000, "PE", 24000.0, 24010.0,
            102.0, 100.0, 100.0, 2.0, 2.0, 2.0, 2.0, 16.0, 0.01, "ATM"),
    ]
    return SimpleNamespace(market=market, market_regime=regime, futures=futures,
                           greeks_summary=greeks, premium_analysis=premiums)


def test_ai_service_returns_consistent_contract_recommendation():
    analysis = AIService().analyze(_dashboard())

    assert analysis.signal == "STRONG_BUY"
    assert analysis.prediction is not None
    assert analysis.recommendation is not None
    assert analysis.recommendation.action == "BUY CALL"
    assert analysis.recommendation.option_type == "CE"
    assert analysis.recommendation.strike_price == 24000
    assert analysis.recommendation.entry_price == 104.0
    assert analysis.trade_action == "BUY_CE"
    assert analysis.option_type == "CE"
    assert len(analysis.reasons) == len(analysis.decision.reasons) + 2

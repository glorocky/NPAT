from types import SimpleNamespace

from core.models import (
    AIAnalysis,
    DecisionAnalysis,
    ForwardPremiumAnalysis,
    FuturesAnalysis,
    GreeksSummary,
    MarketRegimeAnalysis,
    PredictionAnalysis,
)

from services.ai_service import AIService


# =====================================================
# Controlled Market Regime
# =====================================================

regime = MarketRegimeAnalysis(
    regime="STRONG_BULLISH",
    regime_score=66.8712,

    futures_score=80.0,
    breadth_score=70.0759,
    sector_score=66.1613,
    volatility_score=20.0,

    bullish_sectors=14,
    bearish_sectors=0,
    neutral_sectors=1,

    strongest_sector="Consumer Services",
    weakest_sector="Oil Gas & Consumable Fuels",

    confidence=93.0806,

    reasons=(
        "Controlled futures reason.",
        "Controlled breadth reason.",
        "Controlled sector reason.",
        "Controlled volatility reason.",
    ),
)

# =====================================================
# Controlled Futures
# =====================================================

futures = FuturesAnalysis(
    symbol="NIFTY",
    exchange="NSE",
    trading_symbol="NIFTY26AUGFUT",
    expiry="2026-08-25",

    spot_price=24000.0,
    futures_price=24030.0,

    basis=30.0,
    basis_pct=0.125,

    previous_price=23950.0,
    price_change=80.0,
    price_change_pct=0.334,

    previous_oi=100000,
    current_oi=110000,
    oi_change=10000,
    oi_change_pct=10.0,

    positioning="LONG_BUILDUP",

    volume=500000,

    total_buy_quantity=600000,
    total_sell_quantity=400000,

    quantity_imbalance=200000,
    quantity_imbalance_pct=20.0,

    lot_size=65,
)


# =====================================================
# Controlled Greeks
# =====================================================

greeks = GreeksSummary(
    symbol="NIFTY",
    expiry="2026-08-25",

    spot_price=24000.0,
    atm_strike=24000,

    atm_call_delta=0.60,
    atm_put_delta=-0.40,
    delta_balance=0.20,

    atm_call_iv=17.0,
    atm_put_iv=16.0,
    iv_skew=-1.0,

    highest_gamma_strike=24000,
    highest_gamma=0.015,

    total_call_theta=-20.0,
    total_put_theta=-20.0,
    total_theta=-40.0,

    total_call_vega=2.5,
    total_put_vega=2.5,
    total_vega=5.0,
)


# =====================================================
# Controlled Premiums
# =====================================================

premiums = [
    ForwardPremiumAnalysis(
        symbol="NIFTY",
        expiry="2026-08-25",
        strike_price=24000,
        option_type="CE",

        spot_price=24000.0,
        implied_forward=24010.0,

        market_premium=104.0,

        spot_bs_premium=100.0,
        forward_bs_premium=100.0,

        spot_difference=4.0,
        spot_difference_pct=4.0,

        forward_difference=4.0,
        forward_difference_pct=4.0,

        iv=17.0,
        time_to_expiry=0.01,

        moneyness="ATM",
    ),

    ForwardPremiumAnalysis(
        symbol="NIFTY",
        expiry="2026-08-25",
        strike_price=24000,
        option_type="PE",

        spot_price=24000.0,
        implied_forward=24010.0,

        market_premium=102.0,

        spot_bs_premium=100.0,
        forward_bs_premium=100.0,

        spot_difference=2.0,
        spot_difference_pct=2.0,

        forward_difference=2.0,
        forward_difference_pct=2.0,

        iv=16.0,
        time_to_expiry=0.01,

        moneyness="ATM",
    ),
]

# =====================================================
# Controlled Dashboard
# =====================================================

dashboard = SimpleNamespace(
    market_regime=regime,
    futures=futures,
    greeks_summary=greeks,
    premium_analysis=premiums,
)

# =====================================================
# AI Service
# =====================================================

service = AIService()

analysis = service.analyze(
    dashboard=dashboard,
)


# =====================================================
# Validate AI Analysis
# =====================================================

assert isinstance(
    analysis,
    AIAnalysis,
)

assert isinstance(
    analysis.decision,
    DecisionAnalysis,
)

assert analysis.signal == "STRONG_BUY"

assert analysis.score == 66.8712
assert analysis.confidence == 93.0806

assert analysis.decision.signal == analysis.signal
assert analysis.decision.score == analysis.score
assert analysis.decision.confidence == analysis.confidence

assert analysis.reasons == analysis.decision.reasons
assert len(analysis.reasons) == 3

# =====================================================
# Validate Prediction Analysis
# =====================================================

assert analysis.prediction is not None

assert isinstance(
    analysis.prediction,
    PredictionAnalysis,
)

assert analysis.prediction.direction == "STRONG_BULLISH"

assert analysis.prediction.score == 60.4049
assert analysis.prediction.confidence == 84.162

assert analysis.prediction.regime_score == 66.8712
assert analysis.prediction.futures_score == 100.0
assert analysis.prediction.greeks_score == 20.0
assert analysis.prediction.premium_score == 20.0

assert analysis.prediction.bullish_evidence == 4
assert analysis.prediction.bearish_evidence == 0
assert analysis.prediction.neutral_evidence == 0

assert len(
    analysis.prediction.reasons
) == 5


# =====================================================
# Output
# =====================================================

print("Signal       :", analysis.signal)
print("Score        :", analysis.score)
print("Confidence   :", analysis.confidence)

print()

print("Decision     :", analysis.decision.signal)
print(
    "Regime       :",
    analysis.decision.market_regime,
)

print()

print("Reasons")

for reason in analysis.reasons:
    print("-", reason)
    
print(
    "\n========== PREDICTION ==========\n"
)

print(
    "Direction    :",
    analysis.prediction.direction,
)

print(
    "Score        :",
    analysis.prediction.score,
)

print(
    "Confidence   :",
    analysis.prediction.confidence,
)

print()

print(
    "Regime       :",
    analysis.prediction.regime_score,
)

print(
    "Futures      :",
    analysis.prediction.futures_score,
)

print(
    "Greeks       :",
    analysis.prediction.greeks_score,
)

print(
    "Premium      :",
    analysis.prediction.premium_score,
)

print()

print(
    "Bullish      :",
    analysis.prediction.bullish_evidence,
)

print(
    "Bearish      :",
    analysis.prediction.bearish_evidence,
)

print(
    "Neutral      :",
    analysis.prediction.neutral_evidence,
)


print(
    "\nAIService controlled analysis test passed."
)
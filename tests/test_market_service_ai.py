
from datetime import date
import pyotp

from config import GROWW
from growwapi.groww.client import GrowwAPI

from providers.groww_provider import GrowwProvider

from services.ai_service import AIService
from services.market_service import MarketService


# =====================================================
# Test Configuration
# =====================================================

SYMBOL = "NIFTY"
EXCHANGE = "NSE"

# =====================================================
# Authentication
# =====================================================

totp = pyotp.TOTP(
    GROWW.totp_secret
).now()

access_token = GrowwAPI.get_access_token(
    api_key=GROWW.api_key,
    totp=totp,
)

provider = GrowwProvider(
    access_token=access_token,
)

# =====================================================
# Resolve Live Expiry
# =====================================================

expiries = provider.get_expiries(
    exchange=EXCHANGE,
    underlying_symbol=SYMBOL,
)

today = date.today().isoformat()

valid_expiries = sorted(
    expiry
    for expiry in expiries
    if expiry >= today
)

if not valid_expiries:
    raise RuntimeError(
        "Groww returned no active NIFTY expiries."
    )

EXPIRY = valid_expiries[0]

print(
    "Selected Expiry   :",
    EXPIRY,
)

ai_service = AIService()

service = MarketService(
    provider=provider,
    ai_service=ai_service,
)



# =====================================================
# MarketService AI Integration
# =====================================================

print(
    "\n========== NPAT MARKET SERVICE AI ==========\n"
)

snapshot = service.get_dashboard_snapshot(
    symbol=SYMBOL,
    expiry=EXPIRY,
    exchange=EXCHANGE,
)


# =====================================================
# Validate Prerequisites
# =====================================================

assert snapshot.market_regime is not None

# =====================================================
# Validate AI Result
# =====================================================

assert snapshot.ai is not None

assert snapshot.ai.signal is not None

assert snapshot.ai.signal in {
    "STRONG_BUY",
    "BUY",
    "NEUTRAL",
    "SELL",
    "STRONG_SELL",
}

assert snapshot.ai.confidence is not None

assert (
    0.0
    <= snapshot.ai.confidence
    <= 100.0
)

assert snapshot.ai.reasons

assert len(snapshot.ai.reasons) >= 1






# =====================================================
# Validate Decision / Regime Consistency
# =====================================================

expected_signal = (
    ai_service.decision_engine.classify_signal(
        score=snapshot.market_regime.regime_score,
    )
)

assert (
    
    snapshot.ai.signal
    ==
    expected_signal
    
)

assert (
    snapshot.ai.confidence
    ==
    snapshot.market_regime.confidence
)


# =====================================================
# Validate Prediction Result
# =====================================================

assert snapshot.ai.prediction is not None

prediction = snapshot.ai.prediction

assert prediction.direction in {
    "STRONG_BULLISH",
    "BULLISH",
    "NEUTRAL",
    "BEARISH",
    "STRONG_BEARISH",
}

assert (
    -100.0
    <= prediction.score
    <= 100.0
)

assert (
    0.0
    <= prediction.confidence
    <= 100.0
)

assert (
    -100.0
    <= prediction.regime_score
    <= 100.0
)

assert (
    -100.0
    <= prediction.futures_score
    <= 100.0
)

assert (
    -100.0
    <= prediction.greeks_score
    <= 100.0
)

assert (
    -100.0
    <= prediction.premium_score
    <= 100.0
)

assert prediction.bullish_evidence >= 0
assert prediction.bearish_evidence >= 0
assert prediction.neutral_evidence >= 0

assert (
    prediction.bullish_evidence
    + prediction.bearish_evidence
    + prediction.neutral_evidence
    == 4
)

assert prediction.reasons


# =====================================================
# Output
# =====================================================

print(
    "Market Regime      :",
    snapshot.market_regime.regime,
)

print(
    "Market Regime Score:",
    snapshot.market_regime.regime_score,
)

print()

print(
    "AI Signal          :",
    snapshot.ai.signal,
)

print(
    "AI Confidence      :",
    snapshot.ai.confidence,
)

print()

print("AI Reasons")

print("-" * 70)

for reason in snapshot.ai.reasons:
    print("-", reason)

print()

print(
    "========== LIVE PREDICTION =========="
)

print()

print(
    "Direction          :",
    prediction.direction,
)

print(
    "Prediction Score   :",
    prediction.score,
)

print(
    "Confidence         :",
    prediction.confidence,
)

print()

print(
    "Regime Score       :",
    prediction.regime_score,
)

print(
    "Futures Score      :",
    prediction.futures_score,
)

print(
    "Greeks Score       :",
    prediction.greeks_score,
)

print(
    "Premium Score      :",
    prediction.premium_score,
)

print()

print(
    "Bullish Evidence   :",
    prediction.bullish_evidence,
)

print(
    "Bearish Evidence   :",
    prediction.bearish_evidence,
)

print(
    "Neutral Evidence   :",
    prediction.neutral_evidence,
)

print()

print("Prediction Reasons")

print("-" * 70)

for reason in prediction.reasons:
    print("-", reason)
    
print()

print(
    "========== LIVE GREEKS SUMMARY =========="
)

print()

greeks_summary = snapshot.greeks_summary

assert greeks_summary is not None

print(
    "ATM Strike         :",
    greeks_summary.atm_strike,
)

print(
    "ATM Call Delta     :",
    greeks_summary.atm_call_delta,
)

print(
    "ATM Put Delta      :",
    greeks_summary.atm_put_delta,
)

print(
    "Delta Balance      :",
    greeks_summary.delta_balance,
)

print()

print(
    "ATM Call IV        :",
    greeks_summary.atm_call_iv,
)

print(
    "ATM Put IV         :",
    greeks_summary.atm_put_iv,
)

print(
    "IV Skew            :",
    greeks_summary.iv_skew,
)

print()

print(
    "Highest Gamma Strike:",
    greeks_summary.highest_gamma_strike,
)

print(
    "Highest Gamma      :",
    greeks_summary.highest_gamma,
)

print()

print(
    "Total Theta        :",
    greeks_summary.total_theta,
)

print(
    "Total Vega         :",
    greeks_summary.total_vega,
)


# =====================================================
# Live ATM Option Data
# =====================================================

atm_option = next(
    option
    for option in snapshot.market.option_chain
    if option.strike_price
    == snapshot.greeks_summary.atm_strike
)

print()

print(
    "========== LIVE ATM OPTION =========="
)

print()

print(
    "Underlying Price   :",
    atm_option.underlying_price,
)

print(
    "ATM Strike         :",
    atm_option.strike_price,
)

print()

print(
    "Call LTP           :",
    atm_option.call_ltp,
)

print(
    "Put LTP            :",
    atm_option.put_ltp,
)

print()

print(
    "OptionData Call IV :",
    atm_option.call_iv,
)

print(
    "OptionData Put IV  :",
    atm_option.put_iv,
)

print()

print(
    "Call OI            :",
    atm_option.call_oi,
)

print(
    "Put OI             :",
    atm_option.put_oi,
)

print(
    "Call Volume        :",
    atm_option.call_volume,
)

print(
    "Put Volume         :",
    atm_option.put_volume,
)

# =====================================================
# Live ATM Premium Analysis
# =====================================================

atm_premiums = [
    premium
    for premium in snapshot.premium_analysis
    if premium.moneyness == "ATM"
]

assert len(atm_premiums) == 2

atm_call_premium = next(
    premium
    for premium in atm_premiums
    if premium.option_type == "CE"
)

atm_put_premium = next(
    premium
    for premium in atm_premiums
    if premium.option_type == "PE"
)

print()

print(
    "========== LIVE ATM PREMIUM =========="
)

print()

print(
    "ATM Strike         :",
    atm_call_premium.strike_price,
)

print()

print(
    "Call Market Price  :",
    atm_call_premium.market_premium,
)

print(
    "Call Theo Price    :",
    atm_call_premium.forward_bs_premium,
)

print(
    "Call Difference %  :",
    atm_call_premium.forward_difference_pct,
)

print()

print(
    "Put Market Price   :",
    atm_put_premium.market_premium,
)

print(
    "Put Theo Price     :",
    atm_put_premium.forward_bs_premium,
)

print(
    "Put Difference %   :",
    atm_put_premium.forward_difference_pct,
)

relative_richness = (
    atm_call_premium.forward_difference_pct
    - atm_put_premium.forward_difference_pct
)

print()

print(
    "Relative Richness  :",
    relative_richness,
)

print(
    "Premium Score      :",
    snapshot.ai.prediction.premium_score,
)

print(
    "\nMarketService AI integration test passed."
)
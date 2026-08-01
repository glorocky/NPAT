import pyotp

from config import GROWW
from growwapi.groww.client import GrowwAPI
from providers.groww_provider import GrowwProvider
from services.market_service import MarketService
from core.models import VixRangeAnalysis
from analytics.market_regime_analytics import (
    MarketRegimeAnalytics,
)

# =====================================================
# Test Configuration
# =====================================================


SYMBOL = "NIFTY"
EXCHANGE = "NSE"
EXPIRY = "2026-07-28"


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
    access_token=access_token
)

service = MarketService(
    provider=provider
)

# =====================================================
# MarketService VIX Integration
# =====================================================

print(
    "\n========== NPAT MARKET SERVICE VIX ==========\n"
)

snapshot = service.get_dashboard_snapshot(
    symbol=SYMBOL,
    expiry=EXPIRY,
    exchange=EXCHANGE,
)


# =====================================================
# Extract Results
# =====================================================

market = snapshot.market
analysis = snapshot.vix_analysis
volatility_score = (
    MarketRegimeAnalytics.score_volatility(
        vix=analysis,
    )
)


# =====================================================
# Validate Market Snapshot
# =====================================================

assert market is not None

assert market.spot_price > 0
assert market.atm_strike > 0
assert len(market.option_chain) > 0


# =====================================================
# Validate Raw India VIX
# =====================================================

assert snapshot.india_vix is not None

assert snapshot.india_vix > 0


# =====================================================
# Validate VIX Analysis
# =====================================================

assert analysis is not None

assert isinstance(
    analysis,
    VixRangeAnalysis,
)

assert analysis.symbol == SYMBOL

assert analysis.reference_price > 0
assert analysis.india_vix > 0

assert analysis.day_open > 0
assert analysis.day_high > 0
assert analysis.day_low > 0
assert analysis.current_price > 0


# =====================================================
# Validate Expected Range
# =====================================================

assert analysis.expected_move_pct >= 0

assert analysis.expected_move_points >= 0

assert analysis.expected_lower > 0

assert (
    analysis.expected_upper
    >
    analysis.expected_lower
)


# =====================================================
# Validate Market OHLC
# =====================================================

assert (
    analysis.day_high
    >=
    analysis.day_low
)

assert (
    analysis.day_high
    >=
    analysis.day_open
)

assert (
    analysis.day_high
    >=
    analysis.current_price
)

assert (
    analysis.day_low
    <=
    analysis.day_open
)

assert (
    analysis.day_low
    <=
    analysis.current_price
)

# =====================================================
# Validate Market Regime Volatility Score
# =====================================================

assert -100.0 <= volatility_score <= 100.0

# =====================================================
# Output
# =====================================================

print("Symbol              :", analysis.symbol)

print()

print("India VIX           :", snapshot.india_vix)
print("Reference Price     :", analysis.reference_price)
print("Current Price       :", analysis.current_price)

print()

print("Day Open            :", analysis.day_open)
print("Day High            :", analysis.day_high)
print("Day Low             :", analysis.day_low)

print()

print("Expected Move %     :", analysis.expected_move_pct)
print("Expected Move Pts   :", analysis.expected_move_points)

print()

print("Expected Lower      :", analysis.expected_lower)
print("Expected Upper      :", analysis.expected_upper)


# =====================================================
# Optional Range Metrics
# =====================================================

if hasattr(
    analysis,
    "actual_range_points",
):

    print(
        "Actual Range Pts    :",
        analysis.actual_range_points,
    )


if hasattr(
    analysis,
    "range_utilization_pct",
):

    print(
        "Range Utilization % :",
        analysis.range_utilization_pct,
    )

# =====================================================
# Final Result
# =====================================================

print()
print("India VIX              :", analysis.india_vix)
print(
    "Expected Range Exceeded:",
    analysis.expected_range_exceeded,
)
print(
    "Regime Volatility Score:",
    volatility_score,
)
print(
    "\nMarketService VIX integration test passed."
)
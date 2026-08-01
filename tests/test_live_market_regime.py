import pyotp

from config import GROWW
from growwapi.groww.client import GrowwAPI

from providers.groww_provider import GrowwProvider

from services.market_service import MarketService

from analytics.market_regime_analytics import (
    MarketRegimeAnalytics,
)

from core.models import MarketRegimeAnalysis


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

service = MarketService(
    provider=provider,
)


# =====================================================
# Dashboard Snapshot
# =====================================================

print(
    "\n========== NPAT LIVE MARKET REGIME ==========\n"
)

snapshot = service.get_dashboard_snapshot(
    symbol=SYMBOL,
    exchange=EXCHANGE,
)


# =====================================================
# Validate Required Inputs
# =====================================================

assert snapshot.futures is not None
assert snapshot.heatmap_summary is not None
assert snapshot.vix_analysis is not None

assert len(snapshot.sector_strength) > 0

# =====================================================
# Debug Component Scores
# =====================================================

debug_futures_score = (
    MarketRegimeAnalytics.score_futures(
        futures=snapshot.futures,
    )
)

debug_breadth_score = (
    MarketRegimeAnalytics.score_breadth(
        summary=snapshot.heatmap_summary,
    )
)

debug_sector_score = (
    MarketRegimeAnalytics.score_sectors(
        sectors=snapshot.sector_strength,
    )
)

debug_volatility_score = (
    MarketRegimeAnalytics.score_volatility(
        vix=snapshot.vix_analysis,
    )
)

print("DEBUG Futures Score   :", debug_futures_score)
print("DEBUG Breadth Score   :", debug_breadth_score)
print("DEBUG Sector Score    :", debug_sector_score)
print("DEBUG Volatility Score:", debug_volatility_score)

print()

# =====================================================
# Market Regime
# =====================================================

regime = MarketRegimeAnalytics.analyze(
    futures=snapshot.futures,
    breadth=snapshot.heatmap_summary,
    sectors=snapshot.sector_strength,
    volatility=snapshot.vix_analysis,
)


# =====================================================
# Validate Result
# =====================================================

assert isinstance(
    regime,
    MarketRegimeAnalysis,
)

assert regime.regime in {
    "STRONG_BULLISH",
    "BULLISH",
    "NEUTRAL",
    "BEARISH",
    "STRONG_BEARISH",
}

assert -100.0 <= regime.regime_score <= 100.0

assert -100.0 <= regime.futures_score <= 100.0
assert -100.0 <= regime.breadth_score <= 100.0
assert -100.0 <= regime.sector_score <= 100.0
assert -100.0 <= regime.volatility_score <= 100.0

assert 0.0 <= regime.confidence <= 100.0

assert (
    regime.bullish_sectors
    + regime.bearish_sectors
    + regime.neutral_sectors
) == len(snapshot.sector_strength)

assert regime.strongest_sector
assert regime.weakest_sector

assert len(regime.reasons) == 4


# =====================================================
# Output
# =====================================================

print("Regime             :", regime.regime)
print("Regime Score       :", regime.regime_score)
print("Confidence         :", regime.confidence)

print()

print("Futures Score      :", regime.futures_score)
print("Breadth Score      :", regime.breadth_score)
print("Sector Score       :", regime.sector_score)
print("Volatility Score   :", regime.volatility_score)

print()

print("Bullish Sectors    :", regime.bullish_sectors)
print("Bearish Sectors    :", regime.bearish_sectors)
print("Neutral Sectors    :", regime.neutral_sectors)

print()

print("Strongest Sector   :", regime.strongest_sector)
print("Weakest Sector     :", regime.weakest_sector)

print(
    "\nReasons"
)

print("-" * 70)

for reason in regime.reasons:
    print("-", reason)

print(
    "\nLive MarketRegimeAnalytics "
    "integration test passed."
)
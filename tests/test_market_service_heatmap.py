import pyotp

from config import GROWW
from core.models import (
        HeatmapStock, 
        HeatmapSummary,
        MarketRegimeAnalysis
        )

from growwapi.groww.client import GrowwAPI
from providers.groww_provider import GrowwProvider
from services.market_service import MarketService
from analytics.market_regime_analytics import (
    MarketRegimeAnalytics,
)


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
# Dashboard Snapshot
# =====================================================

print(
    "\n========== NPAT MARKET SERVICE HEATMAP ==========\n"
)

snapshot = service.get_dashboard_snapshot(
    symbol=SYMBOL,
    expiry=EXPIRY,
    exchange=EXCHANGE,
)

heatmap = snapshot.heatmap
summary = snapshot.heatmap_summary
sector_breadth = snapshot.sector_breadth
sector_strength = snapshot.sector_strength
market_regime = snapshot.market_regime
breadth_score = MarketRegimeAnalytics.score_breadth(
    summary=summary,
)
sector_score = MarketRegimeAnalytics.score_sectors(
    sectors=sector_strength,
)


# =====================================================
# Validate Heatmap
# =====================================================

assert len(heatmap) == 50

assert all(
    isinstance(stock, HeatmapStock)
    for stock in heatmap
)

symbols = {
    stock.symbol
    for stock in heatmap
}

assert len(symbols) == 50


# =====================================================
# Validate Summary
# =====================================================

assert summary is not None
assert isinstance(summary, HeatmapSummary)

assert summary.total_stocks == 50

assert (
    summary.gainers
    + summary.losers
    + summary.flat
) == 50

assert summary.strongest_symbol in symbols
assert summary.weakest_symbol in symbols

# =====================================================
# Validate Sector Breadth
# =====================================================

assert len(sector_breadth) == 15

assert sum(
    sector.total_stocks
    for sector in sector_breadth
) == 50

assert sum(
    sector.gainers
    for sector in sector_breadth
) == summary.gainers

assert sum(
    sector.losers
    for sector in sector_breadth
) == summary.losers

assert sum(
    sector.flat
    for sector in sector_breadth
) == summary.flat

for sector in sector_breadth:

    assert (
        sector.gainers
        + sector.losers
        + sector.flat
    ) == sector.total_stocks

    assert -100.0 <= sector.breadth_pct <= 100.0
    

# =====================================================
# Validate Sector Strength
# =====================================================

assert len(sector_strength) == 15

assert {
    item.sector
    for item in sector_strength
} == {
    item.sector
    for item in sector_breadth
}

assert all(
    -100.0 <= item.strength_score <= 100.0
    for item in sector_strength
)

assert all(
    item.classification
    in {
        "STRONG_BULLISH",
        "BULLISH",
        "NEUTRAL",
        "BEARISH",
        "STRONG_BEARISH",
    }
    for item in sector_strength
)

assert all(
    sector_strength[index].strength_score
    >= sector_strength[index + 1].strength_score
    for index in range(len(sector_strength) - 1)
)


# =====================================================
# Validate Market Regime Breadth Score
# =====================================================

assert -100.0 <= breadth_score <= 100.0


assert -100.0 <= sector_score <= 100.0

assert sum(
    sector.total_stocks
    for sector in sector_strength
) == 50

# =====================================================
# Validate Market Regime
# =====================================================

assert market_regime is not None

assert isinstance(
    market_regime,
    MarketRegimeAnalysis,
)

assert market_regime.regime in {
    "STRONG_BULLISH",
    "BULLISH",
    "NEUTRAL",
    "BEARISH",
    "STRONG_BEARISH",
}

assert -100.0 <= market_regime.regime_score <= 100.0
assert 0.0 <= market_regime.confidence <= 100.0

assert (
    market_regime.bullish_sectors
    + market_regime.bearish_sectors
    + market_regime.neutral_sectors
) == len(sector_strength)

assert market_regime.strongest_sector
assert market_regime.weakest_sector

assert len(market_regime.reasons) == 4

# =====================================================
# Output
# =====================================================
print("Gainers            :", summary.gainers)
print("Losers             :", summary.losers)
print("Flat               :", summary.flat)

print(
    "Advance/Decline    :",
    round(summary.advance_decline_ratio, 4),
)

print(
    "Average Change %   :",
    round(summary.average_change_pct, 4),
)

print(
    "Strongest          :",
    summary.strongest_symbol,
    round(summary.strongest_change_pct, 2),
    "%",
)

print(
    "Weakest            :",
    summary.weakest_symbol,
    round(summary.weakest_change_pct, 2),
    "%",
)

print()
print("Regime Breadth Score:", breadth_score)

print("Regime Sector Score :", sector_score)

print(
    "\n========== NPAT MARKET REGIME ==========\n"
)

print("Regime             :", market_regime.regime)
print("Regime Score       :", market_regime.regime_score)
print("Confidence         :", market_regime.confidence)

print()
print("Futures Score      :", market_regime.futures_score)
print("Breadth Score      :", market_regime.breadth_score)
print("Sector Score       :", market_regime.sector_score)
print("Volatility Score   :", market_regime.volatility_score)

print()
print("Bullish Sectors    :", market_regime.bullish_sectors)
print("Bearish Sectors    :", market_regime.bearish_sectors)
print("Neutral Sectors    :", market_regime.neutral_sectors)

print(
    "\nMarketService Heatmap integration test passed."
)
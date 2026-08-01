import pyotp

from analytics.heatmap_analytics import HeatmapAnalytics
from config import GROWW
from core.models import HeatmapStock
from data.reference.constituent_loader import ConstituentLoader
from growwapi.groww.client import GrowwAPI
from providers.groww_provider import GrowwProvider
from analytics.sector_strength_analytics import (
    SectorStrengthAnalytics,
)


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


# =====================================================
# Constituents
# =====================================================

constituents = ConstituentLoader.load_nifty50()

symbols = constituents[
    "symbol"
].tolist()

assert len(symbols) == 50


# =====================================================
# Live Batch Market Data
# =====================================================

ltp = provider.get_ltp_batch(
    symbols=symbols,
    exchange="NSE",
    segment="CASH",
)

ohlc = provider.get_ohlc_batch(
    symbols=symbols,
    exchange="NSE",
    segment="CASH",
)


# =====================================================
# Heatmap Analytics
# =====================================================

heatmap = HeatmapAnalytics.analyze_constituents(
    constituents=constituents,
    ltp=ltp,
    ohlc=ohlc,
)

summary = HeatmapAnalytics.summarize(
    heatmap=heatmap,
)

sector_breadth = (
    HeatmapAnalytics.summarize_sectors(
        heatmap=heatmap,
    )
)

sector_strength = (
    SectorStrengthAnalytics.analyze_all(
        sectors=sector_breadth,
    )
)

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

    assert sector.total_stocks > 0

    assert (
        sector.gainers
        + sector.losers
        + sector.flat
    ) == sector.total_stocks

    assert -100.0 <= sector.breadth_pct <= 100.0


# =====================================================
# Validate
# =====================================================

assert len(heatmap) == 50

assert all(
    isinstance(stock, HeatmapStock)
    for stock in heatmap
)

assert {
    stock.symbol
    for stock in heatmap
} == set(symbols)

for stock in heatmap:

    assert stock.last_price > 0
    assert stock.previous_close > 0

    assert stock.open > 0
    assert stock.high > 0
    assert stock.low > 0

    assert stock.direction in {
        "GAINER",
        "LOSER",
        "FLAT",
    }

# =====================================================
# Validate Summary
# =====================================================

assert summary.total_stocks == 50

assert (
    summary.gainers
    + summary.losers
    + summary.flat
) == 50

assert summary.strongest_symbol in symbols
assert summary.weakest_symbol in symbols

assert summary.strongest_change_pct >= (
    summary.weakest_change_pct
)

# =====================================================
# Basic Counts
# =====================================================

gainers = sum(
    stock.direction == "GAINER"
    for stock in heatmap
)

losers = sum(
    stock.direction == "LOSER"
    for stock in heatmap
)

flat = sum(
    stock.direction == "FLAT"
    for stock in heatmap
)

assert gainers + losers + flat == 50

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
# Output
# =====================================================

print(
    "\n========== NPAT LIVE NIFTY 50 HEATMAP ==========\n"
)

print("Heatmap Records :", len(heatmap))
print("Gainers         :", gainers)
print("Losers          :", losers)
print("Flat            :", flat)

print()

ranked = sorted(
    heatmap,
    key=lambda stock: stock.change_pct,
    reverse=True,
)

print("Top 5 Gainers")
print("-" * 55)

for stock in ranked[:5]:

    print(
        f"{stock.symbol:<15} "
        f"{stock.last_price:>10.2f} "
        f"{stock.change_pct:>9.2f}% "
        f"{stock.sector}"
    )

print()

print("Top 5 Losers")
print("-" * 55)

for stock in ranked[-5:][::-1]:

    print(
        f"{stock.symbol:<15} "
        f"{stock.last_price:>10.2f} "
        f"{stock.change_pct:>9.2f}% "
        f"{stock.sector}"
    )

print()


print(
    "\n========== NPAT NIFTY 50 BREADTH ==========\n"
)

print("Total Stocks       :", summary.total_stocks)
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

# =====================================================
# Sector Breadth Output
# =====================================================

print(
    "\n========== NPAT NIFTY 50 SECTOR BREADTH ==========\n"
)

print(
    f"{'Sector':<35}"
    f"{'Stocks':>7}"
    f"{'G':>5}"
    f"{'L':>5}"
    f"{'F':>5}"
    f"{'Breadth':>11}"
    f"{'Avg %':>10}"
)

print("-" * 78)

for sector in sector_breadth:

    print(
        f"{sector.sector:<35}"
        f"{sector.total_stocks:>7}"
        f"{sector.gainers:>5}"
        f"{sector.losers:>5}"
        f"{sector.flat:>5}"
        f"{sector.breadth_pct:>10.2f}%"
        f"{sector.average_change_pct:>9.2f}%"
    )

print()

print(
    "\n========== NPAT NIFTY 50 SECTOR STRENGTH ==========\n"
)

print(
    f"{'Sector':<35}"
    f"{'Breadth':>11}"
    f"{'Avg %':>10}"
    f"{'Score':>10}"
    f"{'Classification':>20}"
)

print("-" * 86)

for sector in sector_strength:

    print(
        f"{sector.sector:<35}"
        f"{sector.breadth_pct:>10.2f}%"
        f"{sector.average_change_pct:>9.2f}%"
        f"{sector.strength_score:>10.2f}"
        f"{sector.classification:>20}"
    )

print()

print(
    "Live NIFTY 50 HeatmapAnalytics "
    "integration test passed."
)
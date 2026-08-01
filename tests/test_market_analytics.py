"""
=========================================================
NPAT - Market Analytics Integration Test
=========================================================

Tests:

Groww authentication
        ↓
GrowwProvider
        ↓
OptionData[]
        ↓
MarketAnalytics
        ↓
MarketSnapshot

=========================================================
"""

import pyotp

from datetime import datetime
from config import GROWW
from core.models import (
    MarketSnapshot,
    PositioningAnalysis,
    PositioningSummary,
)
from growwapi.groww.client import GrowwAPI
from providers.groww_provider import GrowwProvider
from analytics.market_analytics import MarketAnalytics


# =====================================================
# Validate Configuration
# =====================================================

if not GROWW.api_key:
    raise RuntimeError(
        "GROWW_API_KEY is missing from .env"
    )

if not GROWW.totp_secret:
    raise RuntimeError(
        "GROWW_TOTP_SECRET is missing from .env"
    )


# =====================================================
# Generate Groww Access Token
# =====================================================

totp = pyotp.TOTP(
    GROWW.totp_secret
).now()

access_token = GrowwAPI.get_access_token(
    api_key=GROWW.api_key,
    totp=totp,
)

if not isinstance(access_token, str) or not access_token.strip():
    raise RuntimeError(
        "Groww access token generation failed."
    )


# =====================================================
# Initialize Groww Provider
# =====================================================

provider = GrowwProvider(
    access_token=access_token
)

print("GrowwProvider initialized successfully.")

# =====================================================
# Select Nearest Active Expiry
# =====================================================

expiries = provider.get_expiries(
    exchange="NSE",
    underlying_symbol="NIFTY",
)

assert expiries

today = datetime.now().date()

active_expiries = [
    expiry
    for expiry in expiries
    if datetime.strptime(
        expiry,
        "%Y-%m-%d",
    ).date() >= today
]

assert active_expiries, "No active expiries found."

EXPIRY = active_expiries[0]

print(
    "Selected Expiry:",
    EXPIRY,
)


# =====================================================
# Fetch Normalized Option Chain
# =====================================================

options = provider.get_option_chain(
    exchange="NSE",
    symbol="NIFTY",
    expiry=EXPIRY,
)

assert len(options) > 0

print(
    "Option chain received successfully:",
    len(options),
    "strikes",
)

# =====================================================
# Positioning Integration Fixture
# =====================================================

positioning = [
    PositioningAnalysis(
        symbol="NIFTY",
        expiry=EXPIRY,
        strike_price=23750,
        option_type="CE",
        previous_price=125.0,
        current_price=130.0,
        price_change=5.0,
        price_change_pct=4.0,
        previous_oi=25000,
        current_oi=27188,
        oi_change=2188,
        oi_change_pct=8.752,
        classification="LONG_BUILDUP",
    ),
    PositioningAnalysis(
        symbol="NIFTY",
        expiry="2026-07-28",
        strike_price=23750,
        option_type="PE",
        previous_price=120.0,
        current_price=115.0,
        price_change=-5.0,
        price_change_pct=-4.1667,
        previous_oi=50000,
        current_oi=59894,
        oi_change=9894,
        oi_change_pct=19.788,
        classification="SHORT_BUILDUP",
    ),
]


positioning_summary = PositioningSummary(
    total_contracts=2,

    long_buildup=1,
    short_buildup=1,
    long_unwinding=0,
    short_covering=0,
    neutral=0,

    ce_total=1,
    ce_long_buildup=1,
    ce_short_buildup=0,
    ce_long_unwinding=0,
    ce_short_covering=0,
    ce_neutral=0,

    pe_total=1,
    pe_long_buildup=0,
    pe_short_buildup=1,
    pe_long_unwinding=0,
    pe_short_covering=0,
    pe_neutral=0,
)

# =====================================================
# Build Market Snapshot
# =====================================================

snapshot = MarketAnalytics.build_market_snapshot(
    symbol="NIFTY",
    exchange="NSE",
    expiry="2026-07-28",
    options=options,

    positioning_summary=positioning_summary,
    atm_positioning_summary=positioning_summary,

    positioning=positioning,
    atm_positioning=positioning,

    top_oi_additions=positioning,
    top_oi_reductions=[],
)


# =====================================================
# Validate MarketSnapshot
# =====================================================

assert isinstance(
    snapshot,
    MarketSnapshot,
)

assert snapshot.symbol == "NIFTY"

assert snapshot.exchange == "NSE"

assert snapshot.expiry == "2026-07-28"

assert snapshot.spot_price > 0

assert snapshot.atm_strike > 0

assert snapshot.total_call_oi >= 0

assert snapshot.total_put_oi >= 0

assert snapshot.pcr >= 0

assert len(snapshot.option_chain) == len(options)

# =====================================================
# Validate Positioning Integration
# =====================================================

assert snapshot.positioning_summary is not None
assert snapshot.atm_positioning_summary is not None

assert snapshot.positioning_summary.total_contracts == 2
assert snapshot.atm_positioning_summary.total_contracts == 2

assert snapshot.positioning_summary.long_buildup == 1
assert snapshot.positioning_summary.short_buildup == 1

assert len(snapshot.positioning) == 2
assert len(snapshot.atm_positioning) == 2

assert len(snapshot.top_oi_additions) == 2
assert len(snapshot.top_oi_reductions) == 0

assert snapshot.positioning[0].classification == "LONG_BUILDUP"
assert snapshot.positioning[1].classification == "SHORT_BUILDUP"

# =====================================================
# Available Strikes
# =====================================================

available_strikes = {
    option.strike_price
    for option in options
}

# =====================================================
# Validate Option Analytics Integration
# =====================================================

assert snapshot.max_pain is not None
assert snapshot.max_pain in available_strikes

assert len(snapshot.support) == 3
assert len(snapshot.resistance) == 3

assert all(
    level.open_interest >= 0
    for level in snapshot.support
)

assert all(
    level.open_interest >= 0
    for level in snapshot.resistance
)

# =====================================================
# Verify ATM Exists in Option Chain
# =====================================================

assert snapshot.atm_strike in available_strikes

assert len(snapshot.option_chain) == len(options)

# =====================================================
# Verify PCR Calculation
# =====================================================

if snapshot.total_call_oi > 0:

    expected_pcr = (
        snapshot.total_put_oi
        / snapshot.total_call_oi
    )

    assert abs(
        snapshot.pcr - expected_pcr
    ) < 1e-12


# =====================================================
# Result
# =====================================================

print(
    "\n========== NPAT MARKET ANALYTICS ==========\n"
)

print("Symbol        :", snapshot.symbol)
print("Exchange      :", snapshot.exchange)
print("Expiry        :", snapshot.expiry)

print()

print("Spot Price    :", snapshot.spot_price)
print("ATM Strike    :", snapshot.atm_strike)

print()

print("Total Call OI :", snapshot.total_call_oi)
print("Total Put OI  :", snapshot.total_put_oi)
print("PCR           :", round(snapshot.pcr, 4))

print()

print(
    "Option Strikes:",
    len(snapshot.option_chain),
)

print(
    "\nMarketAnalytics integration test passed."
)
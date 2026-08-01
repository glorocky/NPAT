"""
=========================================================
NPAT - Premium Analytics Integration Test
=========================================================

Tests:

GrowwProvider
      ↓
OptionData[]
      ↓
MarketAnalytics
      ↓
ATM Strike
      ↓
PremiumAnalytics
      ↓
ATM ±3 strikes
      ↓
CE + PE PremiumAnalysis

=========================================================
"""
import pyotp
from datetime import datetime

from analytics.market_analytics import MarketAnalytics
from analytics.premium_analytics import PremiumAnalytics
from config import GROWW, RISK_FREE_RATE
from core.models import PremiumAnalysis
from growwapi.groww.client import GrowwAPI
from providers.groww_provider import GrowwProvider


# =====================================================
# Test Configuration
# =====================================================

SYMBOL = "NIFTY"
EXCHANGE = "NSE"


# Fixed time makes Black-Scholes results reproducible.
TEST_TIME = datetime(
    2026,
    7,
    24,
    9,
    30,
)


# =====================================================
# Validate Groww Configuration
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
# Initialize Provider
# =====================================================

provider = GrowwProvider(
    access_token=access_token
)

print(
    "GrowwProvider initialized successfully."
)

# =====================================================
# Select Nearest Active Expiry
# =====================================================

expiries = provider.get_expiries(
    exchange=EXCHANGE,
    underlying_symbol=SYMBOL,
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
    exchange=EXCHANGE,
    symbol=SYMBOL,
    expiry=EXPIRY,
)

assert len(options) > 0

print(
    "Option chain received successfully:",
    len(options),
    "strikes",
)


# =====================================================
# Build Market Snapshot
# =====================================================

snapshot = MarketAnalytics.build_market_snapshot(
    symbol=SYMBOL,
    exchange=EXCHANGE,
    expiry=EXPIRY,
    options=options,
)

assert snapshot.atm_strike > 0

print(
    "ATM strike:",
    snapshot.atm_strike,
)


# =====================================================
# Run Premium Analytics
# =====================================================

premium_analysis = (
    PremiumAnalytics.analyze_atm_window(
        symbol=SYMBOL,
        options=options,
        atm_strike=snapshot.atm_strike,
        expiry=EXPIRY,
        risk_free_rate=RISK_FREE_RATE,
        strikes_each_side=3,
        current_time=TEST_TIME,
    )
)


# =====================================================
# Basic Validation
# =====================================================

assert isinstance(
    premium_analysis,
    list,
)

assert len(premium_analysis) == 14

assert all(
    isinstance(item, PremiumAnalysis)
    for item in premium_analysis
)


# =====================================================
# Validate Strike Window
# =====================================================

analyzed_strikes = sorted(
    {
        item.strike_price
        for item in premium_analysis
    }
)

assert len(analyzed_strikes) == 7

assert snapshot.atm_strike in analyzed_strikes


# =====================================================
# Validate CE / PE Per Strike
# =====================================================

for strike in analyzed_strikes:

    contracts = [
        item
        for item in premium_analysis
        if item.strike_price == strike
    ]

    assert len(contracts) == 2

    option_types = {
        item.option_type
        for item in contracts
    }

    assert option_types == {
        "CE",
        "PE",
    }


# =====================================================
# Validate Premium Values
# =====================================================

for item in premium_analysis:

    assert item.underlying_price > 0

    assert item.market_premium >= 0

    assert item.theoretical_premium >= 0

    assert item.iv >= 0

    assert item.time_to_expiry > 0

    assert item.moneyness in {
        "ITM",
        "ATM",
        "OTM",
    }

    expected_difference = (
        item.market_premium
        - item.theoretical_premium
    )

    assert abs(
        item.premium_difference
        - expected_difference
    ) < 1e-9


# =====================================================
# Validate ATM Contracts
# =====================================================

atm_contracts = [
    item
    for item in premium_analysis
    if item.strike_price
    == snapshot.atm_strike
]

assert len(atm_contracts) == 2

assert all(
    item.moneyness == "ATM"
    for item in atm_contracts
)


# =====================================================
# Display Results
# =====================================================

print(
    "\n========== NPAT PREMIUM ANALYTICS ==========\n"
)

print("Symbol     :", SYMBOL)
print("Expiry     :", EXPIRY)
print("Spot       :", snapshot.spot_price)
print("ATM        :", snapshot.atm_strike)
print("Risk Free  :", RISK_FREE_RATE)

print(
    "Time Left  :",
    round(
        premium_analysis[0].time_to_expiry,
        6,
    ),
    "years",
)

print()

print(
    f"{'Strike':<8}"
    f"{'Type':<6}"
    f"{'Money':<7}"
    f"{'Market':>12}"
    f"{'BS Price':>12}"
    f"{'Diff':>12}"
    f"{'Diff %':>12}"
    f"{'IV %':>10}"
)

print("-" * 79)

for item in premium_analysis:

    print(
        f"{item.strike_price:<8}"
        f"{item.option_type:<6}"
        f"{item.moneyness:<7}"
        f"{item.market_premium:>12.2f}"
        f"{item.theoretical_premium:>12.2f}"
        f"{item.premium_difference:>12.2f}"
        f"{item.premium_difference_pct:>12.2f}"
        f"{item.iv:>10.2f}"
    )


# =====================================================
# Final Result
# =====================================================

print(
    "\nPremiumAnalytics integration test passed."
)
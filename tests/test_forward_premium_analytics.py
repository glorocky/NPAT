"""
=========================================================
NPAT - Forward Premium Analytics Integration Test
=========================================================

Compares:

Market Premium
      vs
Spot Black-Scholes
      vs
Forward Black-Scholes

for ATM ±3 NIFTY strikes.

=========================================================
"""

from datetime import datetime

import pyotp

from analytics.market_analytics import MarketAnalytics
from analytics.premium_analytics import PremiumAnalytics
from config import GROWW, RISK_FREE_RATE
from core.models import ForwardPremiumAnalysis
from growwapi.groww.client import GrowwAPI
from providers.groww_provider import GrowwProvider


# =====================================================
# Test Configuration
# =====================================================

SYMBOL = "NIFTY"
EXCHANGE = "NSE"
EXPIRY = "2026-07-28"

TEST_TIME = datetime(
    2026,
    7,
    24,
    9,
    30,
)


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
# Initialize Provider
# =====================================================

provider = GrowwProvider(
    access_token=access_token
)

print(
    "GrowwProvider initialized successfully."
)


# =====================================================
# Fetch Option Chain
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
# Forward Premium Analytics
# =====================================================

analysis = PremiumAnalytics.analyze_forward_premiums(
    symbol=SYMBOL,
    options=options,
    atm_strike=snapshot.atm_strike,
    expiry=EXPIRY,
    risk_free_rate=RISK_FREE_RATE,
    strikes_each_side=3,
    current_time=TEST_TIME,
)


# =====================================================
# Basic Validation
# =====================================================

assert isinstance(
    analysis,
    list,
)

assert len(analysis) == 14

assert all(
    isinstance(item, ForwardPremiumAnalysis)
    for item in analysis
)


# =====================================================
# Validate 7 Strikes
# =====================================================

strikes = sorted(
    {
        item.strike_price
        for item in analysis
    }
)

assert len(strikes) == 7

assert snapshot.atm_strike in strikes


# =====================================================
# Validate CE + PE
# =====================================================

for strike in strikes:

    contracts = [
        item
        for item in analysis
        if item.strike_price == strike
    ]

    assert len(contracts) == 2

    assert {
        item.option_type
        for item in contracts
    } == {
        "CE",
        "PE",
    }


# =====================================================
# Validate Numerical Results
# =====================================================

for item in analysis:

    assert item.spot_price > 0
    assert item.implied_forward > 0

    assert item.market_premium >= 0

    assert item.spot_bs_premium >= 0
    assert item.forward_bs_premium >= 0

    assert item.iv >= 0
    assert item.time_to_expiry > 0

    assert item.moneyness in {
        "ITM",
        "ATM",
        "OTM",
    }

    expected_spot_difference = (
        item.market_premium
        - item.spot_bs_premium
    )

    assert abs(
        item.spot_difference
        - expected_spot_difference
    ) < 1e-9

    expected_forward_difference = (
        item.market_premium
        - item.forward_bs_premium
    )

    assert abs(
        item.forward_difference
        - expected_forward_difference
    ) < 1e-9


# =====================================================
# Average Absolute Percentage Deviations
# =====================================================

spot_abs_pct = [
    abs(item.spot_difference_pct)
    for item in analysis
]

forward_abs_pct = [
    abs(item.forward_difference_pct)
    for item in analysis
]

average_spot_deviation = (
    sum(spot_abs_pct)
    / len(spot_abs_pct)
)

average_forward_deviation = (
    sum(forward_abs_pct)
    / len(forward_abs_pct)
)


# =====================================================
# Implied Forward Statistics
# =====================================================

forwards = [
    item.implied_forward
    for item in analysis
]

average_forward = (
    sum(forwards)
    / len(forwards)
)

minimum_forward = min(
    forwards
)

maximum_forward = max(
    forwards
)

forward_spread = (
    maximum_forward
    - minimum_forward
)


# =====================================================
# Display Results
# =====================================================

print(
    "\n========== NPAT FORWARD PREMIUM ANALYTICS ==========\n"
)

print("Symbol       :", SYMBOL)
print("Expiry       :", EXPIRY)
print("Spot         :", snapshot.spot_price)
print("ATM          :", snapshot.atm_strike)
print("Risk Free    :", RISK_FREE_RATE)

print()

print(
    f"{'Strike':<8}"
    f"{'Type':<6}"
    f"{'Money':<7}"
    f"{'Market':>10}"
    f"{'Spot BS':>11}"
    f"{'Fwd BS':>11}"
    f"{'Spot %':>10}"
    f"{'Fwd %':>10}"
    f"{'Forward':>12}"
)

print("-" * 85)

for item in analysis:

    print(
        f"{item.strike_price:<8}"
        f"{item.option_type:<6}"
        f"{item.moneyness:<7}"
        f"{item.market_premium:>10.2f}"
        f"{item.spot_bs_premium:>11.2f}"
        f"{item.forward_bs_premium:>11.2f}"
        f"{item.spot_difference_pct:>10.2f}"
        f"{item.forward_difference_pct:>10.2f}"
        f"{item.implied_forward:>12.2f}"
    )


# =====================================================
# Summary
# =====================================================

print()

print(
    "Average |Spot-BS Deviation|    :",
    round(
        average_spot_deviation,
        4,
    ),
    "%",
)

print(
    "Average |Forward-BS Deviation| :",
    round(
        average_forward_deviation,
        4,
    ),
    "%",
)

print()

print(
    "Average Implied Forward        :",
    round(
        average_forward,
        2,
    ),
)

print(
    "Minimum Implied Forward        :",
    round(
        minimum_forward,
        2,
    ),
)

print(
    "Maximum Implied Forward        :",
    round(
        maximum_forward,
        2,
    ),
)

print(
    "Forward Spread                 :",
    round(
        forward_spread,
        2,
    ),
)


# =====================================================
# Final Result
# =====================================================

print(
    "\nForward Premium Analytics integration test passed."
)
"""
=========================================================
NPAT - Put-Call Parity Integration Test
=========================================================

Tests:

GrowwProvider
      ↓
OptionData[]
      ↓
MarketAnalytics
      ↓
ATM ±3
      ↓
PremiumAnalytics
      ↓
Put-Call Parity
      ↓
Implied Forward

=========================================================
"""

from datetime import datetime

import pyotp

from analytics.market_analytics import MarketAnalytics
from analytics.premium_analytics import PremiumAnalytics
from config import GROWW, RISK_FREE_RATE
from core.models import ParityAnalysis
from growwapi.groww.client import GrowwAPI
from providers.groww_provider import GrowwProvider


# =====================================================
# Test Configuration
# =====================================================

SYMBOL = "NIFTY"
EXCHANGE = "NSE"
EXPIRY = "2026-07-28"

# Keep identical to PremiumAnalytics test so results
# are directly comparable.
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


# =====================================================
# Run Put-Call Parity Analysis
# =====================================================

parity = PremiumAnalytics.analyze_put_call_parity(
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
    parity,
    list,
)

assert len(parity) == 7

assert all(
    isinstance(item, ParityAnalysis)
    for item in parity
)


# =====================================================
# Validate Strike Window
# =====================================================

strikes = [
    item.strike_price
    for item in parity
]

assert len(set(strikes)) == 7

assert snapshot.atm_strike in strikes

assert strikes == sorted(strikes)


# =====================================================
# Validate Values
# =====================================================

for item in parity:

    assert item.spot_price > 0

    assert item.strike_price > 0

    assert item.call_premium >= 0

    assert item.put_premium >= 0

    assert item.implied_forward > 0

    assert item.time_to_expiry > 0

    # Market parity must equal C - P.
    expected_market_parity = (
        item.call_premium
        - item.put_premium
    )

    assert abs(
        item.market_parity
        - expected_market_parity
    ) < 1e-9

    # Forward premium must equal F - Spot.
    expected_forward_premium = (
        item.implied_forward
        - item.spot_price
    )

    assert abs(
        item.forward_premium
        - expected_forward_premium
    ) < 1e-9


# =====================================================
# Implied Forward Statistics
# =====================================================

implied_forwards = [
    item.implied_forward
    for item in parity
]

average_forward = (
    sum(implied_forwards)
    / len(implied_forwards)
)

forward_min = min(
    implied_forwards
)

forward_max = max(
    implied_forwards
)

forward_spread = (
    forward_max
    - forward_min
)


# =====================================================
# Display Results
# =====================================================

print(
    "\n========== NPAT PUT-CALL PARITY ==========\n"
)

print("Symbol       :", SYMBOL)
print("Expiry       :", EXPIRY)
print("Spot         :", snapshot.spot_price)
print("ATM          :", snapshot.atm_strike)
print("Risk Free    :", RISK_FREE_RATE)

print()

print(
    f"{'Strike':<9}"
    f"{'CE':>10}"
    f"{'PE':>10}"
    f"{'C-P':>10}"
    f"{'Theo':>11}"
    f"{'Deviation':>12}"
    f"{'Impl Fwd':>12}"
    f"{'Fwd Prem':>11}"
)

print("-" * 85)

for item in parity:

    print(
        f"{item.strike_price:<9}"
        f"{item.call_premium:>10.2f}"
        f"{item.put_premium:>10.2f}"
        f"{item.market_parity:>10.2f}"
        f"{item.theoretical_parity:>11.2f}"
        f"{item.parity_deviation:>12.2f}"
        f"{item.implied_forward:>12.2f}"
        f"{item.forward_premium:>11.2f}"
    )


print(
    "\nAverage Implied Forward :",
    round(
        average_forward,
        2,
    ),
)

print(
    "Minimum Implied Forward :",
    round(
        forward_min,
        2,
    ),
)

print(
    "Maximum Implied Forward :",
    round(
        forward_max,
        2,
    ),
)

print(
    "Forward Spread          :",
    round(
        forward_spread,
        2,
    ),
)


# =====================================================
# Final Result
# =====================================================

print(
    "\nPut-Call Parity integration test passed."
)


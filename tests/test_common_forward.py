"""
=========================================================
NPAT - Common Forward Integration Test
=========================================================

Tests robust common implied-forward calculation using
real Groww NIFTY option-chain data.

=========================================================
"""

from datetime import datetime

import pyotp

from analytics.market_analytics import MarketAnalytics
from analytics.premium_analytics import PremiumAnalytics
from config import GROWW, RISK_FREE_RATE
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


# =====================================================
# Time To Expiry
# =====================================================

time_to_expiry = (
    PremiumAnalytics.calculate_time_to_expiry(
        expiry=EXPIRY,
        current_time=TEST_TIME,
    )
)

assert time_to_expiry > 0


# =====================================================
# Select ATM ±3
# =====================================================

selected_options = (
    PremiumAnalytics.select_atm_window(
        options=options,
        atm_strike=snapshot.atm_strike,
        strikes_each_side=3,
    )
)

assert len(selected_options) == 7


# =====================================================
# Calculate Individual Forwards
# =====================================================

individual_forwards = []

for option in selected_options:

    implied_forward = (
        PremiumAnalytics.calculate_implied_forward(
            strike_price=float(
                option.strike_price
            ),
            call_premium=float(
                option.call_ltp
            ),
            put_premium=float(
                option.put_ltp
            ),
            risk_free_rate=RISK_FREE_RATE,
            time_to_expiry=time_to_expiry,
        )
    )

    individual_forwards.append(
        (
            option.strike_price,
            implied_forward,
        )
    )


# =====================================================
# Calculate Common Forward
# =====================================================

common_forward = (
    PremiumAnalytics.calculate_common_forward(
        options=options,
        atm_strike=snapshot.atm_strike,
        risk_free_rate=RISK_FREE_RATE,
        time_to_expiry=time_to_expiry,
        strikes_each_side=3,
    )
)

assert common_forward > 0


# =====================================================
# Independently Validate Median
# =====================================================

sorted_forwards = sorted(
    forward
    for _, forward
    in individual_forwards
)

expected_median = (
    sorted_forwards[
        len(sorted_forwards) // 2
    ]
)

assert abs(
    common_forward
    - expected_median
) < 1e-9


# =====================================================
# Statistics
# =====================================================

minimum_forward = min(
    sorted_forwards
)

maximum_forward = max(
    sorted_forwards
)

forward_spread = (
    maximum_forward
    - minimum_forward
)


# =====================================================
# Display Results
# =====================================================

print(
    "\n========== NPAT COMMON FORWARD ==========\n"
)

print("Symbol         :", SYMBOL)
print("Expiry         :", EXPIRY)
print("Spot           :", snapshot.spot_price)
print("ATM            :", snapshot.atm_strike)

print()

print(
    f"{'Strike':<10}"
    f"{'Implied Forward':>18}"
)

print("-" * 28)

for strike, forward in individual_forwards:

    print(
        f"{strike:<10}"
        f"{forward:>18.2f}"
    )


print()

print(
    "Common Forward  :",
    round(
        common_forward,
        2,
    ),
)

print(
    "Minimum Forward :",
    round(
        minimum_forward,
        2,
    ),
)

print(
    "Maximum Forward :",
    round(
        maximum_forward,
        2,
    ),
)

print(
    "Forward Spread  :",
    round(
        forward_spread,
        2,
    ),
)

print(
    "Forward vs Spot :",
    round(
        common_forward
        - snapshot.spot_price,
        2,
    ),
)


# =====================================================
# Final Result
# =====================================================

print(
    "\nCommon Forward integration test passed."
)
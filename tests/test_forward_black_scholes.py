"""
=========================================================
NPAT - Forward Black-Scholes Unit Test
=========================================================

Tests the forward form of Black-Scholes independently
from GrowwProvider and the option-chain pipeline.

=========================================================
"""

import math

from analytics.premium_analytics import PremiumAnalytics


# =====================================================
# Test Inputs
# =====================================================

FORWARD_PRICE = 23804.87
STRIKE_PRICE = 23750.0

RISK_FREE_RATE = 0.07
VOLATILITY = 0.1146
TIME_TO_EXPIRY = 0.011644


# =====================================================
# Calculate CE
# =====================================================

call_price = (
    PremiumAnalytics.forward_black_scholes_price(
        forward_price=FORWARD_PRICE,
        strike_price=STRIKE_PRICE,
        time_to_expiry=TIME_TO_EXPIRY,
        risk_free_rate=RISK_FREE_RATE,
        volatility=VOLATILITY,
        option_type="CE",
    )
)


# =====================================================
# Calculate PE
# =====================================================

put_price = (
    PremiumAnalytics.forward_black_scholes_price(
        forward_price=FORWARD_PRICE,
        strike_price=STRIKE_PRICE,
        time_to_expiry=TIME_TO_EXPIRY,
        risk_free_rate=RISK_FREE_RATE,
        volatility=VOLATILITY,
        option_type="PE",
    )
)


# =====================================================
# Basic Validation
# =====================================================

assert call_price > 0
assert put_price > 0

assert math.isfinite(call_price)
assert math.isfinite(put_price)


# =====================================================
# Validate Forward Put-Call Parity
# =====================================================

discount_factor = math.exp(
    -RISK_FREE_RATE * TIME_TO_EXPIRY
)

expected_difference = (
    discount_factor
    * (
        FORWARD_PRICE
        - STRIKE_PRICE
    )
)

actual_difference = (
    call_price
    - put_price
)

assert abs(
    actual_difference
    - expected_difference
) < 1e-9


# =====================================================
# Display
# =====================================================

print(
    "\n========== FORWARD BLACK-SCHOLES ==========\n"
)

print("Forward Price :", FORWARD_PRICE)
print("Strike        :", STRIKE_PRICE)
print("Volatility    :", VOLATILITY)
print("Time          :", TIME_TO_EXPIRY)

print()

print(
    "CE Theoretical:",
    round(call_price, 4),
)

print(
    "PE Theoretical:",
    round(put_price, 4),
)

print()

print(
    "CE - PE       :",
    round(actual_difference, 4),
)

print(
    "Parity Target :",
    round(expected_difference, 4),
)


# =====================================================
# Final Result
# =====================================================

print(
    "\nForward Black-Scholes test passed."
)
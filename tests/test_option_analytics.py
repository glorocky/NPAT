"""
=========================================================
NPAT - Option Analytics Integration Test
=========================================================

Tests:

GrowwProvider
      ↓
OptionData[]
      ↓
OptionAnalytics
      ├── Max Pain
      ├── Support
      └── Resistance

=========================================================
"""

import pyotp

from analytics.option_analytics import OptionAnalytics
from config import GROWW
from core.models import MarketLevel
from growwapi.groww.client import GrowwAPI
from providers.groww_provider import GrowwProvider


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
# Fetch Option Chain
# =====================================================

options = provider.get_option_chain(
    exchange="NSE",
    symbol="NIFTY",
    expiry="2026-07-28",
)

assert len(options) > 0

print(
    "Option chain received successfully:",
    len(options),
    "strikes",
)


# =====================================================
# Calculate Option Analytics
# =====================================================

max_pain = OptionAnalytics.calculate_max_pain(
    options
)

support = OptionAnalytics.calculate_support(
    options=options,
    limit=3,
)

resistance = OptionAnalytics.calculate_resistance(
    options=options,
    limit=3,
)


# =====================================================
# Validate Max Pain
# =====================================================

available_strikes = {
    option.strike_price
    for option in options
}

assert isinstance(max_pain, int)

assert max_pain in available_strikes


# =====================================================
# Validate Support
# =====================================================

assert isinstance(support, list)

assert len(support) == 3

assert all(
    isinstance(level, MarketLevel)
    for level in support
)

assert all(
    support[index].open_interest
    >= support[index + 1].open_interest
    for index in range(len(support) - 1)
)


# =====================================================
# Validate Resistance
# =====================================================

assert isinstance(resistance, list)

assert len(resistance) == 3

assert all(
    isinstance(level, MarketLevel)
    for level in resistance
)

assert all(
    resistance[index].open_interest
    >= resistance[index + 1].open_interest
    for index in range(len(resistance) - 1)
)


# =====================================================
# Result
# =====================================================

print(
    "\n========== NPAT OPTION ANALYTICS ==========\n"
)

print("Max Pain:", max_pain)


print("\nTop 3 Put OI / Potential Support:")

for level in support:
    print(
        f"Strike: {level.strike} | "
        f"OI: {level.open_interest} | "
        f"Change OI: {level.change_in_oi}"
    )


print("\nTop 3 Call OI / Potential Resistance:")

for level in resistance:
    print(
        f"Strike: {level.strike} | "
        f"OI: {level.open_interest} | "
        f"Change OI: {level.change_in_oi}"
    )


print(
    "\nOptionAnalytics integration test passed."
)
"""
=========================================================
NPAT - Live VIX Analytics Integration Test
=========================================================

Live pipeline:

Groww NIFTY Quote
        +
Groww INDIA VIX Quote
        ↓
Normalized NPAT Quote Models
        ↓
VixAnalytics
        ↓
Expected NIFTY Daily Range
=========================================================
"""

import pyotp

from analytics.vix_analytics import VixAnalytics
from config import GROWW
from core.models import Quote, VixRangeAnalysis
from growwapi.groww.client import GrowwAPI
from providers.groww_provider import GrowwProvider


# =====================================================
# Configuration
# =====================================================

SYMBOL = "NIFTY"

EXCHANGE = "NSE"
SEGMENT = "CASH"

NIFTY_TRADING_SYMBOL = "NIFTY"
VIX_TRADING_SYMBOL = "INDIAVIX"


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
# Groww Authentication
# =====================================================

totp = pyotp.TOTP(
    GROWW.totp_secret
).now()

access_token = GrowwAPI.get_access_token(
    api_key=GROWW.api_key,
    totp=totp,
)

if not isinstance(
    access_token,
    str,
) or not access_token.strip():

    raise RuntimeError(
        "Groww access token generation failed."
    )


# =====================================================
# Provider
# =====================================================

provider = GrowwProvider(
    access_token=access_token
)

print(
    "GrowwProvider initialized successfully."
)


# =====================================================
# NIFTY Live Quote
# =====================================================

nifty_quote = provider.get_quote(
    trading_symbol=NIFTY_TRADING_SYMBOL,
    exchange=EXCHANGE,
    segment=SEGMENT,
)

assert isinstance(
    nifty_quote,
    Quote,
)


# =====================================================
# India VIX Live Quote
# =====================================================

vix_quote = provider.get_quote(
    trading_symbol=VIX_TRADING_SYMBOL,
    exchange=EXCHANGE,
    segment=SEGMENT,
)

assert isinstance(
    vix_quote,
    Quote,
)


# =====================================================
# Validate Live Inputs
# =====================================================

assert nifty_quote.last_price > 0
assert nifty_quote.open > 0
assert nifty_quote.high > 0
assert nifty_quote.low > 0
assert nifty_quote.previous_close > 0

assert vix_quote.last_price > 0


# =====================================================
# VIX Range Analytics
# =====================================================

analysis = VixAnalytics.analyze_daily_range(
    symbol=SYMBOL,

    # Fixed NIFTY reference for this calculation.
    reference_price=nifty_quote.previous_close,

    # Live India VIX for V1.
    india_vix=vix_quote.last_price,

    day_open=nifty_quote.open,
    day_high=nifty_quote.high,
    day_low=nifty_quote.low,

    current_price=nifty_quote.last_price,
)


# =====================================================
# Validate Analysis
# =====================================================

assert isinstance(
    analysis,
    VixRangeAnalysis,
)

assert analysis.symbol == SYMBOL

assert analysis.reference_price == (
    nifty_quote.previous_close
)

assert analysis.india_vix == (
    vix_quote.last_price
)

assert analysis.expected_move_pct >= 0
assert analysis.expected_move_points >= 0

assert analysis.expected_lower <= (
    analysis.reference_price
)

assert analysis.expected_upper >= (
    analysis.reference_price
)

assert analysis.actual_range >= 0

assert analysis.upside_remaining >= 0
assert analysis.downside_remaining >= 0


# =====================================================
# Live Inputs
# =====================================================

print(
    "\n========== NPAT LIVE MARKET INPUTS ==========\n"
)

print(
    "NIFTY Previous Close :",
    nifty_quote.previous_close,
)

print(
    "NIFTY Open           :",
    nifty_quote.open,
)

print(
    "NIFTY High           :",
    nifty_quote.high,
)

print(
    "NIFTY Low            :",
    nifty_quote.low,
)

print(
    "NIFTY LTP            :",
    nifty_quote.last_price,
)

print()

print(
    "India VIX            :",
    vix_quote.last_price,
)


# =====================================================
# Expected Range
# =====================================================

print(
    "\n========== NPAT VIX EXPECTED RANGE ==========\n"
)

print(
    "Reference Price      :",
    round(
        analysis.reference_price,
        2,
    ),
)

print(
    "Expected Move %      :",
    round(
        analysis.expected_move_pct,
        4,
    ),
    "%",
)

print(
    "Expected Move Points :",
    round(
        analysis.expected_move_points,
        2,
    ),
)

print(
    "Expected Lower       :",
    round(
        analysis.expected_lower,
        2,
    ),
)

print(
    "Expected Upper       :",
    round(
        analysis.expected_upper,
        2,
    ),
)

print(
    "Expected Total Range :",
    round(
        analysis.expected_total_range,
        2,
    ),
)


# =====================================================
# Actual Range Usage
# =====================================================

print(
    "\n========== NPAT RANGE UTILIZATION ==========\n"
)

print(
    "Actual Range         :",
    round(
        analysis.actual_range,
        2,
    ),
)

print(
    "Actual Range %       :",
    round(
        analysis.actual_range_pct,
        4,
    ),
    "%",
)

print(
    "Range Achieved       :",
    round(
        analysis.range_achieved_pct,
        2,
    ),
    "%",
)

print()

print(
    "Upside Achieved      :",
    round(
        analysis.upside_achieved_points,
        2,
    ),
    "points",
)

print(
    "Upside Achieved %    :",
    round(
        analysis.upside_achieved_pct,
        2,
    ),
    "%",
)

print(
    "Downside Achieved    :",
    round(
        analysis.downside_achieved_points,
        2,
    ),
    "points",
)

print(
    "Downside Achieved %  :",
    round(
        analysis.downside_achieved_pct,
        2,
    ),
    "%",
)


# =====================================================
# Remaining Distance From Current Price
# =====================================================

print(
    "\n========== NPAT RANGE REMAINING ==========\n"
)

print(
    "Upside Remaining     :",
    round(
        analysis.upside_remaining,
        2,
    ),
    "points",
)

print(
    "Downside Remaining   :",
    round(
        analysis.downside_remaining,
        2,
    ),
    "points",
)

# =====================================================
# Expected Range Allowance / Breach
# =====================================================

assert analysis.unused_upside_points >= 0
assert analysis.unused_downside_points >= 0
assert analysis.upside_breach_points >= 0
assert analysis.downside_breach_points >= 0

print(
    "\n========== NPAT RANGE ALLOWANCE ==========\n"
)

print(
    "Unused Upside        :",
    round(
        analysis.unused_upside_points,
        2,
    ),
    "points",
)

print(
    "Unused Downside      :",
    round(
        analysis.unused_downside_points,
        2,
    ),
    "points",
)

print(
    "Upside Breach        :",
    round(
        analysis.upside_breach_points,
        2,
    ),
    "points",
)

print(
    "Downside Breach      :",
    round(
        analysis.downside_breach_points,
        2,
    ),
    "points",
)


# =====================================================
# Breach Status
# =====================================================

print(
    "\n========== NPAT RANGE STATUS ==========\n"
)

print(
    "Upper Range Exceeded :",
    analysis.upper_range_exceeded,
)

print(
    "Lower Range Exceeded :",
    analysis.lower_range_exceeded,
)

print(
    "Any Range Exceeded   :",
    analysis.expected_range_exceeded,
)


# =====================================================
# Final Result
# =====================================================

print(
    "\nLive VixAnalytics integration test passed."
)
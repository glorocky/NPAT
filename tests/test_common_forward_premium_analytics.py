"""
=========================================================
NPAT - Common Forward Premium Analytics Test
=========================================================

Validates:

Real Groww option chain
        ↓
ATM ±3
        ↓
One robust common forward
        ↓
14 CE/PE contracts
        ↓
Market vs Spot-BS vs Common-Forward-BS
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
# Configuration
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
# Groww Authentication
# =====================================================

if not GROWW.api_key:
    raise RuntimeError(
        "GROWW_API_KEY is missing from .env"
    )

if not GROWW.totp_secret:
    raise RuntimeError(
        "GROWW_TOTP_SECRET is missing from .env"
    )


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
# Provider
# =====================================================

provider = GrowwProvider(
    access_token=access_token
)

print(
    "GrowwProvider initialized successfully."
)


# =====================================================
# Option Chain
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
# Market Snapshot
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
# Common Forward Premium Analytics
# =====================================================

analysis = (
    PremiumAnalytics.analyze_common_forward_premiums(
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
    analysis,
    list,
)

assert len(analysis) == 14

assert all(
    isinstance(item, ForwardPremiumAnalysis)
    for item in analysis
)


# =====================================================
# Validate 7 Strikes × CE/PE
# =====================================================

strikes = sorted(
    {
        item.strike_price
        for item in analysis
    }
)

assert len(strikes) == 7

assert snapshot.atm_strike in strikes


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
# Validate ONE Common Forward
# =====================================================

common_forwards = {
    round(
        item.implied_forward,
        10,
    )
    for item in analysis
}

assert len(common_forwards) == 1

common_forward = next(
    iter(common_forwards)
)


# =====================================================
# Independently Calculate Expected Common Forward
# =====================================================

time_to_expiry = (
    PremiumAnalytics.calculate_time_to_expiry(
        expiry=EXPIRY,
        current_time=TEST_TIME,
    )
)

expected_common_forward = (
    PremiumAnalytics.calculate_common_forward(
        options=options,
        atm_strike=snapshot.atm_strike,
        risk_free_rate=RISK_FREE_RATE,
        time_to_expiry=time_to_expiry,
        strikes_each_side=3,
    )
)

assert abs(
    common_forward
    - expected_common_forward
) < 1e-8


# =====================================================
# Validate Pricing Results
# =====================================================

for item in analysis:

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

    assert abs(
        item.spot_difference
        - (
            item.market_premium
            - item.spot_bs_premium
        )
    ) < 1e-9

    assert abs(
        item.forward_difference
        - (
            item.market_premium
            - item.forward_bs_premium
        )
    ) < 1e-9


# =====================================================
# Deviation Statistics
# =====================================================

average_spot_deviation = (
    sum(
        abs(item.spot_difference_pct)
        for item in analysis
    )
    / len(analysis)
)

average_common_forward_deviation = (
    sum(
        abs(item.forward_difference_pct)
        for item in analysis
    )
    / len(analysis)
)


# =====================================================
# Display
# =====================================================

print(
    "\n========== NPAT COMMON-FORWARD PREMIUM ANALYTICS ==========\n"
)

print("Symbol         :", SYMBOL)
print("Expiry         :", EXPIRY)
print("Spot           :", snapshot.spot_price)
print("ATM            :", snapshot.atm_strike)

print(
    "Common Forward :",
    round(
        common_forward,
        2,
    ),
)

print()

print(
    f"{'Strike':<8}"
    f"{'Type':<6}"
    f"{'Money':<7}"
    f"{'Market':>10}"
    f"{'Spot BS':>11}"
    f"{'Common BS':>12}"
    f"{'Spot %':>10}"
    f"{'Common %':>11}"
)

print("-" * 75)


for item in analysis:

    print(
        f"{item.strike_price:<8}"
        f"{item.option_type:<6}"
        f"{item.moneyness:<7}"
        f"{item.market_premium:>10.2f}"
        f"{item.spot_bs_premium:>11.2f}"
        f"{item.forward_bs_premium:>12.2f}"
        f"{item.spot_difference_pct:>10.2f}"
        f"{item.forward_difference_pct:>11.2f}"
    )


# =====================================================
# Summary
# =====================================================

print()

print(
    "Average |Spot-BS Deviation|           :",
    round(
        average_spot_deviation,
        4,
    ),
    "%",
)

print(
    "Average |Common-Forward BS Deviation| :",
    round(
        average_common_forward_deviation,
        4,
    ),
    "%",
)


# =====================================================
# Final Result
# =====================================================

print(
    "\nCommon-Forward Premium Analytics "
    "integration test passed."
)
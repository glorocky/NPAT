"""
=========================================================
NPAT - Greeks Analytics Integration Test
=========================================================

Pipeline:

Groww Option Chain
        ↓
Market Analytics
        ↓
ATM Strike
        ↓
ATM ±3 Strikes
        ↓
CE + PE
        ↓
14 Groww Greeks Requests
        ↓
GreeksAnalysis Models

=========================================================
"""

import pyotp

from analytics.greeks_analytics import GreeksAnalytics
from analytics.market_analytics import MarketAnalytics
from config import GROWW
from core.models import GreeksAnalysis
from growwapi.groww.client import GrowwAPI
from providers.groww_provider import GrowwProvider


# =====================================================
# Configuration
# =====================================================

SYMBOL = "NIFTY"
EXCHANGE = "NSE"


STRIKES_EACH_SIDE = 3


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
# Select Nearest Available Expiry
# =====================================================
from datetime import datetime

expiries = provider.get_expiries(
    exchange=EXCHANGE,
    underlying_symbol=SYMBOL,
)

today = datetime.now().date()

EXPIRY = next(
    expiry
    for expiry in expiries
    if datetime.strptime(
        expiry,
        "%Y-%m-%d",
    ).date() >= today
)

print(
    "Selected Expiry:",
    EXPIRY,
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
# Greeks Analytics
# =====================================================

analysis = GreeksAnalytics.analyze_atm_window(
    provider=provider,
    symbol=SYMBOL,
    exchange=EXCHANGE,
    expiry=EXPIRY,
    options=options,
    atm_strike=snapshot.atm_strike,
    strikes_each_side=STRIKES_EACH_SIDE,
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
    isinstance(item, GreeksAnalysis)
    for item in analysis
)


# =====================================================
# Validate Seven Strikes
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
# Validate CE + PE At Every Strike
# =====================================================

for strike in strikes:

    contracts = [
        item
        for item in analysis
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
# Validate Greeks
# =====================================================

for item in analysis:

    assert item.symbol == SYMBOL

    assert item.expiry == EXPIRY

    assert item.strike_price > 0

    assert item.option_type in {
        "CE",
        "PE",
    }

    assert item.spot_price > 0

    assert item.option_ltp >= 0

    assert item.moneyness in {
        "ITM",
        "ATM",
        "OTM",
    }

    # ---------------------------------------------
    # Delta
    # ---------------------------------------------

    assert -1.0 <= item.delta <= 1.0

    if item.option_type == "CE":
        assert item.delta >= 0.0

    if item.option_type == "PE":
        assert item.delta <= 0.0

    # ---------------------------------------------
    # Gamma
    # ---------------------------------------------

    assert item.gamma >= 0.0

    # ---------------------------------------------
    # IV
    # ---------------------------------------------

    assert item.iv >= 0.0


# =====================================================
# ATM Contracts
# =====================================================

atm_contracts = [
    item
    for item in analysis
    if item.strike_price
    == snapshot.atm_strike
]

assert len(atm_contracts) == 2

atm_call = next(
    item
    for item in atm_contracts
    if item.option_type == "CE"
)

atm_put = next(
    item
    for item in atm_contracts
    if item.option_type == "PE"
)


# =====================================================
# Display Results
# =====================================================

print(
    "\n========== NPAT ATM ±3 GREEKS ==========\n"
)

print("Symbol :", SYMBOL)
print("Expiry :", EXPIRY)
print("Spot   :", snapshot.spot_price)
print("ATM    :", snapshot.atm_strike)

print()

print(
    f"{'Strike':<8}"
    f"{'Type':<6}"
    f"{'Money':<7}"
    f"{'LTP':>10}"
    f"{'Delta':>10}"
    f"{'Gamma':>11}"
    f"{'Theta':>11}"
    f"{'Vega':>11}"
    f"{'Rho':>11}"
    f"{'IV %':>10}"
)

print("-" * 95)


for item in analysis:

    print(
        f"{item.strike_price:<8}"
        f"{item.option_type:<6}"
        f"{item.moneyness:<7}"
        f"{item.option_ltp:>10.2f}"
        f"{item.delta:>10.4f}"
        f"{item.gamma:>11.6f}"
        f"{item.theta:>11.4f}"
        f"{item.vega:>11.4f}"
        f"{item.rho:>11.4f}"
        f"{item.iv:>10.4f}"
    )


# =====================================================
# ATM Summary
# =====================================================

print(
    "\n========== ATM GREEKS SUMMARY ==========\n"
)

print(
    "ATM CE Delta :",
    round(
        atm_call.delta,
        4,
    ),
)

print(
    "ATM PE Delta :",
    round(
        atm_put.delta,
        4,
    ),
)

print(
    "ATM CE Gamma :",
    round(
        atm_call.gamma,
        6,
    ),
)

print(
    "ATM PE Gamma :",
    round(
        atm_put.gamma,
        6,
    ),
)

print(
    "ATM CE Theta :",
    round(
        atm_call.theta,
        4,
    ),
)

print(
    "ATM PE Theta :",
    round(
        atm_put.theta,
        4,
    ),
)

print(
    "ATM CE Vega  :",
    round(
        atm_call.vega,
        4,
    ),
)

print(
    "ATM PE Vega  :",
    round(
        atm_put.vega,
        4,
    ),
)

print(
    "ATM CE IV    :",
    round(
        atm_call.iv,
        4,
    ),
)

print(
    "ATM PE IV    :",
    round(
        atm_put.iv,
        4,
    ),
)


# =====================================================
# Greeks Summary
# =====================================================

summary = GreeksAnalytics.summarize(
    analysis=analysis,
    atm_strike=snapshot.atm_strike,
)


# =====================================================
# Validate Summary
# =====================================================

assert summary.symbol == SYMBOL
assert summary.expiry == EXPIRY

assert summary.spot_price > 0
assert summary.atm_strike == snapshot.atm_strike

assert -1.0 <= summary.atm_call_delta <= 1.0
assert -1.0 <= summary.atm_put_delta <= 1.0

assert summary.highest_gamma_strike in strikes
assert summary.highest_gamma >= 0.0

assert summary.total_vega >= 0.0


# =====================================================
# Display Greeks Summary
# =====================================================

print(
    "\n========== NPAT GREEKS SUMMARY ==========\n"
)

print(
    "ATM CE Delta          :",
    round(summary.atm_call_delta, 4),
)

print(
    "ATM PE Delta          :",
    round(summary.atm_put_delta, 4),
)

print(
    "Delta Balance         :",
    round(summary.delta_balance, 4),
)

print()

print(
    "ATM CE IV             :",
    round(summary.atm_call_iv, 4),
)

print(
    "ATM PE IV             :",
    round(summary.atm_put_iv, 4),
)

print(
    "PE - CE IV Skew       :",
    round(summary.iv_skew, 4),
)

print()

print(
    "Highest Gamma Strike  :",
    summary.highest_gamma_strike,
)

print(
    "Combined Gamma        :",
    round(summary.highest_gamma, 6),
)

print()

print(
    "Total CE Theta        :",
    round(summary.total_call_theta, 4),
)

print(
    "Total PE Theta        :",
    round(summary.total_put_theta, 4),
)

print(
    "Total Theta           :",
    round(summary.total_theta, 4),
)

print()

print(
    "Total CE Vega         :",
    round(summary.total_call_vega, 4),
)

print(
    "Total PE Vega         :",
    round(summary.total_put_vega, 4),
)

print(
    "Total Vega            :",
    round(summary.total_vega, 4),
)


# =====================================================
# Final Summary Validation
# =====================================================

print(
    "\nGreeksSummary integration test passed."
)

# =====================================================
# Final Result
# =====================================================

print(
    "\nGreeksAnalytics integration test passed."
)
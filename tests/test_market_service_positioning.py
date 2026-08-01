import time

import pyotp

from config import GROWW
from growwapi.groww.client import GrowwAPI
from providers.groww_provider import GrowwProvider
from services.market_service import MarketService


SYMBOL = "NIFTY"
EXCHANGE = "NSE"
EXPIRY = "2026-07-28"


# =====================================================
# Authentication
# =====================================================

totp = pyotp.TOTP(
    GROWW.totp_secret
).now()

access_token = GrowwAPI.get_access_token(
    api_key=GROWW.api_key,
    totp=totp,
)

provider = GrowwProvider(
    access_token=access_token
)


# =====================================================
# IMPORTANT:
# One MarketService instance for both polls.
# =====================================================

service = MarketService(
    provider=provider
)


# =====================================================
# Poll 1
# =====================================================

print(
    "\n========== NPAT MARKET SERVICE POLL 1 ==========\n"
)

snapshot_1 = service.get_dashboard_snapshot(
    exchange=EXCHANGE,
    symbol=SYMBOL,
    expiry=EXPIRY,
)

market_1 = snapshot_1.market

print("Spot Price            :", market_1.spot_price)
print("ATM Strike            :", market_1.atm_strike)
print("Option Strikes        :", len(market_1.option_chain))
print("Positioning Contracts :", len(market_1.positioning))

assert market_1.spot_price > 0
assert market_1.atm_strike > 0
assert len(market_1.option_chain) > 0

# First poll establishes the baseline.
assert len(market_1.positioning) == 0


# =====================================================
# Wait before Poll 2
# =====================================================

print(
    "\nWaiting 5 seconds before second poll..."
)

time.sleep(5)


# =====================================================
# Poll 2
# =====================================================

print(
    "\n========== NPAT MARKET SERVICE POLL 2 ==========\n"
)

snapshot_2 = service.get_dashboard_snapshot(
    exchange=EXCHANGE,
    symbol=SYMBOL,
    expiry=EXPIRY,
)

market_2 = snapshot_2.market


# =====================================================
# Validate Positioning
# =====================================================

assert len(market_2.positioning) > 0

assert market_2.positioning_summary is not None
assert market_2.atm_positioning_summary is not None

assert (
    market_2.positioning_summary.total_contracts
    == len(market_2.positioning)
)

assert (
    market_2.atm_positioning_summary.total_contracts
    == len(market_2.atm_positioning)
)


# =====================================================
# Output
# =====================================================

print("Spot Price            :", market_2.spot_price)
print("ATM Strike            :", market_2.atm_strike)

print()

print(
    "Positioning Contracts :",
    len(market_2.positioning),
)

print(
    "ATM Contracts         :",
    len(market_2.atm_positioning),
)

print()

print(
    "Long Buildup          :",
    market_2.positioning_summary.long_buildup,
)

print(
    "Short Buildup         :",
    market_2.positioning_summary.short_buildup,
)

print(
    "Long Unwinding        :",
    market_2.positioning_summary.long_unwinding,
)

print(
    "Short Covering        :",
    market_2.positioning_summary.short_covering,
)

print(
    "Neutral               :",
    market_2.positioning_summary.neutral,
)

print()

print(
    "Top OI Additions      :",
    len(market_2.top_oi_additions),
)

print(
    "Top OI Reductions     :",
    len(market_2.top_oi_reductions),
)

print(
    "\nMarketService positioning integration test passed."
)
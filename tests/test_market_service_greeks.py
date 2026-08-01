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

service = MarketService(
    provider=provider
)


# =====================================================
# Dashboard Snapshot
# =====================================================

print(
    "\n========== NPAT MARKET SERVICE GREEKS ==========\n"
)

snapshot = service.get_dashboard_snapshot(
    symbol=SYMBOL,
    expiry=EXPIRY,
    exchange=EXCHANGE,
)

market = snapshot.market
analysis = snapshot.greeks_analysis
summary = snapshot.greeks_summary


# =====================================================
# Validate Market
# =====================================================

assert market.spot_price > 0
assert market.atm_strike > 0
assert len(market.option_chain) > 0


# =====================================================
# Validate Greeks
# =====================================================

assert analysis
assert summary is not None

assert summary.symbol == SYMBOL
assert summary.expiry == EXPIRY
assert summary.atm_strike == market.atm_strike

assert len(analysis) == 14

atm_contracts = [
    item
    for item in analysis
    if item.strike_price == market.atm_strike
]

assert len(atm_contracts) == 2

assert {
    item.option_type
    for item in atm_contracts
} == {"CE", "PE"}


# =====================================================
# Output
# =====================================================

print("Spot Price       :", market.spot_price)
print("ATM Strike       :", market.atm_strike)
print("Greeks Contracts :", len(analysis))

print()

print("ATM Call Delta   :", summary.atm_call_delta)
print("ATM Put Delta    :", summary.atm_put_delta)
print("Delta Balance    :", summary.delta_balance)

print()

print("ATM Call IV      :", summary.atm_call_iv)
print("ATM Put IV       :", summary.atm_put_iv)
print("IV Skew          :", summary.iv_skew)

print()

print("Highest Gamma @  :", summary.highest_gamma_strike)
print("Highest Gamma    :", summary.highest_gamma)

print()

print("Total Theta      :", summary.total_theta)
print("Total Vega       :", summary.total_vega)

print(
    "\nMarketService Greeks integration test passed."
)
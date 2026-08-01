import pyotp

from config import GROWW
from growwapi.groww.client import GrowwAPI
from providers.groww_provider import GrowwProvider
from services.market_service import MarketService


SYMBOL = "NIFTY"
EXCHANGE = "NSE"
EXPIRY = "2026-08-04"


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
    "\n========== NPAT MARKET SERVICE PREMIUM ==========\n"
)

snapshot = service.get_dashboard_snapshot(
    symbol=SYMBOL,
    expiry=EXPIRY,
    exchange=EXCHANGE,
)

market = snapshot.market
premium_analysis = snapshot.premium_analysis


# =====================================================
# Validate Market
# =====================================================

assert market.spot_price > 0
assert market.atm_strike > 0
assert len(market.option_chain) > 0


# =====================================================
# Validate Premium Analytics
# =====================================================

assert premium_analysis

assert len(premium_analysis) == 14

assert all(
    item.symbol == SYMBOL
    for item in premium_analysis
)

assert all(
    item.expiry == EXPIRY
    for item in premium_analysis
)


# =====================================================
# ATM Contracts
# =====================================================

atm_contracts = [
    item
    for item in premium_analysis
    if item.strike_price == market.atm_strike
]

assert len(atm_contracts) == 2

assert {
    item.option_type
    for item in atm_contracts
} == {"CE", "PE"}


# =====================================================
# Common Forward Validation
# =====================================================

common_forwards = {
    round(item.implied_forward, 8)
    for item in premium_analysis
}

assert len(common_forwards) == 1

common_forward = premium_analysis[0].implied_forward

assert common_forward > 0


# =====================================================
# Output
# =====================================================

print("Spot Price        :", market.spot_price)
print("ATM Strike        :", market.atm_strike)
print("Premium Contracts :", len(premium_analysis))
print("Common Forward    :", common_forward)

print(
    "\n========== ATM PREMIUM ANALYSIS ==========\n"
)

for item in atm_contracts:

    print(
        item.option_type,
        "| Strike:", item.strike_price,
        "| Market:", round(item.market_premium, 4),
        "| Spot BS:", round(item.spot_bs_premium, 4),
        "| Forward BS:", round(item.forward_bs_premium, 4),
        "| Deviation:", round(item.forward_difference, 4),
    )
    
# =====================================================
# ATM Forward Premium Records
# =====================================================

print(
    "\n========== ATM FORWARD PREMIUM RECORDS ==========\n"
)

atm_premiums = [
    premium
    for premium in snapshot.premium_analysis
    if premium.moneyness == "ATM"
]

for premium in atm_premiums:

    print(
        premium.option_type,
        "| Strike:",
        premium.strike_price,
        "| Moneyness:",
        premium.moneyness,
        "| Market:",
        round(premium.market_premium, 4),
        "| Forward BS:",
        round(premium.forward_bs_premium, 4),
        "| Forward Diff:",
        round(premium.forward_difference, 4),
        "| Forward Diff %:",
        round(premium.forward_difference_pct, 4),
    )


# =====================================================
# Validate ATM Pair
# =====================================================

assert len(atm_premiums) == 2

assert {
    premium.option_type
    for premium in atm_premiums
} == {
    "CE",
    "PE",
}

assert len({
    premium.strike_price
    for premium in atm_premiums
}) == 1
    



print(
    "\nMarketService Premium integration test passed."
)
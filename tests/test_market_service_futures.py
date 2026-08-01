import pyotp

from config import GROWW
from growwapi.groww.client import GrowwAPI

from core.models import FuturesAnalysis
from providers.groww_provider import GrowwProvider
from services.market_service import MarketService
from analytics.market_regime_analytics import (
    MarketRegimeAnalytics,
)


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
    "\n========== NPAT MARKET SERVICE FUTURES ==========\n"
)

snapshot = service.get_dashboard_snapshot(
    symbol=SYMBOL,
    expiry=EXPIRY,
    exchange=EXCHANGE,
)

market = snapshot.market
futures = snapshot.futures

futures_score = MarketRegimeAnalytics.score_futures(
    futures=futures,
)

# =====================================================
# Validate Market
# =====================================================

assert market.spot_price > 0
assert market.atm_strike > 0
assert len(market.option_chain) > 0


# =====================================================
# Validate Futures
# =====================================================

assert futures is not None

assert isinstance(
    futures,
    FuturesAnalysis,
)

assert futures.symbol == SYMBOL
assert futures.exchange == EXCHANGE

assert futures.trading_symbol
assert futures.expiry

assert futures.spot_price > 0
assert futures.futures_price > 0

assert futures.lot_size > 0

assert futures.current_oi >= 0
assert futures.previous_oi >= 0

assert futures.positioning in {
    "LONG_BUILDUP",
    "SHORT_BUILDUP",
    "LONG_UNWINDING",
    "SHORT_COVERING",
    "NEUTRAL",
}


# =====================================================
# Cross-Layer Validation
# =====================================================

# MarketService should use the same live NIFTY spot
# context for the Futures analysis.

assert abs(
    futures.spot_price
    - market.spot_price
) < 0.01


# Basis must equal Futures - Spot.

expected_basis = (
    futures.futures_price
    - futures.spot_price
)

assert abs(
    futures.basis
    - expected_basis
) < 0.0001


# OI change must remain internally consistent.

assert (
    futures.oi_change
    == futures.current_oi
    - futures.previous_oi
)


# Quantity imbalance must remain internally consistent.

assert (
    futures.quantity_imbalance
    == futures.total_buy_quantity
    - futures.total_sell_quantity
)

# =====================================================
# Validate Market Regime Futures Score
# =====================================================

assert -100.0 <= futures_score <= 100.0

# =====================================================
# Output
# =====================================================

print("Spot Price          :", futures.spot_price)
print("Futures Price       :", futures.futures_price)

print()

print("Trading Symbol      :", futures.trading_symbol)
print("Expiry              :", futures.expiry)
print("Lot Size            :", futures.lot_size)

print()

print("Basis               :", round(futures.basis, 4))
print("Basis %             :", round(futures.basis_pct, 4))

print()

print("Previous Future     :", futures.previous_price)
print("Price Change        :", round(futures.price_change, 4))
print(
    "Price Change %      :",
    round(futures.price_change_pct, 4),
)

print()

print("Previous OI         :", futures.previous_oi)
print("Current OI          :", futures.current_oi)
print("OI Change           :", futures.oi_change)
print(
    "OI Change %         :",
    round(futures.oi_change_pct, 4),
)

print()

print("Positioning         :", futures.positioning)

print()

print(
    "Total Buy Qty       :",
    futures.total_buy_quantity,
)

print(
    "Total Sell Qty      :",
    futures.total_sell_quantity,
)

print(
    "Quantity Imbalance  :",
    futures.quantity_imbalance,
)

print(
    "Imbalance %         :",
    round(
        futures.quantity_imbalance_pct,
        4,
    ),
)

print()
print("Regime Futures Score:", futures_score)

print(
    "\nMarketService Futures integration test passed."
)
import pyotp

from config import GROWW
from growwapi.groww.client import GrowwAPI

from analytics.futures_analytics import FuturesAnalytics
from core.models import FutureData, FuturesAnalysis
from providers.groww_provider import GrowwProvider

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
# Live NIFTY Spot
# =====================================================

spot_quote = provider.get_quote(
    trading_symbol="NIFTY",
    exchange="NSE",
    segment="CASH",
)

assert spot_quote.last_price > 0


# =====================================================
# Live NIFTY Future
# =====================================================

future = provider.get_future(
    symbol="NIFTY",
    exchange="NSE",
)

assert isinstance(
    future,
    FutureData,
)

assert future.last_price > 0


# =====================================================
# Futures Analytics
# =====================================================

analysis = FuturesAnalytics.analyze(
    future=future,
    spot_price=spot_quote.last_price,
)

assert isinstance(
    analysis,
    FuturesAnalysis,
)


# =====================================================
# Output
# =====================================================

print(
    "\n========== NPAT LIVE FUTURES ANALYTICS ==========\n"
)

print("Symbol              :", analysis.symbol)
print("Trading Symbol      :", analysis.trading_symbol)
print("Expiry              :", analysis.expiry)
print("Lot Size            :", analysis.lot_size)

print()

print("Spot Price          :", analysis.spot_price)
print("Futures Price       :", analysis.futures_price)

print("Basis               :", round(analysis.basis, 4))
print("Basis %             :", round(analysis.basis_pct, 4))

print()

print("Previous Future     :", analysis.previous_price)
print("Price Change        :", round(analysis.price_change, 4))
print(
    "Price Change %      :",
    round(analysis.price_change_pct, 4),
)

print()

print("Previous OI         :", analysis.previous_oi)
print("Current OI          :", analysis.current_oi)
print("OI Change           :", analysis.oi_change)
print(
    "OI Change %         :",
    round(analysis.oi_change_pct, 4),
)

print()

print("Positioning         :", analysis.positioning)
print("Volume              :", analysis.volume)

print()

print(
    "Total Buy Qty       :",
    analysis.total_buy_quantity,
)

print(
    "Total Sell Qty      :",
    analysis.total_sell_quantity,
)

print(
    "Quantity Imbalance  :",
    analysis.quantity_imbalance,
)

print(
    "Imbalance %         :",
    round(
        analysis.quantity_imbalance_pct,
        4,
    ),
)


print(
    "\nLive FuturesAnalytics integration test passed."
)
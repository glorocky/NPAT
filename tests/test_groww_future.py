import pyotp

from config import GROWW
from growwapi.groww.client import GrowwAPI

from core.models import FutureData
from providers.groww_provider import GrowwProvider


# =====================================================
# Test Configuration
# =====================================================

SYMBOL = "NIFTY"
EXCHANGE = "NSE"


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
# Fetch Nearest Futures Contract
# =====================================================

future = provider.get_future(
    symbol=SYMBOL,
    exchange=EXCHANGE,
)


# =====================================================
# Validate Model
# =====================================================

assert isinstance(
    future,
    FutureData,
)

assert future.symbol == SYMBOL
assert future.exchange == EXCHANGE

assert future.trading_symbol
assert future.expiry

assert future.lot_size > 0
assert future.exchange_token

assert future.last_price > 0

assert future.open > 0
assert future.high > 0
assert future.low > 0
assert future.previous_close > 0

assert future.open_interest >= 0
assert future.previous_open_interest >= 0

assert future.volume >= 0
assert future.last_trade_quantity >= 0

assert future.total_buy_quantity >= 0
assert future.total_sell_quantity >= 0


# =====================================================
# Output
# =====================================================

print(
    "\n========== NPAT GROWW FUTURES ==========\n"
)

print("Underlying        :", future.symbol)
print("Trading Symbol    :", future.trading_symbol)
print("Exchange          :", future.exchange)
print("Expiry            :", future.expiry)
print("Lot Size          :", future.lot_size)
print("Exchange Token    :", future.exchange_token)

print()

print("Last Price        :", future.last_price)
print("Previous Close    :", future.previous_close)
print("Open              :", future.open)
print("High              :", future.high)
print("Low               :", future.low)

print()

print("Open Interest     :", future.open_interest)
print("Previous OI       :", future.previous_open_interest)
print("OI Change         :", future.oi_change)
print("OI Change %       :", future.oi_change_pct)

print()

print("Volume            :", future.volume)
print("Last Trade Qty    :", future.last_trade_quantity)
print("Total Buy Qty     :", future.total_buy_quantity)
print("Total Sell Qty    :", future.total_sell_quantity)


# =====================================================
# Final Result
# =====================================================

print(
    "\nGrowwProvider futures integration test passed."
)
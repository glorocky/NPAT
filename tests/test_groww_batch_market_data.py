import pyotp

from config import GROWW
from growwapi.groww.client import GrowwAPI
from providers.groww_provider import GrowwProvider


SYMBOLS = [
    "RELIANCE",
    "HDFCBANK",
    "INFY",
]


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
# Batch LTP
# =====================================================

ltp = provider.get_ltp_batch(
    symbols=SYMBOLS,
    exchange="NSE",
    segment="CASH",
)


# =====================================================
# Batch OHLC
# =====================================================

ohlc = provider.get_ohlc_batch(
    symbols=SYMBOLS,
    exchange="NSE",
    segment="CASH",
)


# =====================================================
# Validate
# =====================================================

assert set(ltp.keys()) == set(SYMBOLS)
assert set(ohlc.keys()) == set(SYMBOLS)

for symbol in SYMBOLS:

    assert ltp[symbol] > 0

    data = ohlc[symbol]

    assert data["open"] > 0
    assert data["high"] > 0
    assert data["low"] > 0
    assert data["previous_close"] > 0


# =====================================================
# Output
# =====================================================

print(
    "\n========== NPAT GROWW BATCH MARKET DATA ==========\n"
)

for symbol in SYMBOLS:

    data = ohlc[symbol]

    print(symbol)
    print("  LTP            :", ltp[symbol])
    print("  Open           :", data["open"])
    print("  High           :", data["high"])
    print("  Low            :", data["low"])
    print("  Previous Close :", data["previous_close"])
    print()

print(
    "GrowwProvider batch market data integration "
    "test passed."
)
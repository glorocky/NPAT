import pyotp

from config import GROWW
from data.reference.constituent_loader import ConstituentLoader
from growwapi.groww.client import GrowwAPI
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
# Load NIFTY 50 Constituents
# =====================================================

constituents = ConstituentLoader.load_nifty50()

symbols = constituents[
    "symbol"
].tolist()

assert len(symbols) == 50
assert len(set(symbols)) == 50


# =====================================================
# Batch Market Data
# =====================================================

ltp = provider.get_ltp_batch(
    symbols=symbols,
    exchange="NSE",
    segment="CASH",
)

ohlc = provider.get_ohlc_batch(
    symbols=symbols,
    exchange="NSE",
    segment="CASH",
)


# =====================================================
# Validate Coverage
# =====================================================

missing_ltp = [
    symbol
    for symbol in symbols
    if symbol not in ltp
]

missing_ohlc = [
    symbol
    for symbol in symbols
    if symbol not in ohlc
]

assert not missing_ltp, (
    f"Missing LTP symbols: {missing_ltp}"
)

assert not missing_ohlc, (
    f"Missing OHLC symbols: {missing_ohlc}"
)

assert len(ltp) == 50
assert len(ohlc) == 50


# =====================================================
# Validate Values
# =====================================================

for symbol in symbols:

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
    "\n========== NPAT NIFTY 50 BATCH MARKET DATA ==========\n"
)

print("Constituents :", len(symbols))
print("LTP Records  :", len(ltp))
print("OHLC Records :", len(ohlc))

print()

for symbol in symbols[:10]:

    data = ohlc[symbol]

    print(
        f"{symbol:<15} "
        f"LTP={ltp[symbol]:>10.2f}  "
        f"Prev={data['previous_close']:>10.2f}"
    )

print()

print(
    "NIFTY 50 batch market data integration test passed."
)
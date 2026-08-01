import pyotp

from config import GROWW
from core.models import HistoricalCandle
from growwapi.groww.client import GrowwAPI
from providers.groww_provider import GrowwProvider


# =====================================================
# Validate Configuration
# =====================================================

if not GROWW.api_key:
    raise RuntimeError("GROWW_API_KEY is missing from .env")

if not GROWW.totp_secret:
    raise RuntimeError("GROWW_TOTP_SECRET is missing from .env")


# =====================================================
# Generate Access Token
# =====================================================

totp = pyotp.TOTP(GROWW.totp_secret).now()

access_token = GrowwAPI.get_access_token(
    api_key=GROWW.api_key,
    totp=totp,
)

if not isinstance(access_token, str) or not access_token.strip():
    raise RuntimeError(
        "Groww access token generation failed."
    )


# =====================================================
# Initialize NPAT Groww Provider
# =====================================================

provider = GrowwProvider(
    access_token=access_token
)

print("GrowwProvider initialized successfully.")


# =====================================================
# Test Historical Data
# =====================================================

candles = provider.get_historical_data(
    exchange="NSE",
    segment="CASH",
    groww_symbol="NSE-NIFTY",
    start_time="2026-07-24 09:15:00",
    end_time="2026-07-24 09:30:00",
    candle_interval="1minute",
)


# =====================================================
# Validate NPAT Models
# =====================================================

assert isinstance(candles, list)

assert len(candles) > 0

assert all(
    isinstance(candle, HistoricalCandle)
    for candle in candles
)


# =====================================================
# Result
# =====================================================

print("\n========== NPAT GROWW HISTORICAL ==========\n")

print("Total candles:", len(candles))

print("\nFirst candle:")
print(candles[0])

print("\nLast candle:")
print(candles[-1])

print("\nGrowwProvider get_historical_data test passed.")
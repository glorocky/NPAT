import pyotp

from config import GROWW
from core.models import Quote
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
# Test Quote
# =====================================================

quote = provider.get_quote(
    trading_symbol="NIFTY",
    exchange="NSE",
    segment="CASH",
)


# =====================================================
# Validate NPAT Model
# =====================================================

assert isinstance(quote, Quote)

assert quote.symbol == "NIFTY"
assert quote.exchange == "NSE"

assert isinstance(quote.last_price, float)
assert isinstance(quote.open, float)
assert isinstance(quote.high, float)
assert isinstance(quote.low, float)
assert isinstance(quote.previous_close, float)

assert isinstance(quote.volume, int)


# =====================================================
# Result
# =====================================================

print("\n========== NPAT GROWW QUOTE ==========\n")

print(quote)

print("\nGrowwProvider get_quote test passed.")
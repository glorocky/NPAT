import pyotp

from config import GROWW
from growwapi.groww.client import GrowwAPI
from providers.groww_provider import GrowwProvider


# =====================================================
# Validate Configuration
# =====================================================

if not GROWW.api_key:
    raise RuntimeError(
        "GROWW_API_KEY is missing from .env"
    )

if not GROWW.totp_secret:
    raise RuntimeError(
        "GROWW_TOTP_SECRET is missing from .env"
    )


# =====================================================
# Generate Access Token
# =====================================================

totp = pyotp.TOTP(
    GROWW.totp_secret
).now()

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
# Test Expiries
# =====================================================

expiries = provider.get_expiries(
    exchange="NSE",
    underlying_symbol="NIFTY",
)


# =====================================================
# Validate NPAT Result
# =====================================================

assert isinstance(expiries, list)

assert len(expiries) > 0

assert all(
    isinstance(expiry, str)
    for expiry in expiries
)


# =====================================================
# Result
# =====================================================

print("\n========== NPAT GROWW EXPIRIES ==========\n")

print("Total expiries:", len(expiries))

print("\nFirst expiry:")
print(expiries[0])

print("\nLast expiry:")
print(expiries[-1])

print("\nAll expiries:")
for expiry in expiries:
    print(expiry)

print("\nGrowwProvider get_expiries test passed.")
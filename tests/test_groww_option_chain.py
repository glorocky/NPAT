
from datetime import date
import pyotp
from config import GROWW
from core.models import OptionData
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
# Select Nearest Active Expiry
# =====================================================

expiries = provider.get_expiries(
    exchange="NSE",
    underlying_symbol="NIFTY",
)

today = date.today()

active_expiries = sorted(
    expiry
    for expiry in expiries
    if date.fromisoformat(expiry) >= today
)

if not active_expiries:
    raise RuntimeError(
        "No active NIFTY option expiry is available."
    )

selected_expiry = active_expiries[0]

print(
    "Selected Expiry:",
    selected_expiry,
)

# =====================================================
# Test Option Chain
# =====================================================

option_chain = provider.get_option_chain(
    exchange="NSE",
    symbol="NIFTY",
    expiry=selected_expiry,
)


# =====================================================
# Diagnostic - Raw Groww Option Chain
# =====================================================

raw_chain = provider.api_client.get_option_chain(
    exchange="NSE",
    underlying="NIFTY",
    expiry_date=selected_expiry,
)

raw_strikes = raw_chain.get("strikes") or {}

if not raw_strikes:
    raise RuntimeError(
        "Raw Groww option chain contains no strikes."
    )


# =====================================================
# Find Strike Nearest To Underlying
# =====================================================

underlying_ltp = float(
    raw_chain["underlying_ltp"]
)

nearest_strike_key = min(
    raw_strikes.keys(),
    key=lambda strike:
    abs(
        float(strike)
        - underlying_ltp
    ),
)

nearest_strike = raw_strikes[
    nearest_strike_key
]

raw_ce = nearest_strike.get("CE") or {}
raw_pe = nearest_strike.get("PE") or {}


# =====================================================
# Display Raw ATM Data
# =====================================================

print(
    "\n========== RAW GROWW ATM STRIKE ==========\n"
)

print(
    "Underlying LTP :",
    underlying_ltp,
)

print(
    "Strike         :",
    nearest_strike_key,
)

print(
    "\nCE keys:"
)

print(
    sorted(raw_ce.keys())
)

print(
    "\nCE data:"
)

print(
    raw_ce
)

print(
    "\nPE keys:"
)

print(
    sorted(raw_pe.keys())
)

print(
    "\nPE data:"
)

print(
    raw_pe
)


# =====================================================
# Validate NPAT Result
# =====================================================

assert isinstance(option_chain, list)

assert len(option_chain) > 0

assert all(
    isinstance(option, OptionData)
    for option in option_chain
)


# =====================================================
# Validate Strike Ordering
# =====================================================

strike_prices = [
    option.strike_price
    for option in option_chain
]

assert strike_prices == sorted(strike_prices)


# =====================================================
# Result
# =====================================================

print("\n========== NPAT GROWW OPTION CHAIN ==========\n")

print("Total strikes:", len(option_chain))

print("\nFirst strike:")
print(option_chain[0])

print("\nMiddle strike:")
print(option_chain[len(option_chain) // 2])

print("\nLast strike:")
print(option_chain[-1])

print(
    "\nGrowwProvider get_option_chain test passed."
)
from datetime import date
import pyotp

from config import GROWW
from core.models import OptionGreeks
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
# Select ATM Strike
# =====================================================

option_chain = provider.get_option_chain(
    exchange="NSE",
    symbol="NIFTY",
    expiry=selected_expiry,
)

if not option_chain:
    raise RuntimeError(
        "NIFTY option chain is empty."
    )

underlying_price = float(
    option_chain[0].underlying_price
)

atm_option = min(
    option_chain,
    key=lambda option: abs(
        option.strike_price - underlying_price
    ),
)

atm_strike = atm_option.strike_price

print(
    "Underlying Price:",
    underlying_price,
)

print(
    "ATM Strike:",
    atm_strike,
)


# =====================================================
# Test Greeks
# =====================================================

greeks = provider.get_greeks(
    exchange="NSE",
    symbol="NIFTY",
    expiry=selected_expiry,
    strike=atm_strike,
    option_type="CE",
)


# =====================================================
# Validate NPAT Model
# =====================================================

assert isinstance(greeks, OptionGreeks)

assert isinstance(greeks.delta, float)
assert isinstance(greeks.gamma, float)
assert isinstance(greeks.theta, float)
assert isinstance(greeks.vega, float)
assert isinstance(greeks.rho, float)
assert isinstance(greeks.iv, float)


# =====================================================
# Basic Sanity Checks
# =====================================================

assert -1.0 <= greeks.delta <= 1.0

assert greeks.gamma >= 0.0

assert greeks.vega >= 0.0

assert greeks.iv >= 0.0


# =====================================================
# Result
# =====================================================

print("\n========== NPAT GROWW GREEKS ==========\n")

print(greeks)

print("\nDelta :", greeks.delta)
print("Gamma :", greeks.gamma)
print("Theta :", greeks.theta)
print("Vega  :", greeks.vega)
print("Rho   :", greeks.rho)
print("IV    :", greeks.iv)

print("\nGrowwProvider get_greeks test passed.")
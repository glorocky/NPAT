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

if not isinstance(
    access_token,
    str,
) or not access_token.strip():

    raise RuntimeError(
        "Groww access token generation failed."
    )


# =====================================================
# Initialize Provider
# =====================================================

provider = GrowwProvider(
    access_token=access_token
)

print(
    "GrowwProvider initialized successfully."
)


# =====================================================
# Instrument Master
# =====================================================

instruments = (
    provider.api_client.get_all_instruments()
)

print(
    "Total instruments:",
    len(instruments),
)

print(
    "\nColumns:"
)

print(
    instruments.columns.tolist()
)


# =====================================================
# Search VIX
# =====================================================

mask = instruments.astype(str).apply(
    lambda column:
    column.str.contains(
        "VIX",
        case=False,
        na=False,
    )
)

vix_rows = instruments[
    mask.any(axis=1)
]


# =====================================================
# Result
# =====================================================

print(
    "\n========== VIX INSTRUMENTS ==========\n"
)

if vix_rows.empty:

    print(
        "No VIX instruments found."
    )

else:

    print(
        vix_rows.to_string(
            index=False
        )
    )


print(
    "\nInstrument lookup test completed."
)

# =====================================================
# India VIX Live Quote
# =====================================================

vix_quote = provider.get_quote(
    trading_symbol="INDIAVIX",
    exchange="NSE",
    segment="CASH",
)


# =====================================================
# Display India VIX Quote
# =====================================================

print(
    "\n========== INDIA VIX LIVE QUOTE ==========\n"
)

print(
    "Symbol         :",
    vix_quote.symbol,
)

print(
    "Last Price     :",
    vix_quote.last_price,
)

print(
    "Open           :",
    vix_quote.open,
)

print(
    "High           :",
    vix_quote.high,
)

print(
    "Low            :",
    vix_quote.low,
)

print(
    "Previous Close :",
    vix_quote.previous_close,
)


# =====================================================
# Validate
# =====================================================

assert vix_quote.symbol == "INDIAVIX"
assert vix_quote.exchange == "NSE"

assert vix_quote.last_price > 0
assert vix_quote.open > 0
assert vix_quote.high > 0
assert vix_quote.low > 0
assert vix_quote.previous_close > 0

print(
    "\nIndia VIX live quote test passed."
)
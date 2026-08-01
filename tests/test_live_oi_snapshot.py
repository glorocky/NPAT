import pyotp

from config import GROWW
from core.models import OptionData
from growwapi.groww.client import GrowwAPI
from providers.groww_provider import GrowwProvider
from analytics.option_positioning_analytics import OptionPositioningAnalytics


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
# Test Option Chain
# =====================================================

option_chain = provider.get_option_chain(
    exchange="NSE",
    underlying="NIFTY",
    expiry_date="2026-07-28",
)

# =====================================================
# Diagnostic - Raw Groww Option Chain
# =====================================================

raw_chain = provider.api_client.get_option_chain(
    exchange="NSE",
    underlying="NIFTY",
    expiry_date="2026-07-28",
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

from datetime import datetime
import time

from storage.oi_snapshot_store import OISnapshotStore


# =====================================================
# Configuration
# =====================================================

SYMBOL = "NIFTY"
EXCHANGE = "NSE"
EXPIRY = "2026-07-28"


# =====================================================
# Initialize OI Store
# =====================================================

store = OISnapshotStore()


# =====================================================
# Poll 1
# =====================================================

options_1 = provider.get_option_chain(
    exchange=EXCHANGE,
    symbol=SYMBOL,
    expiry=EXPIRY,
)

time_1 = datetime.now()

recorded_1 = store.record_option_chain(
    symbol=SYMBOL,
    options=options_1,
    timestamp=time_1,
)

assert recorded_1 == (
    len(options_1) * 2
)


# =====================================================
# Small Delay
# =====================================================

time.sleep(2)


# =====================================================
# Poll 2
# =====================================================

options_2 = provider.get_option_chain(
    exchange=EXCHANGE,
    symbol=SYMBOL,
    expiry=EXPIRY,
)

time_2 = datetime.now()

recorded_2 = store.record_option_chain(
    symbol=SYMBOL,
    options=options_2,
    timestamp=time_2,
)

assert recorded_2 == (
    len(options_2) * 2
)


# =====================================================
# Find ATM
# =====================================================

underlying_price = (
    options_2[0].underlying_price
)

atm_option = min(
    options_2,
    key=lambda option:
    abs(
        option.strike_price
        - underlying_price
    ),
)

atm_strike = (
    atm_option.strike_price
)


# =====================================================
# Retrieve ATM CE
# =====================================================

previous_ce = store.get_previous(
    SYMBOL,
    EXPIRY,
    atm_strike,
    "CE",
)

current_ce = store.get_current(
    SYMBOL,
    EXPIRY,
    atm_strike,
    "CE",
)


# =====================================================
# Retrieve ATM PE
# =====================================================

previous_pe = store.get_previous(
    SYMBOL,
    EXPIRY,
    atm_strike,
    "PE",
)

current_pe = store.get_current(
    SYMBOL,
    EXPIRY,
    atm_strike,
    "PE",
)


# =====================================================
# Validate
# =====================================================

assert previous_ce is not None
assert current_ce is not None

assert previous_pe is not None
assert current_pe is not None

# =====================================================
# Live Full Chain Positioning
# =====================================================

chain_positioning = (
    OptionPositioningAnalytics.analyze_chain(
        symbol=SYMBOL,
        options=options_2,
        store=store,
    )
)


# =====================================================
# Live Positioning Summary
# =====================================================

positioning_summary = (
    OptionPositioningAnalytics.summarize(
        chain_positioning
    )
)


# =====================================================
# Validate Live Positioning
# =====================================================

assert len(chain_positioning) > 0

assert (
    positioning_summary.total_contracts
    == len(chain_positioning)
)

assert (
    positioning_summary.ce_total
    + positioning_summary.pe_total
    == positioning_summary.total_contracts
)

classification_total = (
    positioning_summary.long_buildup
    + positioning_summary.short_buildup
    + positioning_summary.long_unwinding
    + positioning_summary.short_covering
    + positioning_summary.neutral
)

assert (
    classification_total
    == positioning_summary.total_contracts
)


# =====================================================
# Live ATM Window Positioning
# =====================================================

atm_positioning = (
    OptionPositioningAnalytics.filter_atm_window(
        results=chain_positioning,
        atm_strike=atm_strike,
        strikes_each_side=5,
    )
)

atm_summary = (
    OptionPositioningAnalytics.summarize(
        atm_positioning
    )
)


# =====================================================
# Validate Live ATM Window
# =====================================================

assert len(atm_positioning) > 0

assert (
    atm_summary.total_contracts
    == len(atm_positioning)
)

assert (
    atm_summary.ce_total
    + atm_summary.pe_total
    == atm_summary.total_contracts
)

assert all(
    result
    in chain_positioning
    for result in atm_positioning
)

# =====================================================
# Live ATM OI Rankings
# =====================================================

atm_oi_additions = (
    OptionPositioningAnalytics.rank_oi_additions(
        results=atm_positioning,
        limit=5,
    )
)

atm_oi_reductions = (
    OptionPositioningAnalytics.rank_oi_reductions(
        results=atm_positioning,
        limit=5,
    )
)


# =====================================================
# Validate Live ATM OI Rankings
# =====================================================

assert all(
    result.oi_change > 0
    for result in atm_oi_additions
)

assert all(
    result.oi_change < 0
    for result in atm_oi_reductions
)

assert len(atm_oi_additions) <= 5
assert len(atm_oi_reductions) <= 5

# =====================================================
# Result
# =====================================================

print(
    "\n========== NPAT LIVE OI SNAPSHOT ==========\n"
)

print(
    "Underlying Price     :",
    underlying_price,
)

print(
    "ATM Strike           :",
    atm_strike,
)

print(
    "Strikes              :",
    len(options_2),
)

print(
    "Contracts Recorded   :",
    recorded_2,
)

print()

print(
    "ATM CE Previous OI   :",
    previous_ce.open_interest,
)

print(
    "ATM CE Current OI    :",
    current_ce.open_interest,
)

print(
    "ATM CE Interval ΔOI  :",
    current_ce.open_interest
    - previous_ce.open_interest,
)

print()

print(
    "ATM PE Previous OI   :",
    previous_pe.open_interest,
)

print(
    "ATM PE Current OI    :",
    current_pe.open_interest,
)

print(
    "ATM PE Interval ΔOI  :",
    current_pe.open_interest
    - previous_pe.open_interest,
)

print()

print(
    "Poll 1 Time          :",
    time_1,
)

print(
    "Poll 2 Time          :",
    time_2,
)

# =====================================================
# Live Positioning Result
# =====================================================

print(
    "\n========== NPAT LIVE POSITIONING ==========\n"
)

print(
    "Contracts Analyzed   :",
    positioning_summary.total_contracts,
)

print(
    "CE Contracts         :",
    positioning_summary.ce_total,
)

print(
    "PE Contracts         :",
    positioning_summary.pe_total,
)

print()

print(
    "Long Buildup         :",
    positioning_summary.long_buildup,
)

print(
    "Short Buildup        :",
    positioning_summary.short_buildup,
)

print(
    "Long Unwinding       :",
    positioning_summary.long_unwinding,
)

print(
    "Short Covering       :",
    positioning_summary.short_covering,
)

print(
    "Neutral              :",
    positioning_summary.neutral,
)


# =====================================================
# Live CE / PE Summary
# =====================================================

print(
    "\n========== NPAT LIVE CE / PE POSITIONING ==========\n"
)

print("CE")
print(
    "Long Buildup         :",
    positioning_summary.ce_long_buildup,
)
print(
    "Short Buildup        :",
    positioning_summary.ce_short_buildup,
)
print(
    "Long Unwinding       :",
    positioning_summary.ce_long_unwinding,
)
print(
    "Short Covering       :",
    positioning_summary.ce_short_covering,
)
print(
    "Neutral              :",
    positioning_summary.ce_neutral,
)

print()

print("PE")
print(
    "Long Buildup         :",
    positioning_summary.pe_long_buildup,
)
print(
    "Short Buildup        :",
    positioning_summary.pe_short_buildup,
)
print(
    "Long Unwinding       :",
    positioning_summary.pe_long_unwinding,
)
print(
    "Short Covering       :",
    positioning_summary.pe_short_covering,
)
print(
    "Neutral              :",
    positioning_summary.pe_neutral,
)

# =====================================================
# Live ATM Window Result
# =====================================================

print(
    "\n========== NPAT LIVE ATM WINDOW POSITIONING ==========\n"
)

print(
    "ATM Strike             :",
    atm_strike,
)

print(
    "Strikes Each Side      :",
    5,
)

print(
    "Contracts Analyzed     :",
    atm_summary.total_contracts,
)

print()

for result in atm_positioning:

    print(
        f"{result.strike_price} "
        f"{result.option_type} "
        f"{result.classification:<16} "
        f"| Price Δ {result.price_change:>7.2f} "
        f"| OI Δ {result.oi_change:>6}"
    )

print()

print(
    "Long Buildup           :",
    atm_summary.long_buildup,
)

print(
    "Short Buildup          :",
    atm_summary.short_buildup,
)

print(
    "Long Unwinding         :",
    atm_summary.long_unwinding,
)

print(
    "Short Covering         :",
    atm_summary.short_covering,
)

print(
    "Neutral                :",
    atm_summary.neutral,
)

# =====================================================
# Live ATM OI Ranking Result
# =====================================================

print(
    "\n========== NPAT LIVE ATM TOP OI ADDITIONS ==========\n"
)

if atm_oi_additions:

    for rank, result in enumerate(
        atm_oi_additions,
        start=1,
    ):
        print(
            f"{rank:>2}. "
            f"{result.strike_price} "
            f"{result.option_type} "
            f"{result.classification:<16} "
            f"| OI Δ +{result.oi_change} "
            f"| OI Δ% {result.oi_change_pct:>7.2f}% "
            f"| Price Δ {result.price_change:>7.2f}"
        )

else:
    print("No OI additions detected.")


print(
    "\n========== NPAT LIVE ATM TOP OI REDUCTIONS ==========\n"
)

if atm_oi_reductions:

    for rank, result in enumerate(
        atm_oi_reductions,
        start=1,
    ):
        print(
            f"{rank:>2}. "
            f"{result.strike_price} "
            f"{result.option_type} "
            f"{result.classification:<16} "
            f"| OI Δ {result.oi_change} "
            f"| OI Δ% {result.oi_change_pct:>7.2f}% "
            f"| Price Δ {result.price_change:>7.2f}"
        )

else:
    print("No OI reductions detected.")

# =====================================================
# Final Result
# =====================================================

print(
    "\nLive OI Snapshot integration test passed."
)

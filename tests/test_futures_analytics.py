from core.models import FutureData, FuturesAnalysis
from analytics.futures_analytics import FuturesAnalytics


# =========================================================
# Test Helper
# =========================================================

def make_future(
    previous_price: float,
    current_price: float,
    previous_oi: int,
    current_oi: int,
    buy_quantity: int = 120000,
    sell_quantity: int = 100000,
) -> FutureData:

    return FutureData(
        symbol="NIFTY",
        exchange="NSE",
        trading_symbol="NIFTYTESTFUT",
        expiry="2026-07-28",

        lot_size=65,
        exchange_token="12345",

        last_price=current_price,
        open=previous_price,
        high=max(previous_price, current_price),
        low=min(previous_price, current_price),
        previous_close=previous_price,

        open_interest=current_oi,
        previous_open_interest=previous_oi,

        # FutureData contains raw provider values, but
        # FuturesAnalytics independently calculates changes.
        oi_change=current_oi - previous_oi,

        oi_change_pct=(
            ((current_oi - previous_oi) / previous_oi) * 100
            if previous_oi > 0
            else 0.0
        ),

        volume=50000,
        last_trade_quantity=65,

        total_buy_quantity=buy_quantity,
        total_sell_quantity=sell_quantity,
    )


# =========================================================
# Long Buildup
# Price ↑ + OI ↑
# =========================================================

long_buildup = FuturesAnalytics.analyze(
    future=make_future(
        previous_price=23800,
        current_price=23850,
        previous_oi=150000,
        current_oi=160000,
    ),
    spot_price=23750,
)

assert isinstance(
    long_buildup,
    FuturesAnalysis,
)

assert (
    long_buildup.positioning
    == "LONG_BUILDUP"
)

assert long_buildup.price_change == 50.0
assert long_buildup.oi_change == 10000


# =========================================================
# Short Buildup
# Price ↓ + OI ↑
# =========================================================

short_buildup = FuturesAnalytics.analyze(
    future=make_future(
        previous_price=23800,
        current_price=23750,
        previous_oi=150000,
        current_oi=160000,
    ),
    spot_price=23700,
)

assert (
    short_buildup.positioning
    == "SHORT_BUILDUP"
)


# =========================================================
# Long Unwinding
# Price ↓ + OI ↓
# =========================================================

long_unwinding = FuturesAnalytics.analyze(
    future=make_future(
        previous_price=23800,
        current_price=23750,
        previous_oi=160000,
        current_oi=150000,
    ),
    spot_price=23700,
)

assert (
    long_unwinding.positioning
    == "LONG_UNWINDING"
)


# =========================================================
# Short Covering
# Price ↑ + OI ↓
# =========================================================

short_covering = FuturesAnalytics.analyze(
    future=make_future(
        previous_price=23800,
        current_price=23850,
        previous_oi=160000,
        current_oi=150000,
    ),
    spot_price=23750,
)

assert (
    short_covering.positioning
    == "SHORT_COVERING"
)


# =========================================================
# Neutral
# Price unchanged + OI unchanged
# =========================================================

neutral = FuturesAnalytics.analyze(
    future=make_future(
        previous_price=23800,
        current_price=23800,
        previous_oi=150000,
        current_oi=150000,
    ),
    spot_price=23750,
)

assert neutral.positioning == "NEUTRAL"


# =========================================================
# Basis
# =========================================================

assert long_buildup.basis == 100.0

expected_basis_pct = (
    100.0 / 23750.0
) * 100.0

assert abs(
    long_buildup.basis_pct
    - expected_basis_pct
) < 0.0001


# =========================================================
# Quantity Imbalance
# =========================================================

assert (
    long_buildup.quantity_imbalance
    == 20000
)

expected_imbalance_pct = (
    20000 / 220000
) * 100.0

assert abs(
    long_buildup.quantity_imbalance_pct
    - expected_imbalance_pct
) < 0.0001


# =========================================================
# Output
# =========================================================

print(
    "\n========== NPAT FUTURES ANALYTICS ==========\n"
)

print(
    "Long Buildup       :",
    long_buildup.positioning,
    "| Price Δ",
    long_buildup.price_change,
    "| OI Δ",
    long_buildup.oi_change,
)

print(
    "Short Buildup      :",
    short_buildup.positioning,
)

print(
    "Long Unwinding     :",
    long_unwinding.positioning,
)

print(
    "Short Covering     :",
    short_covering.positioning,
)

print(
    "Neutral            :",
    neutral.positioning,
)

print()

print(
    "Basis              :",
    round(long_buildup.basis, 4),
)

print(
    "Basis %            :",
    round(long_buildup.basis_pct, 4),
)

print(
    "Quantity Imbalance :",
    long_buildup.quantity_imbalance,
)

print(
    "Imbalance %        :",
    round(
        long_buildup.quantity_imbalance_pct,
        4,
    ),
)


print(
    "\nFuturesAnalytics calculation test passed."
)
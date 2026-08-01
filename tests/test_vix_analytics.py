"""
NPAT - VIX Analytics Calculation Test

Tests the VIX range engine with fixed values.
No provider/API calls are involved.
"""

from analytics.vix_analytics import VixAnalytics
from core.models import VixRangeAnalysis


# =====================================================
# Fixed Test Inputs
# =====================================================

SYMBOL = "NIFTY"

REFERENCE_PRICE = 23700.0
INDIA_VIX = 15.0

DAY_OPEN = 23720.0
DAY_HIGH = 23850.0
DAY_LOW = 23620.0
CURRENT_PRICE = 23800.0


# =====================================================
# Analyze
# =====================================================

analysis = VixAnalytics.analyze_daily_range(
    symbol=SYMBOL,
    reference_price=REFERENCE_PRICE,
    india_vix=INDIA_VIX,
    day_open=DAY_OPEN,
    day_high=DAY_HIGH,
    day_low=DAY_LOW,
    current_price=CURRENT_PRICE,
)


# =====================================================
# Basic Validation
# =====================================================

assert isinstance(
    analysis,
    VixRangeAnalysis,
)

assert analysis.symbol == SYMBOL

assert analysis.reference_price == REFERENCE_PRICE
assert analysis.india_vix == INDIA_VIX

assert analysis.expected_move_pct > 0
assert analysis.expected_move_points > 0

assert analysis.expected_lower < REFERENCE_PRICE
assert analysis.expected_upper > REFERENCE_PRICE


# =====================================================
# Expected Range Validation
# =====================================================

assert abs(
    analysis.expected_total_range
    - (
        analysis.expected_move_points * 2
    )
) < 1e-9


# =====================================================
# Actual Range Validation
# =====================================================

assert analysis.actual_range == (
    DAY_HIGH - DAY_LOW
)


# =====================================================
# Directional Validation
# =====================================================

assert analysis.upside_achieved_points == (
    DAY_HIGH - REFERENCE_PRICE
)

assert analysis.downside_achieved_points == (
    REFERENCE_PRICE - DAY_LOW
)


# =====================================================
# Remaining Range Validation
# =====================================================

assert analysis.upside_remaining >= 0
assert analysis.downside_remaining >= 0


# =====================================================
# Display
# =====================================================

print(
    "\n========== NPAT VIX RANGE ANALYTICS ==========\n"
)

print("Symbol                 :", analysis.symbol)
print("Reference Price        :", analysis.reference_price)
print("India VIX              :", analysis.india_vix)

print()

print(
    "Expected Daily Move %  :",
    round(
        analysis.expected_move_pct,
        4,
    ),
    "%",
)

print(
    "Expected Move Points   :",
    round(
        analysis.expected_move_points,
        2,
    ),
)

print(
    "Expected Lower         :",
    round(
        analysis.expected_lower,
        2,
    ),
)

print(
    "Expected Upper         :",
    round(
        analysis.expected_upper,
        2,
    ),
)

print(
    "Expected Total Range   :",
    round(
        analysis.expected_total_range,
        2,
    ),
)

print()

print("Day Open               :", analysis.day_open)
print("Day High               :", analysis.day_high)
print("Day Low                :", analysis.day_low)
print("Current Price          :", analysis.current_price)

print()

print(
    "Actual Range           :",
    round(
        analysis.actual_range,
        2,
    ),
)

print(
    "Actual Range %         :",
    round(
        analysis.actual_range_pct,
        4,
    ),
    "%",
)

print(
    "Range Achieved         :",
    round(
        analysis.range_achieved_pct,
        2,
    ),
    "%",
)

print()

print(
    "Upside Achieved        :",
    round(
        analysis.upside_achieved_points,
        2,
    ),
    "points",
)

print(
    "Upside Achieved %      :",
    round(
        analysis.upside_achieved_pct,
        2,
    ),
    "%",
)

print(
    "Downside Achieved      :",
    round(
        analysis.downside_achieved_points,
        2,
    ),
    "points",
)

print(
    "Downside Achieved %    :",
    round(
        analysis.downside_achieved_pct,
        2,
    ),
    "%",
)

print()

print(
    "Upside Remaining       :",
    round(
        analysis.upside_remaining,
        2,
    ),
)

print(
    "Downside Remaining     :",
    round(
        analysis.downside_remaining,
        2,
    ),
)

print()

print(
    "Upper Range Exceeded   :",
    analysis.upper_range_exceeded,
)

print(
    "Lower Range Exceeded   :",
    analysis.lower_range_exceeded,
)

print(
    "Expected Range Exceeded:",
    analysis.expected_range_exceeded,
)


# =====================================================
# Final Result
# =====================================================

print(
    "\nVixAnalytics calculation test passed."
)
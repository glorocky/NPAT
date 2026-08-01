from analytics.positioning_analytics import PositioningAnalytics
from core.models import PositioningAnalysis


# =====================================================
# Test Cases
# =====================================================

test_cases = [
    {
        "name": "Long Buildup",
        "previous_price": 100.0,
        "current_price": 110.0,
        "previous_oi": 10000,
        "current_oi": 12000,
        "expected": "LONG_BUILDUP",
    },
    {
        "name": "Short Buildup",
        "previous_price": 100.0,
        "current_price": 90.0,
        "previous_oi": 10000,
        "current_oi": 12000,
        "expected": "SHORT_BUILDUP",
    },
    {
        "name": "Long Unwinding",
        "previous_price": 100.0,
        "current_price": 90.0,
        "previous_oi": 10000,
        "current_oi": 8000,
        "expected": "LONG_UNWINDING",
    },
    {
        "name": "Short Covering",
        "previous_price": 100.0,
        "current_price": 110.0,
        "previous_oi": 10000,
        "current_oi": 8000,
        "expected": "SHORT_COVERING",
    },
    {
        "name": "Neutral",
        "previous_price": 100.0,
        "current_price": 100.0,
        "previous_oi": 10000,
        "current_oi": 10000,
        "expected": "NEUTRAL",
    },
]


# =====================================================
# Execute Tests
# =====================================================

results = []

for case in test_cases:

    analysis = PositioningAnalytics.analyze(
        symbol="NIFTY",
        expiry="2026-07-28",
        strike_price=23750,
        option_type="CE",
        previous_price=case["previous_price"],
        current_price=case["current_price"],
        previous_oi=case["previous_oi"],
        current_oi=case["current_oi"],
    )

    assert isinstance(
        analysis,
        PositioningAnalysis,
    )

    assert (
        analysis.classification
        == case["expected"]
    )

    results.append(
        (
            case["name"],
            analysis,
        )
    )


# =====================================================
# Validate Individual Changes
# =====================================================

long_buildup = results[0][1]

assert long_buildup.price_change == 10.0
assert long_buildup.oi_change == 2000

assert abs(
    long_buildup.price_change_pct
    - 10.0
) < 1e-9

assert abs(
    long_buildup.oi_change_pct
    - 20.0
) < 1e-9


# =====================================================
# Result
# =====================================================

print(
    "\n========== NPAT POSITIONING ANALYTICS ==========\n"
)

for name, analysis in results:

    print(
        f"{name:<18} : "
        f"{analysis.classification:<16} "
        f"| Price Δ {analysis.price_change:>7.2f} "
        f"| OI Δ {analysis.oi_change:>6}"
    )

print(
    "\nPositioningAnalytics calculation test passed."
)
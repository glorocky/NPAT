from core.models import OIAnalysis
from analytics.oi_analytics import OIAnalytics


# =====================================================
# Test Data
# =====================================================

SYMBOL = "NIFTY"
EXPIRY = "2026-07-28"
STRIKE = 23750
OPTION_TYPE = "CE"

CURRENT_OI = 27188
SESSION_BASELINE_OI = 5783
PREVIOUS_OI = 26500


# =====================================================
# OI Analytics
# =====================================================

analysis = OIAnalytics.analyze(
    symbol=SYMBOL,
    expiry=EXPIRY,
    strike_price=STRIKE,
    option_type=OPTION_TYPE,
    current_oi=CURRENT_OI,
    session_baseline_oi=SESSION_BASELINE_OI,
    previous_oi=PREVIOUS_OI,
)


# =====================================================
# Validate Model
# =====================================================

assert isinstance(
    analysis,
    OIAnalysis,
)

assert analysis.symbol == "NIFTY"
assert analysis.expiry == EXPIRY
assert analysis.strike_price == 23750
assert analysis.option_type == "CE"


# =====================================================
# Validate Session OI
# =====================================================

assert analysis.current_oi == 27188
assert analysis.session_baseline_oi == 5783

assert analysis.session_change_oi == 21405

expected_session_pct = (
    21405
    / 5783
    * 100.0
)

assert abs(
    analysis.session_change_oi_pct
    - expected_session_pct
) < 1e-9


# =====================================================
# Validate Interval OI
# =====================================================

assert analysis.previous_oi == 26500

assert analysis.interval_change_oi == 688

expected_interval_pct = (
    688
    / 26500
    * 100.0
)

assert abs(
    analysis.interval_change_oi_pct
    - expected_interval_pct
) < 1e-9


# =====================================================
# Result
# =====================================================

print(
    "\n========== NPAT OI ANALYTICS ==========\n"
)

print(
    "Symbol                  :",
    analysis.symbol,
)

print(
    "Expiry                  :",
    analysis.expiry,
)

print(
    "Strike                  :",
    analysis.strike_price,
)

print(
    "Option Type             :",
    analysis.option_type,
)

print()

print(
    "Current OI              :",
    analysis.current_oi,
)

print(
    "Session Baseline OI     :",
    analysis.session_baseline_oi,
)

print(
    "Session Change OI       :",
    analysis.session_change_oi,
)

print(
    "Session Change OI %     :",
    round(
        analysis.session_change_oi_pct,
        2,
    ),
    "%",
)

print()

print(
    "Previous Snapshot OI    :",
    analysis.previous_oi,
)

print(
    "Interval Change OI      :",
    analysis.interval_change_oi,
)

print(
    "Interval Change OI %    :",
    round(
        analysis.interval_change_oi_pct,
        2,
    ),
    "%",
)

print(
    "\nOIAnalytics calculation test passed."
)
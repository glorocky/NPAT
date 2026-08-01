from datetime import datetime, timedelta

from analytics.oi_analytics import OIAnalytics
from core.models import OIAnalysis, OISnapshot
from storage.oi_snapshot_store import OISnapshotStore


# =====================================================
# Contract
# =====================================================

SYMBOL = "NIFTY"
EXPIRY = "2026-07-28"
STRIKE = 23750
OPTION_TYPE = "CE"


# =====================================================
# Initialize Store
# =====================================================

store = OISnapshotStore()

base_time = datetime(
    2026,
    7,
    24,
    9,
    15,
)


# =====================================================
# Explicit Session Baseline
# =====================================================

baseline = OISnapshot(
    symbol=SYMBOL,
    expiry=EXPIRY,
    strike_price=STRIKE,
    option_type=OPTION_TYPE,
    open_interest=5783,
    price=100.0,
    timestamp=base_time,
)

store.set_session_baseline(
    baseline
)


# =====================================================
# Snapshot 1
# =====================================================

snapshot_1 = OISnapshot(
    symbol=SYMBOL,
    expiry=EXPIRY,
    strike_price=STRIKE,
    option_type=OPTION_TYPE,
    open_interest=25000,
    price=110.0,
    timestamp=base_time + timedelta(minutes=1),
)

store.record(
    snapshot_1
)


# =====================================================
# Snapshot 2
# =====================================================

snapshot_2 = OISnapshot(
    symbol=SYMBOL,
    expiry=EXPIRY,
    strike_price=STRIKE,
    option_type=OPTION_TYPE,
    open_interest=26500,
    price=120.0,
    timestamp=base_time + timedelta(minutes=2),
)

store.record(
    snapshot_2
)


# =====================================================
# Snapshot 3
# =====================================================

snapshot_3 = OISnapshot(
    symbol=SYMBOL,
    expiry=EXPIRY,
    strike_price=STRIKE,
    option_type=OPTION_TYPE,
    open_interest=27188,
    price=130.0,
    timestamp=base_time + timedelta(minutes=3),
)

store.record(
    snapshot_3
)


# =====================================================
# Retrieve Store State
# =====================================================

current = store.get_current(
    SYMBOL,
    EXPIRY,
    STRIKE,
    OPTION_TYPE,
)

previous = store.get_previous(
    SYMBOL,
    EXPIRY,
    STRIKE,
    OPTION_TYPE,
)

session_baseline = store.get_session_baseline(
    SYMBOL,
    EXPIRY,
    STRIKE,
    OPTION_TYPE,
)


# =====================================================
# Validate Store
# =====================================================

assert current is not None
assert previous is not None
assert session_baseline is not None

assert current.open_interest == 27188
assert previous.open_interest == 26500

# Critical:
# record() must NOT replace the session baseline.

assert session_baseline.open_interest == 5783


# =====================================================
# Connect Store -> OIAnalytics
# =====================================================

analysis = OIAnalytics.analyze(
    symbol=SYMBOL,
    expiry=EXPIRY,
    strike_price=STRIKE,
    option_type=OPTION_TYPE,

    current_oi=current.open_interest,

    session_baseline_oi=(
        session_baseline.open_interest
    ),

    previous_oi=previous.open_interest,
)


# =====================================================
# Validate Analytics
# =====================================================

assert isinstance(
    analysis,
    OIAnalysis,
)

assert analysis.session_change_oi == 21405
assert analysis.interval_change_oi == 688


# =====================================================
# Result
# =====================================================

print(
    "\n========== NPAT OI SNAPSHOT STORE ==========\n"
)

print(
    "Session Baseline OI :",
    session_baseline.open_interest,
)

print(
    "Previous Snapshot OI:",
    previous.open_interest,
)

print(
    "Current OI          :",
    current.open_interest,
)

print()

print(
    "Session Change OI   :",
    analysis.session_change_oi,
)

print(
    "Session Change OI % :",
    round(
        analysis.session_change_oi_pct,
        2,
    ),
    "%",
)

print()

print(
    "Interval Change OI  :",
    analysis.interval_change_oi,
)

print(
    "Interval Change OI %:",
    round(
        analysis.interval_change_oi_pct,
        2,
    ),
    "%",
)

print(
    "\nOI Snapshot Store integration test passed."
)
from datetime import datetime, timedelta

from core.models import OptionData
from storage.oi_snapshot_store import OISnapshotStore
from analytics.positioning_analytics import PositioningAnalytics
from analytics.option_positioning_analytics import OptionPositioningAnalytics


# =====================================================
# Configuration
# =====================================================

SYMBOL = "NIFTY"
EXPIRY = "2026-07-28"

store = OISnapshotStore()

time_1 = datetime(
    2026,
    7,
    24,
    10,
    0,
)

time_2 = time_1 + timedelta(
    minutes=1
)


# =====================================================
# Polling Cycle 1
# =====================================================

options_1 = [
    OptionData(
        strike_price=23700,
        expiry=EXPIRY,
        underlying_price=23750.0,
        call_oi=10000,
        call_change_oi=0,
        call_volume=1000,
        call_iv=12.0,
        call_ltp=150.0,
        put_oi=20000,
        put_change_oi=0,
        put_volume=1500,
        put_iv=13.0,
        put_ltp=100.0,
    ),

    OptionData(
        strike_price=23750,
        expiry=EXPIRY,
        underlying_price=23750.0,
        call_oi=25000,
        call_change_oi=0,
        call_volume=2000,
        call_iv=11.5,
        call_ltp=125.0,
        put_oi=50000,
        put_change_oi=0,
        put_volume=2500,
        put_iv=12.0,
        put_ltp=120.0,
    ),

    OptionData(
        strike_price=23800,
        expiry=EXPIRY,
        underlying_price=23750.0,
        call_oi=30000,
        call_change_oi=0,
        call_volume=1800,
        call_iv=12.5,
        call_ltp=95.0,
        put_oi=22000,
        put_change_oi=0,
        put_volume=1600,
        put_iv=13.0,
        put_ltp=145.0,
    ),
]


recorded_1 = store.record_option_chain(
    symbol=SYMBOL,
    options=options_1,
    timestamp=time_1,
)

assert recorded_1 == 6


# =====================================================
# Validate First Poll
# =====================================================

first_ce = store.get_current(
    SYMBOL,
    EXPIRY,
    23750,
    "CE",
)

first_pe = store.get_current(
    SYMBOL,
    EXPIRY,
    23750,
    "PE",
)

assert first_ce is not None
assert first_pe is not None

assert first_ce.open_interest == 25000
assert first_pe.open_interest == 50000

# No previous snapshot should exist after only one poll.

assert store.get_previous(
    SYMBOL,
    EXPIRY,
    23750,
    "CE",
) is None

assert store.get_previous(
    SYMBOL,
    EXPIRY,
    23750,
    "PE",
) is None


# =====================================================
# Polling Cycle 2
# =====================================================

options_2 = [
    OptionData(
        strike_price=23700,
        expiry=EXPIRY,
        underlying_price=23760.0,
        call_oi=10500,
        call_change_oi=0,
        call_volume=1200,
        call_iv=12.1,
        call_ltp=158.0,
        put_oi=19800,
        put_change_oi=0,
        put_volume=1650,
        put_iv=12.9,
        put_ltp=94.0,
    ),

    OptionData(
        strike_price=23750,
        expiry=EXPIRY,
        underlying_price=23760.0,
        call_oi=27188,
        call_change_oi=0,
        call_volume=2200,
        call_iv=11.6,
        call_ltp=130.0,
        put_oi=59894,
        put_change_oi=0,
        put_volume=2800,
        put_iv=12.1,
        put_ltp=115.0,
    ),

    OptionData(
        strike_price=23800,
        expiry=EXPIRY,
        underlying_price=23760.0,
        call_oi=29500,
        call_change_oi=0,
        call_volume=1950,
        call_iv=12.4,
        call_ltp=100.0,
        put_oi=23000,
        put_change_oi=0,
        put_volume=1750,
        put_iv=13.1,
        put_ltp=140.0,
    ),
]


recorded_2 = store.record_option_chain(
    symbol=SYMBOL,
    options=options_2,
    timestamp=time_2,
)

assert recorded_2 == 6


# =====================================================
# Validate Current / Previous
# =====================================================

current_ce = store.get_current(
    SYMBOL,
    EXPIRY,
    23750,
    "CE",
)

previous_ce = store.get_previous(
    SYMBOL,
    EXPIRY,
    23750,
    "CE",
)

current_pe = store.get_current(
    SYMBOL,
    EXPIRY,
    23750,
    "PE",
)

previous_pe = store.get_previous(
    SYMBOL,
    EXPIRY,
    23750,
    "PE",
)

assert current_ce is not None
assert previous_ce is not None
assert current_pe is not None
assert previous_pe is not None

assert previous_ce.open_interest == 25000
assert current_ce.open_interest == 27188

assert previous_pe.open_interest == 50000
assert current_pe.open_interest == 59894

# =====================================================
# Validate Synchronized Price Snapshots
# =====================================================

assert previous_ce.price == 125.0
assert current_ce.price == 130.0

assert previous_pe.price == 120.0
assert current_pe.price == 115.0

# =====================================================
# Positioning Analytics
# =====================================================

ce_positioning = PositioningAnalytics.analyze(
    symbol=SYMBOL,
    expiry=EXPIRY,
    strike_price=23750,
    option_type="CE",
    previous_price=previous_ce.price,
    current_price=current_ce.price,
    previous_oi=previous_ce.open_interest,
    current_oi=current_ce.open_interest,
)

pe_positioning = PositioningAnalytics.analyze(
    symbol=SYMBOL,
    expiry=EXPIRY,
    strike_price=23750,
    option_type="PE",
    previous_price=previous_pe.price,
    current_price=current_pe.price,
    previous_oi=previous_pe.open_interest,
    current_oi=current_pe.open_interest,
)


# =====================================================
# Validate Positioning
# =====================================================

assert (
    ce_positioning.classification
    == "LONG_BUILDUP"
)

assert (
    pe_positioning.classification
    == "SHORT_BUILDUP"
)


# =====================================================
# Full Chain Positioning Analytics
# =====================================================

chain_positioning = OptionPositioningAnalytics.analyze_chain(
    symbol=SYMBOL,
    options=options_2,
    store=store,
)


# =====================================================
# Validate Full Chain
# =====================================================

assert len(chain_positioning) == 6

assert all(
    result.symbol == SYMBOL
    for result in chain_positioning
)

assert {
    result.strike_price
    for result in chain_positioning
} == {
    23700,
    23750,
    23800,
}

assert {
    result.option_type
    for result in chain_positioning
} == {
    "CE",
    "PE",
}


# =====================================================
# Find 23750 Results
# =====================================================

chain_23750_ce = next(
    result
    for result in chain_positioning
    if (
        result.strike_price == 23750
        and result.option_type == "CE"
    )
)

chain_23750_pe = next(
    result
    for result in chain_positioning
    if (
        result.strike_price == 23750
        and result.option_type == "PE"
    )
)

assert (
    chain_23750_ce.classification
    == "LONG_BUILDUP"
)

assert (
    chain_23750_pe.classification
    == "SHORT_BUILDUP"
)

# =====================================================
# Positioning Summary
# =====================================================

positioning_summary = (
    OptionPositioningAnalytics.summarize(
        chain_positioning
    )
)


# =====================================================
# Validate Positioning Summary
# =====================================================

assert positioning_summary.total_contracts == 6

# Combined

assert positioning_summary.long_buildup == 2
assert positioning_summary.short_buildup == 2
assert positioning_summary.long_unwinding == 1
assert positioning_summary.short_covering == 1
assert positioning_summary.neutral == 0

# CE

assert positioning_summary.ce_total == 3

assert positioning_summary.ce_long_buildup == 2
assert positioning_summary.ce_short_buildup == 0
assert positioning_summary.ce_long_unwinding == 0
assert positioning_summary.ce_short_covering == 1
assert positioning_summary.ce_neutral == 0

# PE

assert positioning_summary.pe_total == 3

assert positioning_summary.pe_long_buildup == 0
assert positioning_summary.pe_short_buildup == 2
assert positioning_summary.pe_long_unwinding == 1
assert positioning_summary.pe_short_covering == 0
assert positioning_summary.pe_neutral == 0

# =====================================================
# ATM Window Positioning
# =====================================================

atm_positioning = (
    OptionPositioningAnalytics.filter_atm_window(
        results=chain_positioning,
        atm_strike=23750,
        strikes_each_side=1,
    )
)


# =====================================================
# Validate ATM Window
# =====================================================

assert len(atm_positioning) == 6

assert {
    result.strike_price
    for result in atm_positioning
} == {
    23700,
    23750,
    23800,
}

assert {
    result.option_type
    for result in atm_positioning
} == {
    "CE",
    "PE",
}


# =====================================================
# ATM Window Summary
# =====================================================

atm_summary = (
    OptionPositioningAnalytics.summarize(
        atm_positioning
    )
)

assert atm_summary.total_contracts == 6
assert atm_summary.ce_total == 3
assert atm_summary.pe_total == 3

# =====================================================
# Positioning OI Ranking
# =====================================================

oi_ranking = (
    OptionPositioningAnalytics.rank_by_oi_change(
        results=chain_positioning,
        limit=6,
    )
)

ce_oi_ranking = (
    OptionPositioningAnalytics.rank_by_oi_change(
        results=chain_positioning,
        limit=3,
        option_type="CE",
    )
)

pe_oi_ranking = (
    OptionPositioningAnalytics.rank_by_oi_change(
        results=chain_positioning,
        limit=3,
        option_type="PE",
    )
)


# =====================================================
# Validate OI Ranking
# =====================================================

assert len(oi_ranking) == 6
assert len(ce_oi_ranking) == 3
assert len(pe_oi_ranking) == 3

assert all(
    item.option_type == "CE"
    for item in ce_oi_ranking
)

assert all(
    item.option_type == "PE"
    for item in pe_oi_ranking
)

assert all(
    abs(oi_ranking[index].oi_change)
    >= abs(oi_ranking[index + 1].oi_change)
    for index in range(len(oi_ranking) - 1)
)

# =====================================================
# OI Addition / Reduction Rankings
# =====================================================

oi_additions = (
    OptionPositioningAnalytics.rank_oi_additions(
        results=chain_positioning,
        limit=5,
    )
)

oi_reductions = (
    OptionPositioningAnalytics.rank_oi_reductions(
        results=chain_positioning,
        limit=5,
    )
)


# =====================================================
# Validate OI Additions
# =====================================================

assert len(oi_additions) == 4

assert all(
    result.oi_change > 0
    for result in oi_additions
)

assert [
    result.oi_change
    for result in oi_additions
] == [
    9894,
    2188,
    1000,
    500,
]


# =====================================================
# Validate OI Reductions
# =====================================================

assert len(oi_reductions) == 2

assert all(
    result.oi_change < 0
    for result in oi_reductions
)

assert [
    result.oi_change
    for result in oi_reductions
] == [
    -500,
    -200,
]


# =====================================================
# Result
# =====================================================

print(
    "\n========== NPAT BULK OI SNAPSHOT ==========\n"
)

print(
    "Strikes                  :",
    len(options_2),
)

print(
    "Contracts per poll       :",
    recorded_2,
)

print()

print(
    "23750 CE Previous OI     :",
    previous_ce.open_interest,
)

print(
    "23750 CE Current OI      :",
    current_ce.open_interest,
)

print(
    "23750 CE Interval Change :",
    current_ce.open_interest
    - previous_ce.open_interest,
)

print(
    "23750 CE Previous LTP    :",
    previous_ce.price,
)

print(
    "23750 CE Current LTP     :",
    current_ce.price,
)

print(
    "23750 CE Price Change    :",
    current_ce.price
    - previous_ce.price,
)

print()

print(
    "23750 PE Previous OI     :",
    previous_pe.open_interest,
)

print(
    "23750 PE Current OI      :",
    current_pe.open_interest,
)

print(
    "23750 PE Interval Change :",
    current_pe.open_interest
    - previous_pe.open_interest,
)

print(
    "23750 PE Previous LTP    :",
    previous_pe.price,
)

print(
    "23750 PE Current LTP     :",
    current_pe.price,
)

print(
    "23750 PE Price Change    :",
    current_pe.price
    - previous_pe.price,
)


# =====================================================
# Positioning Result
# =====================================================

print(
    "\n========== NPAT POSITIONING ==========\n"
)

print(
    "23750 CE Positioning       :",
    ce_positioning.classification,
)

print(
    "23750 CE Price Change %    :",
    round(
        ce_positioning.price_change_pct,
        2,
    ),
    "%",
)

print(
    "23750 CE OI Change %       :",
    round(
        ce_positioning.oi_change_pct,
        2,
    ),
    "%",
)

print()

print(
    "23750 PE Positioning       :",
    pe_positioning.classification,
)

print(
    "23750 PE Price Change %    :",
    round(
        pe_positioning.price_change_pct,
        2,
    ),
    "%",
)

print(
    "23750 PE OI Change %       :",
    round(
        pe_positioning.oi_change_pct,
        2,
    ),
    "%",
)

# =====================================================
# Full Chain Positioning Result
# =====================================================

print(
    "\n========== NPAT FULL CHAIN POSITIONING ==========\n"
)

print(
    "Total Contracts Analyzed :",
    len(chain_positioning),
)

print()

for result in chain_positioning:

    print(
        f"{result.strike_price} "
        f"{result.option_type} "
        f"{result.classification:<16} "
        f"| Price Δ {result.price_change:>7.2f} "
        f"| OI Δ {result.oi_change:>6}"
    )

# =====================================================
# Positioning Summary Result
# =====================================================

print(
    "\n========== NPAT POSITIONING SUMMARY ==========\n"
)

print(
    "Total Contracts       :",
    positioning_summary.total_contracts,
)

print()

print("COMBINED")
print(
    "Long Buildup          :",
    positioning_summary.long_buildup,
)
print(
    "Short Buildup         :",
    positioning_summary.short_buildup,
)
print(
    "Long Unwinding        :",
    positioning_summary.long_unwinding,
)
print(
    "Short Covering        :",
    positioning_summary.short_covering,
)
print(
    "Neutral               :",
    positioning_summary.neutral,
)

print()

print("CE")
print(
    "Total                 :",
    positioning_summary.ce_total,
)
print(
    "Long Buildup          :",
    positioning_summary.ce_long_buildup,
)
print(
    "Short Buildup         :",
    positioning_summary.ce_short_buildup,
)
print(
    "Long Unwinding        :",
    positioning_summary.ce_long_unwinding,
)
print(
    "Short Covering        :",
    positioning_summary.ce_short_covering,
)
print(
    "Neutral               :",
    positioning_summary.ce_neutral,
)

print()

print("PE")
print(
    "Total                 :",
    positioning_summary.pe_total,
)
print(
    "Long Buildup          :",
    positioning_summary.pe_long_buildup,
)
print(
    "Short Buildup         :",
    positioning_summary.pe_short_buildup,
)
print(
    "Long Unwinding        :",
    positioning_summary.pe_long_unwinding,
)
print(
    "Short Covering        :",
    positioning_summary.pe_short_covering,
)
print(
    "Neutral               :",
    positioning_summary.pe_neutral,
)

# =====================================================
# ATM Window Result
# =====================================================

print(
    "\n========== NPAT ATM WINDOW POSITIONING ==========\n"
)

print(
    "ATM Strike             :",
    23750,
)

print(
    "Strikes Each Side      :",
    1,
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
# OI Ranking Result
# =====================================================

print(
    "\n========== NPAT OI CHANGE RANKING ==========\n"
)

for rank, result in enumerate(
    oi_ranking,
    start=1,
):
    print(
        f"{rank:>2}. "
        f"{result.strike_price} "
        f"{result.option_type} "
        f"{result.classification:<16} "
        f"| OI Δ {result.oi_change:>6} "
        f"| OI Δ% {result.oi_change_pct:>7.2f}% "
        f"| Price Δ {result.price_change:>7.2f}"
    )
    
# =====================================================
# OI Addition Ranking Result
# =====================================================

print(
    "\n========== NPAT TOP OI ADDITIONS ==========\n"
)

for rank, result in enumerate(
    oi_additions,
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


# =====================================================
# OI Reduction Ranking Result
# =====================================================

print(
    "\n========== NPAT TOP OI REDUCTIONS ==========\n"
)

for rank, result in enumerate(
    oi_reductions,
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

# =====================================================
# Final Result
# =====================================================

print(
    "\nBulk OI Snapshot test passed."
)

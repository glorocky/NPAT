from ai.prediction_engine import PredictionEngine
from core.models import (
    ForwardPremiumAnalysis,
    FuturesAnalysis,
    GreeksSummary,
    MarketRegimeAnalysis,
)

# =====================================================
# Direction Classification Boundaries
# =====================================================

cases = [
    (100.0, "STRONG_BULLISH"),
    (60.0, "STRONG_BULLISH"),
    (59.99, "BULLISH"),
    (20.0, "BULLISH"),
    (19.99, "NEUTRAL"),
    (0.0, "NEUTRAL"),
    (-19.99, "NEUTRAL"),
    (-20.0, "BEARISH"),
    (-59.99, "BEARISH"),
    (-60.0, "STRONG_BEARISH"),
    (-100.0, "STRONG_BEARISH"),
]


for score, expected in cases:

    actual = PredictionEngine.classify_direction(
        score=score,
    )

    print(
        score,
        "->",
        actual,
    )

    assert actual == expected
    
# =====================================================
# Market Regime Score
# =====================================================

regime = MarketRegimeAnalysis(
    regime="STRONG_BULLISH",
    regime_score=66.8712,

    futures_score=80.0,
    breadth_score=70.0759,
    sector_score=66.1613,
    volatility_score=20.0,

    bullish_sectors=14,
    bearish_sectors=0,
    neutral_sectors=1,

    strongest_sector="Consumer Services",
    weakest_sector="Oil Gas & Consumable Fuels",

    confidence=93.0806,

    reasons=(
        "Controlled futures reason.",
        "Controlled breadth reason.",
        "Controlled sector reason.",
        "Controlled volatility reason.",
    ),
)

regime_score = PredictionEngine.score_regime(
    regime=regime,
)

print(
    "\nRegime Score       :",
    regime_score,
)

assert regime_score == 66.8712

neutral_regime = MarketRegimeAnalysis(
    regime="NEUTRAL",
    regime_score=0.0,

    futures_score=0.0,
    breadth_score=0.0,
    sector_score=0.0,
    volatility_score=0.0,

    bullish_sectors=0,
    bearish_sectors=0,
    neutral_sectors=15,

    strongest_sector=None,
    weakest_sector=None,

    confidence=0.0,

    reasons=(),
)

assert (
    PredictionEngine.score_regime(
        regime=neutral_regime,
    )
    == 0.0
)


bearish_regime = MarketRegimeAnalysis(
    regime="STRONG_BEARISH",
    regime_score=-72.45678,

    futures_score=-80.0,
    breadth_score=-70.0,
    sector_score=-65.0,
    volatility_score=-20.0,

    bullish_sectors=0,
    bearish_sectors=14,
    neutral_sectors=1,

    strongest_sector="Healthcare",
    weakest_sector="Financial Services",

    confidence=90.0,

    reasons=(),
)

assert (
    PredictionEngine.score_regime(
        regime=bearish_regime,
    )
    == -72.4568
)

print(
    "PredictionEngine regime score test passed."
)

# =====================================================
# Futures Score
# =====================================================

futures = FuturesAnalysis(
    symbol="NIFTY",
    exchange="NSE",
    trading_symbol="NIFTY26JULFUT",
    expiry="2026-07-28",

    spot_price=23995.95,
    futures_price=24040.0,

    basis=44.05,
    basis_pct=0.1836,

    previous_price=23806.5,
    price_change=233.5,
    price_change_pct=0.9808,

    previous_oi=157943,
    current_oi=144978,
    oi_change=-12965,
    oi_change_pct=-8.2087,

    positioning="SHORT_COVERING",

    volume=100000,

    total_buy_quantity=251940,
    total_sell_quantity=148005,

    quantity_imbalance=103935,
    quantity_imbalance_pct=25.9873,

    lot_size=65,
)


futures_score = (
    PredictionEngine.score_futures(
        futures=futures,
    )
)

print(
    "\nFutures Score      :",
    futures_score,
)

assert futures_score == 80.0

print(
    "PredictionEngine futures score test passed."
)

# =====================================================
# Greeks Score
# =====================================================


def build_greeks(
    call_iv: float,
    put_iv: float,
) -> GreeksSummary:

    return GreeksSummary(
        symbol="NIFTY",
        expiry="2026-08-04",

        spot_price=24000.0,
        atm_strike=24000,

        atm_call_delta=0.50,
        atm_put_delta=-0.50,
        delta_balance=0.0,

        atm_call_iv=call_iv,
        atm_put_iv=put_iv,
        iv_skew=put_iv - call_iv,

        highest_gamma_strike=24000,
        highest_gamma=0.01,

        total_call_theta=-20.0,
        total_put_theta=-20.0,
        total_theta=-40.0,

        total_call_vega=2.5,
        total_put_vega=2.5,
        total_vega=5.0,
    )
    
# =====================================================
# Premium Score
# =====================================================


def build_premium(
    option_type: str,
    forward_difference_pct: float,
    strike_price: int = 24000,
    moneyness: str = "ATM",
) -> ForwardPremiumAnalysis:

    return ForwardPremiumAnalysis(
        symbol="NIFTY",
        expiry="2026-08-04",
        strike_price=strike_price,
        option_type=option_type,

        spot_price=24000.0,
        implied_forward=24010.0,

        market_premium=100.0,

        spot_bs_premium=100.0,
        forward_bs_premium=100.0,

        spot_difference=0.0,
        spot_difference_pct=0.0,

        forward_difference=forward_difference_pct,
        forward_difference_pct=forward_difference_pct,

        iv=18.0,
        time_to_expiry=0.01,

        moneyness=moneyness,
    )


# -----------------------------------------------------
# Neutral Premium Structure
# -----------------------------------------------------

neutral_premiums = [
    build_premium(
        option_type="CE",
        forward_difference_pct=2.0,
    ),
    build_premium(
        option_type="PE",
        forward_difference_pct=1.5,
    ),
]

neutral_premium_score = (
    PredictionEngine.score_premium(
        premiums=neutral_premiums,
    )
)

assert neutral_premium_score == 0.0


# -----------------------------------------------------
# Call Richness -> Bullish
# -----------------------------------------------------

bullish_premiums = [
    build_premium(
        option_type="CE",
        forward_difference_pct=4.0,
    ),
    build_premium(
        option_type="PE",
        forward_difference_pct=2.0,
    ),
]

bullish_premium_score = (
    PredictionEngine.score_premium(
        premiums=bullish_premiums,
    )
)

assert bullish_premium_score == 20.0


# -----------------------------------------------------
# Put Richness -> Bearish
# -----------------------------------------------------

bearish_premiums = [
    build_premium(
        option_type="CE",
        forward_difference_pct=1.0,
    ),
    build_premium(
        option_type="PE",
        forward_difference_pct=4.0,
    ),
]

bearish_premium_score = (
    PredictionEngine.score_premium(
        premiums=bearish_premiums,
    )
)

assert bearish_premium_score == -30.0


# -----------------------------------------------------
# Saturation
# -----------------------------------------------------

strong_bullish_premiums = [
    build_premium(
        option_type="CE",
        forward_difference_pct=15.0,
    ),
    build_premium(
        option_type="PE",
        forward_difference_pct=0.0,
    ),
]

assert (
    PredictionEngine.score_premium(
        premiums=strong_bullish_premiums,
    )
    == 100.0
)


strong_bearish_premiums = [
    build_premium(
        option_type="CE",
        forward_difference_pct=0.0,
    ),
    build_premium(
        option_type="PE",
        forward_difference_pct=15.0,
    ),
]

assert (
    PredictionEngine.score_premium(
        premiums=strong_bearish_premiums,
    )
    == -100.0
)


# =====================================================
# Output
# =====================================================

print(
    "\nPremium Neutral    :",
    neutral_premium_score,
)

print(
    "Premium Bullish    :",
    bullish_premium_score,
)

print(
    "Premium Bearish    :",
    bearish_premium_score,
)

print(
    "PredictionEngine premium score test passed."
)

# -----------------------------------------------------
# Balanced IV
# -----------------------------------------------------

balanced_greeks = build_greeks(
    call_iv=18.0,
    put_iv=18.0,
)

balanced_score = (
    PredictionEngine.score_greeks(
        greeks=balanced_greeks,
    )
)

assert balanced_score == 0.0


# -----------------------------------------------------
# Put IV Higher -> Bearish
# -----------------------------------------------------

bearish_greeks = build_greeks(
    call_iv=18.0,
    put_iv=19.0,
)

bearish_score = (
    PredictionEngine.score_greeks(
        greeks=bearish_greeks,
    )
)

assert bearish_score == -20.0


# -----------------------------------------------------
# Call IV Higher -> Bullish
# -----------------------------------------------------

bullish_greeks = build_greeks(
    call_iv=19.0,
    put_iv=18.0,
)

bullish_score = (
    PredictionEngine.score_greeks(
        greeks=bullish_greeks,
    )
)

assert bullish_score == 20.0


# -----------------------------------------------------
# Strong Put Skew
# -----------------------------------------------------

strong_bearish_greeks = build_greeks(
    call_iv=18.0,
    put_iv=23.0,
)

assert (
    PredictionEngine.score_greeks(
        greeks=strong_bearish_greeks,
    )
    == -100.0
)


# -----------------------------------------------------
# Strong Call Skew
# -----------------------------------------------------

strong_bullish_greeks = build_greeks(
    call_iv=23.0,
    put_iv=18.0,
)

assert (
    PredictionEngine.score_greeks(
        greeks=strong_bullish_greeks,
    )
    == 100.0
)


# -----------------------------------------------------
# Small Skew -> Neutral
# -----------------------------------------------------

small_skew_greeks = build_greeks(
    call_iv=18.0,
    put_iv=18.49,
)

assert (
    PredictionEngine.score_greeks(
        greeks=small_skew_greeks,
    )
    == 0.0
)


# =====================================================
# Output
# =====================================================

print(
    "\nGreeks Balanced    :",
    balanced_score,
)

print(
    "Greeks Bearish     :",
    bearish_score,
)

print(
    "Greeks Bullish     :",
    bullish_score,
)

print(
    "PredictionEngine Greeks score test passed."
)
        
# =====================================================
# Combined Prediction Score
# =====================================================

combined_score = PredictionEngine.combine_scores(
    regime_score=66.8712,
    futures_score=80.0,
    greeks_score=20.0,
    premium_score=20.0,
)

print(
    "\nCombined Score     :",
    combined_score,
)

assert combined_score == 54.4049

assert (
    PredictionEngine.classify_direction(
        score=combined_score,
    )
    == "BULLISH"
)


# -----------------------------------------------------
# Maximum Bullish
# -----------------------------------------------------

assert (
    PredictionEngine.combine_scores(
        regime_score=100.0,
        futures_score=100.0,
        greeks_score=100.0,
        premium_score=100.0,
    )
    == 100.0
)


# -----------------------------------------------------
# Fully Neutral
# -----------------------------------------------------

assert (
    PredictionEngine.combine_scores(
        regime_score=0.0,
        futures_score=0.0,
        greeks_score=0.0,
        premium_score=0.0,
    )
    == 0.0
)


# -----------------------------------------------------
# Maximum Bearish
# -----------------------------------------------------

assert (
    PredictionEngine.combine_scores(
        regime_score=-100.0,
        futures_score=-100.0,
        greeks_score=-100.0,
        premium_score=-100.0,
    )
    == -100.0
)


# -----------------------------------------------------
# Mixed Evidence
# -----------------------------------------------------

mixed_score = PredictionEngine.combine_scores(
    regime_score=60.0,
    futures_score=-40.0,
    greeks_score=20.0,
    premium_score=-20.0,
)

assert mixed_score == 10.0

assert (
    PredictionEngine.classify_direction(
        score=mixed_score,
    )
    == "NEUTRAL"
)


# -----------------------------------------------------
# Invalid Component Score
# -----------------------------------------------------

try:

    PredictionEngine.combine_scores(
        regime_score=101.0,
        futures_score=0.0,
        greeks_score=0.0,
        premium_score=0.0,
    )

except ValueError:
    pass

else:
    raise AssertionError(
        "Expected ValueError for invalid "
        "component score."
    )


print(
    "PredictionEngine combined score test passed."
)

# =====================================================
# Full Prediction Analysis
# =====================================================

prediction = PredictionEngine.analyze(
    regime=regime,
    futures=futures,
    greeks=bullish_greeks,
    premiums=bullish_premiums,
)


# -----------------------------------------------------
# Validate Result
# -----------------------------------------------------

assert prediction is not None

assert prediction.direction == "BULLISH"

assert prediction.score == 54.4049

assert prediction.regime_score == 66.8712
assert prediction.futures_score == 80.0
assert prediction.greeks_score == 20.0
assert prediction.premium_score == 20.0

assert prediction.bullish_evidence == 4
assert prediction.bearish_evidence == 0
assert prediction.neutral_evidence == 0

assert prediction.confidence == 81.762

assert len(prediction.reasons) == 5


# -----------------------------------------------------
# Output
# -----------------------------------------------------

print(
    "\n========== NPAT PREDICTION ENGINE ==========\n"
)

print(
    "Direction          :",
    prediction.direction,
)

print(
    "Prediction Score   :",
    prediction.score,
)

print(
    "Confidence         :",
    prediction.confidence,
)

print()

print(
    "Regime Score       :",
    prediction.regime_score,
)

print(
    "Futures Score      :",
    prediction.futures_score,
)

print(
    "Greeks Score       :",
    prediction.greeks_score,
)

print(
    "Premium Score      :",
    prediction.premium_score,
)

print()

print(
    "Bullish Evidence   :",
    prediction.bullish_evidence,
)

print(
    "Bearish Evidence   :",
    prediction.bearish_evidence,
)

print(
    "Neutral Evidence   :",
    prediction.neutral_evidence,
)

print(
    "\nReasons"
)

print(
    "-" * 70
)

for reason in prediction.reasons:
    print(
        "-",
        reason,
    )

print(
    "\nPredictionEngine analyze test passed."
)
        
# =====================================================
# Invalid Score Validation
# =====================================================

for invalid_score in (
    100.01,
    -100.01,
):

    try:
        PredictionEngine.classify_direction(
            score=invalid_score,
        )

    except ValueError:
        pass

    else:
        raise AssertionError(
            "Expected ValueError for score "
            f"{invalid_score}."
        )


print(
    "\nPredictionEngine classification "
    "boundary test passed."
)

# =====================================================
# Exact Direction Boundary Tests
# =====================================================

direction_boundaries = {
    100.0: "STRONG_BULLISH",
    60.0: "STRONG_BULLISH",
    59.9999: "BULLISH",
    20.0: "BULLISH",
    19.9999: "NEUTRAL",
    0.0: "NEUTRAL",
    -19.9999: "NEUTRAL",
    -20.0: "BEARISH",
    -59.9999: "BEARISH",
    -60.0: "STRONG_BEARISH",
    -100.0: "STRONG_BEARISH",
}

for score, expected_direction in (
    direction_boundaries.items()
):

    actual_direction = (
        PredictionEngine.classify_direction(
            score=score,
        )
    )

    assert (
        actual_direction
        == expected_direction
    ), (
        f"Score {score}: expected "
        f"{expected_direction}, got "
        f"{actual_direction}."
    )


print(
    "\nPredictionEngine exact direction "
    "boundaries passed."
)

# =====================================================
# All-Neutral Prediction Confidence Test
# =====================================================

neutral_futures = FuturesAnalysis(
    symbol="NIFTY",
    exchange="NSE",
    trading_symbol="NIFTY26AUGFUT",
    expiry="2026-08-04",

    spot_price=24000.0,
    futures_price=24000.0,

    basis=0.0,
    basis_pct=0.0,

    previous_price=24000.0,
    price_change=0.0,
    price_change_pct=0.0,

    previous_oi=100000,
    current_oi=100000,
    oi_change=0,
    oi_change_pct=0.0,

    positioning="NEUTRAL",

    volume=100000,

    total_buy_quantity=100000,
    total_sell_quantity=100000,

    quantity_imbalance=0,
    quantity_imbalance_pct=0.0,

    lot_size=65,
)

neutral_greeks = build_greeks(
    call_iv=18.0,
    put_iv=18.0,
)

all_neutral_prediction = PredictionEngine.analyze(
    regime=neutral_regime,
    futures=neutral_futures,
    greeks=neutral_greeks,
    premiums=neutral_premiums,
)

print()
print("========== ALL-NEUTRAL PREDICTION ==========")
print()

print(
    "Direction          :",
    all_neutral_prediction.direction,
)

print(
    "Prediction Score   :",
    all_neutral_prediction.score,
)

print(
    "Confidence         :",
    all_neutral_prediction.confidence,
)

print()

print(
    "Regime Score       :",
    all_neutral_prediction.regime_score,
)

print(
    "Futures Score      :",
    all_neutral_prediction.futures_score,
)

print(
    "Greeks Score       :",
    all_neutral_prediction.greeks_score,
)

print(
    "Premium Score      :",
    all_neutral_prediction.premium_score,
)

print()

print(
    "Bullish Evidence   :",
    all_neutral_prediction.bullish_evidence,
)

print(
    "Bearish Evidence   :",
    all_neutral_prediction.bearish_evidence,
)

print(
    "Neutral Evidence   :",
    all_neutral_prediction.neutral_evidence,
)


assert all_neutral_prediction.direction == "NEUTRAL"
assert all_neutral_prediction.score == 0.0

assert all_neutral_prediction.regime_score == 0.0
assert all_neutral_prediction.futures_score == 0.0
assert all_neutral_prediction.greeks_score == 0.0
assert all_neutral_prediction.premium_score == 0.0

assert all_neutral_prediction.bullish_evidence == 0
assert all_neutral_prediction.bearish_evidence == 0
assert all_neutral_prediction.neutral_evidence == 4

assert (
    all_neutral_prediction.confidence
    == 0.0
)


print(
    "\nPredictionEngine all-neutral test passed."
)
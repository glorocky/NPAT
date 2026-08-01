from ai.decision_engine import DecisionEngine
from core.models import (
    DecisionAnalysis,
    MarketRegimeAnalysis,
)


# =====================================================
# Signal Classification Boundaries
# =====================================================

cases = [
    (100.0, "STRONG_BUY"),
    (60.0, "STRONG_BUY"),

    (59.99, "BUY"),
    (20.0, "BUY"),

    (19.99, "NEUTRAL"),
    (0.0, "NEUTRAL"),
    (-19.99, "NEUTRAL"),

    (-20.0, "SELL"),
    (-59.99, "SELL"),

    (-60.0, "STRONG_SELL"),
    (-100.0, "STRONG_SELL"),
]


for score, expected in cases:

    result = DecisionEngine.classify_signal(
        score=score,
    )

    print(
        score,
        "->",
        result,
    )

    assert result == expected

# =====================================================
# Controlled Market Regime
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


# =====================================================
# Analyze Decision
# =====================================================

decision = DecisionEngine.analyze_regime(
    regime=regime,
)


# =====================================================
# Validate Decision
# =====================================================

assert isinstance(
    decision,
    DecisionAnalysis,
)

assert decision.signal == "STRONG_BUY"

assert decision.score == 66.8712
assert decision.confidence == 93.0806

assert decision.market_regime == "STRONG_BULLISH"
assert decision.market_regime_score == 66.8712

assert decision.bullish_evidence == 3
assert decision.bearish_evidence == 0
assert decision.neutral_evidence == 0

assert len(decision.reasons) == 3


# =====================================================
# Decision Output
# =====================================================

print()
print("Signal            :", decision.signal)
print("Decision Score    :", decision.score)
print("Confidence        :", decision.confidence)
print("Market Regime     :", decision.market_regime)

print()
print("Bullish Evidence  :", decision.bullish_evidence)
print("Bearish Evidence  :", decision.bearish_evidence)
print("Neutral Evidence  :", decision.neutral_evidence)

print()
print("Reasons")

for reason in decision.reasons:
    print("-", reason)

print(
    "DecisionEngine classification "
    "boundary test passed."
)

print(
    "\nDecisionEngine analyze_regime "
    "test passed."
)
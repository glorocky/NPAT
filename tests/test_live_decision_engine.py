import pyotp

from config import GROWW
from growwapi.groww.client import GrowwAPI

from providers.groww_provider import GrowwProvider
from services.market_service import MarketService

from ai.decision_engine import DecisionEngine

from core.models import DecisionAnalysis


# =====================================================
# Test Configuration
# =====================================================

SYMBOL = "NIFTY"
EXCHANGE = "NSE"
EXPIRY = "2026-07-28"


# =====================================================
# Authentication
# =====================================================

totp = pyotp.TOTP(
    GROWW.totp_secret
).now()

access_token = GrowwAPI.get_access_token(
    api_key=GROWW.api_key,
    totp=totp,
)

provider = GrowwProvider(
    access_token=access_token,
)

service = MarketService(
    provider=provider,
)


# =====================================================
# Dashboard Snapshot
# =====================================================

print(
    "\n========== NPAT LIVE DECISION ENGINE ==========\n"
)

snapshot = service.get_dashboard_snapshot(
    symbol=SYMBOL,
    expiry=EXPIRY,
    exchange=EXCHANGE,
)


# =====================================================
# Validate Input
# =====================================================

assert snapshot.market_regime is not None


# =====================================================
# Decision Engine
# =====================================================

decision = DecisionEngine.analyze_regime(
    regime=snapshot.market_regime,
)


# =====================================================
# Validate Decision
# =====================================================

assert isinstance(
    decision,
    DecisionAnalysis,
)

assert decision.signal in {
    "STRONG_BUY",
    "BUY",
    "NEUTRAL",
    "SELL",
    "STRONG_SELL",
}

assert -100.0 <= decision.score <= 100.0
assert 0.0 <= decision.confidence <= 100.0

assert (
    decision.bullish_evidence
    + decision.bearish_evidence
    + decision.neutral_evidence
) == 3

assert (
    decision.market_regime
    ==
    snapshot.market_regime.regime
)

assert (
    decision.market_regime_score
    ==
    snapshot.market_regime.regime_score
)

assert len(decision.reasons) == 3


# =====================================================
# Output
# =====================================================

print("Signal             :", decision.signal)
print("Decision Score     :", decision.score)
print("Confidence         :", decision.confidence)

print()

print("Market Regime      :", decision.market_regime)
print(
    "Market Regime Score:",
    decision.market_regime_score,
)

print()

print(
    "Futures Score      :",
    snapshot.market_regime.futures_score,
)

print(
    "Breadth Score      :",
    snapshot.market_regime.breadth_score,
)

print(
    "Sector Score       :",
    snapshot.market_regime.sector_score,
)

print(
    "Volatility Score   :",
    snapshot.market_regime.volatility_score,
)

print()

print("Bullish Evidence   :", decision.bullish_evidence)
print("Bearish Evidence   :", decision.bearish_evidence)
print("Neutral Evidence   :", decision.neutral_evidence)

print(
    "\nReasons"
)

print("-" * 70)

for reason in decision.reasons:
    print("-", reason)

print(
    "\nLive DecisionEngine integration test passed."
)
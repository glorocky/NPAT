"""NPAT AI orchestration service."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from ai.decision_engine import DecisionEngine
from ai.prediction_engine import PredictionEngine
from ai.option_selector import OptionSelector
from core.models import AIAnalysis

IST = ZoneInfo("Asia/Kolkata")


class AIService:
    def __init__(self, decision_engine=None, prediction_engine=None) -> None:
        self.decision_engine = decision_engine or DecisionEngine()
        self.prediction_engine = prediction_engine or PredictionEngine()

    def analyze(self, dashboard) -> AIAnalysis:
        if dashboard is None:
            raise ValueError("dashboard cannot be None.")
        if dashboard.market_regime is None:
            raise ValueError("dashboard.market_regime cannot be None.")

        decision = self.decision_engine.analyze_regime(regime=dashboard.market_regime)

        if dashboard.futures is None:
            raise ValueError("dashboard.futures cannot be None.")
        if dashboard.greeks_summary is None:
            raise ValueError("dashboard.greeks_summary cannot be None.")
        if not dashboard.premium_analysis:
            raise ValueError("dashboard.premium_analysis cannot be empty.")

        prediction = self.prediction_engine.analyze(
            regime=dashboard.market_regime,
            futures=dashboard.futures,
            greeks=dashboard.greeks_summary,
            premiums=dashboard.premium_analysis,
        )

        recommendation = OptionSelector.select(
            symbol=dashboard.market.symbol,
            expiry=dashboard.market.expiry,
            spot_price=dashboard.market.spot_price,
            atm_strike=dashboard.market.atm_strike,
            options=dashboard.market.option_chain,
            signal=decision.signal,
            confidence=decision.confidence,
            premium_analysis=dashboard.premium_analysis,
            current_time=datetime.now(IST),
        )

        option_type = recommendation.option_type or "NONE"
        if recommendation.action == "BUY CALL":
            trade_action = "BUY_CE"
        elif recommendation.action == "BUY PUT":
            trade_action = "BUY_PE"
        else:
            trade_action = "NO_TRADE"

        reasons = tuple(decision.reasons) + (
            f"Option recommendation: {recommendation.action} "
            f"{recommendation.symbol} {recommendation.strike_price} "
            f"@ ₹{recommendation.entry_price:.2f}.",
            recommendation.reason,
        )

        return AIAnalysis(
            signal=decision.signal,
            confidence=decision.confidence,
            score=decision.score,
            decision=decision,
            prediction=prediction,
            recommendation=recommendation,
            reasons=reasons,
            option_type=option_type,
            trade_action=trade_action,
        )

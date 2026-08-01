"""
=========================================================
NPAT - AI Service

Orchestrates NPAT decision and prediction engines.

The current implementation uses the deterministic
DecisionEngine. PredictionEngine integration will be
added later without changing the MarketService contract.
=========================================================
"""

from __future__ import annotations

from ai.decision_engine import DecisionEngine
from ai.prediction_engine import PredictionEngine

from core.models import (
    AIAnalysis,
)


class AIService:
    """
    Produce the final AI-layer analysis from a completed
    dashboard snapshot.
    """

    # =====================================================
    # Initialization
    # =====================================================

    def __init__(
        self,
        decision_engine=None,
        prediction_engine=None,
    ) -> None:

        self.decision_engine = (
            decision_engine
            or DecisionEngine()
        )

        self.prediction_engine = (
            prediction_engine
            or PredictionEngine()
        )

    # =====================================================
    # Analyze
    # =====================================================

    def analyze(
        self,
        dashboard,
    ) -> AIAnalysis:
        """
        Analyze a completed dashboard snapshot and return
        the final AI-layer result.
        """

        if dashboard is None:
            raise ValueError(
                "dashboard cannot be None."
            )

        if dashboard.market_regime is None:
            raise ValueError(
                "dashboard.market_regime cannot be None."
            )

        # -------------------------------------------------
        # Deterministic Decision
        # -------------------------------------------------

        decision = (
            self.decision_engine.analyze_regime(
                regime=dashboard.market_regime,
            )
        )
        
        # -------------------------------------------------
        # Predictive Confirmation
        # -------------------------------------------------

        if dashboard.futures is None:
            raise ValueError(
                "dashboard.futures cannot be None."
            )

        if dashboard.greeks_summary is None:
            raise ValueError(
                "dashboard.greeks_summary cannot be None."
            )

        if not dashboard.premium_analysis:
            raise ValueError(
                "dashboard.premium_analysis cannot be empty."
            )

        prediction = (
            self.prediction_engine.analyze(
                regime=dashboard.market_regime,
                futures=dashboard.futures,
                greeks=dashboard.greeks_summary,
                premiums=dashboard.premium_analysis,
            )
        )

        # -------------------------------------------------
        # Final AI Result
        # -------------------------------------------------

        return AIAnalysis(
            signal=decision.signal,
            confidence=decision.confidence,
            score=decision.score,

            decision=decision,
            prediction=prediction,

            reasons=decision.reasons,
        )
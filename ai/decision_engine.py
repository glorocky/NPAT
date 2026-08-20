"""
=========================================================
NPAT - Decision Engine

Deterministic decision layer that converts analyzed
market evidence into an explainable trading bias.

This engine does not perform machine-learning prediction.
=========================================================
"""

from __future__ import annotations

from core.models import (
    DecisionAnalysis,
    MarketRegimeAnalysis,
)


class DecisionEngine:
    """
    Produce an explainable trading decision from
    normalized NPAT analytics.
    """

    # =====================================================
    # Signal Classification
    # =====================================================

    @staticmethod
    def classify_signal(
        score: float,
    ) -> str:
        """
        Convert directional decision score into signal.
        """

        if score >= 60.0:
            return "STRONG_BUY"

        if score >= 20.0:
            return "BUY"

        if score > -20.0:
            return "NEUTRAL"

        if score > -60.0:
            return "SELL"

        return "STRONG_SELL"

    @staticmethod
    def determine_option_decision(signal: str) -> tuple[str, str, str]:
        """Map the existing directional signal to its option-side contract."""
        signal = signal.upper().strip()
        if signal in {"BUY", "STRONG_BUY"}:
            return ("BUY CALL", "CE", "BUY CALL (CE)")
        if signal in {"SELL", "STRONG_SELL"}:
            return ("BUY PUT", "PE", "BUY PUT (PE)")
        return ("NO TRADE", "NONE", "NO OPTION TRADE")

    # =====================================================
    # Analyze Market Regime
    # =====================================================

    @classmethod
    def analyze_regime(
        cls,
        regime: MarketRegimeAnalysis,
    ) -> DecisionAnalysis:
        """
        Build the first deterministic decision from the
        validated market-regime evidence.

        The regime score determines directional bias.

        Regime confidence controls decision confidence,
        but does not change direction.
        """

        if regime is None:
            raise ValueError(
                "market regime cannot be None."
            )

        if not -100.0 <= regime.regime_score <= 100.0:
            raise ValueError(
                "market regime score must be between "
                "-100 and +100."
            )

        if not 0.0 <= regime.confidence <= 100.0:
            raise ValueError(
                "market regime confidence must be "
                "between 0 and 100."
            )

        # -------------------------------------------------
        # Component Evidence
        # -------------------------------------------------

        component_scores = (
            regime.futures_score,
            regime.breadth_score,
            regime.sector_score,
        )

        bullish_evidence = sum(
            score >= 20.0
            for score in component_scores
        )

        bearish_evidence = sum(
            score <= -20.0
            for score in component_scores
        )

        neutral_evidence = (
            len(component_scores)
            - bullish_evidence
            - bearish_evidence
        )

        # -------------------------------------------------
        # Decision Score
        # -------------------------------------------------

        score = float(regime.regime_score)

        signal = cls.classify_signal(
            score=score,
        )
        
        # -------------------------------------------------
        # Option Direction
        # -------------------------------------------------

        option_action, option_type, recommendation = (
            cls.determine_option_decision(signal)
        )

        # -------------------------------------------------
        # Confidence
        # -------------------------------------------------

        confidence = float(
            regime.confidence
        )

        # -------------------------------------------------
        # Option Recommendation
        # -------------------------------------------------

        # -------------------------------------------------
        # Reasons
        # -------------------------------------------------

        reasons = (
            f"Market regime is {regime.regime} "
            f"with score {regime.regime_score:.2f}.",

            f"Directional evidence: "
            f"{bullish_evidence} bullish, "
            f"{bearish_evidence} bearish and "
            f"{neutral_evidence} neutral components.",

            f"Regime confidence is "
            f"{regime.confidence:.2f}%.",

            f"Option recommendation: "
            f"{recommendation}.",
        )

        # -------------------------------------------------
        # Result
        # -------------------------------------------------
        
        return DecisionAnalysis(
            signal=signal,
            confidence=confidence,
            score=score,

            market_regime=regime.regime,
            market_regime_score=regime.regime_score,

            bullish_evidence=bullish_evidence,
            bearish_evidence=bearish_evidence,
            neutral_evidence=neutral_evidence,

            option_action=option_action,
            option_type=option_type,
            recommendation=recommendation,

            reasons=reasons,
)

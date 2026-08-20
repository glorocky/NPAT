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
    
        # =====================================================
        # Option Decision
        # =====================================================

        @staticmethod
        def determine_option_decision(
            signal: str,
            market_regime: str,
        ) -> tuple[str, str, str]:
            """
            Convert directional market signal into an
            actionable option recommendation.

            NPAT currently uses an option-buying model:

            BULLISH  -> BUY CE
            BEARISH  -> BUY PE
            NEUTRAL  -> WAIT
            """

            signal = signal.upper()
            market_regime = market_regime.upper()

            # -------------------------------------------------
            # Bullish
            # -------------------------------------------------

            if market_regime == "BULLISH":
                if signal in ("BUY", "STRONG_BUY"):
                    return (
                        "BUY",
                        "CE",
                        "BUY CALL",
                    )

            # -------------------------------------------------
            # Bearish
            # -------------------------------------------------

            if market_regime == "BEARISH":
                if signal in ("SELL", "STRONG_SELL"):
                    return (
                        "BUY",
                        "PE",
                        "BUY PUT",
                    )

            # -------------------------------------------------
            # Neutral
            # -------------------------------------------------

            return (
                "WAIT",
                "NONE",
                "WAIT",
            )

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

        if signal in ("BUY", "STRONG_BUY"):
            option_action = "BUY CALL"

        elif signal in ("SELL", "STRONG_SELL"):
            option_action = "BUY PUT"

        else:
            option_action = "NO TRADE"

        # -------------------------------------------------
        # Confidence
        # -------------------------------------------------

        confidence = float(
            regime.confidence
        )

        # -------------------------------------------------
        # Option Recommendation
        # -------------------------------------------------

        if signal in ("BUY", "STRONG_BUY"):
            recommendation = "BUY CALL (CE)"

        elif signal in ("SELL", "STRONG_SELL"):
            recommendation = "BUY PUT (PE)"

        else:
            recommendation = "NO OPTION TRADE"

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

            reasons=reasons,
)
        
        # -------------------------------------------------
        # Option Decision
        # -------------------------------------------------

        option_action, option_type, recommendation = (
            cls.determine_option_decision(
                signal=signal,
                market_regime=regime.regime,
            )
        )
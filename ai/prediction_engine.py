"""
=========================================================
NPAT - Prediction Engine

Produces deterministic directional confirmation from
market regime, futures, Greeks and option premium
structure.

This is an analytical prediction layer. It is not a
trained machine-learning model.
=========================================================
"""

from __future__ import annotations
from analytics.market_regime_analytics import (
    MarketRegimeAnalytics,
)
from core.models import (
    ForwardPremiumAnalysis,
    FuturesAnalysis,
    GreeksSummary,
    MarketRegimeAnalysis,
    PredictionAnalysis,
)


class PredictionEngine:
    """
    Produce directional prediction analysis from
    independent market evidence.
    """

    # =====================================================
    # Direction Classification
    # =====================================================

    @staticmethod
    def classify_direction(
        score: float,
    ) -> str:
        """
        Convert a prediction score from -100 to +100
        into a directional classification.
        """

        if score < -100.0 or score > 100.0:
            raise ValueError(
                "score must be between -100 and 100."
            )

        if score >= 60.0:
            return "STRONG_BULLISH"

        if score >= 20.0:
            return "BULLISH"

        if score > -20.0:
            return "NEUTRAL"

        if score > -60.0:
            return "BEARISH"

        return "STRONG_BEARISH"
    
    # =====================================================
    # Market Regime Score
    # =====================================================

    @staticmethod
    def score_regime(
        regime: MarketRegimeAnalysis,
    ) -> float:
        """
        Convert the existing market-regime analysis into
        the prediction engine's regime component score.

        MarketRegimeAnalytics already produces a normalized
        directional score from -100 to +100, so the
        prediction engine preserves that score rather than
        recalculating the underlying evidence.
        """

        if regime is None:
            raise ValueError(
                "regime cannot be None."
            )

        score = float(
            regime.regime_score
        )

        if score < -100.0 or score > 100.0:
            raise ValueError(
                "regime_score must be between "
                "-100 and 100."
            )

        return round(
            score,
            4,
        )
        
    # =====================================================
    # Futures Score
    # =====================================================

    @staticmethod
    def score_futures(
        futures: FuturesAnalysis,
    ) -> float:
        """
        Convert futures positioning into the prediction
        engine's futures component score.

        Futures scoring is delegated to
        MarketRegimeAnalytics so NPAT maintains one
        consistent interpretation of futures evidence.
        """

        if futures is None:
            raise ValueError(
                "futures cannot be None."
            )

        score = (
            MarketRegimeAnalytics.score_futures(
                futures=futures,
            )
        )

        if score is None:
            raise ValueError(
                "Futures scoring returned None."
            )

        score = float(score)

        if score < -100.0 or score > 100.0:
            raise ValueError(
                "futures score must be between "
                "-100 and 100."
            )

        return round(
            score,
            4,
        )
        
    # =====================================================
    # Greeks Score
    # =====================================================

    @staticmethod
    def score_greeks(
        greeks: GreeksSummary,
    ) -> float:
        """
        Convert ATM implied-volatility skew into a
        directional score from -100 to +100.

        IV skew is defined as:

            ATM Put IV - ATM Call IV

        Higher put IV contributes bearish evidence.
        Higher call IV contributes bullish evidence.

        Delta balance, gamma, theta and vega are retained
        as analytical context but are not direct
        directional signals in V1.
        """

        if greeks is None:
            raise ValueError(
                "greeks cannot be None."
            )

        iv_skew = float(
            greeks.iv_skew
        )

        # -------------------------------------------------
        # Neutral Zone
        # -------------------------------------------------

        if abs(iv_skew) < 0.50:
            return 0.0

        # -------------------------------------------------
        # Direction
        # -------------------------------------------------

        direction = (
            -1.0
            if iv_skew > 0.0
            else 1.0
        )

        # -------------------------------------------------
        # Magnitude
        # -------------------------------------------------

        magnitude = min(
            100.0,
            abs(iv_skew) * 20.0,
        )

        return round(
            direction * magnitude,
            4,
        )
        
    # =====================================================
    # Premium Score
    # =====================================================

    @staticmethod
    def score_premium(
        premiums: list[ForwardPremiumAnalysis],
    ) -> float:
        """
        Compare ATM call and put richness relative to
        their common-forward theoretical premiums.

        Positive relative call richness contributes
        bullish evidence.

        Positive relative put richness contributes
        bearish evidence.
        """

        if not premiums:
            raise ValueError(
                "premiums cannot be empty."
            )

        atm_premiums = [
            premium
            for premium in premiums
            if premium.moneyness == "ATM"
        ]

        calls = [
            premium
            for premium in atm_premiums
            if premium.option_type == "CE"
        ]

        puts = [
            premium
            for premium in atm_premiums
            if premium.option_type == "PE"
        ]

        if len(calls) != 1 or len(puts) != 1:
            raise ValueError(
                "Exactly one ATM CE and one ATM PE "
                "premium record are required."
            )

        call = calls[0]
        put = puts[0]

        if call.strike_price != put.strike_price:
            raise ValueError(
                "ATM CE and PE strikes must match."
            )

        call_richness = float(
            call.forward_difference_pct
        )

        put_richness = float(
            put.forward_difference_pct
        )

        relative_richness = (
            call_richness
            - put_richness
        )

        if abs(relative_richness) < 1.0:
            return 0.0

        score = max(
            -100.0,
            min(
                100.0,
                relative_richness * 10.0,
            ),
        )

        return round(
            score,
            4,
        )
    # =====================================================
    # Combined Prediction Score
    # =====================================================

    @staticmethod
    def combine_scores(
        regime_score: float,
        futures_score: float,
        greeks_score: float,
        premium_score: float,
    ) -> float:
        """
        Combine normalized prediction components into one
        directional score from -100 to +100.

        Weights:
            Market Regime : 35%
            Futures       : 30%
            Greeks        : 20%
            Premium       : 15%
        """

        scores = (
            regime_score,
            futures_score,
            greeks_score,
            premium_score,
        )

        if any(
            score < -100.0 or score > 100.0
            for score in scores
        ):
            raise ValueError(
                "All component scores must be between "
                "-100 and 100."
            )

        combined = (
            regime_score * 0.35
            + futures_score * 0.30
            + greeks_score * 0.20
            + premium_score * 0.15
        )

        combined = max(
            -100.0,
            min(
                100.0,
                combined,
            ),
        )

        return round(
            combined,
            4,
        )
        
    # =====================================================
    # Prediction Analysis
    # =====================================================

    @classmethod
    def analyze(
        cls,
        regime: MarketRegimeAnalysis,
        futures: FuturesAnalysis,
        greeks: GreeksSummary,
        premiums: list[ForwardPremiumAnalysis],
    ) -> PredictionAnalysis:
        """
        Produce the complete deterministic NPAT prediction
        analysis from market regime, futures, Greeks and
        option-premium evidence.
        """

        # -------------------------------------------------
        # Component Scores
        # -------------------------------------------------

        regime_score = cls.score_regime(
            regime=regime,
        )

        futures_score = cls.score_futures(
            futures=futures,
        )

        greeks_score = cls.score_greeks(
            greeks=greeks,
        )

        premium_score = cls.score_premium(
            premiums=premiums,
        )

        # -------------------------------------------------
        # Combined Prediction Score
        # -------------------------------------------------

        score = cls.combine_scores(
            regime_score=regime_score,
            futures_score=futures_score,
            greeks_score=greeks_score,
            premium_score=premium_score,
        )

        direction = cls.classify_direction(
            score=score,
        )

        # -------------------------------------------------
        # Evidence Classification
        # -------------------------------------------------

        component_scores = (
            regime_score,
            futures_score,
            greeks_score,
            premium_score,
        )

        bullish_evidence = sum(
            component > 0.0
            for component in component_scores
        )

        bearish_evidence = sum(
            component < 0.0
            for component in component_scores
        )

        neutral_evidence = sum(
            component == 0.0
            for component in component_scores
        )
        
        # -------------------------------------------------
        # Confidence
        # -------------------------------------------------
        #
        # Confidence measures agreement with the predicted
        # directional outcome.
        #
        # Neutral evidence does not increase directional
        # confidence.
        # -------------------------------------------------

        if direction in {
            "STRONG_BULLISH",
            "BULLISH",
        }:
            agreement = (
                bullish_evidence
                / len(component_scores)
            )

        elif direction in {
            "STRONG_BEARISH",
            "BEARISH",
        }:
            agreement = (
                bearish_evidence
                / len(component_scores)
            )

        else:
            agreement = 0.0


        strength = abs(score) / 100.0

        confidence = (
            agreement * 60.0
            + strength * 40.0
        )

 

        confidence = round(
            max(
                0.0,
                min(
                    100.0,
                    confidence,
                ),
            ),
            4,
        )

        # -------------------------------------------------
        # Reasons
        # -------------------------------------------------

        reasons = (
            (
                f"Market regime contributes "
                f"{regime_score:.2f}."
            ),
            (
                f"Futures evidence contributes "
                f"{futures_score:.2f}."
            ),
            (
                f"Greeks evidence contributes "
                f"{greeks_score:.2f}."
            ),
            (
                f"Premium evidence contributes "
                f"{premium_score:.2f}."
            ),
            (
                f"Directional evidence: "
                f"{bullish_evidence} bullish, "
                f"{bearish_evidence} bearish and "
                f"{neutral_evidence} neutral components."
            ),
        )

        # -------------------------------------------------
        # Result
        # -------------------------------------------------

        return PredictionAnalysis(
            direction=direction,
            score=score,
            confidence=confidence,

            regime_score=regime_score,
            futures_score=futures_score,
            greeks_score=greeks_score,
            premium_score=premium_score,

            bullish_evidence=bullish_evidence,
            bearish_evidence=bearish_evidence,
            neutral_evidence=neutral_evidence,

            reasons=reasons,
        )
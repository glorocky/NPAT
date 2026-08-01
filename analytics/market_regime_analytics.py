"""
=========================================================
NPAT - Market Regime Analytics

Combines independent market evidence into a normalized
market regime assessment.

Components will be added and tested incrementally.
=========================================================
"""

from __future__ import annotations

from core.models import (
    FuturesAnalysis,
    HeatmapSummary,
    SectorStrength,
    VixRangeAnalysis,
    MarketRegimeAnalysis,
)


class MarketRegimeAnalytics:
    """
    Build directional market-regime evidence from NPAT
    analytics.
    """
    
        # =====================================================
    # Futures Score
    # =====================================================

    @staticmethod
    def score_futures(
        futures: FuturesAnalysis,
    ) -> float:
        """
        Convert futures positioning and basis into a
        directional score from -100 to +100.

        Positioning is the primary signal.
        Basis and quantity imbalance provide confirmation.
        """

        positioning_scores = {
            "LONG_BUILDUP": 70.0,
            "SHORT_COVERING": 50.0,
            "NEUTRAL": 0.0,
            "LONG_UNWINDING": -50.0,
            "SHORT_BUILDUP": -70.0,
        }

        score = positioning_scores.get(
            futures.positioning,
            0.0,
        )

        # -------------------------------------------------
        # Basis Confirmation
        # -------------------------------------------------

        if futures.basis_pct > 0.10:
            score += 15.0

        elif futures.basis_pct < -0.10:
            score -= 15.0

        # -------------------------------------------------
        # Quantity Imbalance Confirmation
        # -------------------------------------------------

        if futures.quantity_imbalance_pct > 10.0:
            score += 15.0

        elif futures.quantity_imbalance_pct < -10.0:
            score -= 15.0

        return round(
            max(-100.0, min(100.0, score)),
            4,
        )

    # =====================================================
    # Breadth Score
    # =====================================================

    @staticmethod
    def score_breadth(
        summary: HeatmapSummary,
    ) -> float:
        """
        Convert index constituent participation into a
        directional score from -100 to +100.

        Participation contributes 70%.
        Average constituent performance contributes 30%.
        """

        if summary.total_stocks <= 0:
            raise ValueError(
                "total_stocks must be greater than zero."
            )

        # -------------------------------------------------
        # Participation
        # -------------------------------------------------

        participation = (
            summary.gainers - summary.losers
        ) / summary.total_stocks

        participation = max(
            -1.0,
            min(1.0, participation),
        )

        # -------------------------------------------------
        # Average Constituent Performance
        # -------------------------------------------------

        performance = max(
            -1.0,
            min(
                1.0,
                summary.average_change_pct / 2.0,
            ),
        )

        # -------------------------------------------------
        # Combined Score
        # -------------------------------------------------

        score = (
            participation * 0.70
            + performance * 0.30
        )

        return round(
            score * 100.0,
            4,
        )

    # =====================================================
    # Sector Score
    # =====================================================

    @staticmethod
    def score_sectors(
        sectors: list[SectorStrength],
    ) -> float:
        """
        Convert sector strength into an index-level
        directional score from -100 to +100.

        Sector scores are weighted by constituent count so
        larger NIFTY sectors contribute proportionally more
        than one-stock or two-stock sectors.
        """

        if not sectors:
            raise ValueError(
                "sectors cannot be empty."
            )

        total_stocks = sum(
            sector.total_stocks
            for sector in sectors
        )

        if total_stocks <= 0:
            raise ValueError(
                "total sector stock count must be "
                "greater than zero."
            )

        weighted_score = sum(
            sector.strength_score
            * sector.total_stocks
            for sector in sectors
        ) / total_stocks

        return round(
            max(
                -100.0,
                min(100.0, weighted_score),
            ),
            4,
        )
        
    
    # =====================================================
    # Volatility Score
    # =====================================================

    @staticmethod
    def score_volatility(
        vix: VixRangeAnalysis,
    ) -> float:
        """
        Convert India VIX into a normalized market-risk
        score from -100 to +100.

        Lower volatility supports regime stability.
        Higher volatility reduces regime confidence.

        This score is a risk modifier, not an independent
        bullish/bearish directional signal.
        """

        india_vix = float(vix.india_vix)

        if india_vix < 0:
            raise ValueError(
                "india_vix cannot be negative."
            )

        # -------------------------------------------------
        # VIX Risk Bands
        # -------------------------------------------------

        if india_vix <= 12.0:
            score = 60.0

        elif india_vix <= 15.0:
            score = 30.0

        elif india_vix <= 20.0:
            score = 0.0

        elif india_vix <= 25.0:
            score = -30.0

        elif india_vix <= 30.0:
            score = -60.0

        else:
            score = -90.0

        # -------------------------------------------------
        # Expected Range Breach
        # -------------------------------------------------

        if vix.expected_range_exceeded:
            score -= 10.0

        return round(
            max(-100.0, min(100.0, score)),
            4,
        )
    
    # =====================================================
    # Combined Regime Score
    # =====================================================

    @staticmethod
    def combine_scores(
        futures_score: float,
        breadth_score: float,
        sector_score: float,
        volatility_score: float,
    ) -> float:
        """
        Combine independent regime components into one
        directional score from -100 to +100.

        Directional evidence:
            Futures    30%
            Breadth    30%
            Sectors    30%

        Risk modifier:
            Volatility 10%
        """

        scores = (
            futures_score,
            breadth_score,
            sector_score,
            volatility_score,
        )

        if any(
            score < -100.0 or score > 100.0
            for score in scores
        ):
            raise ValueError(
                "regime component scores must be "
                "between -100 and +100."
            )

        combined = (
            futures_score * 0.30
            + breadth_score * 0.30
            + sector_score * 0.30
            + volatility_score * 0.10
        )

        return round(
            max(-100.0, min(100.0, combined)),
            4,
        )
        
    # =====================================================
    # Regime Classification
    # =====================================================

    @staticmethod
    def classify_regime(
        regime_score: float,
    ) -> str:
        """
        Convert combined regime score into directional
        market regime classification.
        """

        if regime_score >= 60.0:
            return "STRONG_BULLISH"

        if regime_score >= 20.0:
            return "BULLISH"

        if regime_score > -20.0:
            return "NEUTRAL"

        if regime_score > -60.0:
            return "BEARISH"

        return "STRONG_BEARISH"
    
    # =====================================================
    # Confidence
    # =====================================================

    @staticmethod
    def calculate_confidence(
        futures_score: float,
        breadth_score: float,
        sector_score: float,
    ) -> float:
        """
        Measure agreement between directional components.

        Confidence is high when Futures, Breadth and
        Sector scores agree closely.

        Volatility is deliberately excluded because it is
        a risk modifier rather than directional evidence.
        """

        scores = (
            futures_score,
            breadth_score,
            sector_score,
        )

        if any(
            score < -100.0 or score > 100.0
            for score in scores
        ):
            raise ValueError(
                "directional scores must be between "
                "-100 and +100."
            )

        spread = max(scores) - min(scores)

        confidence = 100.0 - (spread / 2.0)

        return round(
            max(0.0, min(100.0, confidence)),
            4,
        )
    
    # =====================================================
    # Full Market Regime Analysis
    # =====================================================

    @classmethod
    def analyze(
        cls,
        futures: FuturesAnalysis,
        breadth: HeatmapSummary,
        sectors: list[SectorStrength],
        volatility: VixRangeAnalysis,
    ) -> MarketRegimeAnalysis:
        """
        Build the complete NPAT market regime analysis.
        """

        if not sectors:
            raise ValueError(
                "sectors cannot be empty."
            )

        # -------------------------------------------------
        # Component Scores
        # -------------------------------------------------

        futures_score = cls.score_futures(
            futures=futures,
        )

        breadth_score = cls.score_breadth(
            summary=breadth,
        )

        sector_score = cls.score_sectors(
            sectors=sectors,
        )

        volatility_score = cls.score_volatility(
            vix=volatility,
        )

        # -------------------------------------------------
        # Combined Regime
        # -------------------------------------------------

        regime_score = cls.combine_scores(
            futures_score=futures_score,
            breadth_score=breadth_score,
            sector_score=sector_score,
            volatility_score=volatility_score,
        )

        regime = cls.classify_regime(
            regime_score=regime_score,
        )

        confidence = cls.calculate_confidence(
            futures_score=futures_score,
            breadth_score=breadth_score,
            sector_score=sector_score,
        )

        # -------------------------------------------------
        # Sector Classification Counts
        # -------------------------------------------------

        bullish_classes = {
            "STRONG_BULLISH",
            "BULLISH",
        }

        bearish_classes = {
            "STRONG_BEARISH",
            "BEARISH",
        }

        bullish_sectors = sum(
            sector.classification in bullish_classes
            for sector in sectors
        )

        bearish_sectors = sum(
            sector.classification in bearish_classes
            for sector in sectors
        )

        neutral_sectors = sum(
            sector.classification == "NEUTRAL"
            for sector in sectors
        )

        # -------------------------------------------------
        # Strongest / Weakest Sector
        # -------------------------------------------------

        strongest = max(
            sectors,
            key=lambda sector: sector.strength_score,
        )

        weakest = min(
            sectors,
            key=lambda sector: sector.strength_score,
        )

        # -------------------------------------------------
        # Reasons
        # -------------------------------------------------

        reasons = (
            f"Futures positioning is "
            f"{futures.positioning} "
            f"with score {futures_score:.2f}.",

            f"Market breadth score is "
            f"{breadth_score:.2f} with "
            f"{breadth.gainers} gainers and "
            f"{breadth.losers} losers.",

            f"Sector score is {sector_score:.2f}; "
            f"{bullish_sectors} bullish, "
            f"{bearish_sectors} bearish and "
            f"{neutral_sectors} neutral sectors.",

            f"Volatility score is "
            f"{volatility_score:.2f} with "
            f"India VIX at {volatility.india_vix:.2f}.",
        )

        # -------------------------------------------------
        # Result
        # -------------------------------------------------

        return MarketRegimeAnalysis(
            regime=regime,
            regime_score=regime_score,

            futures_score=futures_score,
            breadth_score=breadth_score,
            sector_score=sector_score,
            volatility_score=volatility_score,

            bullish_sectors=bullish_sectors,
            bearish_sectors=bearish_sectors,
            neutral_sectors=neutral_sectors,

            strongest_sector=strongest.sector,
            weakest_sector=weakest.sector,

            confidence=confidence,

            reasons=reasons,
        )
    
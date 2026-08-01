"""
=========================================================
NPAT - Sector Strength Analytics

Converts sector breadth and constituent performance into
a normalized directional strength assessment.
=========================================================
"""

from __future__ import annotations

from core.models import (
    SectorBreadth,
    SectorStrength,
)


class SectorStrengthAnalytics:
    """
    Analyze directional strength for market sectors.

    Sector breadth measures participation, while average
    percentage change measures performance magnitude.
    """

    # =====================================================
    # Strength Score
    # =====================================================

    @staticmethod
    def _calculate_score(
        breadth_pct: float,
        average_change_pct: float,
    ) -> float:
        """
        Calculate normalized sector strength score.

        Breadth contributes 60% of the score.
        Average constituent performance contributes 40%.

        Average change is normalized so that +/- 2%
        represents the maximum performance contribution.
        """

        normalized_breadth = max(
            -1.0,
            min(1.0, breadth_pct / 100.0),
        )

        normalized_performance = max(
            -1.0,
            min(1.0, average_change_pct / 2.0),
        )

        score = (
            normalized_breadth * 0.60
            + normalized_performance * 0.40
        )

        return round(score * 100.0, 4)

    # =====================================================
    # Classification
    # =====================================================

    @staticmethod
    def _classify(
        strength_score: float,
    ) -> str:
        """
        Convert strength score into directional class.
        """

        if strength_score >= 60.0:
            return "STRONG_BULLISH"

        if strength_score >= 20.0:
            return "BULLISH"

        if strength_score > -20.0:
            return "NEUTRAL"

        if strength_score > -60.0:
            return "BEARISH"

        return "STRONG_BEARISH"

    # =====================================================
    # Analyze One Sector
    # =====================================================

    @classmethod
    def analyze(
        cls,
        sector: SectorBreadth,
    ) -> SectorStrength:
        """
        Analyze one sector breadth record.
        """

        if sector.total_stocks <= 0:
            raise ValueError(
                "sector total_stocks must be greater than zero."
            )

        score = cls._calculate_score(
            breadth_pct=sector.breadth_pct,
            average_change_pct=sector.average_change_pct,
        )

        classification = cls._classify(
            strength_score=score,
        )

        return SectorStrength(
            sector=sector.sector,
            total_stocks=sector.total_stocks,

            breadth_pct=float(
                sector.breadth_pct
            ),

            average_change_pct=float(
                sector.average_change_pct
            ),

            strength_score=float(score),

            classification=classification,

            strongest_symbol=sector.strongest_symbol,
            weakest_symbol=sector.weakest_symbol,
        )

    # =====================================================
    # Analyze All Sectors
    # =====================================================

    @classmethod
    def analyze_all(
        cls,
        sectors: list[SectorBreadth],
    ) -> list[SectorStrength]:
        """
        Analyze and rank all sectors from strongest
        to weakest.
        """

        if not sectors:
            raise ValueError(
                "sectors cannot be empty."
            )

        results = [
            cls.analyze(sector)
            for sector in sectors
        ]

        return sorted(
            results,
            key=lambda item: item.strength_score,
            reverse=True,
        )
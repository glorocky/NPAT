"""
=========================================================
NPAT Dashboard Models
=========================================================

Dashboard-specific models used by the presentation layer.

These models aggregate multiple domain models into
objects optimized for UI rendering.
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from core.models import (
    AIAnalysis,
    ForwardPremiumAnalysis,
    FuturesAnalysis,
    GreeksAnalysis,
    GreeksSummary,
    HeatmapStock,
    HeatmapSummary,
    MarketRegimeAnalysis,
    MarketSnapshot,
    PredictionAnalysis,
    SectorBreadth,
    SectorStrength,
    VixRangeAnalysis,
)


@dataclass(slots=True)
class DashboardSnapshot:
    """
    Complete dashboard snapshot produced by MarketService.
    """

    # =====================================================
    # Core Market
    # =====================================================

    market: MarketSnapshot

    # =====================================================
    # AI
    # =====================================================

    ai: AIAnalysis | None = None

    prediction: PredictionAnalysis | None = None

    market_regime: MarketRegimeAnalysis | None = None

    # =====================================================
    # Greeks
    # =====================================================

    greeks_analysis: list[GreeksAnalysis] | None = None

    greeks_summary: GreeksSummary | None = None

    # =====================================================
    # Premium
    # =====================================================

    premium_analysis: list[ForwardPremiumAnalysis] | None = None
    
    # =====================================================
    # ATM Premium
    # =====================================================

    atm_call_premium: ForwardPremiumAnalysis | None = None

    atm_put_premium: ForwardPremiumAnalysis | None = None

    relative_richness: float | None = None

    # =====================================================
    # Futures
    # =====================================================

    futures: FuturesAnalysis | None = None

    # =====================================================
    # VIX
    # =====================================================

    india_vix: float | None = None

    vix_analysis: VixRangeAnalysis | None = None

    # =====================================================
    # Heatmap
    # =====================================================

    heatmap: list[HeatmapStock] | None = None

    heatmap_summary: HeatmapSummary | None = None

    # =====================================================
    # Sector
    # =====================================================

    sector_breadth: list[SectorBreadth] | None = None

    sector_strength: list[SectorStrength] | None = None

    # =====================================================
    # Participants
    # =====================================================

    participant_data: object | None = None
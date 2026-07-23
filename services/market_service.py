"""
services/market_service.py

Central orchestration service for NPAT.

This service coordinates all providers and analytics modules to build
a complete dashboard snapshot. It contains no provider-specific logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from core.analytics import MarketAnalytics
from core.models import MarketSnapshot, OptionData


@dataclass(slots=True)
class DashboardSnapshot:
    """
    Rich dashboard model.

    Extends the core MarketSnapshot with additional dashboard widgets.
    """

    market: MarketSnapshot

    india_vix: float | None = None

    futures: dict[str, Any] = field(default_factory=dict)

    greeks: dict[str, Any] = field(default_factory=dict)

    participant_data: dict[str, Any] = field(default_factory=dict)

    heatmap: dict[str, Any] = field(default_factory=dict)

    ai_signal: str = "NEUTRAL"

    ai_confidence: float = 0.0

    ai_reasons: list[str] = field(default_factory=list)

    generated_at: datetime = field(default_factory=datetime.now)


class MarketService:
    """
    Central service used by the dashboard.

    The dashboard should communicate only with this class.
    """

    def __init__(
        self,
        provider,
        vix_service=None,
        futures_service=None,
        participant_service=None,
        heatmap_service=None,
        ai_service=None,
    ):
        self.provider = provider

        self.vix_service = vix_service

        self.futures_service = futures_service

        self.participant_service = participant_service

        self.heatmap_service = heatmap_service

        self.ai_service = ai_service

    def get_dashboard_snapshot(
        self,
        symbol: str,
        expiry: str,
    ) -> DashboardSnapshot:
        """
        Returns a complete dashboard snapshot.
        """

        # -----------------------------
        # Option Chain
        # -----------------------------
        options: list[OptionData] = self.provider.get_option_chain(
            symbol=symbol,
            expiry=expiry,
        )

        market_snapshot = MarketAnalytics.build_market_snapshot(
            symbol=symbol,
            expiry=expiry,
            options=options,
        )

        dashboard = DashboardSnapshot(
            market=market_snapshot
        )

        # -----------------------------
        # India VIX
        # -----------------------------
        if self.vix_service:

            dashboard.india_vix = self.vix_service.get_vix()

        # -----------------------------
        # Futures
        # -----------------------------
        if self.futures_service:

            dashboard.futures = (
                self.futures_service.get_futures(symbol)
            )

        # -----------------------------
        # Participant Data
        # -----------------------------
        if self.participant_service:

            dashboard.participant_data = (
                self.participant_service.get_positions()
            )

        # -----------------------------
        # Heatmap
        # -----------------------------
        if self.heatmap_service:

            dashboard.heatmap = (
                self.heatmap_service.get_heatmap(symbol)
            )

        # -----------------------------
        # AI
        # -----------------------------
        if self.ai_service:

            ai = self.ai_service.analyze(dashboard)

            dashboard.ai_signal = ai.signal

            dashboard.ai_confidence = ai.confidence

            dashboard.ai_reasons = ai.reasons

        return dashboard

    def refresh(
        self,
        symbol: str,
        expiry: str,
    ) -> DashboardSnapshot:
        """
        Refresh dashboard data.
        """

        return self.get_dashboard_snapshot(
            symbol,
            expiry,
        )

    def health_check(self) -> dict:
        """
        Basic service health.
        """

        return {
            "provider": self.provider.__class__.__name__,
            "vix": self.vix_service is not None,
            "futures": self.futures_service is not None,
            "participants": self.participant_service is not None,
            "heatmap": self.heatmap_service is not None,
            "ai": self.ai_service is not None,
            "status": "healthy",
        }
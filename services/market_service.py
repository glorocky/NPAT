"""
services/market_service.py

Central orchestration service for NPAT.

This service coordinates all providers and analytics modules to build
a complete dashboard snapshot. It contains no provider-specific logic.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Any
from analytics.futures_analytics import FuturesAnalytics
from analytics.greeks_analytics import GreeksAnalytics
from analytics.market_analytics import MarketAnalytics
from analytics.premium_analytics import PremiumAnalytics
from analytics.heatmap_analytics import HeatmapAnalytics
from data.reference.constituent_loader import ConstituentLoader
from config import RISK_FREE_RATE
from analytics.vix_analytics import VixAnalytics
from analytics.option_positioning_analytics import (
    OptionPositioningAnalytics,
)
from analytics.sector_strength_analytics import (
    SectorStrengthAnalytics,
)
from analytics.market_regime_analytics import (
    MarketRegimeAnalytics,
)
from core.dashboard_models import DashboardSnapshot
from storage.oi_snapshot_store import OISnapshotStore
from core.models import (
    ForwardPremiumAnalysis,
    FuturesAnalysis,
    GreeksAnalysis,
    GreeksSummary,
    HeatmapStock,
    HeatmapSummary,
    SectorBreadth,
    SectorStrength,
    MarketSnapshot,
    OptionData,
    PredictionAnalysis,
    VixRangeAnalysis,
)

    
class MarketService:
    """
    Central service used by the dashboard.

    The dashboard should communicate only with this class.
    """

    def __init__(
        self,
        provider,
        vix_service=None,
        participant_service=None,
        ai_service=None,
    ):
        self.provider = provider

        self.vix_service = vix_service

        self.participant_service = participant_service

        self.ai_service = ai_service
        
        # -----------------------------
        # OI Snapshot State
        # -----------------------------

        self.oi_snapshot_store = OISnapshotStore()

    def get_dashboard_snapshot(
        self,
        symbol: str,
        expiry: str | None = None,
        exchange: str = "NSE",
    ) -> DashboardSnapshot:
        """
        Returns a complete dashboard snapshot.
        """
        # -----------------------------
        # Resolve Active Expiry
        # -----------------------------

        if expiry is None:

            expiries = self.provider.get_expiries(
                exchange=exchange,
                underlying_symbol=symbol,
            )

            if not expiries:
                raise RuntimeError(
                    f"No expiries available for {symbol}."
                )

            today = datetime.now().date()

            active = [
                value
                for value in expiries
                if datetime.strptime(
                    value,
                    "%Y-%m-%d",
                ).date() >= today
            ]

            if not active:
                raise RuntimeError(
                    f"No active expiry available for {symbol}."
                )

            expiry = active[0]
                                
        # -----------------------------
        # Option Chain
        # -----------------------------
        options: list[OptionData] = self.provider.get_option_chain(
            exchange=exchange,
            symbol=symbol,
            expiry=expiry,
        )
        
        # -----------------------------
        # OI / Price Snapshot
        # -----------------------------

        snapshot_time = datetime.now()

        self.oi_snapshot_store.record_option_chain(
            symbol=symbol,
            options=options,
            timestamp=snapshot_time,
        )

        market_snapshot = MarketAnalytics.build_market_snapshot(
            symbol=symbol,
            expiry=expiry,
            options=options,
        )
        
        # -----------------------------
        # Positioning Analytics
        # -----------------------------

        positioning = OptionPositioningAnalytics.analyze_chain(
            symbol=symbol,
            options=options,
            store=self.oi_snapshot_store,
        )

        positioning_summary = (
            OptionPositioningAnalytics.summarize(
                positioning
            )
        )
        
        # -----------------------------
        # ATM Window Positioning
        # -----------------------------

        atm_positioning = (
            OptionPositioningAnalytics.filter_atm_window(
                results=positioning,
                atm_strike=market_snapshot.atm_strike,
                strikes_each_side=5,
            )
        )

        atm_positioning_summary = (
            OptionPositioningAnalytics.summarize(
                atm_positioning
            )
        )
        
        # -----------------------------
        # Top OI Changes
        # -----------------------------

        top_oi_additions = (
            OptionPositioningAnalytics.rank_oi_additions(
                results=atm_positioning,
                limit=5,
            )
        )

        top_oi_reductions = (
            OptionPositioningAnalytics.rank_oi_reductions(
                results=atm_positioning,
                limit=5,
            )
        )
        
        # -----------------------------
        # Enrich Market Snapshot
        # -----------------------------

        market_snapshot = replace(
            market_snapshot,
            positioning=positioning,
            positioning_summary=positioning_summary,
            atm_positioning=atm_positioning,
            atm_positioning_summary=atm_positioning_summary,
            top_oi_additions=top_oi_additions,
            top_oi_reductions=top_oi_reductions,
        )

        dashboard = DashboardSnapshot(
            market=market_snapshot
        )
        
        # -----------------------------
        # Greeks Analytics
        # -----------------------------

        greeks_analysis = GreeksAnalytics.analyze_atm_window(
            provider=self.provider,
            symbol=symbol,
            exchange=exchange,
            expiry=expiry,
            options=options,
            atm_strike=market_snapshot.atm_strike,
            strikes_each_side=3,
        )

        dashboard.greeks_analysis = greeks_analysis

        if greeks_analysis:
            dashboard.greeks_summary = GreeksAnalytics.summarize(
                analysis=greeks_analysis,
                atm_strike=market_snapshot.atm_strike,
            )
            
        # -----------------------------
        # Premium Analytics
        # -----------------------------

        dashboard.premium_analysis = (
            PremiumAnalytics.analyze_common_forward_premiums(
                symbol=symbol,
                options=options,
                atm_strike=market_snapshot.atm_strike,
                expiry=expiry,
                risk_free_rate=RISK_FREE_RATE,
                strikes_each_side=3,
            )
        )
        
        
        # -----------------------------
        # VIX Range Analytics
        # -----------------------------

        nifty_quote = self.provider.get_quote(
            trading_symbol=symbol,
            exchange=exchange,
            segment="CASH",
        )

        vix_quote = self.provider.get_quote(
            trading_symbol="INDIAVIX",
            exchange=exchange,
            segment="CASH",
        )

        dashboard.india_vix = vix_quote.last_price

        dashboard.vix_analysis = VixAnalytics.analyze_daily_range(
            symbol=symbol,
            reference_price=nifty_quote.previous_close,
            india_vix=vix_quote.last_price,
            day_open=nifty_quote.open,
            day_high=nifty_quote.high,
            day_low=nifty_quote.low,
            current_price=nifty_quote.last_price,
        )

        # -----------------------------
        # Futures Analytics
        # -----------------------------

        future = self.provider.get_future(
            symbol=symbol,
            exchange=exchange,
        )

        dashboard.futures = FuturesAnalytics.analyze(
            future=future,
            spot_price=nifty_quote.last_price,
        )
        # -----------------------------
        # Participant Data
        # -----------------------------
        if self.participant_service:

            dashboard.participant_data = (
                self.participant_service.get_positions()
            )
            
        # -----------------------------
        # Heatmap Analytics
        # -----------------------------

        constituents = (
            ConstituentLoader.load_nifty50()
        )

        constituent_symbols = (
            constituents["symbol"].tolist()
        )

        heatmap_ltp = self.provider.get_ltp_batch(
            symbols=constituent_symbols,
            exchange=exchange,
            segment="CASH",
        )

        heatmap_ohlc = self.provider.get_ohlc_batch(
            symbols=constituent_symbols,
            exchange=exchange,
            segment="CASH",
        )

        dashboard.heatmap = (
            HeatmapAnalytics.analyze_constituents(
                constituents=constituents,
                ltp=heatmap_ltp,
                ohlc=heatmap_ohlc,
            )
        )

        dashboard.heatmap_summary = (
            HeatmapAnalytics.summarize(
                heatmap=dashboard.heatmap,
            )
        )
        
        dashboard.sector_breadth = (
            HeatmapAnalytics.summarize_sectors(
                heatmap=dashboard.heatmap,
            )
        )
        
        dashboard.sector_strength = (
            SectorStrengthAnalytics.analyze_all(
                sectors=dashboard.sector_breadth,
            )
        )
        
        # -----------------------------
        # Market Regime
        # -----------------------------
        
        dashboard.market_regime = (
        MarketRegimeAnalytics.analyze(
        futures=dashboard.futures,
        breadth=dashboard.heatmap_summary,
        sectors=dashboard.sector_strength,
        volatility=dashboard.vix_analysis,
            )
        )
        
        # -----------------------------
        # AI
        # -----------------------------
        if self.ai_service:

            dashboard.ai = self.ai_service.analyze(dashboard)

            dashboard.prediction = dashboard.ai.prediction

        return dashboard

    def refresh(
        self,
        symbol: str,
        expiry: str,
        exchange: str = "NSE",
    ) -> DashboardSnapshot:
        """
        Refresh dashboard data.
        """

        return self.get_dashboard_snapshot(
            symbol=symbol,
            expiry=expiry,
            exchange=exchange,
        )

    def health_check(self) -> dict:
        """
        Basic service health.
        """

        return {
            "provider": self.provider.__class__.__name__,
            "vix": self.vix_service is not None,
            "futures": hasattr(self.provider, "get_future"),
            "participants": self.participant_service is not None,
            "heatmap": (
                hasattr(self.provider, "get_ltp_batch")
                and hasattr(self.provider, "get_ohlc_batch")
            ),
            "ai": self.ai_service is not None,
            "status": "healthy",
        }
"""
=========================================================
NPAT - Market Analytics
=========================================================

Purpose
-------
Core market analytics engine.

Converts normalized option-chain data into a
provider-independent MarketSnapshot.

Responsibilities
----------------
- Determine spot price
- Determine ATM strike
- Calculate total Call OI
- Calculate total Put OI
- Calculate PCR
- Build MarketSnapshot

Provider-specific logic must NOT be added here.

Version : 1.0.0
=========================================================
"""

from __future__ import annotations

from analytics.option_analytics import OptionAnalytics
from core.models import (
    MarketSnapshot,
    OptionData,
    PositioningAnalysis,
    PositioningSummary,
)
from providers.exceptions import ProviderDataError


class MarketAnalytics:
    """
    Core provider-independent market analytics.

    Accepts normalized NPAT OptionData objects and produces
    a MarketSnapshot for downstream analytics and services.
    """

    # =====================================================
    # Spot Price
    # =====================================================

    @staticmethod
    def get_spot_price(
        options: list[OptionData],
    ) -> float:
        """
        Return the underlying spot price from the option chain.
        """

        if not options:
            raise ProviderDataError(
                "Cannot determine spot price from an empty option chain."
            )

        spot_price = float(
            options[0].underlying_price
        )

        if spot_price <= 0:
            raise ProviderDataError(
                "Option chain contains an invalid underlying price."
            )

        return spot_price

    # =====================================================
    # ATM Strike
    # =====================================================

    @staticmethod
    def calculate_atm_strike(
        options: list[OptionData],
        spot_price: float,
    ) -> int:
        """
        Return the available strike closest to spot price.

        Using actual available strikes avoids hardcoding
        NIFTY/BANKNIFTY strike intervals in analytics.
        """

        if not options:
            raise ProviderDataError(
                "Cannot calculate ATM from an empty option chain."
            )

        if spot_price <= 0:
            raise ProviderDataError(
                "Cannot calculate ATM using an invalid spot price."
            )

        atm_option = min(
            options,
            key=lambda option: (
                abs(option.strike_price - spot_price),
                option.strike_price,
            ),
        )

        return atm_option.strike_price

    # =====================================================
    # Total Call OI
    # =====================================================

    @staticmethod
    def calculate_total_call_oi(
        options: list[OptionData],
    ) -> int:
        """
        Calculate total Call open interest.
        """

        return sum(
            max(option.call_oi, 0)
            for option in options
        )

    # =====================================================
    # Total Put OI
    # =====================================================

    @staticmethod
    def calculate_total_put_oi(
        options: list[OptionData],
    ) -> int:
        """
        Calculate total Put open interest.
        """

        return sum(
            max(option.put_oi, 0)
            for option in options
        )

    # =====================================================
    # PCR
    # =====================================================

    @staticmethod
    def calculate_pcr(
        total_put_oi: int,
        total_call_oi: int,
    ) -> float:
        """
        Calculate Put-Call Ratio using open interest.

        PCR = Total Put OI / Total Call OI
        """

        if total_call_oi <= 0:
            return 0.0

        return total_put_oi / total_call_oi
    

    # =====================================================
    # Build Market Snapshot
    # =====================================================

    @classmethod
    def build_market_snapshot(
        cls,
        symbol: str,
        expiry: str,
        options: list[OptionData],
        exchange: str = "NSE",
        positioning_summary: PositioningSummary | None = None,
        atm_positioning_summary: PositioningSummary | None = None,
        positioning: list[PositioningAnalysis] | None = None,
        atm_positioning: list[PositioningAnalysis] | None = None,
        top_oi_additions: list[PositioningAnalysis] | None = None,
        top_oi_reductions: list[PositioningAnalysis] | None = None,
    ) -> MarketSnapshot:
        """
        Build the core NPAT MarketSnapshot.
        """

        if not symbol:
            raise ValueError(
                "Symbol is required to build MarketSnapshot."
            )

        if not expiry:
            raise ValueError(
                "Expiry is required to build MarketSnapshot."
            )

        if not options:
            raise ProviderDataError(
                "Cannot build MarketSnapshot from an empty option chain."
            )

        # -------------------------------------------------
        # Spot
        # -------------------------------------------------

        spot_price = cls.get_spot_price(
            options
        )

        # -------------------------------------------------
        # ATM
        # -------------------------------------------------

        atm_strike = cls.calculate_atm_strike(
            options=options,
            spot_price=spot_price,
        )

        # -------------------------------------------------
        # Open Interest
        # -------------------------------------------------

        total_call_oi = cls.calculate_total_call_oi(
            options
        )

        total_put_oi = cls.calculate_total_put_oi(
            options
        )

        # -------------------------------------------------
        # PCR
        # -------------------------------------------------

        pcr = cls.calculate_pcr(
            total_put_oi=total_put_oi,
            total_call_oi=total_call_oi,
        )
        
        # -------------------------------------------------
        # Option Analytics
        # -------------------------------------------------

        max_pain = OptionAnalytics.calculate_max_pain(
            options
        )

        support = OptionAnalytics.calculate_support(
            options=options,
            limit=3,
        )

        resistance = OptionAnalytics.calculate_resistance(
            options=options,
            limit=3,
        )

        # -------------------------------------------------
        # Snapshot
        # -------------------------------------------------

        return MarketSnapshot(
            symbol=symbol,
            exchange=exchange,
            spot_price=spot_price,
            expiry=expiry,
            atm_strike=atm_strike,
            pcr=pcr,
            max_pain=max_pain,
            support=support,
            resistance=resistance,
            total_call_oi=total_call_oi,
            total_put_oi=total_put_oi,
            option_chain=list(options),
            # ---------------------------------------------
            # Positioning Analytics
            # ---------------------------------------------

            positioning_summary=positioning_summary,

            atm_positioning_summary=atm_positioning_summary,

            positioning=list(
                positioning or []
            ),

            atm_positioning=list(
                atm_positioning or []
            ),

            top_oi_additions=list(
                top_oi_additions or []
            ),

            top_oi_reductions=list(
                top_oi_reductions or []
            ),
        )
"""
analytics/positioning_analytics.py

Price and Open Interest positioning analytics for NPAT.
"""

from __future__ import annotations

from core.models import PositioningAnalysis


class PositioningAnalytics:
    """
    Classify market positioning using price change
    and Open Interest change.
    """

    # =====================================================
    # Percentage Change
    # =====================================================

    @staticmethod
    def _change_pct(
        current: float,
        previous: float,
    ) -> float:
        """
        Calculate percentage change.

        Returns 0.0 when previous value is zero.
        """

        if previous == 0:
            return 0.0

        return (
            (current - previous)
            / previous
            * 100.0
        )

    # =====================================================
    # Classification
    # =====================================================

    @staticmethod
    def _classify(
        price_change: float,
        oi_change: int,
    ) -> str:
        """
        Classify price/OI behavior.
        """

        if price_change > 0 and oi_change > 0:
            return "LONG_BUILDUP"

        if price_change < 0 and oi_change > 0:
            return "SHORT_BUILDUP"

        if price_change < 0 and oi_change < 0:
            return "LONG_UNWINDING"

        if price_change > 0 and oi_change < 0:
            return "SHORT_COVERING"

        return "NEUTRAL"

    # =====================================================
    # Analyze
    # =====================================================

    @classmethod
    def analyze(
        cls,
        symbol: str,
        expiry: str,
        strike_price: int,
        option_type: str,
        previous_price: float,
        current_price: float,
        previous_oi: int,
        current_oi: int,
    ) -> PositioningAnalysis:
        """
        Analyze positioning for one contract.
        """

        # -------------------------------------------------
        # Validation
        # -------------------------------------------------

        if not symbol:
            raise ValueError(
                "symbol is required."
            )

        if not expiry:
            raise ValueError(
                "expiry is required."
            )

        if strike_price <= 0:
            raise ValueError(
                "strike_price must be greater than zero."
            )

        option_type = option_type.upper()

        if option_type not in {"CE", "PE"}:
            raise ValueError(
                "option_type must be CE or PE."
            )

        if previous_price < 0:
            raise ValueError(
                "previous_price cannot be negative."
            )

        if current_price < 0:
            raise ValueError(
                "current_price cannot be negative."
            )

        if previous_oi < 0:
            raise ValueError(
                "previous_oi cannot be negative."
            )

        if current_oi < 0:
            raise ValueError(
                "current_oi cannot be negative."
            )

        # -------------------------------------------------
        # Changes
        # -------------------------------------------------

        price_change = (
            current_price
            - previous_price
        )

        oi_change = (
            current_oi
            - previous_oi
        )

        price_change_pct = cls._change_pct(
            current=current_price,
            previous=previous_price,
        )

        oi_change_pct = cls._change_pct(
            current=float(current_oi),
            previous=float(previous_oi),
        )

        # -------------------------------------------------
        # Classification
        # -------------------------------------------------

        classification = cls._classify(
            price_change=price_change,
            oi_change=oi_change,
        )

        # -------------------------------------------------
        # Result
        # -------------------------------------------------

        return PositioningAnalysis(
            symbol=symbol.upper(),
            expiry=expiry,
            strike_price=int(strike_price),
            option_type=option_type,

            previous_price=float(previous_price),
            current_price=float(current_price),
            price_change=float(price_change),
            price_change_pct=float(price_change_pct),

            previous_oi=int(previous_oi),
            current_oi=int(current_oi),
            oi_change=int(oi_change),
            oi_change_pct=float(oi_change_pct),

            classification=classification,
        )
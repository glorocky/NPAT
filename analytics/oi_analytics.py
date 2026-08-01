"""
analytics/oi_analytics.py

Open Interest analytics for NPAT.

Calculates session-level and interval-level changes
in open interest for an option contract.
"""

from __future__ import annotations

from core.models import OIAnalysis


class OIAnalytics:
    """
    Open Interest analytics engine.

    This class performs calculations only.
    Snapshot storage and market-data retrieval belong
    outside the analytics layer.
    """

    # =====================================================
    # Percentage Change
    # =====================================================

    @staticmethod
    def _calculate_change_pct(
        change: int,
        baseline: int,
    ) -> float:
        """
        Calculate percentage change relative to baseline.

        Returns 0.0 when baseline is zero because a
        percentage change is not mathematically defined.
        """

        if baseline == 0:
            return 0.0

        return (
            float(change)
            / float(baseline)
            * 100.0
        )

    # =====================================================
    # Analyze OI
    # =====================================================

    @classmethod
    def analyze(
        cls,
        symbol: str,
        expiry: str,
        strike_price: int,
        option_type: str,
        current_oi: int,
        session_baseline_oi: int,
        previous_oi: int,
    ) -> OIAnalysis:
        """
        Analyze OI changes for one option contract.

        session_change_oi:
            Current OI - session baseline OI

        interval_change_oi:
            Current OI - previous polling snapshot OI
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

        if current_oi < 0:
            raise ValueError(
                "current_oi cannot be negative."
            )

        if session_baseline_oi < 0:
            raise ValueError(
                "session_baseline_oi cannot be negative."
            )

        if previous_oi < 0:
            raise ValueError(
                "previous_oi cannot be negative."
            )

        # -------------------------------------------------
        # Session Change
        # -------------------------------------------------

        session_change_oi = (
            current_oi
            - session_baseline_oi
        )

        session_change_oi_pct = (
            cls._calculate_change_pct(
                change=session_change_oi,
                baseline=session_baseline_oi,
            )
        )

        # -------------------------------------------------
        # Interval Change
        # -------------------------------------------------

        interval_change_oi = (
            current_oi
            - previous_oi
        )

        interval_change_oi_pct = (
            cls._calculate_change_pct(
                change=interval_change_oi,
                baseline=previous_oi,
            )
        )

        # -------------------------------------------------
        # Result
        # -------------------------------------------------

        return OIAnalysis(
            symbol=symbol.upper(),
            expiry=expiry,
            strike_price=int(
                strike_price
            ),
            option_type=option_type,

            current_oi=int(
                current_oi
            ),

            session_baseline_oi=int(
                session_baseline_oi
            ),

            session_change_oi=int(
                session_change_oi
            ),

            session_change_oi_pct=float(
                session_change_oi_pct
            ),

            previous_oi=int(
                previous_oi
            ),

            interval_change_oi=int(
                interval_change_oi
            ),

            interval_change_oi_pct=float(
                interval_change_oi_pct
            ),
        )
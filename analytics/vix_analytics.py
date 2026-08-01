"""
analytics/vix_analytics.py

India VIX expected-range analytics for NPAT.

Calculates the VIX-implied daily NIFTY range and compares
that expected range with the actual intraday movement.
"""

from __future__ import annotations

import math

from core.models import VixRangeAnalysis


class VixAnalytics:
    """
    India VIX range analytics engine.

    This module performs calculations only.
    It does not fetch VIX or NIFTY market data.
    """

    TRADING_DAYS_PER_YEAR = 252

    # =====================================================
    # Expected Daily Move
    # =====================================================

    @classmethod
    def calculate_expected_daily_move_pct(
        cls,
        india_vix: float,
    ) -> float:
        """
        Convert annualized India VIX into an approximate
        one-standard-deviation daily move percentage.

        Example:

        VIX = 16

        daily move ≈ 16 / sqrt(252)
        """

        if india_vix < 0:
            raise ValueError(
                "india_vix cannot be negative."
            )

        return float(
            india_vix
            / math.sqrt(
                cls.TRADING_DAYS_PER_YEAR
            )
        )

    # =====================================================
    # Full Range Analysis
    # =====================================================

    @classmethod
    def analyze_daily_range(
        cls,
        symbol: str,
        reference_price: float,
        india_vix: float,
        day_open: float,
        day_high: float,
        day_low: float,
        current_price: float,
    ) -> VixRangeAnalysis:
        """
        Calculate the VIX-implied expected daily range and
        compare it with the actual range achieved so far.

        reference_price should remain fixed for the session.
        For example, the previous close may be used.

        It should not be replaced continuously with LTP.
        """

        # -------------------------------------------------
        # Validation
        # -------------------------------------------------

        if not symbol:
            raise ValueError(
                "symbol is required."
            )

        if reference_price <= 0:
            raise ValueError(
                "reference_price must be greater than zero."
            )

        if india_vix < 0:
            raise ValueError(
                "india_vix cannot be negative."
            )

        if day_open <= 0:
            raise ValueError(
                "day_open must be greater than zero."
            )

        if day_high <= 0:
            raise ValueError(
                "day_high must be greater than zero."
            )

        if day_low <= 0:
            raise ValueError(
                "day_low must be greater than zero."
            )

        if current_price <= 0:
            raise ValueError(
                "current_price must be greater than zero."
            )

        if day_high < day_low:
            raise ValueError(
                "day_high cannot be below day_low."
            )

        # -------------------------------------------------
        # Expected Daily Move %
        # -------------------------------------------------

        expected_move_pct = (
            cls.calculate_expected_daily_move_pct(
                india_vix=india_vix,
            )
        )

        # -------------------------------------------------
        # Expected Move In Points
        # -------------------------------------------------

        expected_move_points = (
            reference_price
            * expected_move_pct
            / 100.0
        )

        # -------------------------------------------------
        # Expected Bounds
        # -------------------------------------------------

        expected_lower = (
            reference_price
            - expected_move_points
        )

        expected_upper = (
            reference_price
            + expected_move_points
        )

        expected_total_range = (
            expected_upper
            - expected_lower
        )

        # -------------------------------------------------
        # Actual Intraday Range
        # -------------------------------------------------

        actual_range = (
            day_high
            - day_low
        )

        actual_range_pct = (
            actual_range
            / reference_price
            * 100.0
        )

        # -------------------------------------------------
        # Expected Range Achieved
        # -------------------------------------------------

        if expected_total_range > 0:

            range_achieved_pct = (
                actual_range
                / expected_total_range
                * 100.0
            )

        else:

            range_achieved_pct = 0.0
            
        # -------------------------------------------------
        # Directional Range Usage
        # -------------------------------------------------

        upside_achieved_points = max(
            day_high - reference_price,
            0.0,
        )

        downside_achieved_points = max(
            reference_price - day_low,
            0.0,
        )

        if expected_move_points > 0:

            upside_achieved_pct = (
                upside_achieved_points
                / expected_move_points
                * 100.0
            )

            downside_achieved_pct = (
                downside_achieved_points
                / expected_move_points
                * 100.0
            )

        else:

            upside_achieved_pct = 0.0
            downside_achieved_pct = 0.0

        # -------------------------------------------------
        # Remaining Range From Current Price
        # -------------------------------------------------

        upside_remaining = max(
            expected_upper
            - current_price,
            0.0,
        )

        downside_remaining = max(
            current_price
            - expected_lower,
            0.0,
        )
        
        # -------------------------------------------------
        # Unused Expected Allowance
        # -------------------------------------------------

        unused_upside_points = max(
            expected_upper
            - day_high,
            0.0,
        )

        unused_downside_points = max(
            day_low
            - expected_lower,
            0.0,
        )

        # -------------------------------------------------
        # Boundary Breach Distance
        # -------------------------------------------------

        upside_breach_points = max(
            day_high
            - expected_upper,
            0.0,
        )

        downside_breach_points = max(
            expected_lower
            - day_low,
            0.0,
        )

        # -------------------------------------------------
        # Range Exceeded
        # -------------------------------------------------

        upper_range_exceeded = (
            day_high
            >= expected_upper
        )

        lower_range_exceeded = (
            day_low
            <= expected_lower
        )

        expected_range_exceeded = (
            upper_range_exceeded
            or lower_range_exceeded
        )

        # -------------------------------------------------
        # Result
        # -------------------------------------------------

        return VixRangeAnalysis(
            symbol=symbol,

            reference_price=float(
                reference_price
            ),

            india_vix=float(
                india_vix
            ),

            day_open=float(
                day_open
            ),

            day_high=float(
                day_high
            ),

            day_low=float(
                day_low
            ),

            current_price=float(
                current_price
            ),

            expected_move_pct=float(
                expected_move_pct
            ),

            expected_move_points=float(
                expected_move_points
            ),

            expected_lower=float(
                expected_lower
            ),

            expected_upper=float(
                expected_upper
            ),

            expected_total_range=float(
                expected_total_range
            ),

            actual_range=float(
                actual_range
            ),

            actual_range_pct=float(
                actual_range_pct
            ),

            range_achieved_pct=float(
                range_achieved_pct
            ),
            
                        upside_achieved_points=float(
                upside_achieved_points
            ),

            downside_achieved_points=float(
                downside_achieved_points
            ),

            upside_achieved_pct=float(
                upside_achieved_pct
            ),

            downside_achieved_pct=float(
                downside_achieved_pct
            ),

            # -----------------------------------------
            # Remaining Range From Current Price
            # -----------------------------------------

            upside_remaining=float(
                upside_remaining
            ),

            downside_remaining=float(
                downside_remaining
            ),

            # -----------------------------------------
            # Unused Expected Allowance
            # -----------------------------------------

            unused_upside_points=float(
                unused_upside_points
            ),

            unused_downside_points=float(
                unused_downside_points
            ),

            # -----------------------------------------
            # Boundary Breach Distance
            # -----------------------------------------

            upside_breach_points=float(
                upside_breach_points
            ),

            downside_breach_points=float(
                downside_breach_points
            ),

            # -----------------------------------------
            # Range Status
            # -----------------------------------------

            upper_range_exceeded=bool(
                upper_range_exceeded
            ),

            lower_range_exceeded=bool(
                lower_range_exceeded
            ),

            expected_range_exceeded=bool(
                expected_range_exceeded
            ),
        )
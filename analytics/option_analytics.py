"""
=========================================================
NPAT - Option Analytics
=========================================================

Purpose
-------
Provider-independent option-chain analytics.

Responsibilities
----------------
- Calculate Max Pain
- Identify OI-based support
- Identify OI-based resistance
- Rank Call OI concentration
- Rank Put OI concentration

Input
-----
Normalized NPAT OptionData models.

Provider-specific logic must NOT be added here.

Version : 1.0.0
=========================================================
"""

from __future__ import annotations

from core.models import MarketLevel, OptionData


class OptionAnalytics:
    """
    Provider-independent option-chain analytics engine.
    """

    # =====================================================
    # Validation
    # =====================================================

    @staticmethod
    def _validate_options(
        options: list[OptionData],
    ) -> None:
        """
        Validate option-chain input.
        """

        if not options:
            raise ValueError(
                "Option chain cannot be empty."
            )

    # =====================================================
    # Call OI Concentration
    # =====================================================

    @classmethod
    def get_call_oi_levels(
        cls,
        options: list[OptionData],
        limit: int = 3,
    ) -> list[MarketLevel]:
        """
        Return strikes with the highest Call OI.

        These levels may act as resistance zones.
        """

        cls._validate_options(options)

        if limit <= 0:
            return []

        ranked = sorted(
            options,
            key=lambda option: option.call_oi,
            reverse=True,
        )

        return [
            MarketLevel(
                strike=option.strike_price,
                open_interest=option.call_oi,
                change_in_oi=option.call_change_oi,
            )
            for option in ranked[:limit]
        ]

    # =====================================================
    # Put OI Concentration
    # =====================================================

    @classmethod
    def get_put_oi_levels(
        cls,
        options: list[OptionData],
        limit: int = 3,
    ) -> list[MarketLevel]:
        """
        Return strikes with the highest Put OI.

        These levels may act as support zones.
        """

        cls._validate_options(options)

        if limit <= 0:
            return []

        ranked = sorted(
            options,
            key=lambda option: option.put_oi,
            reverse=True,
        )

        return [
            MarketLevel(
                strike=option.strike_price,
                open_interest=option.put_oi,
                change_in_oi=option.put_change_oi,
            )
            for option in ranked[:limit]
        ]

    # =====================================================
    # Support
    # =====================================================

    @classmethod
    def calculate_support(
        cls,
        options: list[OptionData],
        limit: int = 3,
    ) -> list[MarketLevel]:
        """
        Identify OI-based support levels.

        Highest Put OI concentrations are treated as
        potential support zones.
        """

        return cls.get_put_oi_levels(
            options=options,
            limit=limit,
        )

    # =====================================================
    # Resistance
    # =====================================================

    @classmethod
    def calculate_resistance(
        cls,
        options: list[OptionData],
        limit: int = 3,
    ) -> list[MarketLevel]:
        """
        Identify OI-based resistance levels.

        Highest Call OI concentrations are treated as
        potential resistance zones.
        """

        return cls.get_call_oi_levels(
            options=options,
            limit=limit,
        )

    # =====================================================
    # Max Pain
    # =====================================================

    @classmethod
    def calculate_max_pain(
        cls,
        options: list[OptionData],
    ) -> int:
        """
        Calculate the Max Pain strike.

        For every possible settlement strike, calculate the
        aggregate intrinsic-value payout implied by Call and
        Put open interest.

        The strike with the lowest total payout is returned.
        """

        cls._validate_options(options)

        strikes = sorted(
            option.strike_price
            for option in options
        )

        minimum_pain: float | None = None
        max_pain_strike: int | None = None

        for settlement_strike in strikes:

            total_pain = 0.0

            for option in options:

                # -----------------------------------------
                # Call payout
                # -----------------------------------------

                call_intrinsic = max(
                    settlement_strike
                    - option.strike_price,
                    0,
                )

                total_pain += (
                    call_intrinsic
                    * max(option.call_oi, 0)
                )

                # -----------------------------------------
                # Put payout
                # -----------------------------------------

                put_intrinsic = max(
                    option.strike_price
                    - settlement_strike,
                    0,
                )

                total_pain += (
                    put_intrinsic
                    * max(option.put_oi, 0)
                )

            if (
                minimum_pain is None
                or total_pain < minimum_pain
            ):
                minimum_pain = total_pain
                max_pain_strike = settlement_strike

        if max_pain_strike is None:
            raise ValueError(
                "Unable to calculate Max Pain."
            )

        return max_pain_strike
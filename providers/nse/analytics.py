"""
core/analytics.py

Provider-independent options analytics engine.

This module operates exclusively on domain models (OptionData,
MarketLevel and MarketSnapshot) and contains no provider-specific
logic. Any provider (NSE, Groww, Shoonya, etc.) can reuse this
analytics engine after converting its data into OptionData objects.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from core.models import MarketLevel, MarketSnapshot, OptionData

# Floating point tolerance used when validating spot prices
FLOAT_TOLERANCE = 1e-6


class MarketAnalytics:
    """Pure analytics engine built on NPAT domain models."""

    DEFAULT_DEPTH = 5

    @staticmethod
    def get_atm_strike(
        options: list[OptionData],
        spot_price: float,
    ) -> int:
        """
        Returns the ATM strike.

        If two strikes are equally distant from the spot price,
        the lower strike is preferred for deterministic behaviour.
        """
        if not options:
            raise ValueError("Option chain cannot be empty.")

        return min(
            options,
            key=lambda o: (
                abs(o.strike_price - spot_price),
                o.strike_price,
            ),
        ).strike_price

    @staticmethod
    def calculate_total_call_oi(
        options: list[OptionData],
    ) -> int:
        """Returns total Call Open Interest."""
        return sum(option.call_oi for option in options)

    @staticmethod
    def calculate_total_put_oi(
        options: list[OptionData],
    ) -> int:
        """Returns total Put Open Interest."""
        return sum(option.put_oi for option in options)

    @staticmethod
    def calculate_pcr(
        total_call_oi: int,
        total_put_oi: int,
    ) -> float:
        """
        Returns Put Call Ratio.

        Raw float is returned intentionally.
        Presentation layer may round if required.
        """
        if total_call_oi == 0:
            return float("inf") if total_put_oi > 0 else 0.0

        return total_put_oi / total_call_oi

    @staticmethod
    def find_support(
        options: list[OptionData],
        depth: int = DEFAULT_DEPTH,
    ) -> list[MarketLevel]:
        """
        Returns strongest support levels.

        Ranking:
        1. Highest Put OI
        2. Highest Change in Put OI
        3. Lower strike
        """

        ranked = sorted(
            options,
            key=lambda o: (
                -o.put_oi,
                -o.put_change_oi,
                o.strike_price,
            ),
        )

        return [
            MarketLevel(
                strike=option.strike_price,
                open_interest=option.put_oi,
                change_in_oi=option.put_change_oi,
            )
            for option in ranked[:depth]
            if option.put_oi > 0
        ]

    @staticmethod
    def find_resistance(
        options: list[OptionData],
        depth: int = DEFAULT_DEPTH,
    ) -> list[MarketLevel]:
        """
        Returns strongest resistance levels.

        Ranking:
        1. Highest Call OI
        2. Highest Change in Call OI
        3. Lower strike
        """

        ranked = sorted(
            options,
            key=lambda o: (
                -o.call_oi,
                -o.call_change_oi,
                o.strike_price,
            ),
        )

        return [
            MarketLevel(
                strike=option.strike_price,
                open_interest=option.call_oi,
                change_in_oi=option.call_change_oi,
            )
            for option in ranked[:depth]
            if option.call_oi > 0
        ]

    @staticmethod
    def calculate_max_pain(
        options: list[OptionData],
    ) -> Optional[int]:
        """
        Calculates Max Pain.

        Uses the classical option-writer loss model.
        """

        if not options:
            return None

        strikes = sorted(
            {
                option.strike_price
                for option in options
            }
        )

        minimum_loss = float("inf")
        max_pain = None

        for settlement in strikes:

            total_loss = 0

            for option in options:

                if settlement > option.strike_price:

                    total_loss += (
                        option.call_oi
                        * (settlement - option.strike_price)
                    )

                elif settlement < option.strike_price:

                    total_loss += (
                        option.put_oi
                        * (option.strike_price - settlement)
                    )

            if total_loss < minimum_loss:
                minimum_loss = total_loss
                max_pain = settlement

        return max_pain

    @staticmethod
    def build_market_snapshot(
        symbol: str,
        expiry: str,
        options: list[OptionData],
        exchange: str = "NSE",
        timestamp: Optional[datetime] = None,
    ) -> MarketSnapshot:
        """
        Builds a provider-independent MarketSnapshot.
        """

        if not options:
            raise ValueError(
                "Cannot build snapshot from an empty option chain."
            )

        if any(
            option.expiry != expiry
            for option in options
        ):
            raise ValueError(
                f"Mixed expiries detected. Expected '{expiry}'."
            )

        reference_price = options[0].underlying_price

        if any(
            abs(option.underlying_price - reference_price)
            > FLOAT_TOLERANCE
            for option in options
        ):
            raise ValueError(
                "Underlying prices are inconsistent."
            )

        total_call_oi = (
            MarketAnalytics.calculate_total_call_oi(options)
        )

        total_put_oi = (
            MarketAnalytics.calculate_total_put_oi(options)
        )

        snapshot = MarketSnapshot(
            symbol=symbol,
            exchange=exchange,
            expiry=expiry,
            timestamp=timestamp or datetime.now(),
            spot_price=reference_price,
            atm_strike=MarketAnalytics.get_atm_strike(
                options,
                reference_price,
            ),
            total_call_oi=total_call_oi,
            total_put_oi=total_put_oi,
            pcr=MarketAnalytics.calculate_pcr(
                total_call_oi,
                total_put_oi,
            ),
            max_pain=MarketAnalytics.calculate_max_pain(
                options
            ),
            support=MarketAnalytics.find_support(options),
            resistance=MarketAnalytics.find_resistance(options),
            option_chain=options,
        )

        return snapshot
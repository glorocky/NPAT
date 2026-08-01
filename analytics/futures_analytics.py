"""
=========================================================
NPAT - Futures Analytics
=========================================================

Futures-specific analytics built from normalized FutureData.

Responsibilities
----------------
- Spot/Futures Basis
- Futures Price Change
- Futures OI Change
- Price/OI Positioning
- Buy/Sell Quantity Imbalance

No provider-specific logic belongs in this module.
=========================================================
"""

from __future__ import annotations

from core.models import (
    FutureData,
    FuturesAnalysis,
)


class FuturesAnalytics:
    """
    Analyze one normalized futures contract.
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

        Returns 0.0 when previous is zero.
        """

        if previous == 0:
            return 0.0

        return (
            (current - previous)
            / previous
        ) * 100.0

    # =====================================================
    # Futures Positioning
    # =====================================================

    @staticmethod
    def _classify_positioning(
        price_change: float,
        oi_change: int,
    ) -> str:
        """
        Classify futures positioning from price and OI.
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
        future: FutureData,
        spot_price: float,
    ) -> FuturesAnalysis:
        """
        Build futures analytics for one contract.
        """

        # -------------------------------------------------
        # Validation
        # -------------------------------------------------

        if not isinstance(
            future,
            FutureData,
        ):
            raise TypeError(
                "future must be a FutureData object."
            )

        if spot_price <= 0:
            raise ValueError(
                "spot_price must be greater than zero."
            )

        if future.last_price < 0:
            raise ValueError(
                "future last_price cannot be negative."
            )

        if future.previous_close < 0:
            raise ValueError(
                "future previous_close cannot be negative."
            )

        if future.open_interest < 0:
            raise ValueError(
                "future open_interest cannot be negative."
            )

        if future.previous_open_interest < 0:
            raise ValueError(
                "future previous_open_interest cannot be negative."
            )

        # -------------------------------------------------
        # Basis
        # -------------------------------------------------

        basis = (
            future.last_price
            - spot_price
        )

        basis_pct = (
            basis
            / spot_price
        ) * 100.0

        # -------------------------------------------------
        # Price Change
        # -------------------------------------------------

        previous_price = (
            future.previous_close
        )

        price_change = (
            future.last_price
            - previous_price
        )

        price_change_pct = cls._change_pct(
            current=future.last_price,
            previous=previous_price,
        )

        # -------------------------------------------------
        # Open Interest
        # -------------------------------------------------

        previous_oi = (
            future.previous_open_interest
        )

        current_oi = (
            future.open_interest
        )

        oi_change = (
            current_oi
            - previous_oi
        )

        oi_change_pct = cls._change_pct(
            current=float(current_oi),
            previous=float(previous_oi),
        )

        # -------------------------------------------------
        # Positioning
        # -------------------------------------------------

        positioning = cls._classify_positioning(
            price_change=price_change,
            oi_change=oi_change,
        )

        # -------------------------------------------------
        # Quantity Imbalance
        # -------------------------------------------------

        buy_quantity = (
            future.total_buy_quantity
        )

        sell_quantity = (
            future.total_sell_quantity
        )

        quantity_imbalance = (
            buy_quantity
            - sell_quantity
        )

        total_quantity = (
            buy_quantity
            + sell_quantity
        )

        if total_quantity > 0:

            quantity_imbalance_pct = (
                quantity_imbalance
                / total_quantity
            ) * 100.0

        else:

            quantity_imbalance_pct = 0.0

        # -------------------------------------------------
        # Result
        # -------------------------------------------------

        return FuturesAnalysis(
            symbol=future.symbol,
            exchange=future.exchange,
            trading_symbol=future.trading_symbol,
            expiry=future.expiry,

            spot_price=float(spot_price),
            futures_price=float(
                future.last_price
            ),

            basis=float(basis),
            basis_pct=float(basis_pct),

            previous_price=float(
                previous_price
            ),

            price_change=float(
                price_change
            ),

            price_change_pct=float(
                price_change_pct
            ),

            previous_oi=int(
                previous_oi
            ),

            current_oi=int(
                current_oi
            ),

            oi_change=int(
                oi_change
            ),

            oi_change_pct=float(
                oi_change_pct
            ),

            positioning=positioning,

            volume=int(
                future.volume
            ),

            total_buy_quantity=int(
                buy_quantity
            ),

            total_sell_quantity=int(
                sell_quantity
            ),

            quantity_imbalance=int(
                quantity_imbalance
            ),

            quantity_imbalance_pct=float(
                quantity_imbalance_pct
            ),

            lot_size=int(
                future.lot_size
            ),
        )
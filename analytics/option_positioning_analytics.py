"""
analytics/option_positioning_analytics.py

Full option-chain positioning analytics for NPAT.
"""

from __future__ import annotations

from analytics.positioning_analytics import PositioningAnalytics
from core.models import (
    OptionData,
    PositioningAnalysis,
    PositioningSummary,
)
from storage.oi_snapshot_store import OISnapshotStore


class OptionPositioningAnalytics:
    """
    Analyze positioning across an NPAT option chain.

    Each strike can produce:
    - one CE PositioningAnalysis
    - one PE PositioningAnalysis
    """

    # =====================================================
    # Analyze Option Chain
    # =====================================================

    @classmethod
    def analyze_chain(
        cls,
        symbol: str,
        options: list[OptionData],
        store: OISnapshotStore,
    ) -> list[PositioningAnalysis]:
        """
        Analyze all contracts having both previous and
        current snapshots.

        Contracts without sufficient snapshot history
        are skipped.
        """

        if not symbol:
            raise ValueError(
                "symbol is required."
            )

        if not isinstance(store, OISnapshotStore):
            raise TypeError(
                "store must be an OISnapshotStore."
            )

        if not options:
            return []

        results: list[PositioningAnalysis] = []

        for option in options:

            if not isinstance(option, OptionData):
                raise TypeError(
                    "options must contain OptionData objects."
                )

            # =================================================
            # CE / PE
            # =================================================

            for option_type in ("CE", "PE"):

                previous = store.get_previous(
                    symbol=symbol,
                    expiry=option.expiry,
                    strike_price=option.strike_price,
                    option_type=option_type,
                )

                current = store.get_current(
                    symbol=symbol,
                    expiry=option.expiry,
                    strike_price=option.strike_price,
                    option_type=option_type,
                )

                # Two observations are required.
                if previous is None or current is None:
                    continue

                analysis = PositioningAnalytics.analyze(
                    symbol=symbol,
                    expiry=option.expiry,
                    strike_price=option.strike_price,
                    option_type=option_type,

                    previous_price=previous.price,
                    current_price=current.price,

                    previous_oi=previous.open_interest,
                    current_oi=current.open_interest,
                )

                results.append(
                    analysis
                )

        # =================================================
        # Stable Ordering
        # =================================================

        results.sort(
            key=lambda item: (
                item.strike_price,
                item.option_type,
            )
        )

        return results
    # =====================================================
    # Summarize Positioning
    # =====================================================

    @staticmethod
    def summarize(
        results: list[PositioningAnalysis],
    ) -> PositioningSummary:
        """
        Aggregate positioning classifications into
        combined, CE and PE counts.
        """

        # -------------------------------------------------
        # Classification Counter
        # -------------------------------------------------

        def count(
            items: list[PositioningAnalysis],
            classification: str,
        ) -> int:

            return sum(
                1
                for item in items
                if item.classification == classification
            )

        # -------------------------------------------------
        # Split CE / PE
        # -------------------------------------------------

        ce_results = [
            item
            for item in results
            if item.option_type == "CE"
        ]

        pe_results = [
            item
            for item in results
            if item.option_type == "PE"
        ]

        # -------------------------------------------------
        # Build Summary
        # -------------------------------------------------

        return PositioningSummary(
            total_contracts=len(results),

            # Combined
            long_buildup=count(
                results,
                "LONG_BUILDUP",
            ),
            short_buildup=count(
                results,
                "SHORT_BUILDUP",
            ),
            long_unwinding=count(
                results,
                "LONG_UNWINDING",
            ),
            short_covering=count(
                results,
                "SHORT_COVERING",
            ),
            neutral=count(
                results,
                "NEUTRAL",
            ),

            # CE
            ce_total=len(ce_results),

            ce_long_buildup=count(
                ce_results,
                "LONG_BUILDUP",
            ),
            ce_short_buildup=count(
                ce_results,
                "SHORT_BUILDUP",
            ),
            ce_long_unwinding=count(
                ce_results,
                "LONG_UNWINDING",
            ),
            ce_short_covering=count(
                ce_results,
                "SHORT_COVERING",
            ),
            ce_neutral=count(
                ce_results,
                "NEUTRAL",
            ),

            # PE
            pe_total=len(pe_results),

            pe_long_buildup=count(
                pe_results,
                "LONG_BUILDUP",
            ),
            pe_short_buildup=count(
                pe_results,
                "SHORT_BUILDUP",
            ),
            pe_long_unwinding=count(
                pe_results,
                "LONG_UNWINDING",
            ),
            pe_short_covering=count(
                pe_results,
                "SHORT_COVERING",
            ),
            pe_neutral=count(
                pe_results,
                "NEUTRAL",
            ),
        )
        
    # =====================================================
    # ATM Window
    # =====================================================

    @staticmethod
    def filter_atm_window(
        results: list[PositioningAnalysis],
        atm_strike: int,
        strikes_each_side: int = 5,
    ) -> list[PositioningAnalysis]:
        """
        Return positioning results around the ATM strike.

        Example:
            ATM = 23750
            strikes_each_side = 2

        Selected strikes:
            23650
            23700
            23750
            23800
            23850

        The method uses the actual available strike sequence
        rather than assuming a fixed strike interval.
        """

        if atm_strike <= 0:
            raise ValueError(
                "atm_strike must be greater than zero."
            )

        if strikes_each_side < 0:
            raise ValueError(
                "strikes_each_side cannot be negative."
            )

        if not results:
            return []

        # -------------------------------------------------
        # Available Strikes
        # -------------------------------------------------

        strikes = sorted(
            {
                item.strike_price
                for item in results
            }
        )

        if not strikes:
            return []

        # -------------------------------------------------
        # Find Strike Closest To Requested ATM
        # -------------------------------------------------

        actual_atm = min(
            strikes,
            key=lambda strike:
            abs(strike - atm_strike),
        )

        atm_index = strikes.index(
            actual_atm
        )

        # -------------------------------------------------
        # Window Boundaries
        # -------------------------------------------------

        start_index = max(
            0,
            atm_index - strikes_each_side,
        )

        end_index = min(
            len(strikes),
            atm_index + strikes_each_side + 1,
        )

        selected_strikes = set(
            strikes[start_index:end_index]
        )

        # -------------------------------------------------
        # Filter Results
        # -------------------------------------------------

        filtered = [
            item
            for item in results
            if item.strike_price in selected_strikes
        ]

        filtered.sort(
            key=lambda item: (
                item.strike_price,
                item.option_type,
            )
        )

        return filtered
    
    # =====================================================
    # Rank By OI Change
    # =====================================================

    @staticmethod
    def rank_by_oi_change(
        results: list[PositioningAnalysis],
        limit: int = 5,
        option_type: str | None = None,
    ) -> list[PositioningAnalysis]:
        """
        Rank positioning results by absolute OI change.

        The largest OI movements appear first.

        option_type:
            None -> CE and PE
            "CE" -> CE only
            "PE" -> PE only
        """

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero."
            )

        if option_type is not None:
            option_type = option_type.upper()

            if option_type not in ("CE", "PE"):
                raise ValueError(
                    "option_type must be CE, PE, or None."
                )

        # -------------------------------------------------
        # Filter
        # -------------------------------------------------

        filtered = [
            item
            for item in results
            if (
                option_type is None
                or item.option_type == option_type
            )
        ]

        # -------------------------------------------------
        # Rank
        # -------------------------------------------------

        ranked = sorted(
            filtered,
            key=lambda item: abs(item.oi_change),
            reverse=True,
        )

        return ranked[:limit]
    
        # =====================================================
    # Rank OI Additions
    # =====================================================

    @staticmethod
    def rank_oi_additions(
        results: list[PositioningAnalysis],
        limit: int = 5,
        option_type: str | None = None,
    ) -> list[PositioningAnalysis]:
        """
        Rank contracts where OI increased.

        Largest positive OI change appears first.
        """

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero."
            )

        if option_type is not None:
            option_type = option_type.upper()

            if option_type not in ("CE", "PE"):
                raise ValueError(
                    "option_type must be CE, PE, or None."
                )

        filtered = [
            item
            for item in results
            if (
                item.oi_change > 0
                and (
                    option_type is None
                    or item.option_type == option_type
                )
            )
        ]

        ranked = sorted(
            filtered,
            key=lambda item: item.oi_change,
            reverse=True,
        )

        return ranked[:limit]


    # =====================================================
    # Rank OI Reductions
    # =====================================================

    @staticmethod
    def rank_oi_reductions(
        results: list[PositioningAnalysis],
        limit: int = 5,
        option_type: str | None = None,
    ) -> list[PositioningAnalysis]:
        """
        Rank contracts where OI decreased.

        Largest OI reduction appears first.
        """

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero."
            )

        if option_type is not None:
            option_type = option_type.upper()

            if option_type not in ("CE", "PE"):
                raise ValueError(
                    "option_type must be CE, PE, or None."
                )

        filtered = [
            item
            for item in results
            if (
                item.oi_change < 0
                and (
                    option_type is None
                    or item.option_type == option_type
                )
            )
        ]

        ranked = sorted(
            filtered,
            key=lambda item: item.oi_change,
        )

        return ranked[:limit]
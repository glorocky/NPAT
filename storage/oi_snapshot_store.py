"""
storage/oi_snapshot_store.py

In-memory Open Interest snapshot storage for NPAT.

Responsibilities:
- Store current and previous OI snapshots.
- Maintain an explicitly assigned session baseline.
- Keep storage logic separate from OI analytics.
"""

from __future__ import annotations

from core.models import OptionData, OISnapshot


class OISnapshotStore:
    """
    In-memory OI snapshot store.

    Contract identity:
        symbol + expiry + strike_price + option_type
    """

    def __init__(self) -> None:

        self._current: dict[
            tuple[str, str, int, str],
            OISnapshot,
        ] = {}

        self._previous: dict[
            tuple[str, str, int, str],
            OISnapshot,
        ] = {}

        self._session_baseline: dict[
            tuple[str, str, int, str],
            OISnapshot,
        ] = {}

    # =====================================================
    # Contract Key
    # =====================================================

    @staticmethod
    def _make_key(
        symbol: str,
        expiry: str,
        strike_price: int,
        option_type: str,
    ) -> tuple[str, str, int, str]:

        option_type = option_type.upper()

        if option_type not in {"CE", "PE"}:
            raise ValueError(
                "option_type must be CE or PE."
            )

        return (
            symbol.upper(),
            expiry,
            int(strike_price),
            option_type,
        )

    # =====================================================
    # Record Snapshot
    # =====================================================

    def record(
        self,
        snapshot: OISnapshot,
    ) -> None:
        """
        Record a new OI snapshot.

        Existing current snapshot becomes previous.
        Session baseline is NOT changed automatically.
        """

        key = self._make_key(
            symbol=snapshot.symbol,
            expiry=snapshot.expiry,
            strike_price=snapshot.strike_price,
            option_type=snapshot.option_type,
        )

        current = self._current.get(key)

        if current is not None:
            self._previous[key] = current

        self._current[key] = snapshot
        
    
        # =====================================================
    # Record Option Chain
    # =====================================================

    def record_option_chain(
        self,
        symbol: str,
        options: list[OptionData],
        timestamp,
    ) -> int:
        """
        Record CE and PE OI snapshots from a normalized
        NPAT option chain.

        Returns the number of contract snapshots recorded.
        """

        if not symbol:
            raise ValueError(
                "symbol is required."
            )

        if not options:
            return 0

        recorded = 0

        for option in options:

            if not isinstance(option, OptionData):
                raise TypeError(
                    "options must contain OptionData objects."
                )

            # ---------------------------------------------
            # Call Snapshot
            # ---------------------------------------------

            call_snapshot = OISnapshot(
                symbol=symbol.upper(),
                expiry=option.expiry,
                strike_price=option.strike_price,
                option_type="CE",
                open_interest=option.call_oi,
                price=option.call_ltp,
                timestamp=timestamp,
            )

            self.record(
                call_snapshot
            )

            recorded += 1

            # ---------------------------------------------
            # Put Snapshot
            # ---------------------------------------------

            put_snapshot = OISnapshot(
                symbol=symbol.upper(),
                expiry=option.expiry,
                strike_price=option.strike_price,
                option_type="PE",
                open_interest=option.put_oi,
                price=option.put_ltp,
                timestamp=timestamp,
            )

            self.record(
                put_snapshot
            )

            recorded += 1

        return recorded

    # =====================================================
    # Current Snapshot
    # =====================================================

    def get_current(
        self,
        symbol: str,
        expiry: str,
        strike_price: int,
        option_type: str,
    ) -> OISnapshot | None:

        key = self._make_key(
            symbol,
            expiry,
            strike_price,
            option_type,
        )

        return self._current.get(key)

    # =====================================================
    # Previous Snapshot
    # =====================================================

    def get_previous(
        self,
        symbol: str,
        expiry: str,
        strike_price: int,
        option_type: str,
    ) -> OISnapshot | None:

        key = self._make_key(
            symbol,
            expiry,
            strike_price,
            option_type,
        )

        return self._previous.get(key)

    # =====================================================
    # Session Baseline
    # =====================================================

    def set_session_baseline(
        self,
        snapshot: OISnapshot,
    ) -> None:
        """
        Explicitly set the session baseline.
        record() never changes this value.
        """

        key = self._make_key(
            symbol=snapshot.symbol,
            expiry=snapshot.expiry,
            strike_price=snapshot.strike_price,
            option_type=snapshot.option_type,
        )

        self._session_baseline[key] = snapshot

    def get_session_baseline(
        self,
        symbol: str,
        expiry: str,
        strike_price: int,
        option_type: str,
    ) -> OISnapshot | None:

        key = self._make_key(
            symbol,
            expiry,
            strike_price,
            option_type,
        )

        return self._session_baseline.get(key)
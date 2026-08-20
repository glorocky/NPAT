"""
=========================================================
NPAT - Option Selector
=========================================================

Converts the AI directional signal into a concrete
option trade recommendation.

Initial paper-trading policy:

    BULLISH / BUY  -> BUY CALL
    BEARISH / SELL -> BUY PUT

The selector does not place orders.
It only produces a recommendation.
=========================================================
"""

from __future__ import annotations

from core.models import (
    OptionData,
    OptionTradeRecommendation,
)


class OptionSelector:
    """
    Select a directional option contract from the
    completed dashboard snapshot.
    """

    # =====================================================
    # Public API
    # =====================================================

    @classmethod
    def select(
        cls,
        *,
        symbol: str,
        expiry: str,
        spot_price: float,
        atm_strike: int,
        options: list[OptionData],
        signal: str,
        confidence: float,
    ) -> OptionTradeRecommendation:
        """
        Select the ATM option corresponding to the
        current directional AI signal.
        """

        if not options:
            raise ValueError(
                "Option chain cannot be empty."
            )

        normalized_signal = signal.upper().strip()

        # -------------------------------------------------
        # Direction -> Option Type
        # -------------------------------------------------

        if normalized_signal in {
            "BUY",
            "STRONG_BUY",
        }:
            option_type = "CE"
            action = "BUY CALL"

        elif normalized_signal in {
            "SELL",
            "STRONG_SELL",
        }:
            option_type = "PE"
            action = "BUY PUT"

        else:
            return OptionTradeRecommendation(
                action="NO TRADE",
                option_type="",
                symbol=symbol,
                expiry=expiry,
                strike_price=atm_strike,
                entry_price=0.0,
                spot_price=float(spot_price),
                confidence=float(confidence),
                signal=normalized_signal,
                reason=(
                    "AI signal is NEUTRAL. "
                    "No directional option trade selected."
                ),
            )

        # -------------------------------------------------
        # Find ATM Contract
        # -------------------------------------------------

        atm_option = next(
            (
                option
                for option in options
                if option.strike_price == atm_strike
            ),
            None,
        )

        if atm_option is None:
            raise ValueError(
                f"ATM strike {atm_strike} "
                "was not found in the option chain."
            )

        # -------------------------------------------------
        # Select Market Premium
        # -------------------------------------------------

        if option_type == "CE":
            entry_price = float(
                atm_option.call_ltp
            )
        else:
            entry_price = float(
                atm_option.put_ltp
            )

        if entry_price <= 0:
            raise ValueError(
                f"Invalid {option_type} LTP "
                f"for ATM strike {atm_strike}: "
                f"{entry_price}"
            )

        # -------------------------------------------------
        # Reason
        # -------------------------------------------------

        if option_type == "CE":
            reason = (
                f"AI signal is {normalized_signal}. "
                f"Market direction is bullish, so "
                f"ATM {atm_strike} CALL is selected."
            )
        else:
            reason = (
                f"AI signal is {normalized_signal}. "
                f"Market direction is bearish, so "
                f"ATM {atm_strike} PUT is selected."
            )

        # -------------------------------------------------
        # Recommendation
        # -------------------------------------------------

        return OptionTradeRecommendation(
            action=action,
            option_type=option_type,
            symbol=symbol,
            expiry=expiry,
            strike_price=atm_strike,
            entry_price=entry_price,
            spot_price=float(spot_price),
            confidence=float(confidence),
            signal=normalized_signal,
            reason=reason,
        )
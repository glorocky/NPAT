"""NPAT AI option contract selector."""

from __future__ import annotations

from datetime import datetime

from ai.zero_to_hero import is_zero_to_hero_window, rank_candidates
from core.models import OptionData, OptionTradeRecommendation


class OptionSelector:
    """Select the concrete CE/PE contract for the AI direction."""

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
        premium_analysis=None,
        current_time: datetime | None = None,
    ) -> OptionTradeRecommendation:
        if not options:
            raise ValueError("Option chain cannot be empty.")

        normalized_signal = signal.upper().strip()
        if normalized_signal in {"BUY", "STRONG_BUY"}:
            option_type, action = "CE", "BUY CALL"
        elif normalized_signal in {"SELL", "STRONG_SELL"}:
            option_type, action = "PE", "BUY PUT"
        else:
            return OptionTradeRecommendation(
                action="NO TRADE", option_type="", symbol=symbol, expiry=expiry,
                strike_price=atm_strike, entry_price=0.0, spot_price=float(spot_price),
                confidence=float(confidence), signal=normalized_signal,
                reason="AI signal is NEUTRAL. No directional option trade selected.",
            )

        if is_zero_to_hero_window(expiry, current_time):
            candidate = rank_candidates(
                options=options,
                atm_strike=atm_strike,
                option_type=option_type,
                premium_analysis=premium_analysis,
                max_otm_strikes=3,
            )
            if candidate:
                return OptionTradeRecommendation(
                    action=action,
                    option_type=option_type,
                    symbol=symbol,
                    expiry=expiry,
                    strike_price=candidate.strike_price,
                    entry_price=candidate.market_premium,
                    spot_price=float(spot_price),
                    confidence=float(confidence),
                    signal=normalized_signal,
                    reason=(
                        f"{candidate.reason} Selected during the 13:00-13:30 IST expiry window."
                    ),
                )

        atm_option = next((o for o in options if o.strike_price == atm_strike), None)
        if atm_option is None:
            raise ValueError(f"ATM strike {atm_strike} was not found in the option chain.")

        entry_price = float(atm_option.call_ltp if option_type == "CE" else atm_option.put_ltp)
        if entry_price <= 0:
            raise ValueError(f"Invalid {option_type} LTP for ATM strike {atm_strike}: {entry_price}")

        side_name = "CALL" if option_type == "CE" else "PUT"
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
            reason=(
                f"AI signal is {normalized_signal}. Market direction is "
                f"{'bullish' if option_type == 'CE' else 'bearish'}, so ATM "
                f"{atm_strike} {side_name} is selected."
            ),
        )

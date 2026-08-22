"""NPAT AI option contract selector."""

from __future__ import annotations

from datetime import datetime

from ai.zero_to_hero import _is_valid_contract, is_zero_to_hero_window, parse_expiry_date, rank_candidates
from core.models import OptionData, OptionTradeRecommendation


class OptionSelector:
    """Select a validated CE/PE contract without placing an order."""

    @staticmethod
    def _no_trade(*, symbol: str, expiry: str, spot_price: float, atm_strike: int,
                  confidence: float, signal: str, reason: str) -> OptionTradeRecommendation:
        return OptionTradeRecommendation(
            action="NO TRADE", option_type="", symbol=symbol, expiry=expiry,
            strike_price=atm_strike, entry_price=0.0, spot_price=float(spot_price),
            confidence=float(confidence), signal=signal, reason=reason,
        )

    @classmethod
    def _select(cls, *, symbol: str, expiry: str, spot_price: float, atm_strike: int,
               options: list[OptionData], signal: str, confidence: float,
               premium_analysis=None, current_time: datetime | None = None) -> OptionTradeRecommendation:
        normalized_signal = signal.upper().strip()
        if normalized_signal in {"BUY", "STRONG_BUY"}:
            option_type, action = "CE", "BUY CALL"
        elif normalized_signal in {"SELL", "STRONG_SELL"}:
            option_type, action = "PE", "BUY PUT"
        else:
            return cls._no_trade(symbol=symbol, expiry=expiry, spot_price=spot_price, atm_strike=atm_strike,
                confidence=confidence, signal=normalized_signal,
                reason="AI signal is NEUTRAL. No directional option trade selected.")

        if not options:
            return cls._no_trade(symbol=symbol, expiry=expiry, spot_price=spot_price, atm_strike=atm_strike,
                confidence=confidence, signal=normalized_signal,
                reason="Option chain is unavailable; no contract was selected.")

        expiry_is_valid = parse_expiry_date(expiry) is not None
        if is_zero_to_hero_window(expiry, current_time):
            candidate = rank_candidates(options=options, atm_strike=atm_strike, option_type=option_type,
                premium_analysis=premium_analysis, max_otm_strikes=3)
            if candidate:
                return OptionTradeRecommendation(
                    action=action, option_type=option_type, symbol=symbol, expiry=expiry,
                    strike_price=candidate.strike_price, entry_price=candidate.market_premium,
                    spot_price=float(spot_price), confidence=float(confidence), signal=normalized_signal,
                    reason=f"{candidate.reason} Selected during the 13:00–13:30 IST expiry window.")

        atm_option = next((option for option in options if option.strike_price == atm_strike), None)
        if atm_option is None or not _is_valid_contract(atm_option, option_type):
            return cls._no_trade(symbol=symbol, expiry=expiry, spot_price=spot_price, atm_strike=atm_strike,
                confidence=confidence, signal=normalized_signal,
                reason="No valid, liquid ATM contract is available for the AI direction.")

        entry_price = float(atm_option.call_ltp if option_type == "CE" else atm_option.put_ltp)
        expiry_note = "" if expiry_is_valid else " Expiry format was not recognised; normal ATM selection was used."
        return OptionTradeRecommendation(
            action=action, option_type=option_type, symbol=symbol, expiry=expiry,
            strike_price=atm_strike, entry_price=entry_price, spot_price=float(spot_price),
            confidence=float(confidence), signal=normalized_signal,
            reason=(f"AI signal is {normalized_signal}; validated ATM {atm_strike} "
                    f"{'CALL' if option_type == 'CE' else 'PUT'} is selected.{expiry_note}"))

    @classmethod
    def select(cls, **kwargs) -> OptionTradeRecommendation:
        """Select a contract and retain CE/PE quote identity from the chain."""
        recommendation = cls._select(**kwargs)
        option_type = recommendation.option_type
        if option_type not in {"CE", "PE"}:
            return recommendation
        selected = next(
            (option for option in kwargs["options"]
             if option.strike_price == recommendation.strike_price),
            None,
        )
        if selected is None:
            return recommendation
        if option_type == "CE":
            trading_symbol, lot_size = selected.call_trading_symbol, selected.call_lot_size
        else:
            trading_symbol, lot_size = selected.put_trading_symbol, selected.put_lot_size
        return OptionTradeRecommendation(
            action=recommendation.action, option_type=option_type,
            symbol=recommendation.symbol, expiry=recommendation.expiry,
            strike_price=recommendation.strike_price, entry_price=recommendation.entry_price,
            spot_price=recommendation.spot_price, confidence=recommendation.confidence,
            signal=recommendation.signal, reason=recommendation.reason,
            underlying_symbol=recommendation.symbol, exchange="NSE",
            trading_symbol=trading_symbol, lot_size=int(lot_size), quantity=int(lot_size),
        )

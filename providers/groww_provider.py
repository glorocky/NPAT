"""
=========================================================
NPAT - Groww Provider
=========================================================

Purpose:
    Wrapper around the official Groww SDK.

Responsibilities:
    - Initialize Groww API
    - Fetch Option Chain
    - Fetch Quote
    - Fetch LTP
    - Fetch Historical Candles
    - Fetch Expiries
    - Fetch Greeks

Version : Sprint 1.1
=========================================================
"""

from typing import Optional, Tuple

from growwapi.groww.client import GrowwAPI


class GrowwProvider:
    """
    Wrapper around the official Groww SDK.
    """

    def __init__(self, access_token: str):

        if not access_token:
            raise ValueError("GROWW_ACCESS_TOKEN not found.")

        self.api = GrowwAPI(access_token)

        print("✅ Groww Provider Initialized")

    # ----------------------------------------------------
    # API Object
    # ----------------------------------------------------

    def get_api(self):
        """
        Returns GrowwAPI instance.
        """
        return self.api

    # ----------------------------------------------------
    # Option Chain
    # ----------------------------------------------------

    def get_option_chain(
        self,
        exchange: str,
        underlying: str,
        expiry_date: str,
    ) -> dict:

        return self.api.get_option_chain(
            exchange=exchange,
            underlying=underlying,
            expiry_date=expiry_date,
        )

    # ----------------------------------------------------
    # Quote
    # ----------------------------------------------------

    def get_quote(
        self,
        trading_symbol: str,
        exchange: str,
        segment: str,
    ) -> dict:

        return self.api.get_quote(
            trading_symbol=trading_symbol,
            exchange=exchange,
            segment=segment,
        )

    # ----------------------------------------------------
    # LTP
    # ----------------------------------------------------

    def get_ltp(
        self,
        exchange_trading_symbols: Tuple[str],
        segment: str,
    ) -> dict:

        return self.api.get_ltp(
            exchange_trading_symbols=exchange_trading_symbols,
            segment=segment,
        )

    # ----------------------------------------------------
    # Historical Candles
    # ----------------------------------------------------

    def get_historical_candles(
        self,
        exchange: str,
        segment: str,
        groww_symbol: str,
        start_time: str,
        end_time: str,
        candle_interval: str,
    ) -> dict:

        return self.api.get_historical_candles(
            exchange=exchange,
            segment=segment,
            groww_symbol=groww_symbol,
            start_time=start_time,
            end_time=end_time,
            candle_interval=candle_interval,
        )

    # ----------------------------------------------------
    # Expiries
    # ----------------------------------------------------

    def get_expiries(
        self,
        exchange: str,
        underlying_symbol: str,
        year: Optional[int] = None,
        month: Optional[int] = None,
    ) -> dict:

        return self.api.get_expiries(
            exchange=exchange,
            underlying_symbol=underlying_symbol,
            year=year,
            month=month,
        )

    # ----------------------------------------------------
    # Greeks
    # ----------------------------------------------------

    def get_greeks(
        self,
        exchange: str,
        underlying: str,
        trading_symbol: str,
        expiry: str,
    ) -> dict:

        return self.api.get_greeks(
            exchange=exchange,
            underlying=underlying,
            trading_symbol=trading_symbol,
            expiry=expiry,
        )
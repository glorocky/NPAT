"""
yahoo_provider.py

Yahoo Finance Market Data Provider for NPAT

Provides:
- Latest Quote
- Historical OHLCV
- Intraday Data
- Health Check

Author : NPAT Project
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import pandas as pd
import yfinance as yf

from .provider_base import MarketDataProvider

logger = logging.getLogger(__name__)


class YahooProvider(MarketDataProvider):
    """
    Yahoo Finance Provider
    """

    SYMBOL_MAP = {
        "NIFTY": "^NSEI",
        "NIFTY50": "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "VIX": "^INDIAVIX",
    }

    def __init__(self):
        logger.info("Yahoo Finance Provider initialized.")

    # ---------------------------------------------------------
    # Internal Helpers
    # ---------------------------------------------------------

    def _map_symbol(self, symbol: str) -> str:
        return self.SYMBOL_MAP.get(symbol.upper(), symbol)

    # ---------------------------------------------------------
    # Quote
    # ---------------------------------------------------------

    def get_quote(self, symbol: str) -> Dict[str, Any]:

        ticker = yf.Ticker(self._map_symbol(symbol))

        info = ticker.fast_info

        return {
            "symbol": symbol.upper(),
            "last_price": info.get("lastPrice"),
            "open": info.get("open"),
            "day_high": info.get("dayHigh"),
            "day_low": info.get("dayLow"),
            "previous_close": info.get("previousClose"),
            "volume": info.get("lastVolume"),
            "currency": info.get("currency"),
        }

    # ---------------------------------------------------------
    # Historical Data
    # ---------------------------------------------------------

    def get_historical_data(
        self,
        symbol: str,
        interval: str = "5m",
        period: str = "5d",
    ) -> pd.DataFrame:

        ticker = yf.Ticker(self._map_symbol(symbol))

        df = ticker.history(
            period=period,
            interval=interval,
            auto_adjust=False,
            prepost=False,
        )

        if df.empty:
            raise RuntimeError(
                f"No historical data available for {symbol}"
            )

        df.reset_index(inplace=True)

        return df

    # ---------------------------------------------------------
    # Option Chain
    # ---------------------------------------------------------

    def get_option_chain(self, symbol: str):

        raise NotImplementedError(
            "Yahoo Provider does not provide NSE Option Chain."
        )

    # ---------------------------------------------------------
    # Expiry
    # ---------------------------------------------------------

    def get_expiries(self, symbol: str) -> List[str]:

        return []

    # ---------------------------------------------------------
    # Health Check
    # ---------------------------------------------------------

    def health_check(self) -> bool:

        try:

            ticker = yf.Ticker("^NSEI")

            data = ticker.history(period="1d")

            return not data.empty

        except Exception as e:

            logger.exception(e)

            return False
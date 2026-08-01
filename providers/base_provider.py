"""
=========================================================
NPAT - Market Data Provider Base
=========================================================

Purpose
-------
Defines the abstract interface that every market data
provider must implement.

Supported Providers
-------------------
- NSE
- Yahoo Finance
- Groww
- Shoonya
- Zerodha
- Angel One
- Future providers

Using a common interface allows the analytics engine,
strategy engine and dashboard to remain completely
provider-independent.

Author : Rocky Chopra
Version: 2.0.0
=========================================================
"""

from __future__ import annotations
import logging
import time

from abc import ABC, abstractmethod
from typing import Any, Callable, List
from services.telemetry import Telemetry
from providers.exceptions import ProviderConnectionError

from core.models import (
    HistoricalCandle,
    OptionData,
    Quote,
    OptionGreeks,
)



class BaseProvider(ABC):
    
    """
        Base class for every market data provider.

        Every provider must implement these methods so the rest
        of NPAT can consume market data without knowing which
        provider is supplying it.
    """
    
    # =====================================================
    # Constructor
    # =====================================================
    
    def __init__(self, provider_name: str):
        """
        Initialize the provider.

        Parameters
        ----------
        provider_name : str
            Human-readable provider name.
        """
        self.provider_name = provider_name
        self.logger = logging.getLogger(f"providers.{provider_name}")
        self.telemetry = Telemetry()
        
    # =====================================================
    # Provider Information
    # =====================================================

    def provider_info(self) -> dict:
        """
        Return basic provider information.
        """
        return {
            "provider": self.provider_name,
            "class": self.__class__.__name__,
        }
    
    # =====================================================
    # Execute Provider Operation
    # =====================================================

    def _execute(
        self,
        operation: str,
        func: Callable[..., Any],
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute a provider SDK operation with logging,
        telemetry and exception handling.
        """

        start_time = time.perf_counter()

        self.logger.debug("%s started", operation)

        try:

            result = func(*args, **kwargs)

            elapsed = time.perf_counter() - start_time

            self.logger.debug(
                "%s completed in %.4f sec", operation, elapsed
            )

            return result

        except Exception as ex:
            

            elapsed = time.perf_counter() - start_time
            

            self.logger.exception(
                "%s failed after %.4f sec",operation, elapsed    
            )

            raise ProviderConnectionError(
                f"{self.provider_name}: {operation} failed."
            ) from ex
    
    # =====================================================
    # Health Check
    # =====================================================

    @abstractmethod
    def health_check(self) -> bool:
        """
        Verify the provider is reachable.

        Returns
        -------
        bool
            True if provider is operational.
        """
        raise NotImplementedError

    # =====================================================
    # Live Quote
    # =====================================================

    @abstractmethod
    def get_quote(self, *args, **kwargs) -> Quote:
        """
        Return the latest quote for a symbol.

        Parameters
        ----------
        symbol : str

        Returns
        -------
        Quote
        """
        raise NotImplementedError
    
        # =====================================================
    # Batch LTP
    # =====================================================

    def get_ltp_batch(
        self,
        symbols: list[str],
        exchange: str = "NSE",
        segment: str = "CASH",
    ) -> dict[str, float]:
        """
        Return latest prices for multiple symbols.

        Providers supporting efficient batch market-data
        retrieval should override this method.
        """

        raise NotImplementedError(
            f"{self.__class__.__name__} does not support "
            "batch LTP retrieval."
        )

    # =====================================================
    # Batch OHLC
    # =====================================================

    def get_ohlc_batch(
        self,
        symbols: list[str],
        exchange: str = "NSE",
        segment: str = "CASH",
    ) -> dict[str, dict[str, float]]:
        """
        Return OHLC data for multiple symbols.

        Providers supporting efficient batch market-data
        retrieval should override this method.
        """

        raise NotImplementedError(
            f"{self.__class__.__name__} does not support "
            "batch OHLC retrieval."
        )

    # =====================================================
    # Historical Data
    # =====================================================

    @abstractmethod
    def get_historical_data(
        self,
        *args,
        **kwargs,
    ) -> List[HistoricalCandle]:
        """
        Return historical OHLCV candles.

        Parameters
        ----------
        symbol : str

        interval : str

        period : str

        Returns
        -------
        List[HistoricalCandle]
        """
        raise NotImplementedError

    # =====================================================
    # Expiry Dates
    # =====================================================

    @abstractmethod
    def get_expiries(
        self,
        *args,
        **kwargs,
    ) -> List[str]:
        """
        Return available option expiries.

        Parameters
        ----------
        symbol : str

        Returns
        -------
        List[str]
        """
        raise NotImplementedError

    # =====================================================
    # Option Chain
    # =====================================================
    @abstractmethod
    def get_option_chain(
        self,
        exchange: str,
        symbol: str,
        expiry: str | None = None,
    ) -> List[OptionData]:
        """
        Return the normalized option chain.

        Parameters
        ----------
        exchange : str
            Exchange code, for example NSE.

        symbol : str
            Underlying symbol, for example NIFTY.

        expiry : str | None
            Expiry date in YYYY-MM-DD format.

        Returns
        -------
        List[OptionData]
        """
        raise NotImplementedError
    # =====================================================
    # Greeks
    # =====================================================

    @abstractmethod
    def get_greeks(
        self,
        exchange: str,
        symbol: str,
        expiry: str,
        strike: int,
        option_type: str,
    ) -> OptionGreeks:
        """
        Return normalized option Greeks.

        Parameters
        ----------
        exchange : str
            Exchange code.

        symbol : str
            Underlying symbol, for example NIFTY.

        expiry : str
            Expiry date in YYYY-MM-DD format.

        strike : int
            Option strike price.

        option_type : str
            CE or PE.

        Returns
        -------
        OptionGreeks
        """
        raise NotImplementedError
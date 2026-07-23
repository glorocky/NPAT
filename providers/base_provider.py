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

from abc import ABC, abstractmethod
from services.telemetry import Telemetry
from typing import List

from core.models import (
    HistoricalCandle,
    MarketSnapshot,
    OptionData,
    Quote,
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
    def get_quote(self, symbol: str) -> Quote:
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
    # Historical Data
    # =====================================================

    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        interval: str = "5m",
        period: str = "5d",
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
        symbol: str,
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
        symbol: str,
        expiry: str | None = None,
    ) -> List[OptionData]:
        """
        Return the complete option chain.

        Parameters
        ----------
        symbol : str

        expiry : str | None

        Returns
        -------
        List[OptionData]
        """
        raise NotImplementedError

    # =====================================================
    # Market Snapshot
    # =====================================================

    @abstractmethod
    def get_market_snapshot(
        self,
        symbol: str,
        expiry: str | None = None,
    ) -> MarketSnapshot:
        """
        Return a fully analysed market snapshot.

        Includes

        • Spot Price

        • ATM Strike

        • PCR

        • Max Pain

        • Support

        • Resistance

        • Complete Option Chain

        Parameters
        ----------
        symbol : str

        expiry : str | None

        Returns
        -------
        MarketSnapshot
        """
        raise NotImplementedError
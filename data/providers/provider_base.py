"""
provider_base.py

Abstract base class for all market data providers used by NPAT.

Every provider (Yahoo, NSE, Groww, Shoonya, etc.) must implement
this interface so that the analytics engine remains provider-independent.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class MarketDataProvider(ABC):
    """Abstract base class for market data providers."""

    @abstractmethod
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Return latest quote for a symbol."""
        pass

    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        interval: str = "5m",
        period: str = "5d",
    ) -> Any:
        """Return historical OHLCV data."""
        pass

    @abstractmethod
    def get_option_chain(self, symbol: str) -> Dict[str, Any]:
        """Return complete option chain."""
        pass

    @abstractmethod
    def get_expiries(self, symbol: str) -> List[str]:
        """Return available expiry dates."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Return True if provider is reachable."""
        pass
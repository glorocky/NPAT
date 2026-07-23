"""
=========================================================
NPAT - NSE API
=========================================================

Purpose
-------
Thin wrapper around the official NSE REST APIs.

Responsibilities
----------------
✔ Fetch available expiry dates
✔ Fetch Option Chain V3
✔ Hide NSE response structure
✔ Return clean normalized payloads
✔ Validate NSE responses

Author  : Rocky Chopra
Version : 2.1.0
=========================================================
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .constants import (
    DEFAULT_EXPIRY_INDEX,
    NSE_CONTRACT_INFO_URL,
    NSE_OPTION_CHAIN_V3_URL,
    SUPPORTED_SYMBOLS,
)
from .session import NSESessionManager

logger = logging.getLogger(__name__)


class NSEApi:
    """
    Thin wrapper around NSE REST APIs.

    This class is responsible only for downloading data
    from NSE and converting the raw NSE response into
    a clean internal format.

    It intentionally does NOT perform any analytics or
    parsing into dataclasses.
    """

    def __init__(self, session: NSESessionManager):
        self.session = session

    # -----------------------------------------------------
    # Symbol Validation
    # -----------------------------------------------------

    @staticmethod
    def _validate_symbol(symbol: str) -> str:
        """
        Validate NSE symbol.
        """

        symbol = symbol.upper()

        if symbol not in SUPPORTED_SYMBOLS:
            raise ValueError(f"Unsupported symbol: {symbol}")

        return symbol

    # -----------------------------------------------------
    # Health Check
    # -----------------------------------------------------

    def health_check(self) -> bool:
        """
        Verify NSE API is reachable.
        """

        try:
            self.get_expiries("NIFTY")
            return True

        except Exception:
            logger.exception("NSE API health check failed")
            return False

    # -----------------------------------------------------
    # Expiry Dates
    # -----------------------------------------------------

    def get_expiries(
        self,
        symbol: str,
    ) -> List[str]:
        """
        Fetch available expiry dates.
        """

        symbol = self._validate_symbol(symbol)

        payload = self.session.get_json(
            NSE_CONTRACT_INFO_URL,
            params={
                "symbol": symbol,
            },
        )

        if not isinstance(payload, dict):
            raise ValueError(
                "Invalid response received from NSE."
            )

        expiries = (
            payload.get("expiryDates")
            or payload.get("value")
            or []
        )

        if not isinstance(expiries, list):
            raise ValueError(
                "Invalid expiry list received from NSE."
            )

        if not expiries:
            raise ValueError(
                f"No expiry dates available for {symbol}."
            )

        return expiries

    # -----------------------------------------------------
    # Option Chain
    # -----------------------------------------------------

    def get_option_chain(
        self,
        symbol: str,
        expiry: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetch Option Chain and return a normalized payload.

        Returns
        -------
        {
            "symbol": str,
            "expiry": str,
            "underlyingValue": float,
            "timestamp": str,
            "expiryDates": list,
            "data": list
        }
        """

        symbol = self._validate_symbol(symbol)

        if expiry is None:
            expiry = self.get_expiries(symbol)[
                DEFAULT_EXPIRY_INDEX
            ]

        payload = self.session.get_json(
            NSE_OPTION_CHAIN_V3_URL,
            params={
                "type": SUPPORTED_SYMBOLS[symbol],
                "symbol": symbol,
                "expiry": expiry,
            },
        )

        if not isinstance(payload, dict):
            raise ValueError(
                "Invalid response received from NSE."
            )

        records = payload.get("records")

        if not isinstance(records, dict):
            raise ValueError(
                "Invalid NSE response: missing or invalid 'records' object."
            )

        data = records.get("data", [])

        if not isinstance(data, list):
            raise ValueError(
                "Invalid NSE response: 'records.data' is not a list."
            )

        expiry_dates = records.get("expiryDates", [])

        if not isinstance(expiry_dates, list):
            expiry_dates = []

        return {
            "symbol": symbol,
            "expiry": expiry,
            "underlyingValue": records.get("underlyingValue"),
            "timestamp": records.get("timestamp"),
            "expiryDates": expiry_dates,
            "data": data,
        }
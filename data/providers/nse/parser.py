"""
=========================================================
NPAT - NSE Option Chain Parser
=========================================================

Purpose
-------
Convert the normalized NSE Option Chain payload returned
by NSEApi into strongly typed OptionData objects.

Responsibilities
----------------
✔ Parse normalized NSE option chain payload
✔ Convert raw dictionaries into OptionData
✔ Safely handle missing CE / PE data
✔ Never expose raw JSON to upper layers
✔ Ensure numeric fields always contain valid values

Author  : Rocky Chopra
Version : 2.0.0
=========================================================
"""

from __future__ import annotations

import logging
from typing import Any

from core.models import OptionData

logger = logging.getLogger(__name__)


class NSEParser:
    """
    Parser for normalized NSE Option Chain payloads.
    """

    # -----------------------------------------------------
    # Safe Converters
    # -----------------------------------------------------

    @staticmethod
    def _to_int(value: Any) -> int:
        """
        Safely convert a value to int.
        """

        if value is None:
            return 0

        try:
            return int(value)

        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _to_float(value: Any) -> float:
        """
        Safely convert a value to float.
        """

        if value is None:
            return 0.0

        try:
            return float(value)

        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _to_str(value: Any) -> str:
        """
        Safely convert a value to string.
        """

        if value is None:
            return ""

        return str(value)

    # -----------------------------------------------------
    # Option Chain Parser
    # -----------------------------------------------------

    @classmethod
    def parse_option_chain(
        cls,
        payload: dict[str, Any],
    ) -> list[OptionData]:
        """
        Parse normalized Option Chain payload.

        Parameters
        ----------
        payload : dict

        Returns
        -------
        list[OptionData]
        """

        if not isinstance(payload, dict):
            raise ValueError(
                "Option chain payload must be a dictionary."
            )

        data = payload.get("data", [])

        if not isinstance(data, list):
            raise ValueError(
                "Option chain 'data' must be a list."
            )

        underlying = cls._to_float(
            payload.get("underlyingValue")
        )

        options: list[OptionData] = []

        for row in data:

            if not isinstance(row, dict):
                logger.warning(
                    "Skipping invalid option chain row."
                )
                continue

            ce = row.get("CE") or {}
            pe = row.get("PE") or {}

            option = OptionData(

                strike_price=cls._to_int(
                    row.get("strikePrice")
                ),

                expiry=cls._to_str(
                    row.get("expiryDates")
                ),

                underlying_price=underlying,

                # -----------------------------------------
                # CALL SIDE
                # -----------------------------------------

                call_oi=cls._to_int(
                    ce.get("openInterest")
                ),

                call_change_oi=cls._to_int(
                    ce.get("changeinOpenInterest")
                ),

                call_volume=cls._to_int(
                    ce.get("totalTradedVolume")
                ),

                call_iv=cls._to_float(
                    ce.get("impliedVolatility")
                ),

                call_ltp=cls._to_float(
                    ce.get("lastPrice")
                ),

                # -----------------------------------------
                # PUT SIDE
                # -----------------------------------------

                put_oi=cls._to_int(
                    pe.get("openInterest")
                ),

                put_change_oi=cls._to_int(
                    pe.get("changeinOpenInterest")
                ),

                put_volume=cls._to_int(
                    pe.get("totalTradedVolume")
                ),

                put_iv=cls._to_float(
                    pe.get("impliedVolatility")
                ),

                put_ltp=cls._to_float(
                    pe.get("lastPrice")
                ),
            )

            options.append(option)

        logger.info(
            "Successfully parsed %d option strikes.",
            len(options),
        )

        return options
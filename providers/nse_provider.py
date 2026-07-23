"""
nse_provider.py

NSE Option Chain Provider

Provides:
- Complete Option Chain
- Expiry Dates
- PCR
- ATM Strike
- Support
- Resistance

Author : NPAT Project
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import requests

from .provider_base import MarketDataProvider

logger = logging.getLogger(__name__)


class NSEProvider(MarketDataProvider):

    BASE_URL = "https://www.nseindia.com"

    API = {
        "NIFTY": "/api/option-chain-indices?symbol=NIFTY",
        "BANKNIFTY": "/api/option-chain-indices?symbol=BANKNIFTY",
    }

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent":
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "application/json,text/html",
                "Referer": "https://www.nseindia.com/",
            }
        )

        # Obtain cookies
        self.session.get(self.BASE_URL, timeout=10)

        logger.info("NSE Provider initialized.")

    # -------------------------------------------------------
    # Required Interface
    # -------------------------------------------------------

    def health_check(self):

        try:

            r = self.session.get(
                self.BASE_URL,
                timeout=5,
            )

            return r.status_code == 200

        except Exception:

            return False

    def get_quote(self, symbol):

        snapshot = self.get_market_snapshot(symbol)

        return {
            "symbol": symbol,
            "spot": snapshot["spot"],
        }

    def get_historical_data(self, *args, **kwargs):

        raise NotImplementedError(
            "Historical data comes from Yahoo Provider."
        )

    def get_option_chain(self, symbol):

        symbol = symbol.upper()

        if symbol not in self.API:

            raise ValueError(f"Unsupported symbol : {symbol}")

        url = self.BASE_URL + self.API[symbol]

        r = self.session.get(url, timeout=10)

        r.raise_for_status()

        data = r.json()

        return data

    def get_expiries(self, symbol):

        data = self.get_option_chain(symbol)

        return data["records"]["expiryDates"]

    # -------------------------------------------------------
    # NPAT Methods
    # -------------------------------------------------------

    def get_market_snapshot(self, symbol="NIFTY"):

        data = self.get_option_chain(symbol)

        records = data["records"]

        spot = records["underlyingValue"]

        expiry = records["expiryDates"][0]

        strikes = records["data"]

        total_call_oi = 0

        total_put_oi = 0

        support = {}

        resistance = {}

        atm = None

        min_diff = float("inf")

        for row in strikes:

            strike = row["strikePrice"]

            diff = abs(strike - spot)

            if diff < min_diff:

                min_diff = diff

                atm = strike

            if "CE" in row:

                oi = row["CE"]["openInterest"]

                total_call_oi += oi

                resistance[strike] = oi

            if "PE" in row:

                oi = row["PE"]["openInterest"]

                total_put_oi += oi

                support[strike] = oi

        pcr = round(
            total_put_oi / total_call_oi,
            2
        ) if total_call_oi else 0

        support_levels = sorted(
            support.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        resistance_levels = sorted(
            resistance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        return {

            "spot": spot,

            "expiry": expiry,

            "atm_strike": atm,

            "pcr": pcr,

            "support": support_levels,

            "resistance": resistance_levels,

            "total_call_oi": total_call_oi,

            "total_put_oi": total_put_oi,

            "option_chain": strikes,
        }
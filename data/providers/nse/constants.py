"""
=========================================================
NPAT - NSE Constants
=========================================================

Purpose
-------
Central constants used by the NSE provider.

This module contains only immutable values used by the
NSE provider architecture. It intentionally contains no
business logic.

Author : Rocky Chopra
Version: 2.0.0
=========================================================
"""

from __future__ import annotations

# =========================================================
# NSE Base URLs
# =========================================================

NSE_BASE_URL = "https://www.nseindia.com"

NSE_OPTION_CHAIN_PAGE = (
    f"{NSE_BASE_URL}/option-chain"
)

NSE_CONTRACT_INFO_URL = (
    f"{NSE_BASE_URL}/api/option-chain-contract-info"
)

NSE_OPTION_CHAIN_V3_URL = (
    f"{NSE_BASE_URL}/api/option-chain-v3"
)

# =========================================================
# Supported Underlyings
# =========================================================

SUPPORTED_SYMBOLS = {
    "NIFTY": "Indices",
    "BANKNIFTY": "Indices",
    "FINNIFTY": "Indices",
    "MIDCPNIFTY": "Indices",
}

# =========================================================
# Strike Intervals
# =========================================================

STRIKE_INTERVAL = {
    "NIFTY": 50,
    "BANKNIFTY": 100,
    "FINNIFTY": 50,
    "MIDCPNIFTY": 25,
}

# =========================================================
# Default Analytics Configuration
# =========================================================

TOP_SUPPORT_LEVELS = 3

TOP_RESISTANCE_LEVELS = 3

DEFAULT_PCR = 0.0

# =========================================================
# NSE Specific Request Headers
# =========================================================

NSE_HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": NSE_OPTION_CHAIN_PAGE,
    "Origin": NSE_BASE_URL,
    "Connection": "keep-alive",
}

# =========================================================
# NSE Session Behaviour
# =========================================================

# Refresh cookies whenever these HTTP status codes are received.
COOKIE_REFRESH_STATUS_CODES = {
    401,
    403,
    429,
}

# Number of retries after refreshing NSE cookies.
COOKIE_REFRESH_RETRIES = 2

# Backoff (seconds) before retrying after HTTP 429.
RATE_LIMIT_BACKOFF = 2

# =========================================================
# Default Expiry Selection
# =========================================================

DEFAULT_EXPIRY_INDEX = 0
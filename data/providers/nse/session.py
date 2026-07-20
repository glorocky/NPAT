"""
=========================================================
NPAT - NSE Session Manager
=========================================================

Purpose
-------
Manages the NSE web session for all API requests.

Responsibilities
----------------
✔ Acquire initial NSE cookies
✔ Refresh expired cookies
✔ Retry failed requests (401/403/429)
✔ Return JSON payloads
✔ Centralize NSE session handling

Author : Rocky Chopra
Version: 1.0.0
=========================================================
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

from data.utils.http_client import HttpClient

from .constants import (
    COOKIE_REFRESH_RETRIES,
    COOKIE_REFRESH_STATUS_CODES,
    NSE_HEADERS,
    NSE_OPTION_CHAIN_PAGE,
    RATE_LIMIT_BACKOFF,
)

logger = logging.getLogger(__name__)


class NSESessionManager:
    """
    Handles NSE session lifecycle.

    This class is responsible only for maintaining a valid
    NSE session. It contains no parsing or analytics logic.
    """

    def __init__(self, http_client: HttpClient) -> None:

        self.http = http_client

        # Add NSE specific headers
        self.http.update_headers(NSE_HEADERS)

        self.refresh()

    # ----------------------------------------------------
    # Session Refresh
    # ----------------------------------------------------

    def refresh(self) -> None:
        """
        Refresh NSE cookies.

        The option-chain webpage issues the cookies required
        by all NSE API endpoints.
        """

        logger.info("Refreshing NSE session...")

        self.http.clear_cookies()

        self.http.get(
            NSE_OPTION_CHAIN_PAGE,
        )

        logger.info("NSE session established.")

    # ----------------------------------------------------
    # GET JSON
    # ----------------------------------------------------

    def get_json(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a GET request and return JSON.

        Automatically refreshes cookies when NSE rejects
        the request.
        """

        retries = COOKIE_REFRESH_RETRIES

        while True:

            try:

                response = self.http.get(
                    url=url,
                    params=params,
                )

                return response.json()

            except Exception as exc:

                status = getattr(
                    getattr(exc, "response", None),
                    "status_code",
                    None,
                )

                if status not in COOKIE_REFRESH_STATUS_CODES:

                    raise

                logger.warning(
                    "NSE session expired (HTTP %s).",
                    status,
                )

                if retries <= 0:

                    raise

                retries -= 1

                if status == 429:

                    logger.warning(
                        "Rate limited by NSE. Waiting %s seconds...",
                        RATE_LIMIT_BACKOFF,
                    )

                    time.sleep(RATE_LIMIT_BACKOFF)

                self.refresh()

    # ----------------------------------------------------
    # Health
    # ----------------------------------------------------

    def is_session_alive(self) -> bool:
        """
        Verify session validity.
        """

        try:

            self.http.get(
                NSE_OPTION_CHAIN_PAGE,
            )

            return True

        except Exception:

            return False
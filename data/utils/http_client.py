"""
=========================================================
NPAT - HTTP Client
=========================================================

Purpose
-------
Central HTTP client used across the project.

Features
--------
✔ Persistent Session
✔ Automatic Retry
✔ Timeout Handling
✔ Logging
✔ Future Cookie Refresh Support
✔ Future Proxy Support

Author:
Rocky Chopra

Version:
1.0.0
=========================================================
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

import requests

from config import (
    HTTP_RETRIES,
    HTTP_RETRY_DELAY,
    HTTP_TIMEOUT,
    USER_AGENT,
)

logger = logging.getLogger(__name__)


class HttpClient:
    """
    Shared HTTP client for all NPAT providers.
    """

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept": "application/json,text/html,*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
            }
        )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = HTTP_TIMEOUT,
    ) -> requests.Response:

        for attempt in range(1, HTTP_RETRIES + 1):

            try:

                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=timeout,
                )

                response.raise_for_status()

                return response

            except requests.RequestException as e:

                logger.warning(
                    f"GET Attempt {attempt}/{HTTP_RETRIES} failed : {e}"
                )

                if attempt == HTTP_RETRIES:

                    logger.error("Maximum retry limit reached.")

                    raise

                time.sleep(HTTP_RETRY_DELAY)

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    def post(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = HTTP_TIMEOUT,
    ) -> requests.Response:

        for attempt in range(1, HTTP_RETRIES + 1):

            try:

                response = self.session.post(
                    url,
                    json=json,
                    data=data,
                    headers=headers,
                    timeout=timeout,
                )

                response.raise_for_status()

                return response

            except requests.RequestException as e:

                logger.warning(
                    f"POST Attempt {attempt}/{HTTP_RETRIES} failed : {e}"
                )

                if attempt == HTTP_RETRIES:

                    logger.error("Maximum retry limit reached.")

                    raise

                time.sleep(HTTP_RETRY_DELAY)

    # --------------------------------------------------------
    # Session Helpers
    # --------------------------------------------------------

    def update_headers(self, headers: Dict[str, str]) -> None:

        self.session.headers.update(headers)

    def clear_cookies(self) -> None:

        self.session.cookies.clear()

    def close(self) -> None:

        self.session.close()
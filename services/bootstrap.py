"""
=========================================================
NPAT Bootstrap
=========================================================

Creates fully initialized services required by the
application.

This module centralizes:

- Groww authentication
- Provider creation
- AI service creation
- Market service creation

=========================================================
"""

from datetime import date

import pyotp

from config import GROWW
from growwapi.groww.client import GrowwAPI

from providers.groww_provider import GrowwProvider

from services.ai_service import AIService
from services.market_service import MarketService


def create_market_service() -> MarketService:
    """
    Create a fully initialized MarketService.
    """

    # -------------------------------------------------
    # Authentication
    # -------------------------------------------------

    totp = pyotp.TOTP(
        GROWW.totp_secret,
    ).now()

    access_token = GrowwAPI.get_access_token(
        api_key=GROWW.api_key,
        totp=totp,
    )

    # -------------------------------------------------
    # Provider
    # -------------------------------------------------

    provider = GrowwProvider(
        access_token=access_token,
    )

    # -------------------------------------------------
    # AI
    # -------------------------------------------------

    ai_service = AIService()

    # -------------------------------------------------
    # Market Service
    # -------------------------------------------------

    return MarketService(
        provider=provider,
        ai_service=ai_service,
    )


def get_default_symbol() -> str:
    """
    Default dashboard symbol.
    """

    return "NIFTY"


def get_default_exchange() -> str:
    """
    Default exchange.
    """

    return "NSE"
"""
=========================================================
NPAT - Provider Exceptions
=========================================================

Custom exceptions for all market data providers.

These exceptions allow the rest of the application to
handle provider failures consistently, regardless of
whether the data comes from Groww, NSE, Yahoo, or any
future provider.

Author : Rocky Chopra
Version: 1.0.0
=========================================================
"""


class ProviderError(Exception):
    """
    Base exception for all provider-related errors.
    """
    pass


class ProviderConnectionError(ProviderError):
    """
    Raised when a provider cannot be reached.
    """
    pass


class ProviderAuthenticationError(ProviderError):
    """
    Raised when authentication with a provider fails.
    """
    pass


class ProviderDataError(ProviderError):
    """
    Raised when a provider returns invalid or incomplete data.
    """
    pass


class ProviderRateLimitError(ProviderError):
    """
    Raised when a provider rate limit is exceeded.
    """
    pass


class ProviderTimeoutError(ProviderError):
    """
    Raised when a provider request times out.
    """
    pass


class ProviderNotSupportedError(ProviderError):
    """
    Raised when a requested feature is not supported by a provider.
    """
    pass
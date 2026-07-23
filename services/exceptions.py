"""
services/exceptions.py

Central exception hierarchy for NPAT.

All infrastructure, provider, analytics, AI and dashboard modules
should derive their exceptions from this file.
"""

from __future__ import annotations

from typing import Optional


class NPATException(Exception):
    """
    Root exception for the entire NPAT platform.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r})"
        )


class ServiceException(NPATException):
    """
    Raised for transport, HTTP, network,
    timeout and upstream provider failures.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[str] = None,
        provider: Optional[str] = None,
    ):
        super().__init__(message)

        self.status_code = status_code
        self.details = details
        self.provider = provider

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"status_code={self.status_code!r}, "
            f"provider={self.provider!r})"
        )


class TimeoutException(ServiceException):
    """
    Raised when an external request exceeds
    the configured timeout.
    """
    pass


class ProviderException(ServiceException):
    """
    Raised when an upstream provider returns
    invalid, incomplete or malformed data.
    """
    pass


class CircuitOpenException(ServiceException):
    """
    Raised when a request is blocked because
    the circuit breaker is open.
    """
    pass


class RateLimitExceededException(ServiceException):
    """
    Raised when a request exceeds the configured
    rate limit.
    """
    pass


class CacheException(NPATException):
    """
    Raised when the cache layer encounters
    storage or retrieval failures.
    """
    pass


class ParseException(NPATException):
    """
    Raised when JSON, HTML, CSV or other
    external payloads cannot be parsed.
    """
    pass


class AnalyticsException(NPATException):
    """
    Raised when an analytics computation
    fails unexpectedly.
    """
    pass


class AIException(NPATException):
    """
    Raised when the AI engine fails during
    reasoning or prediction.
    """
    pass


class DashboardException(NPATException):
    """
    Raised when dashboard rendering or widget
    generation fails.
    """
    pass


class ConfigurationException(NPATException):
    """
    Raised when configuration values are
    missing or invalid.
    """
    pass


class ValidationException(NPATException):
    """
    Raised when domain model validation fails.
    """
    pass
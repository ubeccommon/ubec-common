"""
Module: models/exceptions.py
Service: erdpuls
Purpose: Custom exceptions for this service (see §7 Python Code Standards).
License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""


class UBECBaseError(Exception):
    """Base exception for all UBEC service errors."""


class HubConnectionError(UBECBaseError):
    """Raised when the Hub API (iot.ubec.network) is unreachable or times out."""


class StellarError(UBECBaseError):
    """Raised on Stellar blockchain interaction failures."""


class TokenAccountNotFoundError(StellarError):
    """Raised when a queried Stellar account does not exist."""


class ObservationValidationError(UBECBaseError):
    """Raised when a phenomenological observation fails quality validation."""


class DataSovereigntyError(UBECBaseError):
    """Raised when an operation would violate GDPR or Gaia-X data sovereignty rules."""

"""Domain-specific exceptions for ale_switcher."""

from __future__ import annotations


class AleSwitcherError(Exception):
    """Base exception for all ale_switcher domain errors."""

    pass


class NoAccountsAvailable(AleSwitcherError):
    """No accounts registered or all exhausted."""

    pass


class TokenUnavailable(AleSwitcherError):
    """Could not obtain valid access token."""

    pass


class SessionRegistrationError(AleSwitcherError):
    """Failed to register or track session."""

    pass


class AccountNotFound(AleSwitcherError):
    """Account identifier does not match any registered account."""

    pass


class InvalidCredentials(AleSwitcherError):
    """Credentials JSON is malformed or missing required fields."""

    pass


class UsageFetchError(AleSwitcherError):
    """Failed to retrieve usage data from API."""

    pass


class ProfileFetchError(AleSwitcherError):
    """Failed to retrieve profile data from API."""

    pass

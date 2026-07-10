"""listingsAPI SDK exceptions. Catch specific errors for fine-grained handling."""

from __future__ import annotations

from typing import Any


class ListingsAPIError(Exception):
    """Base exception for all listingsAPI SDK errors."""


class APIError(ListingsAPIError):
    """Raised when the API reports a failure.

    Covers both non-2xx HTTP responses and error payloads the API returns with
    HTTP 200 (the platform reports auth and validation failures in an errors[]
    body; mutations report success=false plus errors[]).

    Attributes:
        status_code: HTTP status code of the response (may be 200 for
            payload-level errors).
        response_body: Raw response text from the API, when available.
        code: The first API error code (e.g. "SY10005"), when the API sent one.
        errors: Parsed API error entries, each normalized to a dict with
            "code", "message", and "context" keys.

    Example:
        try:
            client.locations.list()
        except listingsapi.APIError as e:
            print(e.status_code, e.code)
            for err in e.errors:
                print(err["code"], err["message"])
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
        errors: list[dict[str, Any]] | None = None,
    ):
        self.status_code = status_code
        self.response_body = response_body
        self.errors = errors or []
        self.code = self.errors[0].get("code") if self.errors else None
        detail = "; ".join(
            f"{e['code']}: {e['message']}" if e.get("code") else str(e.get("message", ""))
            for e in self.errors
        )
        if detail:
            full = f"{message} — {detail}"
        elif response_body:
            full = f"{message} — {response_body}"
        else:
            full = message
        super().__init__(full)


class AuthenticationError(APIError):
    """401 — Invalid or missing API key."""


class PermissionDeniedError(APIError):
    """403 — Insufficient permissions for this action."""


class NotFoundError(APIError):
    """404 — Resource not found."""


class ValidationError(APIError):
    """400/422 — Invalid request parameters."""


class RateLimitError(APIError):
    """429 — Too many requests. Check retry_after for backoff.

    Attributes:
        retry_after: Seconds to wait before retrying (from Retry-After header), or None.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
        retry_after: str | None = None,
        errors: list[dict[str, Any]] | None = None,
    ):
        super().__init__(message, status_code=status_code, response_body=response_body, errors=errors)
        self.retry_after = float(retry_after) if retry_after else None


class InternalServerError(APIError):
    """5xx — Server-side error. Safe to retry."""


class APIConnectionError(ListingsAPIError):
    """Network failure — could not reach the API."""


# Backward compat
APIError = APIError

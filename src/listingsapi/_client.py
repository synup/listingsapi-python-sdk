"""Main listingsAPI client."""

from __future__ import annotations

import logging
import os
import re
import time
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from listingsapi._types import APIObject
from listingsapi._utils import encode_location_id
from listingsapi.exceptions import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ValidationError,
)

logger = logging.getLogger("listingsapi")

DEFAULT_BASE_URL = "https://listingsapi.com"
DEFAULT_TIMEOUT = 240.0
DEFAULT_MAX_RETRIES = 2
DEFAULT_BACKOFF_FACTOR = 0.5
_IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
_RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})


class ListingsAPI:
    """Client for the listingsAPI platform.

    Example:
        import listingsapi

        # Reads LISTINGSAPI_KEY from environment
        client = listingsapi.ListingsAPI()

        # Or pass explicitly
        client = listingsapi.ListingsAPI(api_key="your-key")

        # With custom config
        client = listingsapi.ListingsAPI(api_key="...", timeout=60.0, max_retries=3)

        # Use resources
        page = client.locations.list(first=10)
        for location in page:
            print(location.name, location.city)
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        self.api_key = api_key or os.environ.get("LISTINGSAPI_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "No API key provided. Set the LISTINGSAPI_KEY environment variable "
                "or pass api_key= to ListingsAPI().",
                status_code=401,
            )

        self._base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries

        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"API {self.api_key}",
                "Content-Type": "application/json",
            }
        )

        retry = Retry(
            total=max_retries,
            backoff_factor=DEFAULT_BACKOFF_FACTOR,
            status_forcelist=list(_RETRYABLE_STATUSES),
            allowed_methods=_IDEMPOTENT_METHODS,
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

        # Resources — lazy imports to avoid circular deps
        from listingsapi.resources import (
            Analytics,
            ConnectedAccounts,
            Listings,
            Locations,
            Photos,
            Posts,
            Reviews,
            Workflows,
        )

        self.locations = Locations(self)
        self.reviews = Reviews(self)
        self.posts = Posts(self)
        self.listings = Listings(self)
        self.analytics = Analytics(self)
        self.connected_accounts = ConnectedAccounts(self)
        self.photos = Photos(self)
        self.workflows = Workflows(self)

    # --- HTTP methods (used by resources) ---

    def _get(self, path: str, params: dict | None = None) -> dict[str, Any]:
        url = f"{self._base_url}/api/v4/{path}"
        logger.debug("GET %s params=%s", url, params)
        try:
            response = self._session.get(url, params=params or {}, timeout=self._timeout)
        except requests.ConnectionError as e:
            raise APIConnectionError(f"Connection error: {e}") from e
        except requests.Timeout as e:
            raise APIConnectionError(f"Request timed out: {e}") from e
        return self._handle_response(response)

    def _post(
        self,
        path: str,
        json_body: dict[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        url = f"{self._base_url}/api/v4/{path}"
        logger.debug("POST %s", url)
        response = self._send_write("POST", url, json_body, idempotency_key)
        data = self._handle_response(response)
        self._raise_for_mutation_errors(data, response)
        return data

    def _delete(
        self,
        path: str,
        json_body: dict[str, Any] | None = None,
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        url = f"{self._base_url}/api/v4/{path}"
        logger.debug("DELETE %s", url)
        response = self._send_write("DELETE", url, json_body, idempotency_key)
        data = self._handle_response(response)
        self._raise_for_mutation_errors(data, response)
        return data

    def _send_write(
        self,
        method: str,
        url: str,
        json_body: dict[str, Any] | None,
        idempotency_key: str | None,
    ) -> requests.Response:
        """Send a write request, retrying only when it is safe to repeat.

        Writes are not idempotent, so by default they are sent exactly once and
        any 429/5xx is surfaced immediately — a blind retry after a
        completed-but-5xx write could duplicate a create, reply, or post. When
        the caller supplies an idempotency key the request carries an
        ``Idempotency-Key`` header and is retried on 429/5xx up to
        ``max_retries`` times, since the server can then dedupe repeats.
        """
        headers = {"Idempotency-Key": idempotency_key} if idempotency_key else None
        attempts = self._max_retries + 1 if idempotency_key else 1
        for attempt in range(attempts):
            try:
                response = self._session.request(
                    method, url, json=json_body, headers=headers, timeout=self._timeout
                )
            except requests.ConnectionError as e:
                raise APIConnectionError(f"Connection error: {e}") from e
            except requests.Timeout as e:
                raise APIConnectionError(f"Request timed out: {e}") from e
            is_last = attempt + 1 >= attempts
            if is_last or response.status_code not in _RETRYABLE_STATUSES:
                return response
            _sleep_before_retry(attempt, response)
        raise RuntimeError("no write attempt was made")  # pragma: no cover

    def _location_get(
        self, location_id: str | int, path_suffix: str, params: dict | None = None
    ) -> dict[str, Any]:
        encoded_id = encode_location_id(location_id)
        return self._get(f"locations/{encoded_id}/{path_suffix}", params)

    def _handle_response(self, response: requests.Response) -> dict[str, Any]:
        if response.ok:
            data = response.json()
            if isinstance(data, dict):
                errors = _parse_error_entries(data.get("errors"))
                if errors:
                    raise _exception_for_errors(errors, response)
            return data

        status = response.status_code
        body = response.text
        errors = _error_entries_from_response(response)
        msg = f"API request failed: {status}"

        if status == 401:
            raise AuthenticationError(msg, status_code=status, response_body=body, errors=errors)
        elif status == 403:
            raise PermissionDeniedError(msg, status_code=status, response_body=body, errors=errors)
        elif status == 404:
            raise NotFoundError(msg, status_code=status, response_body=body, errors=errors)
        elif status == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                msg, status_code=status, response_body=body, retry_after=retry_after, errors=errors
            )
        elif status in (400, 422):
            raise ValidationError(msg, status_code=status, response_body=body, errors=errors)
        elif status >= 500:
            raise InternalServerError(msg, status_code=status, response_body=body, errors=errors)
        else:
            raise APIError(msg, status_code=status, response_body=body, errors=errors)

    def _raise_for_mutation_errors(self, data: dict[str, Any], response: requests.Response) -> None:
        if not isinstance(data, dict):
            return
        payload = data.get("data")
        if not isinstance(payload, dict):
            return
        for result in payload.values():
            if not isinstance(result, dict):
                continue
            errors = _parse_error_entries(result.get("errors"))
            if errors or result.get("success") is False:
                if not errors:
                    errors = [{"code": None, "message": "The API reported success=false", "context": {}}]
                raise ValidationError(
                    "API request failed",
                    status_code=response.status_code,
                    response_body=response.text,
                    errors=errors,
                )

    # --- Account-level convenience methods ---

    def plan_sites(self) -> list[APIObject]:
        """Get supported directories for your plan."""
        data = self._get("plan-sites")
        items = data.get("data", {}).get("planSites") or []
        return [APIObject(item) for item in items]

    def subcategories(self) -> list[APIObject]:
        """Get business subcategories (use the databaseId as subCategoryId when creating locations)."""
        data = self._get("sub-categories")
        items = data.get("data", {}).get("subcategories") or []
        return [APIObject(item) for item in items]

    def countries(self) -> list[APIObject]:
        """Get supported countries and states (ISO codes)."""
        data = self._get("countries")
        items = data.get("data", {}).get("supportedCountries") or []
        return [APIObject(item) for item in items]

    def subscriptions(self) -> list[APIObject]:
        """Get active subscriptions for the account."""
        data = self._get("subscriptions")
        items = data.get("data", {}).get("activeSubscriptions") or []
        return [APIObject(item) for item in items]


_CODE_PREFIX_RE = re.compile(r"^\s*(SY\d+)\s*:\s*(.*)$", re.DOTALL)


def _split_code_prefix(message: str) -> tuple[str | None, str]:
    """Split a leading ``SYxxxxx:`` error code out of a message.

    The platform embeds error codes as a prefix in the message string
    (``"SY90005: Invalid Token"``) rather than as a separate field. Returns the
    code and the message with the prefix stripped, or ``(None, message)`` when
    the message has no code prefix.
    """
    match = _CODE_PREFIX_RE.match(message)
    if match:
        return match.group(1), match.group(2).strip()
    return None, message


def _parse_error_entries(raw: Any) -> list[dict[str, Any]]:
    if not raw:
        return []
    entries: list[dict[str, Any]] = []
    for item in raw if isinstance(raw, list) else [raw]:
        if isinstance(item, dict):
            message = item.get("message") or str(item)
            code = item.get("code")
            if not code:
                code, message = _split_code_prefix(message)
            entries.append({"code": code, "message": message, "context": item.get("context") or {}})
        else:
            code, message = _split_code_prefix(str(item))
            entries.append({"code": code, "message": message, "context": {}})
    return entries


def _error_entries_from_response(response: requests.Response) -> list[dict[str, Any]]:
    """Best-effort parse of error entries from a non-2xx response body.

    Handles the ``errors[]`` envelope, a bare ``{"message": ..., "code": ...}``
    body (the shape the platform uses for 401s), and plain-text bodies (which
    yield no entries).
    """
    try:
        data = response.json()
    except ValueError:
        return []
    if not isinstance(data, dict):
        return []
    if data.get("errors"):
        return _parse_error_entries(data.get("errors"))
    if data.get("message"):
        return _parse_error_entries([{"code": data.get("code"), "message": data.get("message")}])
    return []


def _sleep_before_retry(attempt: int, response: requests.Response) -> None:
    retry_after = response.headers.get("Retry-After")
    delay = DEFAULT_BACKOFF_FACTOR * (2 ** attempt)
    if retry_after:
        try:
            delay = float(retry_after)
        except ValueError:
            pass
    time.sleep(delay)


_AUTH_CODES = {"SY90005", "SY90001"}
_PERMISSION_CODES = {"SY90003"}


def _exception_for_errors(errors: list[dict[str, Any]], response: requests.Response) -> APIError:
    codes = {e["code"] for e in errors if e.get("code")}
    kwargs: dict[str, Any] = {
        "status_code": response.status_code,
        "response_body": response.text,
        "errors": errors,
    }
    if codes & _AUTH_CODES:
        return AuthenticationError("Authentication failed", **kwargs)
    if codes & _PERMISSION_CODES:
        return PermissionDeniedError("Permission denied", **kwargs)
    if codes == {"RATE_LIMITED"}:
        return RateLimitError("Rate limit exceeded", **kwargs)
    return APIError("API request failed", **kwargs)

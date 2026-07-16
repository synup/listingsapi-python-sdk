"""Base class for API resources."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from listingsapi._client import ListingsAPI


class APIResource:
    """Base class that all resources inherit from. Provides access to the client's HTTP methods."""

    def __init__(self, client: ListingsAPI) -> None:
        self._client = client

    def _get(self, path: str, params: dict | None = None) -> dict[str, Any]:
        return self._client._get(path, params)

    def _post(
        self, path: str, json_body: dict[str, Any], *, idempotency_key: str | None = None
    ) -> dict[str, Any]:
        return self._client._post(path, json_body, idempotency_key=idempotency_key)

    def _delete(
        self, path: str, json_body: dict[str, Any] | None = None, *, idempotency_key: str | None = None
    ) -> dict[str, Any]:
        return self._client._delete(path, json_body, idempotency_key=idempotency_key)

    def _location_get(
        self, location_id: str | int, path_suffix: str, params: dict | None = None
    ) -> dict[str, Any]:
        return self._client._location_get(location_id, path_suffix, params)

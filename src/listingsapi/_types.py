"""Response types for the listingsAPI SDK."""

from __future__ import annotations

from typing import Any, Callable, Generator


class APIObject:
    """API response object with attribute access. Works like a dict but with dot notation.

    Example:
        location = client.locations.retrieve(16808)
        print(location.name)        # "StarBucks New York"
        print(location.city)        # "New York"
        print(location["stateIso"]) # "NY"  (dict-style also works)
        print(location.to_dict())   # raw dict
    """

    def __init__(self, data: dict[str, Any] | None = None):
        object.__setattr__(self, "_data", data or {})

    def __getattr__(self, name: str) -> Any:
        try:
            value = self._data[name]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")
        if isinstance(value, dict):
            return APIObject(value)
        if isinstance(value, list):
            return [APIObject(v) if isinstance(v, dict) else v for v in value]
        return value

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def __repr__(self) -> str:
        return repr(self._data)

    def __str__(self) -> str:
        return str(self._data)

    def __bool__(self) -> bool:
        return bool(self._data)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        """Return the raw dict."""
        return self._data


class SyncPage:
    """A page of results with built-in pagination.

    Example:
        page = client.locations.list(first=10)
        for location in page:
            print(location.name)

        # Auto-paginate through all results
        for location in page.auto_paging_iter():
            print(location.name)

        # Manual pagination
        if page.has_more:
            next_page = page.next_page()
    """

    def __init__(
        self,
        data: list[dict[str, Any]],
        has_more: bool = False,
        end_cursor: str | None = None,
        total: int | None = None,
        _fetch_next: Callable[..., "SyncPage"] | None = None,
    ):
        self.data: list[APIObject] = [
            APIObject(item) if isinstance(item, dict) else item for item in data
        ]
        self.has_more = has_more
        self.total = total
        self._end_cursor = end_cursor
        self._fetch_next = _fetch_next

    def __iter__(self):
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __bool__(self) -> bool:
        return bool(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __repr__(self) -> str:
        return f"SyncPage(items={len(self.data)}, has_more={self.has_more})"

    def next_page(self) -> SyncPage | None:
        """Fetch the next page of results, or None if no more pages."""
        if not self.has_more or not self._fetch_next:
            return None
        return self._fetch_next(self._end_cursor)

    def auto_paging_iter(self) -> Generator[APIObject, None, None]:
        """Iterate through all pages automatically.

        Example:
            for location in client.locations.list(first=10).auto_paging_iter():
                print(location.name)
        """
        page: SyncPage | None = self
        while page is not None:
            yield from page.data
            if not page.has_more:
                break
            page = page.next_page()

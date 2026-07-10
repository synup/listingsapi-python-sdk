"""Tags resource — client.tags.*"""

from __future__ import annotations

from listingsapi._types import APIObject
from listingsapi._utils import encode_location_id
from listingsapi.resources._base import APIResource


class Tags(APIResource):
    """Manage location tags.

    Example:
        tags = client.tags.list()
        client.tags.add(16808, "vip")
    """

    def list(self) -> list[APIObject]:
        """Get all tags in the account."""
        data = self._get("tags")
        items = data.get("data", {}).get("listAllTags") or []
        return [APIObject(item) for item in items]

    def add(self, location_id: str | int, tag: str) -> APIObject:
        """Add a tag to a location (tag is created if it doesn't exist)."""
        data = self._post(
            "locations/tags",
            {"input": {"locationId": encode_location_id(location_id), "tag": tag}},
        )
        return APIObject(data.get("data", {}).get("addTag") or {})

    def remove(self, location_id: str | int, tag: str) -> APIObject:
        """Remove a tag from a location."""
        data = self._post(
            "locations/tags/remove",
            {"input": {"locationId": encode_location_id(location_id), "tag": tag}},
        )
        return APIObject(data.get("data", {}).get("removeTag") or {})

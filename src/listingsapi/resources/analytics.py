"""Analytics resource — client.analytics.*"""

from __future__ import annotations

from typing import Any

from listingsapi._types import APIObject
from listingsapi.resources._base import APIResource


class Analytics(APIResource):
    """Profile and ranking analytics.

    Example:
        google = client.analytics.google(16808, from_date="2024-01-01")
        bing = client.analytics.bing(16808)
    """

    def google(
        self, location_id: str | int, *, from_date: str | None = None, to_date: str | None = None
    ) -> APIObject:
        """Get Google (GMB) profile analytics for a location."""
        params: dict[str, str] = {}
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date
        data = self._location_get(location_id, "google-analytics", params)
        return APIObject(data.get("data", {}).get("googleInsights") or {})

    def bing(
        self, location_id: str | int, *, from_date: str | None = None, to_date: str | None = None
    ) -> APIObject:
        """Get Bing profile analytics for a location."""
        params: dict[str, str] = {}
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date
        data = self._location_get(location_id, "bing-analytics", params)
        return APIObject(data.get("data", {}).get("bingInsights") or {})

    def facebook(
        self, location_id: str | int, *, from_date: str | None = None, to_date: str | None = None
    ) -> APIObject:
        """Get Facebook page analytics for a location."""
        params: dict[str, str] = {}
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date
        data = self._location_get(location_id, "facebook-analytics", params)
        return APIObject(data.get("data", {}).get("facebookInsights") or {})


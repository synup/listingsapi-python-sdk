"""Automations resource — client.automations.*"""

from __future__ import annotations

from listingsapi._types import APIObject
from listingsapi._utils import encode_location_id
from listingsapi.resources._base import APIResource


class Automations(APIResource):
    """Location automations (temporary close, etc.).

    Example:
        result = client.automations.temporary_close(
            name="Holiday", start_date="2025-12-24", start_time="18:00:00",
            end_date="2025-12-26", location_id=16808,
        )
    """

    def temporary_close(
        self,
        name: str,
        start_date: str,
        start_time: str,
        end_date: str,
        location_id: str | int,
    ) -> APIObject:
        """Temporarily close a location with a reopening date (Google/Facebook)."""
        data = self._post(
            "automations/temporary-close-location-with-reopening-date",
            {
                "input": {
                    "name": name,
                    "startDate": start_date,
                    "startTime": start_time,
                    "endDate": end_date,
                    "locationId": encode_location_id(location_id),
                }
            },
        )
        return APIObject(data.get("data", {}).get("createFlowFromRecipe") or {})

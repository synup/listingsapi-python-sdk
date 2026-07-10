"""Grid reports resource — client.grid_reports.*"""

from __future__ import annotations

from typing import Any

from listingsapi._types import APIObject
from listingsapi._utils import encode_location_id
from listingsapi.resources._base import APIResource


class GridReports(APIResource):
    """Local Rank Grid reports.

    Example:
        result = client.grid_reports.create(16808, keywords=["italian restaurant"], ...)
        report = client.grid_reports.retrieve("report-uuid")
    """

    def create(
        self,
        location_id: str | int,
        keywords: list[str],
        business_name: str,
        business_street: str,
        business_city: str,
        business_state: str,
        business_country: str,
        latitude: float,
        longitude: float,
        distance: int,
        distance_unit: str,
        grid_size: int,
    ) -> APIObject:
        """Create a Local Rank Grid report. Max 25 keywords; grid_size 3, 5, or 7."""
        data = self._post(
            "create-grid-report",
            {
                "locationId": encode_location_id(location_id),
                "keywords": keywords,
                "businessName": business_name,
                "businessStreet": business_street,
                "businessCity": business_city,
                "businessState": business_state,
                "businessCountry": business_country,
                "latitude": latitude,
                "longitude": longitude,
                "distance": distance,
                "distanceUnit": distance_unit,
                "gridSize": grid_size,
            },
        )
        return APIObject(data.get("data", {}).get("createGridrankReport") or {})

    def retrieve(self, report_id: str) -> APIObject:
        """Get a grid report by ID."""
        data = self._get(f"grid-report/{report_id}")
        return APIObject(data.get("data", {}).get("gridrankReportById") or {})

    def list(
        self,
        location_id: str | int,
        *,
        search_string: str | None = None,
        grid_size: int | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        sort_field: str | None = None,
        sort_order: str | None = None,
        page_size: int | None = None,
        page: int | None = None,
    ) -> APIObject:
        """Get all grid reports for a location."""
        params: dict[str, Any] = {}
        if search_string is not None:
            params["searchString"] = search_string
        if grid_size is not None:
            params["gridSize"] = grid_size
        if from_date is not None:
            params["fromDate"] = from_date
        if to_date is not None:
            params["toDate"] = to_date
        if sort_field is not None:
            params["sortField"] = sort_field
        if sort_order is not None:
            params["sortOrder"] = sort_order
        if page_size is not None:
            params["pageSize"] = page_size
        if page is not None:
            params["page"] = page
        data = self._location_get(location_id, "grid-reports", params)
        result = data.get("data", {}).get("allGridrankReports") or {}
        return APIObject({"reports": result.get("reports") or [], "total": result.get("total")})

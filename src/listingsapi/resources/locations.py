"""Locations resource — client.locations.*"""

from __future__ import annotations

import json
from typing import Any

from listingsapi._types import APIObject, SyncPage
from listingsapi._utils import encode_location_id
from listingsapi.resources._base import APIResource


class Locations(APIResource):
    """Manage locations.

    Example:
        # List locations
        page = client.locations.list(first=10)
        for loc in page:
            print(loc.name, loc.city)

        # Auto-paginate
        for loc in client.locations.list(first=50).auto_paging_iter():
            print(loc.name)

        # Create
        result = client.locations.create({"name": "Acme", "street": "123 Main St", ...})
    """

    def list(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        before: str | None = None,
        last: int | None = None,
    ) -> SyncPage:
        """List locations with cursor-based pagination.

        Returns:
            SyncPage of location objects. Use .auto_paging_iter() to iterate all.
        """
        params: dict[str, Any] = {}
        if first is not None:
            params["first"] = first
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before
        if last is not None:
            params["last"] = last

        data = self._get("locations", params)
        all_locs = data.get("data", {}).get("allLocations") or {}
        edges = all_locs.get("edges") or []
        page_info = all_locs.get("pageInfo") or {}
        items = [edge["node"] for edge in edges]
        end_cursor = edges[-1]["cursor"] if edges else None

        return SyncPage(
            data=items,
            has_more=page_info.get("hasNextPage", False),
            end_cursor=end_cursor,
            total=page_info.get("total"),
            _fetch_next=lambda cursor: self.list(first=first, after=cursor),
        )

    def retrieve(self, location_id: str | int) -> APIObject:
        """Get a single location by ID.

        Args:
            location_id: Numeric (e.g. 16808) or base64-encoded ID.
        """
        results = self.list_by_ids([location_id])
        if not results:
            from listingsapi.exceptions import NotFoundError

            raise NotFoundError(f"Location {location_id} not found", status_code=404)
        return results[0]

    def list_by_ids(self, location_ids: list[str | int]) -> list[APIObject]:
        """Get locations by a list of IDs (numeric or base64)."""
        if not location_ids:
            return []
        encoded = [encode_location_id(lid) for lid in location_ids]
        data = self._get("locations-by-ids", {"ids": json.dumps(encoded)})
        items = data.get("data", {}).get("getLocationsByIds") or []
        return [APIObject(item) for item in items]

    def list_by_store_codes(self, store_codes: list[str]) -> list[APIObject]:
        """Get locations matching the given store codes."""
        if not store_codes:
            return []
        data = self._get("locations-by-store-codes", {"storeCodes": json.dumps(store_codes)})
        items = data.get("data", {}).get("getLocationsByStoreCodes") or []
        return [APIObject(item) for item in items]

    def search(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        first: int | None = None,
        after: str | None = None,
        before: str | None = None,
        last: int | None = None,
    ) -> SyncPage:
        """Search locations by keyword (name, address, or store ID).

        Args:
            query: Search term.
            fields: Restrict search to specific fields (e.g. ["name"], ["store_id"]).
        """
        params: dict[str, Any] = {"query": query}
        if fields is not None:
            params["fields"] = json.dumps(fields)
        if first is not None:
            params["first"] = first
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before
        if last is not None:
            params["last"] = last

        data = self._get("locations/search", params)
        result = data.get("data", {}).get("searchLocations") or {}
        edges = result.get("edges") or []
        page_info = result.get("pageInfo") or {}
        items = [e["node"] for e in edges]
        end_cursor = edges[-1]["cursor"] if edges else None

        return SyncPage(
            data=items,
            has_more=page_info.get("hasNextPage", False),
            end_cursor=end_cursor,
            total=page_info.get("total"),
            _fetch_next=lambda cursor: self.search(query, fields=fields, first=first, after=cursor),
        )



    def create(self, input: dict[str, Any]) -> APIObject:
        """Create a new location from a raw input dict. Pass camelCase field names.

        Required by the API: name, description (min 200 characters), subCategoryId,
        countryIso, and city (for countries with city-level addressing). Prefer
        locations.add() for keyword arguments and client-side validation.

        Args:
            input: Location data dict with camelCase keys.
        """
        data = self._post("locations", {"input": input})
        return APIObject(data.get("data", {}).get("createLocation") or {})

    def add(
        self,
        *,
        name: str,
        description: str,
        sub_category_id: int,
        country_iso: str,
        city: str | None = None,
        street: str | None = None,
        state_iso: str | None = None,
        postal_code: str | None = None,
        phone: str | None = None,
        website: str | None = None,
        store_id: str | None = None,
        hide_address: bool | None = None,
        business_hours: list[dict[str, Any]] | None = None,
        folder_ids: list[str] | None = None,
        service_area: dict[str, Any] | None = None,
        place_action_links: list[dict[str, Any]] | None = None,
        enabled_site_ids: list[int] | None = None,
        additional_fields: dict[str, Any] | None = None,
    ) -> APIObject:
        """Create a location in one call with every mandatory field as a keyword argument.

        Validates the API's create requirements client-side and raises ValidationError
        before any network call, so a bad payload fails fast with a clear message.

        Args:
            name: Business name, 2-150 characters.
            description: Business description, minimum 200 characters. Publishers use
                it as the primary listing copy.
            sub_category_id: Primary subcategory ID (see the subcategories endpoint
                for valid IDs).
            country_iso: Two-letter country ISO code (must be a supported country).
            city: City. Required for countries with city-level addressing; may be
                omitted only for service-area businesses with hide_address=True.
            street: Street address.
            state_iso: State/region ISO code.
            postal_code: Postal or ZIP code.
            phone: Primary phone number, validated for the country.
            website: Business website URL.
            store_id: Your unique store code; must be unique across the account.
            hide_address: Hide the street address (service-area businesses).
            business_hours: Weekly hours, e.g. [{"day": "MONDAY", "slots": [...]}].
            folder_ids: Folder IDs to place the location in.
            service_area: Service-area config: {businessType, regionCode, placeInfos}.
            place_action_links: Google action links, e.g.
                [{"placeActionType": "APPOINTMENT", "uri": "https://...", "isPreferred": True}].
            enabled_site_ids: Site IDs to publish this location to, when you want a
                subset of your plan's sites (see the plan-sites endpoint for IDs).
            additional_fields: Extra camelCase fields merged into the payload as-is.

        Returns:
            The createLocation payload; .location holds the new location and .success
            is True on success.

        Example:
            result = client.locations.add(
                name="Acme Dental",
                description="Acme Dental is a family-owned dental practice...",  # 200+ chars
                sub_category_id=1432,
                country_iso="US",
                city="New York",
                street="123 Jump Street",
                postal_code="10013",
                phone="6443859313",
            )
            print(result.location.id)
        """
        problems: list[str] = []
        if not name or not (2 <= len(name.strip()) <= 150):
            problems.append("name must be 2-150 characters")
        if not description or len(description.strip()) < 200:
            got = len(description.strip()) if description else 0
            problems.append(f"description must be at least 200 characters (got {got})")
        if not sub_category_id:
            problems.append("sub_category_id is required")
        if not country_iso or not str(country_iso).strip():
            problems.append("country_iso is required")
        if not (city and city.strip()) and hide_address is not True:
            problems.append(
                "city is required for countries with city-level addressing "
                "(omit only for service-area businesses with hide_address=True)"
            )
        if problems:
            from listingsapi.exceptions import ValidationError

            raise ValidationError("Invalid location: " + "; ".join(problems))

        input: dict[str, Any] = {
            "name": name.strip(),
            "description": description.strip(),
            "subCategoryId": sub_category_id,
            "countryIso": country_iso,
        }
        optional = {
            "city": city,
            "street": street,
            "stateIso": state_iso,
            "postalCode": postal_code,
            "phone": phone,
            "website": website,
            "storeId": store_id,
            "hideAddress": hide_address,
            "businessHours": business_hours,
            "folderIds": folder_ids,
            "serviceArea": service_area,
            "placeActionLinks": place_action_links,
            "enabledSiteIds": enabled_site_ids,
        }
        input.update({k: v for k, v in optional.items() if v is not None})
        if additional_fields:
            input.update(additional_fields)

        return self.create(input)

    def update(self, input: dict[str, Any]) -> APIObject:
        """Update a location. Pass id plus fields to change."""
        if "id" in input:
            input = {**input, "id": encode_location_id(input["id"])}
        data = self._post("locations/update", {"input": input})
        return APIObject(data.get("data", {}).get("updateLocation") or {})

    def archive(self, location_ids: list[str | int]) -> APIObject:
        """Archive one or more locations."""
        encoded = [encode_location_id(lid) for lid in location_ids]
        data = self._post("locations/archive", {"input": {"locationIds": encoded}})
        return APIObject(data.get("data", {}).get("archiveLocations") or {})


    def cancel_archive(
        self, location_ids: list[str | int], selection_type: str, changed_by: str
    ) -> APIObject:
        """Cancel a scheduled archival."""
        encoded = [encode_location_id(lid) for lid in location_ids]
        data = self._post(
            "locations/cancel_archive",
            {"input": {"locationIds": encoded, "selectionType": selection_type, "changedBy": changed_by}},
        )
        return APIObject(data.get("data", {}).get("cancelLocationsArchive") or {})


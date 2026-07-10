"""Listings resource — client.listings.*"""

from __future__ import annotations

from typing import Any

from listingsapi._types import APIObject
from listingsapi._utils import encode_location_id
from listingsapi.resources._base import APIResource


class Listings(APIResource):
    """Manage directory listings for locations.

    Example:
        listings = client.listings.premium(16808)
        for listing in listings:
            print(listing.site, listing.syncStatus)
    """

    def premium(self, location_id: str | int) -> list[APIObject]:
        """Get premium directory listings (Google, Yelp, etc.)."""
        data = self._location_get(location_id, "listings/premium")
        items = data.get("data", {}).get("listingsForLocation") or []
        return [APIObject(item) for item in items]

    def voice(self, location_id: str | int) -> list[APIObject]:
        """Get voice assistant listings (Google, Alexa, Siri)."""
        data = self._location_get(location_id, "voice-assistants")
        items = data.get("data", {}).get("voiceAssistantsForLocation") or []
        return [APIObject(item) for item in items]


    def duplicates(self, location_id: str | int) -> list[APIObject]:
        """Get duplicate listings for a location."""
        data = self._location_get(location_id, "listings/duplicates")
        items = data.get("data", {}).get("duplicateListingsForLocation") or []
        return [APIObject(item) for item in items]

    def all_duplicates(self, *, tag: str | None = None, page: int | None = None) -> APIObject:
        """Get duplicate listings across all locations."""
        params: dict[str, Any] = {}
        if tag is not None:
            params["tag"] = tag
        if page is not None:
            params["page"] = page
        data = self._get("locations/listings/duplicates", params)
        return APIObject(data.get("data", {}).get("duplicateListingsRollup") or {})

    def mark_duplicate(self, location_id: str | int, listing_item_ids: list[str]) -> APIObject:
        """Mark listing items as duplicates."""
        data = self._post(
            "locations/listings/mark-as-duplicate",
            {"input": {"locationId": encode_location_id(location_id), "listingItemIds": listing_item_ids}},
        )
        return APIObject(data.get("data", {}).get("markAsDuplicate") or {})

    def mark_not_duplicate(self, location_id: str | int, listing_item_ids: list[str]) -> APIObject:
        """Clear duplicate status for listing items."""
        data = self._post(
            "locations/listings/mark-as-not-duplicate",
            {"input": {"locationId": encode_location_id(location_id), "listingItemIds": listing_item_ids}},
        )
        return APIObject(data.get("data", {}).get("markAsNotDuplicate") or {})

    def connect(
        self, location_id: str | int, connected_account_listing_id: str, connected_account_id: str
    ) -> APIObject:
        """Link a location to a listing from a connected account."""
        data = self._post(
            "connected-accounts/connect-listing",
            {
                "input": {
                    "locationId": encode_location_id(location_id),
                    "connectedAccountListingId": connected_account_listing_id,
                    "connectedAccountId": connected_account_id,
                }
            },
        )
        return APIObject(data.get("data", {}).get("connectListing") or {})

    def disconnect(self, location_id: str | int, site: str) -> APIObject:
        """Disconnect a location from its Google or Facebook listing."""
        data = self._post(
            "connected-accounts/disconnect-listing",
            {"input": {"locationId": encode_location_id(location_id), "site": site.upper()}},
        )
        return APIObject(data.get("data", {}).get("disconnectConnectedAccountsLocations") or {})

    def create_gmb(
        self, location_id: str | int, connected_account_id: str, *, folder_id: str | None = None
    ) -> APIObject:
        """Create a Google Business Profile listing for an existing location."""
        payload: dict[str, Any] = {
            "locationId": encode_location_id(location_id),
            "connectedAccountId": connected_account_id,
        }
        if folder_id is not None:
            payload["folderId"] = folder_id
        data = self._post("locations/create/gmb-listing", {"input": payload})
        return APIObject(data.get("data", {}).get("createGmbListingForLocation") or {})

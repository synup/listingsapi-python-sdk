"""Campaigns resource — client.campaigns.*"""

from __future__ import annotations

from typing import Any

from listingsapi._types import APIObject
from listingsapi._utils import encode_location_id
from listingsapi.resources._base import APIResource


class Campaigns(APIResource):
    """Manage review campaigns.

    Example:
        campaigns = client.campaigns.list(16808)
        result = client.campaigns.create(16808, name="Holiday Feedback", customers=[...])
    """

    def list(
        self, location_id: str | int, *, start_date: str | None = None, end_date: str | None = None
    ) -> list[APIObject]:
        """Get review campaigns for a location."""
        params: dict[str, str] = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        data = self._location_get(location_id, "review-campaigns", params)
        result = data.get("data", {}).get("listReviewCampaigns") or {}
        items = result.get("reviewCampaigns") or []
        return [APIObject(item) for item in items]

    def create(
        self,
        location_id: str | int,
        name: str,
        customers: list[dict[str, Any]],
        *,
        screening: bool | None = None,
        landing_page_template: dict[str, Any] | None = None,
        opening_email_template: dict[str, Any] | None = None,
        sms_template: dict[str, Any] | None = None,
        email_details: dict[str, Any] | None = None,
        sms_details: dict[str, Any] | None = None,
    ) -> APIObject:
        """Create a review campaign for a location."""
        payload: dict[str, Any] = {
            "locationId": encode_location_id(location_id),
            "name": name,
            "locationCustomers": customers,
        }
        if screening is not None:
            payload["screening"] = screening
        if landing_page_template is not None:
            payload["landingPageTemplate"] = landing_page_template
        if opening_email_template is not None:
            payload["openingEmailTemplate"] = opening_email_template
        if sms_template is not None:
            payload["smsTemplate"] = sms_template
        if email_details is not None:
            payload["emailDetails"] = email_details
        if sms_details is not None:
            payload["smsDetails"] = sms_details
        data = self._post("locations/review-campaigns", {"input": payload})
        return APIObject(data.get("data", {}).get("createReviewCampaign") or {})

    def customers(self, campaign_id: str) -> APIObject:
        """Get customer details for a review campaign."""
        data = self._get(f"locations/review-campaigns/{campaign_id}/customers")
        return APIObject(data.get("data", {}).get("reviewCampaignInfo") or {})

    def add_customers(self, campaign_id: str, customers: list[dict[str, Any]]) -> APIObject:
        """Add customers to an existing campaign."""
        data = self._post(
            "locations/review-campaigns/customers",
            {"input": {"reviewCampaignId": campaign_id, "locationCustomers": customers}},
        )
        return APIObject(data.get("data", {}).get("addCustomersToReviewCampaign") or {})

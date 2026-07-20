"""Reviews resource — client.reviews.*"""

from __future__ import annotations

import builtins
import json
from typing import Any

from listingsapi._types import APIObject, SyncPage
from listingsapi._utils import encode_location_id
from listingsapi.resources._base import APIResource


class ReviewAnalytics:
    """Review analytics sub-resource — client.reviews.analytics.*"""

    def __init__(self, resource: Reviews) -> None:
        self._resource = resource

    def _location_get(self, location_id, path, params=None):
        return self._resource._location_get(location_id, path, params)

    def overview(
        self, location_id: str | int, *, start_date: str | None = None, end_date: str | None = None
    ) -> APIObject:
        """Get overall review analytics (totals, rating, response rate)."""
        params: dict[str, str] = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        data = self._location_get(location_id, "review-analytics-overview", params)
        return APIObject(data.get("data", {}).get("interactionsAnalyticsStats") or {})

    def timeline(
        self, location_id: str | int, *, start_date: str | None = None, end_date: str | None = None
    ) -> APIObject:
        """Get review analytics over time."""
        params: dict[str, str] = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        data = self._location_get(location_id, "review-analytics-timeline", params)
        return APIObject(data.get("data", {}).get("interactionsChartData") or {})

    def sites_stats(
        self, location_id: str | int, *, start_date: str | None = None, end_date: str | None = None
    ) -> APIObject:
        """Get review analytics broken down by site."""
        params: dict[str, str] = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        data = self._location_get(location_id, "review-analytics-sites-stats", params)
        return APIObject(data.get("data", {}).get("interactionsSitesStats") or {})


class Reviews(APIResource):
    """Manage reviews and interactions.

    Example:
        page = client.reviews.list(16808, first=10)
        for review in page:
            print(review.content, review.rating)

        client.reviews.respond(interaction_id="...", content="Thank you!")
    """

    def __init__(self, client) -> None:
        super().__init__(client)
        self.analytics = ReviewAnalytics(self)

    def list(
        self,
        location_id: str | int,
        *,
        first: int | None = None,
        after: str | None = None,
        before: str | None = None,
        last: int | None = None,
        site_urls: builtins.list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        category: str | None = None,
        rating_filters: builtins.list[int] | None = None,
    ) -> SyncPage:
        """List reviews for a location with optional filters."""
        params: dict[str, Any] = {}
        if first is not None:
            params["first"] = first
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before
        if last is not None:
            params["last"] = last
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if category:
            params["category"] = category
        if site_urls:
            params["siteUrls"] = json.dumps(site_urls)
        if rating_filters:
            params["ratingFilters"] = json.dumps(rating_filters)

        data = self._location_get(location_id, "reviews", params)
        result = data.get("data", {}).get("interactions") or {}
        edges = result.get("edges") or []
        page_info = result.get("pageInfo") or {}
        items = [edge["node"] for edge in edges]
        end_cursor = edges[-1]["cursor"] if edges else None

        return SyncPage(
            data=items,
            has_more=page_info.get("hasNextPage", False),
            end_cursor=end_cursor,
            _fetch_next=lambda cursor: self.list(
                location_id,
                first=first,
                after=cursor,
                site_urls=site_urls,
                start_date=start_date,
                end_date=end_date,
                category=category,
                rating_filters=rating_filters,
            ),
        )

    def respond(self, interaction_id: str, content: str) -> APIObject:
        """Post a reply to a review."""
        data = self._post(
            "locations/reviews/respond",
            {"interactionId": interaction_id, "responseContent": content},
        )
        return APIObject(data.get("data", {}).get("respondToInteraction") or {})

    def edit_response(self, review_id: str, response_id: str, content: str) -> APIObject:
        """Edit an existing reply."""
        data = self._post(
            "locations/reviews/respond/edit",
            {"reviewId": review_id, "responseId": response_id, "responseContent": content},
        )
        return APIObject(data.get("data", {}).get("editResponse") or {})

    def archive_response(self, response_id: str) -> APIObject:
        """Archive (hide) a reply."""
        data = self._post("locations/reviews/respond/archive", {"responseId": response_id})
        return APIObject(data.get("data", {}).get("archiveResponse") or {})

    def settings(self, location_id: str | int) -> APIObject:
        """Get review source settings for a location."""
        data = self._location_get(location_id, "reviews/settings")
        return APIObject(data.get("data", {}).get("interactionsSetting") or {})

    def edit_settings(self, location_id: str | int, site_urls: builtins.list[dict[str, Any]]) -> APIObject:
        """Update review source URLs for a location."""
        data = self._post(
            "locations/reviews/settings/edit",
            {"locationId": encode_location_id(location_id), "siteUrls": site_urls},
        )
        return APIObject(data.get("data", {}).get("editInteractionsSetting") or {})

    def details(self, interaction_ids: builtins.list[str]) -> APIObject:
        """Get detailed info for specific reviews by ID."""
        if not interaction_ids:
            return APIObject({})
        data = self._get("reviewDetails", {"interactionIds": json.dumps(interaction_ids)})
        return APIObject(data.get("data", {}).get("interactionDetails") or {})

    def phrases(
        self,
        location_ids: builtins.list[str],
        *,
        site_urls: builtins.list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> builtins.list[APIObject]:
        """Get commonly mentioned phrases from reviews."""
        if not location_ids:
            return []
        params: dict[str, str] = {"locationIds": json.dumps(location_ids)}
        if site_urls:
            params["siteUrls"] = json.dumps(site_urls)
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        data = self._get("review-phrases", params)
        items = data.get("data", {}).get("newReviewPhrases") or []
        return [APIObject(item) for item in items]

    def site_config(self) -> builtins.list[APIObject]:
        """Get eligible review sites for the account."""
        data = self._get("reviews/site-config")
        items = data.get("data", {}).get("interactionSiteConfig") or []
        return [APIObject(item) for item in items]

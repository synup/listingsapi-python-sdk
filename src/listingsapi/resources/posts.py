"""Posts resource — client.posts.*"""

from __future__ import annotations

import json
from typing import Any

from listingsapi._types import APIObject
from listingsapi._utils import encode_location_id
from listingsapi.exceptions import ValidationError
from listingsapi.resources._base import APIResource

POST_SITES = ("GOOGLE", "FACEBOOK")
POST_TYPES = ("ANNOUNCEMENT", "EVENT", "OFFER", "COVID19", "PRODUCT")
CTA_TYPES = ("BOOK", "ORDER", "SHOP", "LEARN_MORE", "SIGN_UP", "GET_OFFER")


class Posts(APIResource):
    """Create and manage social posts on Google and Facebook.

    Example:
        # One post, many locations, both sites
        result = client.posts.bulk_publish(
            name="Summer opening hours",
            location_ids=[16808, 16809],
            message="We are open late all summer!",
            sites=["GOOGLE", "FACEBOOK"],
        )
        print(result.socialPost.id)
    """

    def create(self, body: dict[str, Any]) -> APIObject:
        """Create a post from a raw body dict (flat fields, not input-wrapped).

        Required: postName, locationIds (base64), postType, postSites. Prefer
        create_announcement / create_event / create_offer for keyword arguments
        and client-side validation.
        """
        data = self._post("posts", body)
        return APIObject(data.get("data", {}).get("createSocialPost") or {})

    def create_announcement(
        self,
        *,
        name: str,
        location_ids: list[str | int],
        message: str | dict[str, str],
        sites: list[str] | None = None,
        cta_type: str | None = None,
        cta_url: str | None = None,
        media_url: str | None = None,
        scheduled_dates: dict[str, Any] | None = None,
        additional_fields: dict[str, Any] | None = None,
    ) -> APIObject:
        """Create an ANNOUNCEMENT post: a plain message with optional CTA and media.

        Args:
            name: Internal campaign name (not shown to customers).
            location_ids: Locations to publish to (numeric or base64 IDs).
            message: Post body. A string publishes the same text to every site;
                a dict maps site to text, e.g. {"GOOGLE": "...", "FACEBOOK": "..."}.
            sites: Target sites, default ["GOOGLE"]. Valid: GOOGLE, FACEBOOK.
            cta_type: Optional call-to-action button (BOOK, ORDER, SHOP,
                LEARN_MORE, SIGN_UP, GET_OFFER); requires cta_url.
            cta_url: Destination for the CTA button.
            media_url: Optional public image URL attached on every site.
            scheduled_dates: Optional {"startDatetime", "endDatetime"} window.
            additional_fields: Extra flat camelCase fields merged as-is.
        """
        return self._create_typed(
            post_type="ANNOUNCEMENT",
            name=name,
            location_ids=location_ids,
            message=message,
            sites=sites,
            cta_type=cta_type,
            cta_url=cta_url,
            media_url=media_url,
            scheduled_dates=scheduled_dates,
            context_info=None,
            additional_fields=additional_fields,
        )

    def create_event(
        self,
        *,
        name: str,
        location_ids: list[str | int],
        message: str | dict[str, str],
        title: str,
        start_day: str,
        end_day: str,
        start_time: str | None = None,
        end_time: str | None = None,
        sites: list[str] | None = None,
        cta_type: str | None = None,
        cta_url: str | None = None,
        media_url: str | None = None,
        scheduled_dates: dict[str, Any] | None = None,
        additional_fields: dict[str, Any] | None = None,
    ) -> APIObject:
        """Create an EVENT post with a title and a start/end window.

        Google requires the event title. start_day/end_day are dates
        (YYYY-MM-DD); start_time/end_time are display strings like "10:00am".
        """
        if not title or not title.strip():
            raise ValidationError("Invalid post: title is required for events")
        context: dict[str, Any] = {"title": title, "startDay": start_day, "endDay": end_day}
        if start_time is not None:
            context["startTime"] = start_time
        if end_time is not None:
            context["endTime"] = end_time
        return self._create_typed(
            post_type="EVENT",
            name=name,
            location_ids=location_ids,
            message=message,
            sites=sites,
            cta_type=cta_type,
            cta_url=cta_url,
            media_url=media_url,
            scheduled_dates=scheduled_dates,
            context_info=context,
            additional_fields=additional_fields,
        )

    def create_offer(
        self,
        *,
        name: str,
        location_ids: list[str | int],
        message: str | dict[str, str],
        title: str,
        coupon_code: str | None = None,
        discount: str | None = None,
        redeem_url: str | None = None,
        terms_conditions: str | None = None,
        start_day: str | None = None,
        end_day: str | None = None,
        sites: list[str] | None = None,
        cta_type: str | None = None,
        cta_url: str | None = None,
        media_url: str | None = None,
        scheduled_dates: dict[str, Any] | None = None,
        additional_fields: dict[str, Any] | None = None,
    ) -> APIObject:
        """Create an OFFER post with a coupon, discount, and terms.

        title labels the offer; start_day/end_day (YYYY-MM-DD) bound its validity.
        """
        if not title or not title.strip():
            raise ValidationError("Invalid post: title is required for offers")
        context: dict[str, Any] = {"title": title}
        for key, value in (
            ("couponCode", coupon_code),
            ("discount", discount),
            ("redeemUrl", redeem_url),
            ("termsConditions", terms_conditions),
            ("startDay", start_day),
            ("endDay", end_day),
        ):
            if value is not None:
                context[key] = value
        return self._create_typed(
            post_type="OFFER",
            name=name,
            location_ids=location_ids,
            message=message,
            sites=sites,
            cta_type=cta_type,
            cta_url=cta_url,
            media_url=media_url,
            scheduled_dates=scheduled_dates,
            context_info=context,
            additional_fields=additional_fields,
        )

    def bulk_publish(
        self,
        *,
        name: str,
        location_ids: list[str | int],
        message: str | dict[str, str],
        sites: list[str] | None = None,
        post_type: str = "ANNOUNCEMENT",
        cta_type: str | None = None,
        cta_url: str | None = None,
        media_url: str | None = None,
        scheduled_dates: dict[str, Any] | None = None,
        context_info: dict[str, Any] | None = None,
        additional_fields: dict[str, Any] | None = None,
    ) -> APIObject:
        """Publish one post across many locations on Google and Facebook in one call.

        Defaults to both sites. The single message (or per-site dict) is expanded
        into one entry per site, location IDs are encoded automatically, and the
        payload is validated client-side before any network call.

        Args:
            name: Internal campaign name.
            location_ids: All locations to publish to (numeric or base64 IDs).
            message: Post body for every site, or a per-site dict.
            sites: Default ["GOOGLE", "FACEBOOK"].
            post_type: ANNOUNCEMENT (default), EVENT, OFFER, COVID19, or PRODUCT.
            cta_type / cta_url: Optional call-to-action button on every site.
            media_url: Optional public image URL attached on every site.
            scheduled_dates: Optional {"startDatetime", "endDatetime"} window.
            context_info: Event/offer details when post_type needs them.
            additional_fields: Extra flat camelCase fields merged as-is.

        Example:
            result = client.posts.bulk_publish(
                name="Holiday hours",
                location_ids=[16808, 16809, 16810],
                message="Open until 10pm through the holidays!",
                media_url="https://cdn.example.com/holiday.jpg",
                cta_type="LEARN_MORE",
                cta_url="https://example.com/holiday-hours",
            )
        """
        body = self._build_post_body(
            post_type=post_type,
            name=name,
            location_ids=location_ids,
            message=message,
            sites=sites if sites is not None else list(POST_SITES),
            cta_type=cta_type,
            cta_url=cta_url,
            media_url=media_url,
            scheduled_dates=scheduled_dates,
            context_info=context_info,
            additional_fields=additional_fields,
        )
        data = self._post("bulk-posts", body)
        return APIObject(data.get("data", {}).get("createBulkSocialPost") or {})

    def retrieve(self, post_id: str) -> APIObject:
        """Get a post with its content, per-site publish status, and analytics."""
        data = self._get(f"posts/{post_id}")
        return APIObject(data.get("data", {}).get("socialPostView") or {})

    def delete(self, post_id: str) -> APIObject:
        """Delete a post and remove it from every site it was published to."""
        data = self._delete(f"posts/{post_id}")
        return APIObject(data.get("data", {}).get("deleteSocialPost") or {})

    def list_for_location(
        self,
        location_id: str | int,
        *,
        tag: str = "all",
        page: int | None = None,
        per_page: int | None = None,
        filters: dict[str, Any] | None = None,
        sort_fields: dict[str, Any] | None = None,
    ) -> APIObject:
        """List post campaigns targeting a location.

        Offset-paginated: returns .records plus .pageInfo with totalPages,
        totalRecords, hasNextPage. tag defaults to "all" (the API errors when
        it is omitted).
        """
        params = self._list_params(tag, page, per_page, filters, sort_fields)
        encoded = encode_location_id(location_id)
        data = self._get(f"locations/{encoded}/posts", params)
        return APIObject(data.get("data", {}).get("rollupSocialPosts") or {})

    def bulk_retrieve(self, bulk_post_id: str) -> APIObject:
        """Get a bulk campaign with per-location publish status and analytics."""
        data = self._get(f"bulk-posts/{bulk_post_id}")
        return APIObject(data.get("data", {}).get("socialPostViewBulk") or {})

    def bulk_list_for_location(
        self,
        location_id: str | int,
        *,
        tag: str = "all",
        page: int | None = None,
        per_page: int | None = None,
        filters: dict[str, Any] | None = None,
        sort_fields: dict[str, Any] | None = None,
    ) -> APIObject:
        """List bulk (multi-location) campaigns that include a location."""
        params = self._list_params(tag, page, per_page, filters, sort_fields)
        encoded = encode_location_id(location_id)
        data = self._get(f"locations/{encoded}/bulk-posts", params)
        return APIObject(data.get("data", {}).get("rollupSocialPosts") or {})

    def _create_typed(self, **kwargs: Any) -> APIObject:
        sites = kwargs.pop("sites")
        body = self._build_post_body(
            sites=sites if sites is not None else ["GOOGLE"],
            **kwargs,
        )
        data = self._post("posts", body)
        return APIObject(data.get("data", {}).get("createSocialPost") or {})

    def _build_post_body(
        self,
        *,
        post_type: str,
        name: str,
        location_ids: list[str | int],
        message: str | dict[str, str],
        sites: list[str],
        cta_type: str | None,
        cta_url: str | None,
        media_url: str | None,
        scheduled_dates: dict[str, Any] | None,
        context_info: dict[str, Any] | None,
        additional_fields: dict[str, Any] | None,
    ) -> dict[str, Any]:
        problems: list[str] = []
        if not name or not name.strip():
            problems.append("name is required")
        if not location_ids:
            problems.append("location_ids must not be empty")
        if post_type not in POST_TYPES:
            problems.append(f"post_type must be one of {', '.join(POST_TYPES)}")
        invalid_sites = [s for s in sites if s not in POST_SITES]
        if not sites or invalid_sites:
            problems.append(f"sites must be a non-empty subset of {', '.join(POST_SITES)}")
        if isinstance(message, dict):
            missing = [s for s in sites if not (message.get(s) or "").strip()]
            if missing:
                problems.append(f"message missing for sites: {', '.join(missing)}")
        elif not message or not message.strip():
            problems.append("message is required")
        if (cta_type is None) != (cta_url is None):
            problems.append("cta_type and cta_url must be provided together")
        if cta_type is not None and cta_type not in CTA_TYPES:
            problems.append(f"cta_type must be one of {', '.join(CTA_TYPES)}")
        if problems:
            raise ValidationError("Invalid post: " + "; ".join(problems))

        per_site_message = (
            message if isinstance(message, dict) else {site: message for site in sites}
        )
        body: dict[str, Any] = {
            "postName": name.strip(),
            "locationIds": [encode_location_id(lid) for lid in location_ids],
            "postType": post_type,
            "postSites": list(sites),
            "postMessage": [{"site": s, "message": per_site_message[s]} for s in sites],
        }
        if cta_type is not None:
            body["postCta"] = [{"site": s, "type": cta_type, "url": cta_url} for s in sites]
        if media_url is not None:
            body["postMediaUrl"] = [{"site": s, "url": media_url, "type": "IMAGE"} for s in sites]
        if scheduled_dates is not None:
            body["postScheduledDates"] = scheduled_dates
        if context_info is not None:
            body["postContextInfo"] = context_info
        if additional_fields:
            body.update(additional_fields)
        return body

    def _list_params(
        self,
        tag: str,
        page: int | None,
        per_page: int | None,
        filters: dict[str, Any] | None,
        sort_fields: dict[str, Any] | None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"tag": tag}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["perPage"] = per_page
        if filters is not None:
            params["filters"] = json.dumps(filters)
        if sort_fields is not None:
            params["sortFields"] = json.dumps(sort_fields)
        return params

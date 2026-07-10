"""High-level workflow functions — client.workflows.*

Workflows combine multiple API calls into single, product-level operations.
These are the functions that turn raw API calls into real automation.

Example:
    import listingsapi

    client = listingsapi.ListingsAPI()

    # Auto-reply to all unanswered reviews
    client.workflows.auto_reply_to_reviews(16808, template="Thank you for your feedback!")

    # Full listings health audit in one call
    report = client.workflows.listings_health_audit(16808)
"""

from __future__ import annotations

import csv
from typing import Any

from listingsapi._types import APIObject
from listingsapi._utils import encode_location_id
from listingsapi.resources._base import APIResource


class Workflows(APIResource):
    """Pre-built automations that combine multiple SDK calls.

    These are real product features, not just API wrappers.
    """

    def auto_reply_to_reviews(
        self,
        location_id: str | int,
        *,
        template: str = "Thank you for your feedback!",
        min_rating: int = 4,
        only_unanswered: bool = True,
        dry_run: bool = False,
    ) -> list[dict[str, Any]]:
        """Auto-reply to reviews for a location.

        Fetches recent reviews, filters by rating and response status,
        and posts replies using your template. Perfect for maintaining
        response rates without manual effort.

        Args:
            location_id: Location to process.
            template: Reply text for matching reviews.
            min_rating: Only reply to reviews with this rating or higher (default 4).
            only_unanswered: Skip reviews that already have a response (default True).
            dry_run: If True, return what would be replied to without actually posting.

        Returns:
            List of dicts with review id, rating, and reply status.

        Example:
            results = client.workflows.auto_reply_to_reviews(
                16808,
                template="Thanks for the {rating}-star review!",
                min_rating=4,
            )
            print(f"Replied to {len(results)} reviews")
        """
        from listingsapi.resources.reviews import Reviews

        reviews_resource = Reviews(self._client)
        results = []

        for review in reviews_resource.list(location_id, first=50).auto_paging_iter():
            raw = review.to_dict()
            rating = raw.get("rating") or raw.get("ratingValue") or 0
            has_response = bool(raw.get("responses") or raw.get("responseContent"))

            if rating < min_rating:
                continue
            if only_unanswered and has_response:
                continue

            reply_text = template.replace("{rating}", str(rating))
            interaction_id = raw.get("interactionId") or raw.get("uid") or raw.get("id", "")
            entry = {"id": interaction_id, "rating": rating, "reply": reply_text}

            if not dry_run and interaction_id:
                try:
                    reviews_resource.respond(interaction_id, reply_text)
                    entry["status"] = "sent"
                except Exception as e:
                    entry["status"] = f"error: {e}"
            else:
                entry["status"] = "dry_run"

            results.append(entry)

        return results

    def onboard_location(
        self,
        name: str,
        street: str,
        city: str,
        state: str,
        postal_code: str,
        country: str,
        phone: str,
        *,
        store_id: str | None = None,
        folder_name: str | None = None,
        tags: list[str] | None = None,
        keywords: list[str] | None = None,
        **extra: Any,
    ) -> APIObject:
        """Onboard a new location in one call — creates it, assigns folder, tags, and keywords.

        Combines: create_location + add_to_folder + add_tags + add_keywords

        Args:
            name: Business name.
            street: Street address.
            city: City.
            state: State ISO code (e.g. "NY").
            postal_code: Zip/postal code.
            country: Country ISO code (e.g. "US").
            phone: Phone number.
            store_id: Optional store identifier.
            folder_name: Optional folder to assign location to.
            tags: Optional tags to add.
            keywords: Optional keywords to track for rankings.
            **extra: Additional fields passed to create_location.

        Returns:
            APIObject with created location data and onboarding status.

        Example:
            result = client.workflows.onboard_location(
                name="Acme Coffee",
                street="123 Main St",
                city="New York",
                state="NY",
                postal_code="10001",
                country="US",
                phone="5551234567",
                folder_name="NYC Stores",
                tags=["new", "coffee"],
                keywords=["coffee shop near me"],
            )
        """
        from listingsapi.resources.folders import Folders
        from listingsapi.resources.keywords import Keywords
        from listingsapi.resources.locations import Locations
        from listingsapi.resources.tags import Tags

        locations = Locations(self._client)
        input_data: dict[str, Any] = {
            "name": name,
            "street": street,
            "city": city,
            "stateIso": state,
            "postalCode": postal_code,
            "countryIso": country,
            "phone": phone,
        }
        if store_id:
            input_data["storeId"] = store_id
        input_data.update(extra)

        result = locations.create(input_data)
        location_data = result.to_dict()
        location_id = location_data.get("location", {}).get("id") or location_data.get("id")
        status: dict[str, Any] = {"location": location_data, "folder": None, "tags": [], "keywords": []}

        if location_id:
            if folder_name:
                folders = Folders(self._client)
                status["folder"] = folders.add_locations(folder_name, [location_id]).to_dict()

            if tags:
                tags_resource = Tags(self._client)
                for tag in tags:
                    status["tags"].append(tags_resource.add(location_id, tag).to_dict())

            if keywords:
                kw_resource = Keywords(self._client)
                status["keywords"] = [kw.to_dict() for kw in kw_resource.add(location_id, keywords)]

        return APIObject(status)

    def bulk_onboard_locations(
        self,
        csv_path: str,
        *,
        folder_name: str | None = None,
        tags: list[str] | None = None,
        dry_run: bool = False,
    ) -> list[dict[str, Any]]:
        """Onboard locations in bulk from a CSV file.

        CSV columns: name, street, city, state, postal_code, country, phone, store_id (optional)

        Args:
            csv_path: Path to CSV file.
            folder_name: Optional folder to assign all locations to.
            tags: Optional tags to add to all locations.
            dry_run: If True, validate CSV and return parsed rows without creating.

        Returns:
            List of results per row — each with location data or error.

        Example:
            results = client.workflows.bulk_onboard_locations(
                "locations.csv",
                folder_name="Batch Import",
                tags=["imported"],
            )
            succeeded = [r for r in results if r["status"] == "created"]
            print(f"Created {len(succeeded)} of {len(results)} locations")
        """
        results = []
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                entry: dict[str, Any] = {"row": row}
                if dry_run:
                    entry["status"] = "dry_run"
                    results.append(entry)
                    continue
                try:
                    result = self.onboard_location(
                        name=row.get("name", ""),
                        street=row.get("street", ""),
                        city=row.get("city", ""),
                        state=row.get("state", ""),
                        postal_code=row.get("postal_code", ""),
                        country=row.get("country", ""),
                        phone=row.get("phone", ""),
                        store_id=row.get("store_id"),
                        folder_name=folder_name,
                        tags=tags,
                    )
                    entry["result"] = result.to_dict()
                    entry["status"] = "created"
                except Exception as e:
                    entry["status"] = f"error: {e}"
                results.append(entry)
        return results

    def weekly_reputation_report(
        self, location_id: str | int, *, start_date: str | None = None, end_date: str | None = None
    ) -> APIObject:
        """Generate a reputation report for a location — reviews, ratings, analytics, listings status.

        Combines: reviews + review_analytics + google_analytics + listings status

        Args:
            location_id: Location to report on.
            start_date: Optional start date (YYYY-MM-DD).
            end_date: Optional end date (YYYY-MM-DD).

        Returns:
            APIObject with review_summary, analytics, and listings_health.

        Example:
            report = client.workflows.weekly_reputation_report(16808)
            print(f"Average rating: {report.review_summary.get('averageRating')}")
            print(f"Google views: {report.analytics.get('google', {}).get('views')}")
        """
        from listingsapi.resources.analytics import Analytics
        from listingsapi.resources.listings import Listings
        from listingsapi.resources.reviews import Reviews

        reviews = Reviews(self._client)
        analytics = Analytics(self._client)
        listings = Listings(self._client)

        date_params: dict[str, str] = {}
        if start_date:
            date_params["start_date"] = start_date
        if end_date:
            date_params["end_date"] = end_date

        review_overview = reviews.analytics.overview(location_id, **date_params).to_dict()

        review_page = reviews.list(location_id, first=50, **date_params)
        recent_reviews = [r.to_dict() for r in review_page]

        google = analytics.google(location_id, from_date=start_date, to_date=end_date).to_dict()
        bing = analytics.bing(location_id, from_date=start_date, to_date=end_date).to_dict()

        premium = [l.to_dict() for l in listings.premium(location_id)]
        synced = [l for l in premium if l.get("syncStatus") == "SYNCED"]

        return APIObject({
            "location_id": location_id,
            "review_summary": review_overview,
            "recent_reviews": recent_reviews,
            "analytics": {"google": google, "bing": bing},
            "listings_health": {
                "total": len(premium),
                "synced": len(synced),
                "sync_rate": f"{len(synced) / len(premium) * 100:.0f}%" if premium else "N/A",
            },
        })

    def listings_health_audit(self, location_id: str | int) -> APIObject:
        """Run a full listings health audit for a location.

        Checks premium listings, voice listings, duplicates, and connection status.

        Returns:
            APIObject with premium, voice, duplicates, connection_status, and health_score.

        Example:
            audit = client.workflows.listings_health_audit(16808)
            print(f"Health score: {audit.health_score}%")
            print(f"Duplicates found: {len(audit.duplicates)}")
        """
        from listingsapi.resources.listings import Listings
        from listingsapi.resources.locations import Locations

        listings = Listings(self._client)
        locations = Locations(self._client)

        premium = [l.to_dict() for l in listings.premium(location_id)]
        voice = [l.to_dict() for l in listings.voice(location_id)]
        dupes = [l.to_dict() for l in listings.duplicates(location_id)]
        connection = locations.connection_info(location_id).to_dict()

        synced = [l for l in premium if l.get("syncStatus") == "SYNCED"]
        issues = [l for l in premium if l.get("syncStatus") not in ("SYNCED", None)]

        health_score = int(len(synced) / len(premium) * 100) if premium else 0

        return APIObject({
            "location_id": location_id,
            "premium": premium,
            "voice": voice,
            "duplicates": dupes,
            "connection_status": connection,
            "synced_count": len(synced),
            "issue_count": len(issues),
            "issues": issues,
            "health_score": health_score,
        })

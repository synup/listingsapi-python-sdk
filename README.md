<p align="center">
  <img src="assets/listingsapi-logo.svg" alt="listingsAPI" width="104" height="104" />
</p>

<h1 align="center">listingsAPI Python SDK</h1>

<p align="center">
  <a href="https://pypi.org/project/listingsapi/"><img src="https://img.shields.io/pypi/v/listingsapi?color=2C6BE0" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/listingsapi/"><img src="https://img.shields.io/pypi/dm/listingsapi?color=5BB0FF" alt="PyPI downloads" /></a>
  <a href="https://pypi.org/project/listingsapi/"><img src="https://img.shields.io/badge/python-3.9%2B-2C6BE0" alt="Python 3.9+" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License: MIT" /></a>
  <a href="https://www.listingsapi.com"><img src="https://img.shields.io/badge/Visit-listingsapi.com-2C6BE0" alt="Website" /></a>
</p>

The official Python SDK for [listingsAPI](https://www.listingsapi.com): business listings, reviews, posts, and analytics for local marketing, in one typed client.

```python
import listingsapi

client = listingsapi.ListingsAPI()  # reads LISTINGSAPI_KEY from env

for location in client.locations.list(first=10):
    print(location.name, location.city)
```

Full API reference and guides: [docs.listingsapi.com](https://docs.listingsapi.com)

## Contents

- [Installation](#installation)
- [Authentication](#authentication)
- [Quickstart](#quickstart)
- [Pagination](#pagination)
- [Locations](#locations)
- [Reviews](#reviews)
- [Posts](#posts)
- [Listings](#listings)
- [Analytics](#analytics)
- [Photos](#photos)
- [Connected accounts](#connected-accounts)
- [Supporting APIs](#supporting-apis)
- [Workflows: pre-built automations](#workflows-pre-built-automations)
- [Method reference](#method-reference)
- [Error handling](#error-handling)
- [Configuration](#configuration)
- [Examples and development](#examples-and-development)

## Installation

```bash
pip install listingsapi
```

Requires Python 3.9+. The only runtime dependency is `requests`.

## Authentication

Get an API key from your [listingsAPI dashboard](https://listingsapi.com/dashboard/api-keys) and export it:

```bash
export LISTINGSAPI_KEY="your-api-key"
```

```python
import listingsapi

client = listingsapi.ListingsAPI()                      # reads LISTINGSAPI_KEY
client = listingsapi.ListingsAPI(api_key="your-key")    # or pass it explicitly
```

## Quickstart

Auto-reply to positive reviews in ten lines:

```python
import listingsapi

client = listingsapi.ListingsAPI()

results = client.workflows.auto_reply_to_reviews(
    16808,
    template="Thanks for the {rating}-star review! We appreciate your support.",
    min_rating=4,
)
print(f"Replied to {len(results)} reviews")
```

Audit your listings health in three:

```python
audit = client.workflows.listings_health_audit(16808)
print(f"Health score: {audit.health_score}%")
print(f"Synced: {audit.synced_count}, Issues: {audit.issue_count}")
```

## Pagination

List endpoints return a `SyncPage`. Iterate it directly, page manually, or let it walk every page for you:

```python
page = client.locations.list(first=50)
for loc in page:
    print(loc.name)

if page.has_more:                      # manual paging
    next_page = page.next_page()

for loc in page.auto_paging_iter():    # every record, all pages
    print(loc.name)
```

Responses are `APIObject`s: dot access (`loc.name`), dict access (`loc["stateIso"]`), and `loc.to_dict()` all work.

## Locations

Create a location in one call. `locations.add()` takes every mandatory field as a keyword argument and validates them client-side (name length, 200-character description, category, country, city) before any network call:

```python
result = client.locations.add(
    name="Acme Dental",
    description=(
        "Acme Dental is a family-owned dental practice in downtown New York "
        "offering preventive care, cosmetic dentistry, orthodontics, and "
        "emergency appointments. Our board-certified team combines modern "
        "equipment with a gentle, patient-first approach."
    ),
    sub_category_id=1432,
    country_iso="US",
    city="New York",
    street="123 Jump Street",
    postal_code="10013",
    phone="6443859313",
)
print(result.location.id)
```

Optional keyword arguments: `state_iso`, `website`, `store_id`, `hide_address`, `business_hours`, `folder_ids`, `service_area`, `place_action_links`, `enabled_site_ids` (publish to a subset of your plan's sites), and `additional_fields` for anything else. Get valid category IDs from `client.subcategories()`.

Find and fetch:

```python
location = client.locations.retrieve(16808)
page = client.locations.search("cafe", first=20)

locations = client.locations.list_by_ids([16808, 16749])
locations = client.locations.list_by_store_codes(["STORE01", "STORE02"])
```

Update and lifecycle:

```python
client.locations.update({"id": 16808, "phone": "5559876543"})
client.locations.archive([16808])
client.locations.cancel_archive([16808], "manual", "ops@example.com")
```

`locations.create(input_dict)` is also available when you already have a raw camelCase payload.

## Reviews

```python
# List with filters, or walk everything
page = client.reviews.list(16808, first=20, rating_filters=[1, 2])
for review in client.reviews.list(16808, first=50).auto_paging_iter():
    print(review.rating, review.content)

# Respond, edit, archive
client.reviews.respond(interaction_id="uuid-here", content="Thank you!")
client.reviews.edit_response(review_id="...", response_id="...", content="Updated reply")
client.reviews.archive_response(response_id="...")

# Analytics and phrases
overview = client.reviews.analytics.overview(16808, start_date="2024-01-01")
timeline = client.reviews.analytics.timeline(16808)
sites = client.reviews.analytics.sites_stats(16808)
phrases = client.reviews.phrases(["TG9jYXRpb246MTY4MDg="], start_date="2024-01-01")
```

## Posts

Publish announcements, events, and offers to Google and Facebook.

`posts.bulk_publish()` is the one-call way to put the same post on both sites across many locations. It expands your message per site, encodes location IDs, and validates the payload client-side before any network call:

```python
result = client.posts.bulk_publish(
    name="Holiday hours",
    location_ids=[16808, 16809, 16810],
    message="Open until 10pm through the holidays!",
    media_url="https://cdn.example.com/holiday.jpg",
    cta_type="LEARN_MORE",
    cta_url="https://example.com/holiday-hours",
)
print(result.socialPost.id, result.socialPost.status)  # INPROGRESS, publishes async
```

Pass a dict as `message` for per-site copy: `{"GOOGLE": "...", "FACEBOOK": "..."}`. `sites` defaults to both.

Typed creates for single campaigns:

```python
# Announcement: plain message, optional CTA and image
result = client.posts.create_announcement(
    name="Grand Opening",
    location_ids=[16808],
    message="We are now open!",
    sites=["GOOGLE"],
    cta_type="LEARN_MORE",
    cta_url="https://example.com/opening",
)

# Event: title plus start/end window
result = client.posts.create_event(
    name="Live music",
    location_ids=[16808],
    message="Join us Friday!",
    title="Jazz Night",
    start_day="2026-08-01",
    end_day="2026-08-01",
    start_time="7:00pm",
    end_time="10:00pm",
)

# Offer: coupon, discount, terms
result = client.posts.create_offer(
    name="Summer sale",
    location_ids=[16808],
    message="20% off all week!",
    title="Summer Sale",
    coupon_code="SUMMER20",
    discount="20%",
    redeem_url="https://example.com/sale",
    start_day="2026-08-01",
    end_day="2026-08-07",
)
```

Read, monitor, and delete:

```python
post = client.posts.retrieve("U29jaWFsUG9zdDo0NDEyMg==")   # per-site publish status + analytics
page = client.posts.list_for_location(16808, page=1, per_page=10)
bulk = client.posts.bulk_retrieve("QnVsa1Bvc3Q6OTk=")        # per-location publish status
campaigns = client.posts.bulk_list_for_location(16808)
client.posts.delete("U29jaWFsUG9zdDo0NDEyMg==")
```

Publishing is asynchronous: creates return `status: INPROGRESS`; poll `retrieve()` until `SUCCESS` and check `publishDetails[].submissionError` for per-site failures.

## Listings

```python
premium = client.listings.premium(16808)
voice = client.listings.voice(16808)

# Duplicates
dupes = client.listings.duplicates(16808)
client.listings.mark_duplicate(16808, ["listing-item-id"])
client.listings.mark_not_duplicate(16808, ["listing-item-id"])

# Connect and disconnect
client.listings.connect(16808, "listing-id", "account-id")
client.listings.disconnect(16808, "GOOGLE")
```

## Analytics

```python
google = client.analytics.google(16808, from_date="2024-01-01")
bing = client.analytics.bing(16808)
facebook = client.analytics.facebook(16808)
```

## Photos

```python
photos = client.photos.list(16808)
client.photos.add(16808, [{"photo": "https://example.com/img.jpg", "type": "ADDITIONAL"}])
client.photos.remove(16808, ["photo-id"])
client.photos.star(16808, ["media-id"], starred=True)
status = client.photos.upload_status("request-id")
```

## Connected accounts

```python
accounts = client.connected_accounts.list()
url = client.connected_accounts.connect_google("https://ok.com", "https://err.com")
client.connected_accounts.disconnect_google("account-id")

# OAuth for a single location
url = client.connected_accounts.oauth_url(16808, "GOOGLE", "https://ok.com", "https://err.com")
client.connected_accounts.oauth_disconnect(16808, "FACEBOOK")
```

## Supporting APIs

```python
sites = client.plan_sites()          # directories included in your plan
countries = client.countries()       # supported countries and states
subcategories = client.subcategories()  # business categories (IDs for locations.add)
subs = client.subscriptions()        # active subscriptions
```

## Workflows: pre-built automations

High-level functions that combine multiple API calls into real product features.

```python
# Auto-reply to positive reviews (dry_run previews without sending)
results = client.workflows.auto_reply_to_reviews(
    16808,
    template="Thanks for the {rating}-star review!",
    min_rating=4,
    dry_run=True,
)

# Weekly reputation report
report = client.workflows.weekly_reputation_report(16808)
print(report.review_summary, report.analytics, report.listings_health)

# Listings health audit
audit = client.workflows.listings_health_audit(16808)
print(f"Score: {audit.health_score}%, Issues: {audit.issue_count}")
```

## Method reference

### Supporting APIs (client-level)

| Method | Description |
|--------|-------------|
| `client.plan_sites()` | Directories included in your plan |
| `client.countries()` | Supported countries and states (ISO codes) |
| `client.subcategories()` | Business categories (IDs for `locations.add`) |
| `client.subscriptions()` | Active subscriptions for the account |

### Locations

| Method | Description |
|--------|-------------|
| `locations.list(first, after, before, last)` | List locations with cursor pagination |
| `locations.retrieve(location_id)` | Fetch a single location by ID |
| `locations.list_by_ids(location_ids)` | Fetch specific locations by ID |
| `locations.list_by_store_codes(store_codes)` | Fetch locations by store code |
| `locations.search(query, fields, first, after)` | Search by name, address, or store ID |
| `locations.add(**fields)` | One-call create with keyword args and client-side validation |
| `locations.create(input_dict)` | Create from a raw camelCase payload |
| `locations.update(input_dict)` | Update fields on a location (pass `id` plus changes) |
| `locations.archive(location_ids)` | Archive locations |
| `locations.cancel_archive(location_ids, selection_type, changed_by)` | Cancel a pending archive |

### Posts

| Method | Description |
|--------|-------------|
| `posts.bulk_publish(**fields)` | One post to Google and Facebook across many locations |
| `posts.create_announcement(**fields)` | Create an ANNOUNCEMENT post |
| `posts.create_event(**fields)` | Create an EVENT post with title and date window |
| `posts.create_offer(**fields)` | Create an OFFER post with coupon and terms |
| `posts.create(body)` | Create from a raw flat payload |
| `posts.retrieve(post_id)` | Get a post with per-site publish status and analytics |
| `posts.delete(post_id)` | Delete a post from every published site |
| `posts.list_for_location(location_id, tag, page, per_page)` | List post campaigns for a location |
| `posts.bulk_retrieve(bulk_post_id)` | Get a bulk campaign with per-location status |
| `posts.bulk_list_for_location(location_id, tag, page, per_page)` | List bulk campaigns touching a location |

### Reviews

| Method | Description |
|--------|-------------|
| `reviews.list(location_id, first, rating_filters, ...)` | List reviews/interactions with filters |
| `reviews.details(interaction_ids)` | Detailed review data for specific interactions |
| `reviews.respond(interaction_id, content)` | Reply to a review |
| `reviews.edit_response(review_id, response_id, content)` | Edit a reply |
| `reviews.archive_response(response_id)` | Archive a reply |
| `reviews.settings(location_id)` | Review notification settings |
| `reviews.edit_settings(location_id, site_urls)` | Update notification settings |
| `reviews.site_config()` | Review site configuration for the account |
| `reviews.phrases(location_ids, start_date, ...)` | Frequently used phrases across reviews |
| `reviews.analytics.overview(location_id, start_date, end_date)` | Review analytics overview |
| `reviews.analytics.timeline(location_id, ...)` | Review volume/rating over time |
| `reviews.analytics.sites_stats(location_id, ...)` | Per-site review stats |

### Listings

| Method | Description |
|--------|-------------|
| `listings.premium(location_id)` | Premium directory listings |
| `listings.voice(location_id)` | Voice assistant listings |
| `listings.duplicates(location_id)` | Duplicate listings for a location |
| `listings.all_duplicates(tag, page)` | Duplicates across all locations |
| `listings.mark_duplicate(location_id, listing_item_ids)` | Mark listings as duplicates |
| `listings.mark_not_duplicate(location_id, listing_item_ids)` | Unmark duplicates |
| `listings.connect(location_id, listing_id, account_id)` | Connect a listing to a profile |
| `listings.disconnect(location_id, site)` | Disconnect a listing |
| `listings.create_gmb(location_id, ...)` | Create a Google Business Profile listing |

### Analytics

| Method | Description |
|--------|-------------|
| `analytics.google(location_id, from_date, to_date)` | Google Business Profile insights |
| `analytics.bing(location_id, from_date, to_date)` | Bing Places insights |
| `analytics.facebook(location_id, from_date, to_date)` | Facebook page insights |

### Photos

| Method | Description |
|--------|-------------|
| `photos.list(location_id)` | List photos for a location |
| `photos.add(location_id, photos)` | Upload photos by URL |
| `photos.remove(location_id, photo_ids)` | Delete photos |
| `photos.star(location_id, media_ids, starred)` | Star or unstar photos |
| `photos.upload_status(request_id)` | Status of a bulk photo upload |

### Connected accounts

| Method | Description |
|--------|-------------|
| `connected_accounts.list(...)` | List connected Google/Facebook accounts |
| `connected_accounts.details(connected_account_id)` | Account details |
| `connected_accounts.folders(connected_account_id, folder_name)` | Folders/location groups in the account |
| `connected_accounts.suggestions(...)` | Suggested listing-to-location matches |
| `connected_accounts.listings(...)` | Listings available in a connected account |
| `connected_accounts.connect_google(success_url, error_url)` | Start Google OAuth connect |
| `connected_accounts.connect_facebook(success_url, error_url)` | Start Facebook OAuth connect |
| `connected_accounts.disconnect_google(connected_account_id)` | Disconnect a Google account |
| `connected_accounts.disconnect_facebook(connected_account_id)` | Disconnect a Facebook account |
| `connected_accounts.trigger_matches(connected_account_ids)` | Trigger profile-to-location matching |
| `connected_accounts.confirm_matches(match_record_ids)` | Confirm suggested matches |
| `connected_accounts.oauth_url(location_id, site, success_url, error_url)` | OAuth connect URL for one location |
| `connected_accounts.oauth_disconnect(location_id, site)` | Disconnect one location's profile |

### Workflows

| Method | Description |
|--------|-------------|
| `workflows.auto_reply_to_reviews(location_id, template, min_rating, dry_run)` | Auto-reply to unanswered positive reviews |
| `workflows.weekly_reputation_report(location_id)` | Reviews + analytics + listings health in one report |
| `workflows.listings_health_audit(location_id)` | Sync status and duplicate audit with health score |

## Error handling

Every SDK error derives from `listingsapi.ListingsAPIError`. API failures raise `APIError` or one of its subclasses, whether the platform reports them as an HTTP status or inside the response body. The platform returns some failures (invalid tokens, mutation validation) as HTTP 200 with an `errors[]` payload, and the SDK raises for those too, so you never have to inspect `success` flags yourself.

```
ListingsAPIError                 base class for everything below
├── APIError                     any failure reported by the API
│   ├── AuthenticationError      401 or invalid-token error payloads
│   ├── PermissionDeniedError    403 or permission error payloads
│   ├── NotFoundError            404
│   ├── ValidationError          400/422, or mutations with success=false / errors[]
│   ├── RateLimitError           429, carries retry_after
│   └── InternalServerError      5xx, safe to retry
└── APIConnectionError           network failure, nothing reached the API
```

| Attribute | Meaning |
|---|---|
| `status_code` | HTTP status of the response (can be 200 for payload-level errors) |
| `code` | First platform error code, e.g. `"SY10005"` |
| `errors` | Every error entry, normalized to `{"code", "message", "context"}` |
| `response_body` | Raw response text |
| `retry_after` | Seconds to wait (RateLimitError only) |

```python
import listingsapi

client = listingsapi.ListingsAPI()

try:
    result = client.locations.add(
        name="Acme Dental",
        description=DESCRIPTION,  # min 200 characters
        sub_category_id=1432,
        country_iso="US",
        city="New York",
    )
except listingsapi.ValidationError as e:
    # Raised client-side for missing/short mandatory fields, or by the API
    # (e.g. SY10005 description too short, SY10072 duplicate storeId)
    for err in e.errors:
        print(err["code"], err["message"])
except listingsapi.AuthenticationError:
    print("Invalid API key. Check LISTINGSAPI_KEY.")
except listingsapi.RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s.")
except listingsapi.APIConnectionError:
    print("Network error. Could not reach the API.")
```

The client automatically retries **read** requests (GET) on 429 and 5xx responses — up to `max_retries` attempts (default 2), honoring `Retry-After`. Writes (creates, replies, posts, deletes) are **not** retried automatically: they are not idempotent, so a blind retry after a completed-but-5xx write could duplicate the record. If you need to retry a write, do it yourself only when the operation is safe to repeat. A `RateLimitError` means retries were exhausted; back off for `e.retry_after` seconds before trying again:

```python
import time
import listingsapi

def with_backoff(fn, attempts=3):
    for attempt in range(attempts):
        try:
            return fn()
        except listingsapi.RateLimitError as e:
            if attempt == attempts - 1:
                raise
            time.sleep(e.retry_after or 2 ** attempt)

page = with_backoff(lambda: client.locations.list(first=50))
```

See [examples/12_error_handling.py](examples/12_error_handling.py) for a runnable walkthrough.

## Configuration

```python
client = listingsapi.ListingsAPI(
    api_key="your-api-key",
    base_url="https://listingsapi.com",  # default
    timeout=300.0,
    max_retries=3,
)
```

| Option | Default | Description |
|---|---|---|
| `api_key` | `LISTINGSAPI_KEY` env var | Your API key |
| `base_url` | `https://listingsapi.com` | API host |
| `timeout` | `240.0` | Request timeout in seconds |
| `max_retries` | `2` | Automatic retries on 429 and 5xx for read (GET) requests; writes are never auto-retried |

## Examples and development

Runnable scripts for every area live in [examples/](examples/), from a 10-line quickstart to a full FastAPI backend.

```bash
git clone https://github.com/listings-api/listingsapi-python-sdk.git
cd listingsapi-python-sdk
pip install -e ".[dev]"
pytest
```

## License

[MIT](LICENSE)

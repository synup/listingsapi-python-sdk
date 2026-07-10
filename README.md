# listingsAPI Python SDK

[![PyPI](https://img.shields.io/pypi/v/listingsapi)](https://pypi.org/project/listingsapi/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://pypi.org/project/listingsapi/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

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
- [Listings](#listings)
- [Analytics](#analytics)
- [Photos](#photos)
- [Connected accounts](#connected-accounts)
- [Supporting APIs](#supporting-apis)
- [Workflows: pre-built automations](#workflows-pre-built-automations)
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

The client automatically retries 429 and 5xx responses (default 2 attempts, honoring `Retry-After`). A `RateLimitError` means retries were exhausted; back off for `e.retry_after` seconds before trying again:

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
| `max_retries` | `2` | Automatic retries on 429 and 5xx |

## Examples and development

Runnable scripts for every area live in [examples/](examples/), from a 10-line quickstart to a full FastAPI backend.

```bash
git clone https://github.com/synup/listingsapi-python-sdk.git
cd listingsapi-python-sdk
pip install -e ".[dev]"
pytest
```

## License

[MIT](LICENSE)

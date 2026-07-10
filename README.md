# listingsAPI Python SDK

Build local presence automations in minutes — review auto-responders, listings monitors, reputation dashboards, bulk onboarding tools, and more.

## Installation

```bash
pip install listingsapi
```

## Quick start: auto-reply to reviews in 10 lines

```python
import listingsapi

client = listingsapi.ListingsAPI()  # reads LISTINGSAPI_KEY from env

# Auto-reply to all 4-5 star reviews that haven't been answered
results = client.workflows.auto_reply_to_reviews(
    16808,
    template="Thanks for the {rating}-star review! We appreciate your support.",
    min_rating=4,
)
print(f"Replied to {len(results)} reviews")
```

## Quick start: listings health audit in 3 lines

```python
import listingsapi

client = listingsapi.ListingsAPI()

audit = client.workflows.listings_health_audit(16808)
print(f"Health score: {audit.health_score}%")
print(f"Synced: {audit.synced_count}, Issues: {audit.issue_count}")
print(f"Duplicates found: {len(audit.duplicates)}")
```

## Configuration

```python
import listingsapi

# Minimal — reads LISTINGSAPI_KEY env var
client = listingsapi.ListingsAPI()

# Explicit key
client = listingsapi.ListingsAPI(api_key="your-api-key")

# With custom config
client = listingsapi.ListingsAPI(
    api_key="your-api-key",
    timeout=300.0,       # request timeout in seconds (default: 240)
    max_retries=3,       # auto-retry on 429/5xx (default: 2)
)
```

## Locations

### Create a location in one call

`locations.add()` takes every mandatory field as a keyword argument and validates
them client-side (name length, 200-character description, category, country, city)
before any network call:

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


```python
# List with pagination
page = client.locations.list(first=10)
for loc in page:
    print(loc.name, loc.city, loc.stateIso)

# Next page
if page.has_more:
    next_page = page.next_page()

# Auto-paginate all
for loc in client.locations.list(first=100).auto_paging_iter():
    print(loc.name)

# Retrieve single location
location = client.locations.retrieve(16808)
print(location.name)

# Search
page = client.locations.search("cafe", first=20)

# By IDs, store codes, folder, or tags
locations = client.locations.list_by_ids([16808, 16749])
locations = client.locations.list_by_store_codes(["STORE01", "STORE02"])
locations = client.locations.list_by_folder(folder_name="franchise")
page = client.locations.list_by_tags(["vip", "recent"], first=20)

# Create
result = client.locations.create({
    "name": "Acme Inc",
    "storeId": "ACME01",
    "street": "123 Main St",
    "city": "New York",
    "stateIso": "NY",
    "postalCode": "10001",
    "countryIso": "US",
    "phone": "5551234567",
})
print(result.success, result.errors)

# Update, archive, activate
client.locations.update({"id": 16808, "phone": "5559876543"})
client.locations.archive([16808])
client.locations.activate([16808])
```

## Reviews

```python
# List reviews with filters
page = client.reviews.list(16808, first=20, rating_filters=[1, 2])
for review in page:
    print(review.content, review.rating)

# Auto-paginate all reviews
for review in client.reviews.list(16808, first=50).auto_paging_iter():
    print(review.content)

# Respond to a review
client.reviews.respond(interaction_id="uuid-here", content="Thank you!")

# Edit or archive a response
client.reviews.edit_response(review_id="...", response_id="...", content="Updated reply")
client.reviews.archive_response(response_id="...")

# Review analytics
overview = client.reviews.analytics.overview(16808, start_date="2024-01-01")
timeline = client.reviews.analytics.timeline(16808)
sites = client.reviews.analytics.sites_stats(16808)

# Review phrases
phrases = client.reviews.phrases(["TG9jYXRpb246MTY4MDg="], start_date="2024-01-01")
```

## Listings

```python
# Premium, voice, and AI listings
premium = client.listings.premium(16808)
voice = client.listings.voice(16808)
ai = client.listings.ai(16808)

# Duplicates
dupes = client.listings.duplicates(16808)
client.listings.mark_duplicate(16808, ["listing-item-id"])
client.listings.mark_not_duplicate(16808, ["listing-item-id"])

# Connect/disconnect
client.listings.connect(16808, "listing-id", "account-id")
client.listings.disconnect(16808, "GOOGLE")
```

## Analytics

```python
google = client.analytics.google(16808, from_date="2024-01-01")
bing = client.analytics.bing(16808)
facebook = client.analytics.facebook(16808)
```

## Keywords

```python
keywords = client.keywords.list(16808)
performance = client.keywords.performance(16808, from_date="2024-01-01")
created = client.keywords.add(16808, ["plumber", "plumbing near me"])
client.keywords.archive("keyword-id")
```

## Campaigns

```python
campaigns = client.campaigns.list(16808)
result = client.campaigns.create(
    16808,
    name="Holiday Feedback",
    customers=[{"name": "John", "email": "john@example.com"}],
    screening=False,
)
client.campaigns.add_customers("campaign-id", [{"name": "Jane", "email": "jane@example.com"}])
```

## Folders

```python
folders = client.folders.list()
tree = client.folders.tree()
client.folders.create("franchise", parent_folder_name="all_franchise")
client.folders.rename("Old Name", "New Name")
client.folders.add_locations("franchise", [16808, 16749])
client.folders.remove_locations([16808])
client.folders.delete("folder-name")
```

## Users

```python
users = client.users.list()
roles = client.users.roles()
result = client.users.create(email="jane@example.com", role_id="...", first_name="Jane")
client.users.update("user-id", first_name="Jane Updated")
client.users.add_locations("user-id", [16808])
client.users.remove_locations("user-id", [16808])
```

## Tags

```python
tags = client.tags.list()
client.tags.add(16808, "vip")
client.tags.remove(16808, "old-tag")
```

## Photos

```python
photos = client.photos.list(16808)
client.photos.add(16808, [{"photo": "https://example.com/img.jpg", "type": "ADDITIONAL"}])
client.photos.remove(16808, ["photo-id"])
client.photos.star(16808, ["media-id"], starred=True)
```

## Connected accounts

```python
accounts = client.connected_accounts.list()
url = client.connected_accounts.connect_google("https://ok.com", "https://err.com")
client.connected_accounts.disconnect_google("account-id")

# OAuth for single location
url = client.connected_accounts.oauth_url(16808, "GOOGLE", "https://ok.com", "https://err.com")
client.connected_accounts.oauth_disconnect(16808, "FACEBOOK")
```

## Grid reports

```python
result = client.grid_reports.create(
    location_id=16808,
    keywords=["italian restaurant"],
    business_name="Chianti",
    business_street="No 12, 5th Block",
    business_city="Bengaluru",
    business_state="Karnataka",
    business_country="India",
    latitude=12.935216,
    longitude=77.619961,
    distance=20,
    distance_unit="km",
    grid_size=3,
)
report = client.grid_reports.retrieve("report-id")
reports = client.grid_reports.list(16808, page_size=20, page=1)
```

## Automations

```python
result = client.automations.temporary_close(
    name="Holiday closure",
    start_date="2025-12-24",
    start_time="18:00:00",
    end_date="2025-12-26",
    location_id=16808,
)
```

## Account-level

```python
sites = client.plan_sites()
countries = client.countries()
subs = client.subscriptions()
```

## Workflows — pre-built automations

High-level functions that combine multiple API calls into real product features.

```python
# Auto-reply to positive reviews
results = client.workflows.auto_reply_to_reviews(
    16808,
    template="Thanks for the {rating}-star review!",
    min_rating=4,
    dry_run=True,  # preview without sending
)

# Onboard a location with folder, tags, and keywords in one call
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

# Bulk onboard from CSV
results = client.workflows.bulk_onboard_locations("locations.csv", folder_name="Imported")

# Weekly reputation report
report = client.workflows.weekly_reputation_report(16808)
print(report.review_summary, report.analytics, report.listings_health)

# Listings health audit
audit = client.workflows.listings_health_audit(16808)
print(f"Score: {audit.health_score}%, Issues: {audit.issue_count}")
```

## Error handling

Every SDK error derives from `listingsapi.ListingsAPIError`. API failures raise
`APIError` or one of its subclasses, whether the platform reports them as an
HTTP status or inside the response body — the platform returns some failures
(invalid tokens, mutation validation) as HTTP 200 with an `errors[]` payload,
and the SDK raises for those too, so you never have to inspect `success` flags
yourself.

```
ListingsAPIError                 base class for everything below
├── APIError                     any failure reported by the API
│   ├── AuthenticationError      401 or invalid-token error payloads
│   ├── PermissionDeniedError    403 or permission error payloads
│   ├── NotFoundError            404
│   ├── ValidationError          400/422, or mutations with success=false / errors[]
│   ├── RateLimitError           429 — carries retry_after
│   └── InternalServerError      5xx — safe to retry
└── APIConnectionError           network failure, nothing reached the API
```

Every `APIError` carries:

- `status_code` — the HTTP status (can be 200 for payload-level errors)
- `code` — the first platform error code, e.g. `"SY10005"`
- `errors` — every error entry, normalized to `{"code", "message", "context"}`
- `response_body` — the raw response text

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
    print("Invalid API key — check LISTINGSAPI_KEY")
except listingsapi.RateLimitError as e:
    print(f"Rate limited — retry after {e.retry_after}s")
except listingsapi.APIConnectionError:
    print("Network error — could not reach the API")
```

Retries: the client automatically retries 429 and 5xx responses (default 2
attempts, honoring `Retry-After`). A `RateLimitError` means retries were
exhausted — back off for `e.retry_after` seconds before trying again.

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

See `examples/12_error_handling.py` for a runnable walkthrough.

## Version

Current version: 0.5.0

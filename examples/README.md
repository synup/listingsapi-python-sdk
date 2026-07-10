# listingsAPI SDK Examples

Runnable scripts demonstrating common use cases with the `listingsapi.ListingsAPI()` resource-based API. Set your API key before running:

```bash
export LISTINGSAPI_KEY="your_api_key"
```

## Core Examples

| # | Script | Description |
|---|--------|-------------|
| 01 | `01_quickstart.py` | Connect and fetch your first locations |
| 02 | `02_bulk_export_locations.py` | Export all locations to CSV with auto-pagination |
| 03 | `03_review_monitoring.py` | Monitor reviews and flag negative ones |
| 04 | `04_bulk_respond_reviews.py` | Auto-reply to unanswered reviews with templates |
| 05 | `05_analytics_report.py` | Pull Google and review analytics per location |
| 06 | `06_listings_audit.py` | Audit listing sync status across locations |
| 08 | `08_google_connect_flow.py` | Connect Google Business Profiles via OAuth |
| 11 | `11_fastapi_backend.py` | Wire the SDK into a FastAPI backend |
| 12 | `12_error_handling.py` | Catch, inspect, and retry API errors |
| 13 | `13_bulk_posting.py` | Publish one post to Google and Facebook across locations |

## Workflow Examples

These scripts use the `client.workflows.*` helper functions that combine multiple API calls into single, high-level automations:

| Script | Description |
|--------|-------------|
| `review_auto_responder.py` | Auto-reply to positive reviews (dry-run supported) |
| `weekly_report.py` | Generate a full reputation report for a location |
| `listings_health_check.py` | Run a listings sync and duplicate audit |

## API Quick Reference

```python
import listingsapi

client = listingsapi.ListingsAPI()  # reads LISTINGSAPI_KEY from env

# Locations
page = client.locations.list(first=10)
for loc in page:
    print(loc.name, loc.city)

# Auto-paginate all results
for loc in client.locations.list(first=100).auto_paging_iter():
    print(loc.name)

# Reviews
reviews = client.reviews.list(location_id, first=20)
client.reviews.respond(interaction_id, "Thank you!")

# Listings
premium = client.listings.premium(location_id)
voice = client.listings.voice(location_id)

# Analytics
google = client.analytics.google(location_id, from_date="2024-01-01")
overview = client.reviews.analytics.overview(location_id)

# Workflows
client.workflows.auto_reply_to_reviews(location_id, min_rating=4)
client.workflows.listings_health_audit(location_id)
report = client.workflows.weekly_reputation_report(location_id)
```

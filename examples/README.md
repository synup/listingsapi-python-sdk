# Synup SDK Examples

Runnable scripts demonstrating common use cases with the `synup.Synup()` resource-based API. Set your API key before running:

```bash
export SYNUP_API_KEY="your_api_key"
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
| 07 | `07_user_management.py` | Create users and manage roles and access |
| 08 | `08_google_connect_flow.py` | Connect Google Business Profiles via OAuth |
| 09 | `09_grid_rank_report.py` | Create Local Rank Grid reports |
| 10 | `10_review_campaign.py` | Run review solicitation campaigns |
| 11 | `11_fastapi_backend.py` | Wire the SDK into a FastAPI backend |

## Workflow Examples

These scripts use the `client.workflows.*` helper functions that combine multiple API calls into single, high-level automations:

| Script | Description |
|--------|-------------|
| `review_auto_responder.py` | Auto-reply to positive reviews (dry-run supported) |
| `bulk_location_onboarding.py` | Import locations from a CSV file |
| `weekly_report.py` | Generate a full reputation report for a location |
| `listings_health_check.py` | Run a listings sync and duplicate audit |

## Full-stack Sample

The `fullstack/` directory contains a complete working app -- a **Locations & Listings Dashboard** with a FastAPI backend and HTML frontend.

```bash
pip install synup-sdk fastapi uvicorn
SYNUP_API_KEY='your_key' python examples/fullstack/server.py
# Open http://localhost:3000
```

Features:
- Browse locations in a card grid with search
- Click a location to see its listings (premium, voice, additional) and reviews
- Slide-out detail panel with tabbed view

## API Quick Reference

```python
import synup

client = synup.Synup()  # reads SYNUP_API_KEY from env

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

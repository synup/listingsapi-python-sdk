"""Analytics report: Pull Google profile analytics and review stats for every location.

Generates a per-location summary covering Google impressions,
review counts, ratings, and per-site breakdowns for a given date range.

Usage:
    export LISTINGSAPI_KEY="your_api_key"
    python 05_analytics_report.py
"""

import listingsapi

client = listingsapi.ListingsAPI()

FROM_DATE = "2024-01-01"
TO_DATE = "2024-12-31"

# Auto-paginate all locations, but cap at 10 for a demo run
all_locations = list(client.locations.list(first=100).auto_paging_iter())
print(f"Generating report for {len(all_locations)} locations ({FROM_DATE} to {TO_DATE})\n")

for loc in all_locations[:10]:
    print(f"--- {loc.name} ---")

    # Google profile analytics (views, searches, actions)
    google = client.analytics.google(loc.id, from_date=FROM_DATE, to_date=TO_DATE)
    if google:
        print(f"  Google: {google.to_dict()}")

    # Review analytics overview (totals, avg rating, response rate)
    review_stats = client.reviews.analytics.overview(loc.id, start_date=FROM_DATE, end_date=TO_DATE)
    if review_stats:
        print(f"  Reviews: {review_stats.to_dict()}")

    # Per-site review breakdown
    sites = client.reviews.analytics.sites_stats(loc.id, start_date=FROM_DATE, end_date=TO_DATE)
    if sites:
        print(f"  Sites: {sites.to_dict()}")

    print()

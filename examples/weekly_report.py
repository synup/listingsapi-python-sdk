"""Weekly reputation report: Generate a single-location report with one workflow call.

Pulls review stats, Google analytics, and listing sync health into a single
report object. Schedule this weekly (e.g. via cron) and pipe the output to
email, Slack, or a dashboard.

Usage:
    export LISTINGSAPI_KEY="your_api_key"
    python weekly_report.py
"""

import json
import listingsapi

client = listingsapi.ListingsAPI()

LOCATION_ID = 16808  # Replace with your location ID

# Generate a full reputation report for the past week
report = client.workflows.weekly_reputation_report(
    LOCATION_ID,
    start_date="2024-12-23",
    end_date="2024-12-31",
)

# --- Review summary ---
summary = report.review_summary if hasattr(report, "review_summary") else {}
print("=== Review Summary ===")
if isinstance(summary, dict):
    print(f"  Average rating:  {summary.get('averageRating', 'N/A')}")
    print(f"  Total reviews:   {summary.get('totalReviews', 'N/A')}")
    print(f"  Response rate:   {summary.get('responseRate', 'N/A')}")
else:
    print(f"  {summary}")

# --- Recent reviews ---
recent = getattr(report, "recent_reviews", []) or []
print(f"\n=== Recent Reviews ({len(recent)}) ===")
for r in recent[:5]:
    if isinstance(r, dict):
        print(f"  [{r.get('rating', '?')}] {r.get('authorName', 'Anonymous')}: {(r.get('content') or '')[:60]}")

# --- Analytics ---
analytics = getattr(report, "analytics", {})
print("\n=== Analytics ===")
if isinstance(analytics, dict):
    google = analytics.get("google", {})
    bing = analytics.get("bing", {})
    print(f"  Google: {json.dumps(google, default=str)[:120]}")
    print(f"  Bing:   {json.dumps(bing, default=str)[:120]}")

# --- Listings health ---
health = getattr(report, "listings_health", {})
print("\n=== Listings Health ===")
if isinstance(health, dict):
    print(f"  Total listings: {health.get('total', 'N/A')}")
    print(f"  Synced:         {health.get('synced', 'N/A')}")
    print(f"  Sync rate:      {health.get('sync_rate', 'N/A')}")

# Dump full report as JSON for downstream processing
# with open("weekly_report.json", "w") as f:
#     json.dump(report.to_dict(), f, indent=2, default=str)
#     print(f"\nFull report saved to weekly_report.json")

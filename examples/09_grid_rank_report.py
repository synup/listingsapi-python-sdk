"""Grid Rank: Create a Local Rank Grid report and fetch the results.

A grid rank report places a geographic grid around your location and
checks your Google ranking for target keywords at every grid point.

Usage:
    export LISTINGSAPI_KEY="your_api_key"
    python 09_grid_rank_report.py
"""

import time
import listingsapi

client = listingsapi.ListingsAPI()

LOCATION_ID = 16808  # Replace with your location ID

# Create a 3x3 grid rank report for two keywords
result = client.grid_reports.create(
    location_id=LOCATION_ID,
    keywords=["italian restaurant", "pizza near me"],
    business_name="Your Business",
    business_street="123 Main St",
    business_city="New York",
    business_state="NY",
    business_country="US",
    latitude=40.7128,
    longitude=-74.0060,
    distance=10,
    distance_unit="mi",
    grid_size=3,
)

report_ids = getattr(result, "reportIds", None) or []
print(f"Created {len(report_ids)} grid reports")

# Wait for generation, then fetch each report
if report_ids:
    print("Waiting for report generation...")
    time.sleep(10)

    for rid in report_ids:
        report = client.grid_reports.retrieve(rid)
        print(f"\nReport {rid}:")
        print(f"  Keyword: {getattr(report, 'keyword', 'N/A')}")
        grid_points = getattr(report, "gridPoints", []) or []
        print(f"  Grid data: {len(grid_points)} points")

# List all existing reports for this location
all_reports = client.grid_reports.list(LOCATION_ID, page_size=5, page=1)
print(f"\nTotal grid reports: {getattr(all_reports, 'total', 0)}")

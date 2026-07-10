"""Bulk location onboarding: Import locations from a CSV file using workflows.

Reads a CSV with columns (name, street, city, state, postal_code, country, phone)
and creates each location in listingsAPI, optionally assigning them to a folder and
tagging them. Run with dry_run=True first to validate your data.

Usage:
    export LISTINGSAPI_KEY="your_api_key"
    python bulk_location_onboarding.py

Expected CSV format (locations.csv):
    name,street,city,state,postal_code,country,phone,store_id
    Acme Coffee Downtown,123 Main St,New York,NY,10001,US,5551234567,NYC-001
    Acme Coffee Midtown,456 Park Ave,New York,NY,10022,US,5559876543,NYC-002
"""

import listingsapi

client = listingsapi.ListingsAPI()

CSV_PATH = "locations.csv"  # Replace with your CSV file path

# Dry run: validate the CSV without creating anything
print("=== Dry Run (validation only) ===")
preview = client.workflows.bulk_onboard_locations(
    CSV_PATH,
    folder_name="New Imports",
    tags=["imported", "needs-review"],
    dry_run=True,
)

for entry in preview:
    row = entry["row"]
    print(f"  {row.get('name', '?')} -- {row.get('city', '?')}, {row.get('state', '?')} [{entry['status']}]")

print(f"\n{len(preview)} rows parsed. Review above, then uncomment below to import.\n")

# Uncomment to actually create the locations
# print("=== Creating Locations ===")
# results = client.workflows.bulk_onboard_locations(
#     CSV_PATH,
#     folder_name="New Imports",
#     tags=["imported", "needs-review"],
#     dry_run=False,
# )
#
# created = [r for r in results if r["status"] == "created"]
# errors = [r for r in results if r["status"].startswith("error")]
# print(f"Created: {len(created)}, Errors: {len(errors)}")
# for err in errors:
#     print(f"  Error for {err['row'].get('name', '?')}: {err['status']}")

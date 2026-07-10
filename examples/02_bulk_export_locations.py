"""Bulk export: Download every location in your account to a CSV file.

Uses auto_paging_iter() to walk through all pages automatically so you
never have to manage cursors yourself.

Usage:
    export LISTINGSAPI_KEY="your_api_key"
    python 02_bulk_export_locations.py
"""

import csv
import listingsapi

client = listingsapi.ListingsAPI()

# auto_paging_iter() handles pagination end-to-end
locations = list(client.locations.list(first=100).auto_paging_iter())
print(f"Fetched {len(locations)} locations")

# Write to CSV
output_file = "locations_export.csv"
fields = ["id", "name", "storeId", "street", "city", "stateIso", "postalCode", "countryIso", "phone"]

with open(output_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for loc in locations:
        writer.writerow(loc.to_dict())

print(f"Exported to {output_file}")

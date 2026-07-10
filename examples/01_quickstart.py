"""Quickstart: Connect to listingsAPI and list your locations in under 10 lines.

The ListingsAPI() client reads your API key from the LISTINGSAPI_KEY environment
variable automatically -- no boilerplate needed.

Usage:
    export LISTINGSAPI_KEY="your_api_key"
    python 01_quickstart.py
"""

import listingsapi

client = listingsapi.ListingsAPI()

# Fetch the first 5 locations -- returns a SyncPage you can iterate directly
page = client.locations.list(first=5)

for loc in page:
    print(f"{loc.name} -- {getattr(loc, 'city', 'N/A')}, {getattr(loc, 'stateIso', 'N/A')}")

print(f"\nTotal locations on page: {len(page)}")
print(f"Has more pages: {page.has_more}")

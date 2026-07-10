"""Listings audit: Check listing sync status, voice assistants, and AI suggestions.

Walks through your locations and prints a per-location breakdown of
premium listing health, voice coverage, and any AI-generated suggestions.

Usage:
    export LISTINGSAPI_KEY="your_api_key"
    python 06_listings_audit.py
"""

import listingsapi

client = listingsapi.ListingsAPI()

# Get first 10 locations (use auto_paging_iter() for all)
page = client.locations.list(first=10)
print(f"Auditing listings for {len(page)} locations\n")

for loc in page:
    print(f"--- {loc.name} ---")

    # Premium listings (Google, Yelp, Facebook, etc.)
    premium = client.listings.premium(loc.id)
    synced = [l for l in premium if l.syncStatus == "SYNCED"]
    not_synced = [l for l in premium if getattr(l, "syncStatus", None) != "SYNCED"]
    print(f"  Premium: {len(synced)} synced, {len(not_synced)} not synced")
    for listing in not_synced:
        print(f"    [{getattr(listing, 'syncStatus', 'UNKNOWN')}] {getattr(listing, 'site', 'N/A')}")

    # Voice assistant listings (Alexa, Google Assistant, Siri)
    voice = client.listings.voice(loc.id)
    print(f"  Voice: {len(voice)} listings")

    # AI listing suggestions
    ai = client.listings.ai(loc.id)
    if ai:
        print(f"  AI suggestions available: True")

    print()

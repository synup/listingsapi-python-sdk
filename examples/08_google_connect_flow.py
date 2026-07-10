"""Google connect flow: Wire up Google Business Profile connections.

Walks through the full OAuth flow:
1. Get a connect URL (redirect your user here)
2. List already-connected Google accounts
3. Review match suggestions
4. Inspect listings under each account

Usage:
    export LISTINGSAPI_KEY="your_api_key"
    python 08_google_connect_flow.py
"""

import listingsapi

client = listingsapi.ListingsAPI()

# Step 1: Generate an OAuth URL for Google account connection
result = client.connected_accounts.connect_google(
    success_url="https://yourapp.com/connect/success",
    error_url="https://yourapp.com/connect/error",
)
print(f"Step 1 -- Redirect user to: {getattr(result, 'url', 'N/A')}")

# Step 2: List already connected Google accounts
accounts = client.connected_accounts.list(publisher="google")
connected = getattr(accounts, "connectedAccounts", None) or []
print(f"\nStep 2 -- Connected Google accounts:")
for acc in connected:
    print(f"  {acc.email} -- status: {acc.status}")
    acc_id = acc.id

    # Step 3: Check match suggestions
    suggestions = client.connected_accounts.suggestions(acc_id, page=1, per_page=10)
    records = getattr(suggestions, "matchedRecords", None) or []
    print(f"  Suggestions: {len(records)} matches found")

    # Step 4: Inspect listings under this account
    listings = client.connected_accounts.listings(acc_id, page=1, per_page=10)
    records = getattr(listings, "records", None) or []
    for rec in records[:3]:
        print(f"    - {rec.locationName} ({getattr(rec, 'address', 'N/A')})")

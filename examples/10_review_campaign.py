"""Review campaigns: Create a campaign, add customers, and track results.

Sends review solicitation emails/SMS to a list of customers. You can
add more customers later and pull campaign-level stats at any time.

Usage:
    export LISTINGSAPI_KEY="your_api_key"
    python 10_review_campaign.py
"""

import listingsapi
from listingsapi import APIError

client = listingsapi.ListingsAPI()

LOCATION_ID = 16808  # Replace with your location ID

# Create a campaign with an initial customer list
customers = [
    {"name": "Alice Johnson", "email": "alice@example.com"},
    {"name": "Bob Smith", "email": "bob@example.com", "phone": "5551234567"},
]

result = client.campaigns.create(
    location_id=LOCATION_ID,
    name="Q1 Feedback Campaign",
    customers=customers,
    screening=False,
)

campaign_data = result.to_dict()
if campaign_data.get("success") is not False:
    campaign = getattr(result, "reviewCampaign", result)
    campaign_id = getattr(campaign, "id", None)
    print(f"Created campaign: {getattr(campaign, 'name', 'N/A')} (id: {campaign_id})")

    if campaign_id:
        # Add more customers later
        more_customers = [
            {"name": "Charlie Davis", "email": "charlie@example.com"},
        ]
        add_result = client.campaigns.add_customers(campaign_id, more_customers)
        print(f"Added customers: {add_result.to_dict()}")

        # List campaign customers
        info = client.campaigns.customers(campaign_id)
        print(f"Campaign info: {info.to_dict()}")
else:
    print(f"Failed: {campaign_data}")

# List all campaigns for this location
campaigns = client.campaigns.list(LOCATION_ID)
print(f"\nAll campaigns ({len(campaigns)}):")
for c in campaigns:
    print(f"  {c.name} -- {getattr(c, 'status', 'N/A')}")

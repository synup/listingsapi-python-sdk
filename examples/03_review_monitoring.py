"""Review monitoring: Scan recent reviews across locations and flag anything negative.

Loops through your first 5 locations, pulls the latest reviews, and
highlights any 1- or 2-star review that still needs a response.

Usage:
    export LISTINGSAPI_KEY="your_api_key"
    python 03_review_monitoring.py
"""

import listingsapi

client = listingsapi.ListingsAPI()

# Get first 5 locations
page = client.locations.list(first=5)

for loc in page:
    print(f"\n--- {loc.name} ---")

    # Fetch 10 most recent reviews
    reviews = client.reviews.list(loc.id, first=10)
    if not reviews:
        print("  No recent reviews")
        continue

    for review in reviews:
        rating = getattr(review, "rating", "N/A")
        author = getattr(review, "authorName", "Anonymous")
        site = getattr(review, "siteName", "Unknown")
        content = (getattr(review, "content", "") or "")[:80]
        responded = bool(getattr(review, "responses", None))

        flag = " ** NEEDS ATTENTION **" if isinstance(rating, (int, float)) and rating <= 2 else ""
        status = "Responded" if responded else "No reply"
        print(f"  [{rating}] {author} on {site} ({status}){flag}")
        if content:
            print(f"       {content}...")

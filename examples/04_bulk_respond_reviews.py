"""Bulk respond: Reply to every unanswered review with a rating-based template.

In production you would swap in an LLM to generate personalised replies --
the pattern here shows how to iterate, filter, and respond at scale.

Usage:
    export LISTINGSAPI_KEY="your_api_key"
    python 04_bulk_respond_reviews.py
"""

import listingsapi
from listingsapi import APIError

client = listingsapi.ListingsAPI()

LOCATION_ID = 16808  # Replace with your location ID

TEMPLATES = {
    5: "Thank you so much for the wonderful review! We're thrilled you had a great experience.",
    4: "Thank you for your kind review! We're glad you enjoyed your visit.",
    3: "Thank you for your feedback. We'd love to hear how we can improve -- please reach out to us directly.",
    2: "We're sorry to hear about your experience. Please contact us so we can make it right.",
    1: "We sincerely apologize for your experience. Please reach out to us directly so we can resolve this.",
}

# Fetch reviews and filter to unanswered ones
reviews_page = client.reviews.list(LOCATION_ID, first=50)

unanswered = [
    r for r in reviews_page
    if not getattr(r, "responses", None) and getattr(r, "interactionId", None)
]
print(f"Found {len(unanswered)} unanswered reviews")

for review in unanswered:
    rating = getattr(review, "rating", 3)
    template = TEMPLATES.get(rating, TEMPLATES[3])
    interaction_id = review.interactionId

    try:
        client.reviews.respond(interaction_id, template)
        print(f"  Replied to {getattr(review, 'authorName', 'Anonymous')} ({rating} stars)")
    except APIError as e:
        print(f"  Failed: {e}")

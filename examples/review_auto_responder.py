"""Review auto-responder: Automatically reply to positive reviews using workflows.

Uses client.workflows.auto_reply_to_reviews() to find every unanswered
4- or 5-star review and post a templated "thank you" response. Run this
on a schedule (e.g. daily cron) to keep your response rate high without
manual work.

Usage:
    export LISTINGSAPI_KEY="your_api_key"
    python review_auto_responder.py
"""

import listingsapi

client = listingsapi.ListingsAPI()

LOCATION_ID = 16808  # Replace with your location ID

# Dry-run first to preview which reviews will be answered
print("=== Dry Run ===")
preview = client.workflows.auto_reply_to_reviews(
    LOCATION_ID,
    template="Thanks for the {rating}-star review! We really appreciate your kind words.",
    min_rating=4,
    only_unanswered=True,
    dry_run=True,
)

for entry in preview:
    print(f"  Would reply to review {entry['id']} ({entry['rating']} stars): {entry['reply'][:60]}...")

print(f"\n{len(preview)} reviews would receive a reply.")

# Uncomment the block below to actually send replies
# print("\n=== Sending Replies ===")
# results = client.workflows.auto_reply_to_reviews(
#     LOCATION_ID,
#     template="Thanks for the {rating}-star review! We really appreciate your kind words.",
#     min_rating=4,
#     only_unanswered=True,
#     dry_run=False,
# )
#
# sent = [r for r in results if r["status"] == "sent"]
# errors = [r for r in results if r["status"].startswith("error")]
# print(f"Sent: {len(sent)}, Errors: {len(errors)}")
# for err in errors:
#     print(f"  Error on review {err['id']}: {err['status']}")

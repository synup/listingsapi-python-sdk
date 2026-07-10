"""Bulk posting: publish one post to Google and Facebook across your locations.

Run:
    export LISTINGSAPI_KEY="your-api-key"
    python examples/13_bulk_posting.py
"""

import os
import time

import listingsapi


def main() -> None:
    if not os.environ.get("LISTINGSAPI_KEY"):
        print("Set LISTINGSAPI_KEY to run this example")
        return

    client = listingsapi.ListingsAPI()

    locations = client.locations.list(first=25)
    location_ids = [loc.id for loc in locations]
    if not location_ids:
        print("No locations in this account yet")
        return
    print(f"Publishing to {len(location_ids)} locations on Google and Facebook")

    result = client.posts.bulk_publish(
        name="Summer hours announcement",
        location_ids=location_ids,
        message={
            "GOOGLE": "We are open late all summer! Come see us until 10pm.",
            "FACEBOOK": "Summer hours are here: open until 10pm every night!",
        },
        media_url="https://cdn.example.com/summer.jpg",
        cta_type="LEARN_MORE",
        cta_url="https://example.com/summer-hours",
    )
    bulk_id = result.socialPost.id
    print(f"Created bulk post {bulk_id}, status: {result.socialPost.status}")

    for _ in range(10):
        time.sleep(30)
        post = client.posts.bulk_retrieve(bulk_id)
        info = post.socialPostInfo
        print(f"Status: {info.status}")
        if info.status != "INPROGRESS":
            break

    for detail in post.socialPostInfo.publishDetails or []:
        marker = "ok " if not detail.get("submissionError") else "ERR"
        print(f"  [{marker}] {detail.get('site')}: {detail.get('status')} {detail.get('submissionError') or ''}")


if __name__ == "__main__":
    main()

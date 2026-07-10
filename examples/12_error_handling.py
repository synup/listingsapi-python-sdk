"""Error handling: catch, inspect, and retry listingsAPI errors.

Run:
    export LISTINGSAPI_KEY="your-api-key"
    python examples/12_error_handling.py
"""

import os
import time

import listingsapi

DESCRIPTION = (
    "Acme Dental is a family-owned dental practice in downtown New York offering "
    "preventive care, cosmetic dentistry, orthodontics, and emergency appointments. "
    "Our board-certified team combines modern equipment with a gentle approach."
)


def main() -> None:
    if not os.environ.get("LISTINGSAPI_KEY"):
        print("Set LISTINGSAPI_KEY to run this example")
        return

    client = listingsapi.ListingsAPI()

    # 1. Client-side validation fails fast, before any network call
    try:
        client.locations.add(
            name="Acme Dental",
            description="Too short.",
            sub_category_id=1432,
            country_iso="US",
            city="New York",
        )
    except listingsapi.ValidationError as e:
        print(f"Client-side validation: {e}")

    # 2. API-side errors carry the platform error code and every entry
    try:
        client.locations.add(
            name="Acme Dental",
            description=DESCRIPTION,
            sub_category_id=999999999,
            country_iso="US",
            city="New York",
        )
    except listingsapi.ValidationError as e:
        print(f"API rejected the payload (HTTP {e.status_code}):")
        for err in e.errors:
            print(f"  {err['code']}: {err['message']}")
    except listingsapi.AuthenticationError:
        print("Invalid API key — check LISTINGSAPI_KEY")

    # 3. Distinguish error families for different recovery strategies
    try:
        client.locations.retrieve(999999999)
    except listingsapi.NotFoundError:
        print("Location does not exist — nothing to recover, skip it")
    except listingsapi.PermissionDeniedError:
        print("Key lacks access to this location — check the key's scope")
    except listingsapi.APIConnectionError:
        print("Network problem — safe to retry the same call")

    # 4. Rate limits: the client already retries 429s twice; if RateLimitError
    #    still surfaces, back off for retry_after seconds
    def with_backoff(fn, attempts=3):
        for attempt in range(attempts):
            try:
                return fn()
            except listingsapi.RateLimitError as e:
                if attempt == attempts - 1:
                    raise
                wait = e.retry_after or 2**attempt
                print(f"Rate limited, waiting {wait}s")
                time.sleep(wait)

    page = with_backoff(lambda: client.locations.list(first=10))
    if page is not None:
        print(f"Fetched {len(page)} locations")


if __name__ == "__main__":
    main()

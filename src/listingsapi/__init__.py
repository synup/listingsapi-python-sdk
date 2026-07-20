"""listingsAPI Python SDK — listings, reviews, posts, and analytics for local marketing.

Example:
    import listingsapi

    client = listingsapi.ListingsAPI()  # reads LISTINGSAPI_KEY from env

    for location in client.locations.list(first=10):
        print(location.name, location.city)
"""

from listingsapi._client import ListingsAPI
from listingsapi._types import APIObject, SyncPage
from listingsapi.exceptions import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    InternalServerError,
    ListingsAPIError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ValidationError,
)

__version__ = "0.5.1"

__all__ = [
    # Client
    "ListingsAPI",
    # Types
    "APIObject",
    "SyncPage",
    # Exceptions
    "ListingsAPIError",
    "APIError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "InternalServerError",
    "APIConnectionError",
    # Version
    "__version__",
]

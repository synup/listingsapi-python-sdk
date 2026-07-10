"""listingsAPI resources."""

from listingsapi.resources.locations import Locations
from listingsapi.resources.posts import Posts
from listingsapi.resources.reviews import Reviews
from listingsapi.resources.listings import Listings
from listingsapi.resources.analytics import Analytics
from listingsapi.resources.connected_accounts import ConnectedAccounts
from listingsapi.resources.photos import Photos
from listingsapi.resources.workflows import Workflows

__all__ = [
    "Locations",
    "Posts",
    "Reviews",
    "Listings",
    "Analytics",
    "ConnectedAccounts",
    "Photos",
    "Workflows",
]

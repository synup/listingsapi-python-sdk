"""listingsAPI resources."""

from listingsapi.resources.locations import Locations
from listingsapi.resources.reviews import Reviews
from listingsapi.resources.listings import Listings
from listingsapi.resources.analytics import Analytics
from listingsapi.resources.folders import Folders
from listingsapi.resources.users import Users
from listingsapi.resources.keywords import Keywords
from listingsapi.resources.campaigns import Campaigns
from listingsapi.resources.connected_accounts import ConnectedAccounts
from listingsapi.resources.tags import Tags
from listingsapi.resources.grid_reports import GridReports
from listingsapi.resources.photos import Photos
from listingsapi.resources.automations import Automations
from listingsapi.resources.workflows import Workflows

__all__ = [
    "Locations",
    "Reviews",
    "Listings",
    "Analytics",
    "Folders",
    "Users",
    "Keywords",
    "Campaigns",
    "ConnectedAccounts",
    "Tags",
    "GridReports",
    "Photos",
    "Automations",
    "Workflows",
]

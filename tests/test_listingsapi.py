"""Tests for the resource-based listingsAPI client."""

import os

import pytest
import requests_mock

import listingsapi
from listingsapi import ListingsAPI, APIObject, SyncPage
from listingsapi.exceptions import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ValidationError,
)


# --- Fixtures ---

@pytest.fixture
def client():
    return ListingsAPI(api_key="test-key")


@pytest.fixture
def locations_response():
    return {
        "data": {
            "allLocations": {
                "edges": [
                    {
                        "cursor": "TG9jYXRpb246MTQwMjQ=",
                        "node": {
                            "id": "TG9jYXRpb246MTQwMjQ=",
                            "name": "Stumptown Coffee",
                            "city": "New York",
                            "stateIso": "NY",
                        },
                    },
                    {
                        "cursor": "TG9jYXRpb246MTQwMjM=",
                        "node": {
                            "id": "TG9jYXRpb246MTQwMjM=",
                            "name": "Blue Bottle",
                            "city": "San Francisco",
                            "stateIso": "CA",
                        },
                    },
                ],
                "pageInfo": {
                    "hasNextPage": True,
                    "hasPreviousPage": False,
                    "total": 50,
                },
            }
        }
    }


@pytest.fixture
def empty_response():
    return {"data": {"allLocations": {"edges": [], "pageInfo": {"hasNextPage": False}}}}


# --- Client initialization ---

def test_client_reads_env_var(monkeypatch):
    monkeypatch.setenv("LISTINGSAPI_KEY", "env-key")
    client = ListingsAPI()
    assert client.api_key == "env-key"


def test_client_explicit_key_overrides_env(monkeypatch):
    monkeypatch.setenv("LISTINGSAPI_KEY", "env-key")
    client = ListingsAPI(api_key="explicit-key")
    assert client.api_key == "explicit-key"


def test_client_raises_without_key(monkeypatch):
    monkeypatch.delenv("LISTINGSAPI_KEY", raising=False)
    with pytest.raises(AuthenticationError):
        ListingsAPI()


def test_client_default_base_url(client):
    assert client._base_url == "https://listingsapi.com"


def test_client_custom_base_url():
    c = ListingsAPI(api_key="key", base_url="https://custom.listingsapi.com/")
    assert c._base_url == "https://custom.listingsapi.com"


def test_client_has_resources(client):
    assert hasattr(client, "locations")
    assert hasattr(client, "reviews")
    assert hasattr(client, "listings")
    assert hasattr(client, "analytics")
    assert hasattr(client, "folders")
    assert hasattr(client, "users")
    assert hasattr(client, "keywords")
    assert hasattr(client, "campaigns")
    assert hasattr(client, "connected_accounts")
    assert hasattr(client, "tags")
    assert hasattr(client, "grid_reports")
    assert hasattr(client, "photos")
    assert hasattr(client, "automations")


# --- APIObject ---

def test_api_object_attribute_access():
    obj = APIObject({"name": "Test", "city": "NYC"})
    assert obj.name == "Test"
    assert obj.city == "NYC"


def test_api_object_dict_access():
    obj = APIObject({"name": "Test"})
    assert obj["name"] == "Test"


def test_api_object_nested():
    obj = APIObject({"outer": {"inner": "value"}})
    assert obj.outer.inner == "value"


def test_api_object_list_of_dicts():
    obj = APIObject({"photos": [{"name": "a"}, {"name": "b"}]})
    assert obj.photos[0].name == "a"
    assert obj.photos[1].name == "b"
    assert obj["photos"][0]["name"] == "a"


def test_api_object_get():
    obj = APIObject({"name": "Test"})
    assert obj.get("name") == "Test"
    assert obj.get("missing", "default") == "default"


def test_api_object_contains():
    obj = APIObject({"name": "Test"})
    assert "name" in obj
    assert "missing" not in obj


def test_api_object_to_dict():
    data = {"name": "Test", "city": "NYC"}
    obj = APIObject(data)
    assert obj.to_dict() == data


def test_api_object_missing_attr():
    obj = APIObject({"name": "Test"})
    with pytest.raises(AttributeError):
        obj.nonexistent


# --- SyncPage ---

def test_sync_page_iteration():
    page = SyncPage(data=[{"name": "a"}, {"name": "b"}], has_more=False)
    names = [item.name for item in page]
    assert names == ["a", "b"]


def test_sync_page_len():
    page = SyncPage(data=[{"a": 1}, {"b": 2}], has_more=False)
    assert len(page) == 2


def test_sync_page_indexing():
    page = SyncPage(data=[{"name": "first"}, {"name": "second"}], has_more=False)
    assert page[0].name == "first"
    assert page[1].name == "second"


def test_sync_page_has_more():
    page = SyncPage(data=[{"a": 1}], has_more=True, end_cursor="abc")
    assert page.has_more is True


def test_sync_page_next_page_none_when_no_more():
    page = SyncPage(data=[], has_more=False)
    assert page.next_page() is None


def test_sync_page_auto_paging_iter():
    page2 = SyncPage(data=[{"name": "c"}], has_more=False)
    page1 = SyncPage(
        data=[{"name": "a"}, {"name": "b"}],
        has_more=True,
        end_cursor="cursor1",
        _fetch_next=lambda cursor: page2,
    )
    names = [item.name for item in page1.auto_paging_iter()]
    assert names == ["a", "b", "c"]


# --- Exceptions ---

def test_exception_hierarchy():
    assert issubclass(AuthenticationError, APIError)
    assert issubclass(NotFoundError, APIError)
    assert issubclass(RateLimitError, APIError)
    assert issubclass(ValidationError, APIError)
    assert issubclass(APIError, listingsapi.ListingsAPIError)
    assert issubclass(APIConnectionError, listingsapi.ListingsAPIError)


def test_rate_limit_error_retry_after():
    err = RateLimitError("too fast", status_code=429, retry_after="30")
    assert err.retry_after == 30.0


def test_api_error_export():
    assert listingsapi.APIError is APIError


# --- Locations resource ---

def test_locations_list(client, locations_response):
    with requests_mock.Mocker() as m:
        m.get("https://listingsapi.com/api/v4/locations", json=locations_response)
        page = client.locations.list(first=10)

        assert isinstance(page, SyncPage)
        assert len(page) == 2
        assert page[0].name == "Stumptown Coffee"
        assert page[1].city == "San Francisco"
        assert page.has_more is True
        assert page.total == 50


def test_locations_list_empty(client, empty_response):
    with requests_mock.Mocker() as m:
        m.get("https://listingsapi.com/api/v4/locations", json=empty_response)
        page = client.locations.list(first=10)
        assert len(page) == 0
        assert page.has_more is False


def test_locations_list_by_ids(client):
    response = {
        "data": {
            "getLocationsByIds": [
                {"id": "TG9jYXRpb246MTY4MDg=", "name": "Test Location"},
            ]
        }
    }
    with requests_mock.Mocker() as m:
        m.get("https://listingsapi.com/api/v4/locations-by-ids", json=response)
        locations = client.locations.list_by_ids([16808])
        assert len(locations) == 1
        assert locations[0].name == "Test Location"


def test_locations_search(client):
    response = {
        "data": {
            "searchLocations": {
                "edges": [
                    {"cursor": "c1", "node": {"id": "1", "name": "Cafe A"}},
                ],
                "pageInfo": {"hasNextPage": False, "total": 1},
            }
        }
    }
    with requests_mock.Mocker() as m:
        m.get("https://listingsapi.com/api/v4/locations/search", json=response)
        page = client.locations.search("cafe", first=10)
        assert len(page) == 1
        assert page[0].name == "Cafe A"


def test_locations_create(client):
    response = {
        "data": {
            "createLocation": {
                "success": True,
                "location": {"id": "new-id", "name": "Acme"},
                "errors": [],
            }
        }
    }
    with requests_mock.Mocker() as m:
        m.post("https://listingsapi.com/api/v4/locations", json=response)
        result = client.locations.create({"name": "Acme", "city": "NYC"})
        assert result.success is True


# --- Error handling ---

def test_401_raises_authentication_error(client):
    with requests_mock.Mocker() as m:
        m.get("https://listingsapi.com/api/v4/locations", status_code=401, text="Unauthorized")
        with pytest.raises(AuthenticationError) as exc:
            client.locations.list()
        assert exc.value.status_code == 401


def test_404_raises_not_found_error(client):
    with requests_mock.Mocker() as m:
        m.get("https://listingsapi.com/api/v4/tags", status_code=404, text="Not found")
        with pytest.raises(NotFoundError) as exc:
            client.tags.list()
        assert exc.value.status_code == 404


def test_400_raises_validation_error(client):
    with requests_mock.Mocker() as m:
        m.post("https://listingsapi.com/api/v4/locations", status_code=400, text="Bad request")
        with pytest.raises(ValidationError):
            client.locations.create({"invalid": "data"})


def test_429_raises_rate_limit_error(client):
    with requests_mock.Mocker() as m:
        m.get(
            "https://listingsapi.com/api/v4/locations",
            status_code=429,
            text="Rate limited",
            headers={"Retry-After": "60"},
        )
        with pytest.raises(RateLimitError) as exc:
            client.locations.list()
        assert exc.value.retry_after == 60.0


# --- Reviews resource ---

def test_reviews_list(client):
    response = {
        "data": {
            "interactions": {
                "edges": [
                    {"cursor": "c1", "node": {"id": "r1", "content": "Great!", "rating": 5}},
                ],
                "pageInfo": {"hasNextPage": False},
            }
        }
    }
    with requests_mock.Mocker() as m:
        m.get(
            "https://listingsapi.com/api/v4/locations/TG9jYXRpb246MTY4MDg=/reviews",
            json=response,
        )
        page = client.reviews.list(16808, first=10)
        assert len(page) == 1
        assert page[0].content == "Great!"
        assert page[0].rating == 5


# --- Listings resource ---

def test_listings_premium(client):
    response = {"data": {"listingsForLocation": [{"id": "l1", "site": "google.com"}]}}
    with requests_mock.Mocker() as m:
        m.get(
            "https://listingsapi.com/api/v4/locations/TG9jYXRpb246MTY4MDg=/listings/premium",
            json=response,
        )
        listings = client.listings.premium(16808)
        assert len(listings) == 1
        assert listings[0].site == "google.com"


# --- Analytics resource ---

def test_analytics_google(client):
    response = {"data": {"googleInsights": {"views": 1000}}}
    with requests_mock.Mocker() as m:
        m.get(
            "https://listingsapi.com/api/v4/locations/TG9jYXRpb246MTY4MDg=/google-analytics",
            json=response,
        )
        result = client.analytics.google(16808)
        assert result.views == 1000


# --- Folders resource ---

def test_folders_list(client):
    response = {"data": {"getUserFolders": [{"id": "f1", "name": "franchise"}]}}
    with requests_mock.Mocker() as m:
        m.get("https://listingsapi.com/api/v4/folders/flat", json=response)
        folders = client.folders.list()
        assert len(folders) == 1
        assert folders[0].name == "franchise"


def test_folders_create(client):
    response = {"data": {"createFolder": {"success": True}}}
    with requests_mock.Mocker() as m:
        m.post("https://listingsapi.com/api/v4/folders/create", json=response)
        result = client.folders.create("new-folder")
        assert result.success is True


# --- Tags resource ---

def test_tags_list(client):
    response = {"data": {"listAllTags": [{"id": "t1", "name": "vip"}]}}
    with requests_mock.Mocker() as m:
        m.get("https://listingsapi.com/api/v4/tags", json=response)
        tags = client.tags.list()
        assert len(tags) == 1
        assert tags[0].name == "vip"


# --- Users resource ---

def test_users_list(client):
    response = {"data": {"users": [{"id": "u1", "email": "jane@example.com"}]}}
    with requests_mock.Mocker() as m:
        m.get("https://listingsapi.com/api/v4/users", json=response)
        users = client.users.list()
        assert len(users) == 1
        assert users[0].email == "jane@example.com"


def test_users_create(client):
    response = {"data": {"addUser": {"success": True, "user": {"id": "new"}}}}
    with requests_mock.Mocker() as m:
        m.post("https://listingsapi.com/api/v4/users/create", json=response)
        result = client.users.create(email="j@example.com", role_id="role1", first_name="Jane")
        assert result.success is True


# --- Keywords resource ---

def test_keywords_list(client):
    response = {"data": {"keywordsByLocationId": [{"id": "k1", "name": "plumber"}]}}
    with requests_mock.Mocker() as m:
        m.get(
            "https://listingsapi.com/api/v4/locations/TG9jYXRpb246MTY4MDg=/keywords",
            json=response,
        )
        keywords = client.keywords.list(16808)
        assert len(keywords) == 1
        assert keywords[0].name == "plumber"


# --- Version ---

def test_version():
    assert listingsapi.__version__ == "0.5.0"


# --- locations.add (one-call create with validation) ---

VALID_DESCRIPTION = (
    "Acme Dental is a family-owned dental practice in downtown New York offering "
    "preventive care, cosmetic dentistry, orthodontics, and emergency appointments. "
    "Our board-certified team combines modern equipment with a gentle approach."
)


def test_locations_add_posts_full_payload(client):
    response = {
        "data": {
            "createLocation": {
                "success": True,
                "location": {"id": "new-id", "name": "Acme Dental"},
                "errors": [],
            }
        }
    }
    with requests_mock.Mocker() as m:
        m.post("https://listingsapi.com/api/v4/locations", json=response)
        result = client.locations.add(
            name="Acme Dental",
            description=VALID_DESCRIPTION,
            sub_category_id=1432,
            country_iso="US",
            city="New York",
            street="123 Jump Street",
            postal_code="10013",
            phone="6443859313",
            place_action_links=[
                {"placeActionType": "APPOINTMENT", "uri": "https://book.example.com", "isPreferred": True}
            ],
            enabled_site_ids=[4, 5, 6],
        )
        assert result.success is True
        sent = m.last_request.json()["input"]
        assert sent["name"] == "Acme Dental"
        assert sent["description"] == VALID_DESCRIPTION
        assert sent["subCategoryId"] == 1432
        assert sent["countryIso"] == "US"
        assert sent["city"] == "New York"
        assert sent["postalCode"] == "10013"
        assert sent["placeActionLinks"][0]["placeActionType"] == "APPOINTMENT"
        assert sent["enabledSiteIds"] == [4, 5, 6]
        assert "storeId" not in sent
        assert "hideAddress" not in sent


def test_locations_add_short_description_fails_before_http(client):
    with requests_mock.Mocker() as m:
        m.post("https://listingsapi.com/api/v4/locations", json={})
        with pytest.raises(ValidationError) as exc:
            client.locations.add(
                name="Acme Dental",
                description="Too short.",
                sub_category_id=1432,
                country_iso="US",
                city="New York",
            )
        assert "200 characters" in str(exc.value)
        assert m.call_count == 0


def test_locations_add_missing_city_fails(client):
    with pytest.raises(ValidationError) as exc:
        client.locations.add(
            name="Acme Dental",
            description=VALID_DESCRIPTION,
            sub_category_id=1432,
            country_iso="US",
        )
    assert "city" in str(exc.value)


def test_locations_add_hide_address_allows_missing_city(client):
    response = {"data": {"createLocation": {"success": True, "location": {"id": "x"}, "errors": []}}}
    with requests_mock.Mocker() as m:
        m.post("https://listingsapi.com/api/v4/locations", json=response)
        result = client.locations.add(
            name="Acme Mobile Detailing",
            description=VALID_DESCRIPTION,
            sub_category_id=77,
            country_iso="US",
            hide_address=True,
            service_area={"businessType": "CUSTOMER_LOCATION_ONLY", "regionCode": "US"},
        )
        assert result.success is True
        sent = m.last_request.json()["input"]
        assert sent["hideAddress"] is True
        assert "city" not in sent


def test_locations_add_collects_all_problems(client):
    with pytest.raises(ValidationError) as exc:
        client.locations.add(name="A", description="short", sub_category_id=0, country_iso="")
    msg = str(exc.value)
    assert "name" in msg and "description" in msg and "sub_category_id" in msg and "country_iso" in msg


def test_locations_add_additional_fields_merge(client):
    response = {"data": {"createLocation": {"success": True, "location": {"id": "x"}, "errors": []}}}
    with requests_mock.Mocker() as m:
        m.post("https://listingsapi.com/api/v4/locations", json=response)
        client.locations.add(
            name="Acme Dental",
            description=VALID_DESCRIPTION,
            sub_category_id=1432,
            country_iso="US",
            city="New York",
            additional_fields={"tags": ["brand:acme"], "yearOfIncorporation": 1999},
        )
        sent = m.last_request.json()["input"]
        assert sent["tags"] == ["brand:acme"]
        assert sent["yearOfIncorporation"] == 1999


# --- Payload-level error handling (HTTP 200 bodies with errors) ---

def test_top_level_errors_on_200_raise_authentication_error(client):
    body = {"errors": [{"message": "Invalid Token", "context": {}, "code": "SY90005"}]}
    with requests_mock.Mocker() as m:
        m.get("https://listingsapi.com/api/v4/locations", json=body, status_code=200)
        with pytest.raises(AuthenticationError) as exc:
            client.locations.list()
        assert exc.value.code == "SY90005"
        assert exc.value.status_code == 200
        assert exc.value.errors[0]["message"] == "Invalid Token"


def test_top_level_permission_error_code(client):
    body = {"errors": [{"message": "Forbidden", "context": {}, "code": "SY90003"}]}
    with requests_mock.Mocker() as m:
        m.get("https://listingsapi.com/api/v4/locations", json=body)
        with pytest.raises(PermissionDeniedError):
            client.locations.list()


def test_mutation_envelope_errors_raise_validation_error(client):
    body = {
        "data": {
            "createLocation": {
                "success": False,
                "location": None,
                "errors": [
                    {"code": "SY10005", "message": "Description must be at least 200 characters"}
                ],
            }
        }
    }
    with requests_mock.Mocker() as m:
        m.post("https://listingsapi.com/api/v4/locations", json=body)
        with pytest.raises(ValidationError) as exc:
            client.locations.create({"name": "Acme"})
        assert exc.value.code == "SY10005"
        assert "200 characters" in str(exc.value)


def test_mutation_success_false_without_errors_raises(client):
    body = {"data": {"archiveLocations": {"success": False, "errors": None}}}
    with requests_mock.Mocker() as m:
        m.post("https://listingsapi.com/api/v4/locations/archive", json=body)
        with pytest.raises(ValidationError):
            client.locations.archive([16808])


def test_mutation_string_errors_are_normalized(client):
    body = {"data": {"createLocation": {"success": False, "errors": ["storeId already taken"]}}}
    with requests_mock.Mocker() as m:
        m.post("https://listingsapi.com/api/v4/locations", json=body)
        with pytest.raises(ValidationError) as exc:
            client.locations.create({"name": "Acme"})
        assert exc.value.errors[0]["message"] == "storeId already taken"
        assert exc.value.code is None


def test_successful_mutation_unaffected_by_envelope_check(client):
    body = {"data": {"createLocation": {"success": True, "location": {"id": "x"}, "errors": []}}}
    with requests_mock.Mocker() as m:
        m.post("https://listingsapi.com/api/v4/locations", json=body)
        result = client.locations.create({"name": "Acme"})
        assert result.success is True

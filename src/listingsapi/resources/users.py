"""Users resource — client.users.*"""

from __future__ import annotations

import json
from typing import Any

from listingsapi._types import APIObject
from listingsapi._utils import encode_location_id
from listingsapi.resources._base import APIResource


class Users(APIResource):
    """Manage users, roles, and access.

    Example:
        users = client.users.list()
        client.users.create(email="j@example.com", role_id="...", first_name="Jane")
    """

    def list(self) -> list[APIObject]:
        """Get all users in the account."""
        data = self._get("users")
        items = data.get("data", {}).get("users") or data.get("users") or []
        return [APIObject(item) for item in items]

    def list_by_ids(self, user_ids: list[str]) -> list[APIObject]:
        """Get users by a list of IDs."""
        if not user_ids:
            return []
        data = self._get("users-by-ids", {"userIds": json.dumps(user_ids)})
        items = data.get("data", {}).get("usersByIds") or []
        return [APIObject(item) for item in items]

    def create(
        self,
        email: str,
        role_id: str,
        first_name: str,
        *,
        last_name: str | None = None,
        direct_customer: bool | None = None,
        **extra: Any,
    ) -> APIObject:
        """Create a user with the given role."""
        payload: dict[str, Any] = {"email": email, "roleId": role_id, "firstName": first_name}
        if last_name is not None:
            payload["lastName"] = last_name
        if direct_customer is not None:
            payload["directCustomer"] = direct_customer
        payload.update(extra)
        data = self._post("users/create", {"input": payload})
        return APIObject(data.get("data", {}).get("addUser") or {})

    def update(
        self,
        user_id: str,
        *,
        email: str | None = None,
        role_id: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
        archived: bool | None = None,
        direct_customer: bool | None = None,
        **extra: Any,
    ) -> APIObject:
        """Update a user. Pass only the fields to change."""
        payload: dict[str, Any] = {"id": user_id}
        if email is not None:
            payload["email"] = email
        if role_id is not None:
            payload["roleId"] = role_id
        if first_name is not None:
            payload["firstName"] = first_name
        if last_name is not None:
            payload["lastName"] = last_name
        if phone is not None:
            payload["phone"] = phone
        if archived is not None:
            payload["archived"] = archived
        if direct_customer is not None:
            payload["directCustomer"] = direct_customer
        payload.update(extra)
        data = self._post("users/update", {"input": payload})
        return APIObject(data.get("data", {}).get("updateUser") or {})

    def roles(self) -> list[APIObject]:
        """Get all roles in the account."""
        data = self._get("roles")
        items = data.get("data", {}).get("fetchAccountRoles") or []
        return [APIObject(item) for item in items]

    def resources(self, user_id: str) -> list[APIObject]:
        """Get resources assigned to a user."""
        data = self._get(f"users/{user_id}/resources")
        items = data.get("data", {}).get("listUserResources") or []
        return [APIObject(item) for item in items]

    def add_locations(self, user_id: str, location_ids: list[str | int]) -> APIObject:
        """Assign locations to a user."""
        encoded = [encode_location_id(lid) for lid in location_ids]
        data = self._post("users/locations/add", {"input": {"userId": user_id, "locationIds": encoded}})
        return APIObject(data.get("data", {}).get("addLocationsForUser") or {})

    def remove_locations(self, user_id: str, location_ids: list[str | int]) -> APIObject:
        """Remove location assignments from a user."""
        encoded = [encode_location_id(lid) for lid in location_ids]
        data = self._post("users/locations/remove", {"input": {"userId": user_id, "locationIds": encoded}})
        return APIObject(data.get("data", {}).get("removeLocationsForUser") or {})

    def add_folders(self, user_id: str, folder_ids: list[str]) -> APIObject:
        """Assign folders to a user."""
        data = self._post("users/folders/add", {"input": {"userId": user_id, "folderIds": folder_ids}})
        return APIObject(data.get("data", {}).get("addFoldersForUser") or {})

    def remove_folders(self, user_id: str, folder_ids: list[str]) -> APIObject:
        """Remove folder assignments from a user."""
        data = self._post("users/folders/remove", {"input": {"userId": user_id, "folderIds": folder_ids}})
        return APIObject(data.get("data", {}).get("removeFoldersForUser") or {})

    def add_user_and_folder(self, input: dict[str, Any]) -> APIObject:
        """Create a user and folder, then assign the folder to the user in one call."""
        data = self._post("users/add_user_and_folder", {"input": input})
        return APIObject(data.get("data", {}).get("addUserAndFolder") or {})

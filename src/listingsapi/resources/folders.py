"""Folders resource — client.folders.*"""

from __future__ import annotations

from typing import Any

from listingsapi._types import APIObject
from listingsapi._utils import encode_location_id
from listingsapi.resources._base import APIResource


class Folders(APIResource):
    """Manage folders for organizing locations.

    Example:
        folders = client.folders.list()
        client.folders.create("franchise", parent_folder_name="all_franchise")
    """

    def list(self) -> list[APIObject]:
        """Get all folders as a flat list."""
        data = self._get("folders/flat")
        items = data.get("data", {}).get("getUserFolders") or []
        return [APIObject(item) for item in items]

    def tree(self) -> list[APIObject]:
        """Get all folders as a nested tree structure."""
        data = self._get("folders/tree")
        items = data.get("data", {}).get("getFolderTree") or []
        return [APIObject(item) for item in items]

    def details(self, *, folder_id: str | None = None, folder_name: str | None = None) -> APIObject:
        """Get details for a specific folder."""
        if not folder_id and not folder_name:
            raise ValueError("Provide either folder_id or folder_name")
        params: dict[str, str] = {}
        if folder_id:
            params["folderId"] = folder_id
        if folder_name:
            params["folderName"] = folder_name
        data = self._get("folder-details", params)
        return APIObject(data.get("data", {}).get("getFolderDetails") or {})

    def create(
        self, name: str, *, parent_folder: str | None = None, parent_folder_name: str | None = None
    ) -> APIObject:
        """Create a folder. Optionally nest under a parent."""
        payload: dict[str, Any] = {"name": name}
        if parent_folder is not None:
            payload["parentFolder"] = parent_folder
        if parent_folder_name is not None:
            payload["parentFolderName"] = parent_folder_name
        data = self._post("folders/create", {"input": payload})
        return APIObject(data.get("data", {}).get("createFolder") or {})

    def rename(self, old_name: str, new_name: str) -> APIObject:
        """Rename a folder."""
        data = self._post("locations/folders/rename", {"input": {"oldName": old_name, "name": new_name}})
        return APIObject(data.get("data", {}).get("renameFolder") or {})

    def delete(self, name: str) -> APIObject:
        """Delete a folder by name. Locations in the folder are not deleted."""
        data = self._post("folders/delete", {"input": {"name": name}})
        return APIObject(data.get("data", {}).get("deleteFolder") or {})

    def add_locations(self, folder_name: str, location_ids: list[str | int]) -> APIObject:
        """Add locations to a folder (created if it doesn't exist)."""
        encoded = [encode_location_id(lid) for lid in location_ids]
        data = self._post("locations/folders", {"input": {"name": folder_name, "locationIds": encoded}})
        return APIObject(data.get("data", {}).get("addLocationsToFolder") or {})

    def remove_locations(self, location_ids: list[str | int]) -> APIObject:
        """Remove locations from their current folder."""
        encoded = [encode_location_id(lid) for lid in location_ids]
        data = self._post("locations/folders/remove", {"input": {"locationIds": encoded}})
        return APIObject(data.get("data", {}).get("deleteLocationsFromFolder") or {})

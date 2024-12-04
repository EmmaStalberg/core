from typing import Any

import aiohttp

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


class OpenStreetMapError(Exception):
    """General OpenStreetMap error."""


class OpenStreetMapAuthError(OpenStreetMapError):
    """Raised when authentication fails."""


class OpenStreetMapClient:
    """Class for Open Street Map client."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the OpenStreetMap client."""
        self._session = session
        self._base_url = "https://api.openstreetmap.org"  # needed???

    async def test_connection(self) -> None:
        """Test connection to the OpenStreetMap API."""
        async with self._session.get(f"{self._base_url}/status") as response:
            if response.status != 200:
                raise OpenStreetMapError("Failed to connect to OpenStreetMap")

    async def search_address(self, query: str) -> list[dict[str, Any]]:
        """Search for addresses using the OpenStreetMap API.

        Args:
            query (str): The address to search for.

        Returns:
            list[dict[str, Any]]: A list of search results.

        Raises:
            OpenStreetMapError: If the API request fails.

        """
        params = {"q": query, "format": "json"}
        try:
            async with self._session.get(NOMINATIM_URL, params=params) as response:
                if response.status != 200:
                    raise OpenStreetMapError(f"API request failed: {response.status}")
                return await response.json()
        except aiohttp.ClientError as err:
            raise OpenStreetMapError(f"API request error: {err}") from err

    async def get_address_coordinates(self, query: str) -> dict[str, Any]:
        """Get coordinates for a given address query.

        Args:
            query (str): The address to search for.

        Returns:
            dict[str, Any]: Coordinates or error message.

        """
        results = await self.search_address(query)
        if not results:
            return {"error": "No results found"}

        try:
            latitude = float(results[0]["lat"])
            longitude = float(results[0]["lon"])
            return {"latitude": latitude, "longitude": longitude}
        except (IndexError, KeyError, ValueError):
            return {"error": "Invalid response from API"}

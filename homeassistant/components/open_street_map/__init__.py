"""The OpenStreetMap integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import _LOGGER, HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv  # , device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

# from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .osm_client import OpenStreetMapAuthError, OpenStreetMapClient, OpenStreetMapError

# from .search import (
#     get_address_coordinates,
#     get_Coordinates,
#     # AddressSearchView,
#     search_address,  # imports search function from search.py
# )

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# TODO List the platforms that you want to support. # pylint: disable=fixme
# For your initial PR, limit it to 1 platform.
# PLATFORMS: list[Platform] = [Platform.LIGHT]
PLATFORMS: list[Platform] = []

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

# TODO Create ConfigEntry type alias with API object
# TODO Rename type alias and update all entry annotations
# type OpenStreetMapConfigEntry = ConfigEntry[MyApi]  # noqa: F821


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the OpenStreetMap integration."""
    # Initialize the domain-specific data
    hass.data[DOMAIN] = {}

    # Optionally, set a state or initialize any service here
    hass.states.async_set(f"{DOMAIN}.integration", "loaded")

    _setup_all_services(hass)

    return True


# TODO uncomment this code and fix the todos. Note! Need to uncomment the imports as well
# TODO Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OpenStreetMap from a config entry."""

    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access
    # entry.runtime_data = MyAPI(...)

    # Home Assistant's shared session
    session = async_get_clientsession(hass)

    # The client handles API communication, interact with OSM
    client = OpenStreetMapClient(session)

    # validating the API connection
    try:
        await client.test_connection()
    except OpenStreetMapAuthError as error:
        raise ConfigEntryAuthFailed("Authentication failed") from error
    except OpenStreetMapError as error:
        raise ConfigEntryNotReady("Unable to connect to OpenStreetMap") from error

    # not sure if this is needed??
    # # The device need to be registered in HA. The device represents the services
    # # maybe change api key to something else...
    # if not entry.unique_id:
    #     hass.config_entries.async_update_entry(entry, unique_id=entry.data["api_key"])

    # device_registry = dr.async_get(hass)
    # device_registry.async_get_or_create(
    #     config_entry_id=entry.entry_id,
    #     identifiers={(DOMAIN, entry.unique_id)},
    #     entry_type=DeviceEntryType.SERVICE,
    #     manufacturer="OpenStreetMap",
    #     name="OpenStreetMap API",
    # )

    # hass.data.setdefault(DOMAIN, {})
    # hass.data[DOMAIN][entry.entry_id] = client

    # The integration should be able to reach the client so we store it
    # or just = client? maybe same???
    # hass.data[DOMAIN][entry.entry_id] = client ?????
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "client": client,
    }

    # The entry should be forwarded to platforms
    # Maybe map is a platform that needs to be added???
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Clean up data
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok


def _setup_all_services(hass: HomeAssistant) -> None:
    async def async_handle_search(
        hass: HomeAssistant, call: ServiceCall
    ) -> dict[str, str]:
        """Handle a service call to search for an address or coordinates with OpenStreetMap.

        Fetches results based on the query from the service call and updates the last search state in Home Assistant.

        Args:
            hass (HomeAssistant): The Home Assistant instance.
            call (ServiceCall): The service call object containing the data payload.

        Returns:
            dict[str, str]: A dictionary containing the search results if successful, or an error message.

        """
        client = hass.data[DOMAIN][call.data["config_entry_id"]]
        query = call.data.get("query")
        if not query:
            error_message = {"error": "Query is missing or empty"}
            hass.states.async_set(
                f"{DOMAIN}.last_search", f"Error: {error_message['error']}"
            )
            return error_message

        results = await client.search_address(query)

        # not sure if needed???
        if "error" in results:
            hass.states.async_set(f"{DOMAIN}.last_search", f"Error: {results['error']}")

        ## NOT SURE IF THIS IS NEEDED ??
        # hass.bus.async_fire(
        #     f"{DOMAIN}_event",
        #     {"type": "search", "query": query, "results": results},
        # )

        return results

    # Service handler for getting coordinates from an address
    async def async_handle_get_address_coordinates(
        hass: HomeAssistant, call: ServiceCall
    ) -> dict[str, str]:
        """Handle the service call to get coordinates from an address query.

        Args:
            hass (HomeAssistant): The Home Assistant instance.
            call (ServiceCall): The service call object containing the data payload.

        Returns:
            dict[str, str]: A dictionary containing the search results if json_data, or an error message.

        """
        client = hass.data[DOMAIN][call.data["config_entry_id"]]
        query = call.data.get("query")
        if not query:
            error_message = {"error": "Query is missing or empty"}
            hass.states.async_set(
                f"{DOMAIN}.last_search", f"Error: {error_message['error']}"
            )
            return error_message

        coordinates = await client.get_address_coordinates(query)
        hass.states.async_set(DOMAIN, coordinates)

        # not sure if needed???
        if "error" in coordinates:
            _LOGGER.error(f"Error fetching coordinates: {coordinates['error']}")
            hass.states.async_set(
                f"{DOMAIN}.last_search", f"Error: {coordinates['error']}"
            )

        ## NOT SURE IF THIS IS NEEDED ??
        # hass.bus.async_fire(
        #     f"{DOMAIN}_event",
        #     {"type": "get_address_coordinates", "query": query, "coordinates": coordinates},
        # )

        return coordinates

    # Register the search service
    hass.services.async_register(
        DOMAIN,
        "search",
        async_handle_search,
        schema=vol.Schema({vol.Required("query"): str}),
        supports_response=SupportsResponse.ONLY,
    )

    # Register the get_address_coordinates service
    hass.services.async_register(
        DOMAIN,
        "get_address_coordinates",
        async_handle_get_address_coordinates,
        schema=vol.Schema({vol.Required("query"): str}),
        # schema=cv.make_entity_service_schema({vol.Required("query"): str}),
        supports_response=SupportsResponse.ONLY,
    )

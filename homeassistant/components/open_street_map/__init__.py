"""The OpenStreetMap integration."""

from __future__ import annotations

# from collections.abc import Callable, Iterable
# import dataclasses
# import datetime
from http import HTTPStatus

# from itertools import groupby
import logging

# import re
# from typing import Any, Final, cast, final
from aiohttp import web

# from dateutil.rrule import rrulestr
import voluptuous as vol

from homeassistant.components import frontend, http, websocket_api
from homeassistant.components.websocket_api import (
    ERR_NOT_FOUND,
    # ERR_NOT_SUPPORTED,
    # ActiveConnection,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import (
    # CALLBACK_TYPE,
    HomeAssistant,
    # ServiceCall,
    # ServiceResponse,
    SupportsResponse,
    # callback,
)

# from homeassistant.exceptions import (
#     ConfigEntryAuthFailed,
#     ConfigEntryNotReady,
#     HomeAssistantError,
# )
from homeassistant.helpers import config_validation as cv

# from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.typing import ConfigType

# from homeassistant.util.json import JsonValueType
from .const import DOMAIN, DOMAIN_DATA

# from .osm_client import OpenStreetMapAuthError, OpenStreetMapClient, OpenStreetMapError
from .search import get_address_coordinates  # , search_address

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

_LOGGER = logging.getLogger(__name__)
ENTITY_ID_FORMAT = DOMAIN + ".{}"
PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA
PLATFORM_SCHEMA_BASE = cv.PLATFORM_SCHEMA_BASE
PLATFORMS: list[Platform] = []
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

SEARCH_SERVICE = "search"
GET_ADDRESS_COORDINATES_SERVICE = "get_address_coordinates"
SEARCH_SCHEMA = vol.Schema({vol.Required("query"): str})
GET_ADDRESS_COORDINATES_SCHEMA = vol.Schema({vol.Required("query"): str})

WEBSOCKET_EVENT_SCHEMA = vol.Schema({vol.Required("query"): str})  ## ???


def _empty_as_none(value: str | None) -> str | None:
    """Convert any empty string values to None."""
    return value or None


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration."""
    component = hass.data[DOMAIN_DATA] = EntityComponent[OpenStreetMapEntity](
        _LOGGER, DOMAIN, hass
    )

    hass.http.register_view(OpenStreetMapView(component))
    frontend.async_register_built_in_panel(
        hass, DOMAIN, DOMAIN, "hass:OpenStreetMap"
    )  # ??? last parameter

    # ??? hass might be open_street_map/methodname
    websocket_api.async_register_command(hass, async_handle_get_address_coordinates)

    component.async_register_entity_service(
        GET_ADDRESS_COORDINATES_SERVICE,
        GET_ADDRESS_COORDINATES_SCHEMA,
        async_handle_get_address_coordinates,
        supports_response=SupportsResponse.ONLY,
    )
    await component.async_setup(config)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry."""
    return await hass.data[DOMAIN_DATA].async_setup_entry(entry)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.data[DOMAIN_DATA].async_unload_entry(entry)


# @dataclasses.dataclass
# class CalendarEvent
# _event_dict_factory osv
#


class OpenStreetMapEntity(Entity):
    """Base class for the openstreetmap entities."""

    ## not sure what is going in here ???
    def __init__(self, query: str) -> None:
        """Initialize osm entity."""
        self._query = query
        self._latestSearchedCoordinates = None
        # may want to change this to the entire search results and also below in state

    @property
    def _unique_id(self) -> str:
        return f"{DOMAIN}_{self._query}"

    @property
    def coordsFromLatestSearch(self) -> str | None:
        """Returns coordinates from latest search."""
        return self._latestSearchedCoordinates

    # this below might be a @callback async_write_ha_state instead??????!!!
    # maybe not like this???
    # async def async_update(self) -> None:
    #     """Fetch the latest data from the OpenStreetMap API."""
    #     # Example of fetching coordinates (pseudo-code)
    #     try:
    #         self._coordinates = await self._fetch_coordinates(self._query)
    #     except Exception as err:
    #         self._coordinates = None
    #         self.hass.logger.error(f"Failed to update {self.name}: {err}")

    # async def _fetch_coordinates(self, query: str) -> str:
    #     """Make an API call to fetch coordinates."""
    #     # Add logic for calling the OpenStreetMap API ???
    #     return f"Coordinates for {query}"


class OpenStreetMapView(http.HomeAssistantView):
    """View to retrieve content for OpenStreetMap."""

    url = NOMINATIM_URL  # i guess ???
    # name = ???

    def __init__(self, component: EntityComponent[OpenStreetMapEntity]) -> None:
        """Initialize the OpenStreetMap view."""
        self.component = component

    async def get(self, request: web.Request, entity_id: str) -> web.Response:
        """Return address coordinates."""
        if not (entity := self.component.get_entity(entity_id)) or not isinstance(
            entity, OpenStreetMapEntity
        ):
            return web.Response(status=HTTPStatus.BAD_REQUEST)

        # needed???
        # hass = request.app[http.KEY_HASS]

        # eller ska jag göra states nånting här? rad 714 gr1

        lat = request.query.get("lat")
        lon = request.query.get("lon")

        if lat is None or lon is None:
            return web.Response(status=HTTPStatus.BAD_REQUEST)
        # beh ev köra try except op await entity.async_get_address_coordinates
        # med denna request.app[http.KEY_HASS] och lat och lon

        return self.json([{"lat": lat, "lon": lon}])


@websocket_api.websocket_command(
    {
        vol.Required("type"): "open_street_map/async_get_address_coordinates",
        vol.Required("entity_id"): cv.entity_id,
        "event": WEBSOCKET_EVENT_SCHEMA,
    }
)
@websocket_api.async_response
async def async_handle_get_address_coordinates(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg
):
    """Handle getting address coordinates."""
    # if not (entity := hass.data[DOMAIN_DATA].get_entity(msg["entity_id"])):
    #     connection.send_error(msg["id"], ERR_NOT_FOUND, "Entity not found")
    #     return None

    # ska den kalla på entity.nån metod???
    query = msg.get("query")
    if not query:
        _LOGGER.error("No query provided")
        return {"error": "No query provided"}

    coordinates = get_address_coordinates(query)

    connection.send_result(msg["id"], {"results": coordinates})
    # ??? return None tror jag inte
    return coordinates


###################################################################
###################################################################
###################################################################
###################################################################
###################################################################
###################################################################
###################################################################
###################################################################


# async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
#     """Set up the OpenStreetMap integration."""
#     # Initialize the domain-specific data
#     hass.data[DOMAIN] = {}

#     # Optionally, set a state or initialize any service here
#     hass.states.async_set(f"{DOMAIN}.integration", "loaded")

#     _setup_all_services(hass)

#     return True


# # TODO uncomment this code and fix the todos. Note! Need to uncomment the imports as well
# # TODO Update entry annotation
# async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
#     """Set up OpenStreetMap from a config entry."""

#     # TODO 1. Create API instance
#     # TODO 2. Validate the API connection (and authentication)
#     # TODO 3. Store an API object for your platforms to access
#     # entry.runtime_data = MyAPI(...)

#     # Home Assistant's shared session
#     session = async_get_clientsession(hass)

#     # The client handles API communication, interact with OSM
#     client = OpenStreetMapClient(session)

#     # validating the API connection
#     try:
#         await client.test_connection()
#     except OpenStreetMapAuthError as error:
#         raise ConfigEntryAuthFailed("Authentication failed") from error
#     except OpenStreetMapError as error:
#         raise ConfigEntryNotReady("Unable to connect to OpenStreetMap") from error

#     # not sure if this is needed??
#     # # The device need to be registered in HA. The device represents the services
#     # # maybe change api key to something else...
#     # if not entry.unique_id:
#     #     hass.config_entries.async_update_entry(entry, unique_id=entry.data["api_key"])

#     # device_registry = dr.async_get(hass)
#     # device_registry.async_get_or_create(
#     #     config_entry_id=entry.entry_id,
#     #     identifiers={(DOMAIN, entry.unique_id)},
#     #     entry_type=DeviceEntryType.SERVICE,
#     #     manufacturer="OpenStreetMap",
#     #     name="OpenStreetMap API",
#     # )

#     # hass.data.setdefault(DOMAIN, {})
#     # hass.data[DOMAIN][entry.entry_id] = client

#     # The integration should be able to reach the client so we store it
#     # or just = client? maybe same???
#     # hass.data[DOMAIN][entry.entry_id] = client ?????
#     hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
#         "client": client,
#     }

#     # The entry should be forwarded to platforms
#     # Maybe map is a platform that needs to be added???
#     await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

#     return True


# async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
#     """Unload a config entry."""
#     # Unload platforms
#     unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

#     # Clean up data
#     if unload_ok:
#         hass.data[DOMAIN].pop(entry.entry_id, None)

#     return unload_ok


# def _setup_all_services(hass: HomeAssistant) -> None:
#     async def async_handle_search(
#         hass: HomeAssistant, call: ServiceCall
#     ) -> dict[str, str]:
#         """Handle a service call to search for an address or coordinates with OpenStreetMap.

#         Fetches results based on the query from the service call and updates the last search state in Home Assistant.

#         Args:
#             hass (HomeAssistant): The Home Assistant instance.
#             call (ServiceCall): The service call object containing the data payload.

#         Returns:
#             dict[str, str]: A dictionary containing the search results if successful, or an error message.

#         """
#         client = hass.data[DOMAIN][call.data["config_entry_id"]]
#         query = call.data.get("query")
#         if not query:
#             error_message = {"error": "Query is missing or empty"}
#             hass.states.async_set(
#                 f"{DOMAIN}.last_search", f"Error: {error_message['error']}"
#             )
#             return error_message

#         results = await client.search_address(query)

#         # not sure if needed???
#         if "error" in results:
#             hass.states.async_set(f"{DOMAIN}.last_search", f"Error: {results['error']}")

#         ## NOT SURE IF THIS IS NEEDED ??
#         # hass.bus.async_fire(
#         #     f"{DOMAIN}_event",
#         #     {"type": "search", "query": query, "results": results},
#         # )

#         return results

#     # Service handler for getting coordinates from an address
#     async def async_handle_get_address_coordinates(
#         hass: HomeAssistant, call: ServiceCall
#     ) -> dict[str, str]:
#         """Handle the service call to get coordinates from an address query.

#         Args:
#             hass (HomeAssistant): The Home Assistant instance.
#             call (ServiceCall): The service call object containing the data payload.

#         Returns:
#             dict[str, str]: A dictionary containing the search results if json_data, or an error message.

#         """
#         client = hass.data[DOMAIN][call.data["config_entry_id"]]
#         query = call.data.get("query")
#         if not query:
#             error_message = {"error": "Query is missing or empty"}
#             hass.states.async_set(
#                 f"{DOMAIN}.last_search", f"Error: {error_message['error']}"
#             )
#             return error_message

#         coordinates = await client.get_address_coordinates(query)
#         hass.states.async_set(DOMAIN, coordinates)

#         # not sure if needed???
#         if "error" in coordinates:
#             _LOGGER.error(f"Error fetching coordinates: {coordinates['error']}")
#             hass.states.async_set(
#                 f"{DOMAIN}.last_search", f"Error: {coordinates['error']}"
#             )

#         ## NOT SURE IF THIS IS NEEDED ??
#         # hass.bus.async_fire(
#         #     f"{DOMAIN}_event",
#         #     {"type": "get_address_coordinates", "query": query, "coordinates": coordinates},
#         # )

#         return coordinates

#     # Register the search service
#     hass.services.async_register(
#         DOMAIN,
#         "search",
#         async_handle_search,
#         schema=vol.Schema({vol.Required("query"): str}),
#         supports_response=SupportsResponse.ONLY,
#     )

#     # Register the get_address_coordinates service
#     hass.services.async_register(
#         DOMAIN,
#         "get_address_coordinates",
#         async_handle_get_address_coordinates,
#         schema=vol.Schema({vol.Required("query"): str}),
#         # schema=cv.make_entity_service_schema({vol.Required("query"): str}),
#         supports_response=SupportsResponse.ONLY,
#     )

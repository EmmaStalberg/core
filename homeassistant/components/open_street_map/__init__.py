"""The OpenStreetMap integration."""

from __future__ import annotations

from http import HTTPStatus
import logging
from typing import Any

from aiohttp import web
import voluptuous as vol

from homeassistant.components import frontend, http, websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, SupportsResponse
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, DOMAIN_DATA, OpenStreetMapEntityFeature
from .search import get_address_coordinates

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

_LOGGER = logging.getLogger(__name__)
ENTITY_ID_FORMAT = DOMAIN + ".{}"

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

SEARCH_SERVICE = "search"
GET_ADDRESS_COORDINATES_SERVICE = "get_address_coordinates"
SEARCH_SCHEMA = vol.Schema({vol.Required("query"): str})
GET_ADDRESS_COORDINATES_SCHEMA = vol.Schema({vol.Required("query"): str})


def _empty_as_none(value: str | None) -> str | None:
    """Convert any empty string values to None."""
    return value or None


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the OpenStreetMap integration for Home Assistant.

    This function initializes the integration by creating the required components,
    registering HTTP views, frontend panels, WebSocket commands, and custom entity services.

    Args:
        hass (HomeAssistant): The Home Assistant instance. It provides access
            to core Home Assistant features such as HTTP, WebSocket APIs,
            and entity management.
        config (ConfigType): A configuration dictionary for the integration,
            as defined by Home Assistant.

    Returns:
        bool: True if the integration is successfully set up; otherwise, False.

    """
    component = hass.data[DOMAIN_DATA] = EntityComponent[OpenStreetMapEntity](
        _LOGGER, DOMAIN, hass
    )

    hass.http.register_view(OpenStreetMapView(component))

    frontend.async_register_built_in_panel(
        hass,
        component_name="open-street-map",
        sidebar_title="Open Street Map",
        sidebar_icon="mdi:map",
    )

    websocket_api.async_register_command(hass, async_handle_get_address_coordinates)

    component.async_register_entity_service(
        GET_ADDRESS_COORDINATES_SERVICE,
        GET_ADDRESS_COORDINATES_SCHEMA,
        async_handle_get_address_coordinates,
        required_features=[OpenStreetMapEntityFeature.GET_COORDINATES_EVENT],
        supports_response=SupportsResponse.OPTIONAL,
    )
    await component.async_setup(config)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a configuration entry for the OpenStreetMap integration.

    Args:
        hass (HomeAssistant): The Home Assistant instance, providing access to the
            core features and management of integrations.
        entry (ConfigEntry): The configuration entry representing the integration's
            setup data, such as connection details and user preferences.

    Returns:
        bool: True if the configuration entry is successfully set up; otherwise, False.

    """
    return await hass.data[DOMAIN_DATA].async_setup_entry(entry)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a configuration entry for the OpenStreetMap integration.

    Args:
        hass (HomeAssistant): The Home Assistant instance, providing access to the
            core features and management of integrations.
        entry (ConfigEntry): The configuration entry representing the integration's
            setup data that is to be unloaded.

    Returns:
    bool: True if the configuration entry is successfully unloaded; otherwise, False.

    """
    return await hass.data[DOMAIN_DATA].async_unload_entry(entry)


class OpenStreetMapEntity(Entity):
    """Base class for OpenStreetMap entities in Home Assistant.

    Attributes:
        _entity_component_unrecorded_attributes (frozenset): A set of attributes
            that should not be recorded in the state registry.
        _query (str): The search query used to fetch location data.
        _latestSearchedCoordinates (list[float] | None): The latest fetched
            coordinates for the entity.
        _state (str | None): The current state of the entity, typically its coordinates.

    """

    _entity_component_unrecorded_attributes = frozenset({"description", "coordinates"})

    def __init__(self, query: str) -> None:
        """Initialize an OpenStreetMap entity.

        Args:
            query (str): The search query used to retrieve location data
                from the OpenStreetMap API.

        """
        self._query = query
        self._latestSearchedCoordinates: list[float] | None = None
        self._state: str | None = None

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return f"{DOMAIN} - {self._query}"

    @property
    def _unique_id(self) -> str:
        return f"{DOMAIN}_{self._query}"

    @property
    def state(self) -> str | None:
        """Return the state (coordinates) of the entity."""
        return self._state

    @property
    def state_attributes(self) -> dict[str, Any] | None:
        """Return the attributes for the entity (e.g., coordinates, description)."""
        if self._latestSearchedCoordinates is None:
            return None
        return {
            "coordinates": self._latestSearchedCoordinates,
            "query": self._query,
        }

    @property
    def coordsFromLatestSearch(self) -> list[float] | None:
        """Returns coordinates from latest search."""
        return self._latestSearchedCoordinates

    async def async_update(self) -> None:
        """Fetch the latest data from OpenStreetMap and update the entity's state."""
        coordinates = await self.fetch_coordinates(self._query)
        if coordinates:
            self._latestSearchedCoordinates = coordinates
            self._state = f"{coordinates[0]},{coordinates[1]}"

    async def fetch_coordinates(self, query: str) -> list[float] | None:
        """Fetch coordinates for the given query using the OpenStreetMap API."""
        result = get_address_coordinates(query)  # Call the existing function you have
        # if isinstance(result, dict) and "error" in result:
        if "error" in result:
            return None
        return result

    async def async_added_to_hass(self) -> None:
        """Run when the entity is added to Home Assistant."""
        await self.async_update()

    async def async_will_remove_from_hass(self) -> None:
        """Run when the entity is removed from Home Assistant."""


class OpenStreetMapView(http.HomeAssistantView):
    """View to retrieve content for OpenStreetMap.

    Attributes:
        url (str): The URL path for the OpenStreetMap API endpoint.
        name (str): The name identifier for the API endpoint.
        component (EntityComponent[OpenStreetMapEntity]): The entity component that
            manages OpenStreetMap entities in Home Assistant.

    """

    url = "/api/open_street_map"
    name = "api:openstreetmap"

    def __init__(self, component: EntityComponent[OpenStreetMapEntity]) -> None:
        """Initialize the OpenStreetMap view."""
        self.component = component

    async def get(self, request: web.Request, entity_id: str) -> web.Response:
        """Return address coordinates."""
        if not (entity := self.component.get_entity(entity_id)) or not isinstance(
            entity, OpenStreetMapEntity
        ):
            return web.Response(status=HTTPStatus.BAD_REQUEST)

        lat = request.query.get("lat")
        lon = request.query.get("lon")

        if lat is None or lon is None:
            return web.Response(status=HTTPStatus.BAD_REQUEST)

        return self.json([{"lat": lat, "lon": lon}])


@websocket_api.websocket_command(
    {
        vol.Required("type"): "open_street_map/async_get_address_coordinates",
        vol.Required("entry_id"): str,
        vol.Required("query"): str,
    }
)
@websocket_api.async_response
async def async_handle_get_address_coordinates(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg
):
    """Handle getting address coordinates."""
    config = hass.config_entries.async_get_entry(msg["entry_id"])
    if config is None:
        return

    query = msg.get("query")
    if not query:
        _LOGGER.error("No query provided")
        return

    coordinates = get_address_coordinates(query)
    _LOGGER.info("Coordinates fetched in init 269")
    if not coordinates:
        connection.send_error(
            msg["id"], websocket_api.ERR_NOT_FOUND, "Coordinates not found"
        )
        return

    hass.config_entries.async_update_entry(
        config, data={**config.data, "coordinates": coordinates}
    )

    connection.send_result(msg["id"], config)


# TODO uncomment this code and fix the todos. Note! Need to uncomment the imports as well # pylint: disable=fixme
# TODO Update entry annotation # pylint: disable=fixme
# async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
#     """Set up OpenStreetMap from a config entry."""

#     # TODO 1. Create API instance # pylint: disable=fixme
#     # TODO 2. Validate the API connection (and authentication) # pylint: disable=fixme
#     # TODO 3. Store an API object for your platforms to access # pylint: disable=fixme
#     # entry.runtime_data = MyAPI(...)

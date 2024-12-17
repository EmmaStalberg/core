"""The OpenStreetMap integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.const import Platform
from homeassistant.core import _LOGGER, HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .search import (
    get_address_coordinates,
    get_coordinates,
    search_address,
)

PLATFORMS: list[Platform] = []


async def async_setup(hass: HomeAssistant) -> bool:
    """Set up the OpenStreetMap integration."""
    hass.data[DOMAIN] = {}
    hass.states.async_set(f"{DOMAIN}.integration", "loaded")
    register_services(hass)
    return True


def register_services(hass: HomeAssistant) -> None:
    """Register services for the OpenStreetMap integration."""
    hass.services.async_register(
        DOMAIN,
        "search",
        async_handle_search,
        schema=vol.Schema({vol.Required("query"): str}),
    )

    hass.services.async_register(
        DOMAIN,
        "get_coordinates",
        async_handle_get_coordinates,
        schema=cv.make_entity_service_schema({vol.Required("json_data"): cv.Any}),
    )

    hass.services.async_register(
        DOMAIN,
        "get_address_coordinates",
        async_handle_get_address_coordinates,
        schema=vol.Schema({vol.Required("query"): str}),
    )


async def async_handle_search(hass: HomeAssistant, call: ServiceCall) -> dict[str, str]:
    query = call.data.get("query", "")
    if not query:
        return log_and_return_error(hass, "Query is missing or empty", "last_search")

    results = search_address(query)
    if "error" in results:
        return log_and_return_error(hass, results["error"], "last_search")

    hass.bus.async_fire(f"{DOMAIN}_event", {"type": "search", "query": query, "results": results})
    return results


async def async_handle_get_coordinates(hass: HomeAssistant, call: ServiceCall) -> dict[str, str]:
    json_data = call.data.get("json_data")
    if not json_data:
        _LOGGER.error("No JSON data provided")
        return {"error": "No JSON data provided"}

    return get_coordinates(json_data)


async def async_handle_get_address_coordinates(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, str]:
    query = call.data.get("query")
    if not query:
        return log_and_return_error(hass, "No query provided", "get_coordinates")

    coordinates = get_address_coordinates(query)
    if "error" in coordinates:
        return log_and_return_error(hass, coordinates["error"], "get_coordinates")

    hass.bus.async_fire(
        f"{DOMAIN}_event",
        {"type": "get_coordinates", "query": query, "coordinates": coordinates},
    )
    return coordinates


def log_and_return_error(hass: HomeAssistant, error_message: str, state: str) -> dict[str, str]:
    _LOGGER.error(error_message)
    hass.states.async_set(f"{DOMAIN}.{state}", f"Error: {error_message}")
    hass.bus.async_fire(f"{DOMAIN}_event", {"error": error_message})
    return {"error": error_message}

"""Constants for the OpenStreetMap integration."""

from __future__ import annotations

from enum import IntFlag
from typing import TYPE_CHECKING

from homeassistant.util.hass_dict import HassKey

if TYPE_CHECKING:
    from homeassistant.helpers.entity_component import EntityComponent

    from . import OpenStreetMapEntity

# The domain name for the OpenStreetMap integration.
DOMAIN = "open_street_map"
# The domain name for the OpenStreetMap integration.
DOMAIN_DATA: HassKey[EntityComponent[OpenStreetMapEntity]] = HassKey(DOMAIN)


class OpenStreetMapEntityFeature(IntFlag):
    """Supported features of the open street map entity."""

    GET_COORDINATES_EVENT = 1

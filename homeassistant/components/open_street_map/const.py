"""Constants for the OpenStreetMap integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.util.hass_dict import HassKey

if TYPE_CHECKING:
    from homeassistant.helpers.entity_component import EntityComponent

    from . import OpenStreetMapEntity

DOMAIN = "open_street_map"
DOMAIN_DATA: HassKey[EntityComponent[OpenStreetMapEntity]] = HassKey(DOMAIN)

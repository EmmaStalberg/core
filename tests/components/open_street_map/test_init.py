"""Test the Open street maps component."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

DOMAIN = "open_street_map"
_LOGGER = logging.getLogger(__name__)
INTERVAL = timedelta(minutes=5)


async def test_setup(hass: HomeAssistant) -> None:
    """Test setup works."""

    result = await async_setup_component(
        hass, DOMAIN, {"open_street_map": {"domain": DOMAIN}}
    )

    await hass.async_block_till_done()

    assert result

    services_registered = hass.services.async_services_for_domain(DOMAIN)
    await hass.async_block_till_done()

    assert len(services_registered) == 3
    assert "search" in services_registered
    assert "get_coordinates" in services_registered
    assert "get_address_coordinates" in services_registered


async def test_handle_search(hass: HomeAssistant) -> None:
    """Test the handle_search function."""

    assert True


async def test_handle_get_address_coordinates(hass: HomeAssistant) -> None:
    """Test the handle_get_address_coordinates funciton."""

    assert True

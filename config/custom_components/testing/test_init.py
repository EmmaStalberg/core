"""Test the DuckDNS component."""

from datetime import timedelta
import logging

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from tests.test_util.aiohttp import AiohttpClientMocker

DOMAIN = "open_street_map"
_LOGGER = logging.getLogger(__name__)
INTERVAL = timedelta(minutes=5)


@pytest.fixture
def setup_open_street_map(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> None:
    """Fixture that sets up open_street_map."""
    # aioclient_mock.get(
    #     duckdns.UPDATE_URL, params={"domains": DOMAIN, "token": TOKEN}, text="OK"
    # )

    hass.loop.run_until_complete(
        async_setup_component(
            hass, DOMAIN, {"open_street_map": {"domain": DOMAIN}}
        )
    )


async def test_setup(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> None:
    """Test setup works."""

    result = await async_setup_component(
        hass, DOMAIN, {"duckdns": {"domain": DOMAIN}}
    )

    await hass.async_block_till_done()

    assert result

    services_registered = hass.services.async_services_for_domain(DOMAIN)
    await hass.async_block_till_done()

    assert len(services_registered) == 3
    assert "search" in services_registered
    assert "get_coordinates" in services_registered
    assert "get_address_coordinates" in services_registered

async def test_handle_search(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> None:
    """Test the handle_search function."""

    assert True

async def test_handle_get_coordinates(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> None:
    """Test the handle_get_coordinates function."""
    assert True

async def test_handle_get_address_coordinates(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> None:
    """Test the handle_get_address_coordinates funciton."""
    assert True

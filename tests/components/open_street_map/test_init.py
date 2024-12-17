"""Test the Open street maps component."""

from datetime import timedelta
import logging
from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant, ServiceCall
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


async def test_service_call(hass: HomeAssistant) -> None:
    """Test that services are called as expected, and that sent data arrives."""

    service_mock = MagicMock()
    hass.services.async_register(DOMAIN, "search", service_mock)

    await hass.services.async_call(DOMAIN, "search", {"query": "test query"}, blocking=True)

    service_mock.assert_called_once()

    service_call = service_mock.call_args[0][0]
    assert isinstance(service_call, ServiceCall)
    assert service_call.service == "search"
    assert service_call.data == {"query": "test query"}


## TODO tests for handlers. These are not implemented as we do not know why it doesn't work

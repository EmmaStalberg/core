"""Tests for config_flow.py."""
"""Tests for the Open street maps config flow."""

import unittest

from homeassistant.components.open_street_map.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


class TestSearchFunctions(unittest.TestCase):
    """Class for tests regarding the config_flow."""

    async def test_full_user_flow(
        hass: HomeAssistant,
    ) -> None:
        """Test the full user configuration flow."""
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )

        assert result.get("type") is FlowResultType.FORM
        assert result.get("step_id") == "user"

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
        )

        assert result2.get("type") is FlowResultType.CREATE_ENTRY

if __name__ == "__main__":
    unittest.main()

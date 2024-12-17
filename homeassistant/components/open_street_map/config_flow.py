"""Config flow for OpenStreetMap integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class OpenStreetMapConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenStreetMap."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is not None:
            # Directly create an entry as no input is needed
            return self.async_create_entry(
                title="OpenStreetMap",
                data={},
            )

        # Show the configuration form to the user
        return self.async_show_form(step_id="user")

"""Config flow för Göteborgs Energi integration."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class GoteborgEnergiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Hantera config flow för Göteborgs Energi."""
    
    VERSION = 1
    
    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Hantera det initiala steget."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({}),
                description_placeholders={
                    "description": "Denna integration hämtar elpriser för Göteborg från öppna API:er."
                }
            )
        
        # Kontrollera om integration redan är konfigurerad
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        
        return self.async_create_entry(
            title="Göteborgs Energi Elpriser",
            data=user_input,
        )

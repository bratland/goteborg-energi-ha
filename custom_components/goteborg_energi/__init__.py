"""Göteborgs Energi integration för Home Assistant."""
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Sätt upp Göteborgs Energi från en config entry."""
    
    coordinator = GoteborgEnergiDataUpdateCoordinator(hass)
    
    # Försök att hämta initial data, men fortsätt även om det misslyckas
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.warning("Kunde inte hämta initial data vid setup: %s. Integrationen kommer att försöka igen senare.", err)
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Ladda ur en config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok

class GoteborgEnergiDataUpdateCoordinator(DataUpdateCoordinator):
    """Klass för att hantera datauppdateringar från Göteborgs Energi API:er."""
    
    def __init__(self, hass: HomeAssistant) -> None:
        """Initiera coordinatorn."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=1),
        )
        self.hass = hass
    
    async def _async_update_data(self):
        """Hämta data från API:erna."""
        from .api import GoteborgEnergiAPI
        
        api = GoteborgEnergiAPI(self.hass)
        
        try:
            # Hämta spotpriser för SE3 (Göteborg)
            spot_prices = await api.get_spot_prices()
            
            # Hämta elnätspriser från RISE API
            grid_prices = await api.get_grid_prices()
            
            return {
                "spot_prices": spot_prices,
                "grid_prices": grid_prices,
                "last_update": api.get_last_update(),
            }
        except Exception as err:
            _LOGGER.error("Fel vid hämtning av elpriser: %s", err)
            # Returnera tom data istället för att kasta exception
            return {
                "spot_prices": {},
                "grid_prices": {},
                "last_update": None,
            }

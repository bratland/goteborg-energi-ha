"""API-klient för Göteborgs Energi elpriser."""
import aiohttp
import logging
from datetime import datetime, date
from typing import Dict, Optional, Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import ELPRISET_API_URL, RISE_GRID_API_URL, ELECTRICITY_AREA

_LOGGER = logging.getLogger(__name__)

class GoteborgEnergiAPI:
    """API-klient för att hämta elpriser för Göteborg."""
    
    def __init__(self, hass: HomeAssistant) -> None:
        """Initiera API-klienten."""
        self.hass = hass
        self.session = async_get_clientsession(hass)
        self._last_update = None
    
    async def get_spot_prices(self) -> Dict[str, Any]:
        """Hämta spotpriser från elprisetjustnu.se API."""
        today = date.today()
        url = f"{ELPRISET_API_URL}/{today.year}/{today.month:02d}-{today.day:02d}_{ELECTRICITY_AREA}.json"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    self._last_update = datetime.now()
                    return self._process_spot_prices(data)
                else:
                    _LOGGER.error("Fel vid hämtning av spotpriser: %s", response.status)
                    return {}
        except aiohttp.ClientError as err:
            _LOGGER.error("Nätverksfel vid hämtning av spotpriser: %s", err)
            return {}
    
    def _process_spot_prices(self, data: Dict) -> Dict[str, Any]:
        """Bearbeta spotprisdata från API."""
        current_hour = datetime.now().hour
        prices = {}
        
        if not data:
            return prices
        
        # Hitta nuvarande och nästa timmes pris
        for price_data in data:
            time_start = datetime.fromisoformat(price_data["time_start"].replace("Z", "+00:00"))
            hour = time_start.hour
            
            if hour == current_hour:
                prices["current"] = {
                    "price": price_data["SEK_per_kWh"],
                    "time": time_start,
                    "currency": "SEK"
                }
            elif hour == (current_hour + 1) % 24:
                prices["next_hour"] = {
                    "price": price_data["SEK_per_kWh"],
                    "time": time_start,
                    "currency": "SEK"
                }
        
        # Beräkna genomsnittspris för dagen
        if data:
            avg_price = sum(p["SEK_per_kWh"] for p in data) / len(data)
            prices["daily_average"] = avg_price
        
        return prices
    
    async def get_grid_prices(self) -> Dict[str, Any]:
        """Hämta elnätspriser från RISE API."""
        # Placeholder för när RISE API blir tillgängligt
        # För nu returnerar vi statiska värden baserat på Göteborgs Energis hemsida
        
        return {
            "energy_tariff": 0.249,  # kr/kWh (elöverföringsavgift)
            "fixed_fee": 25.0,       # kr/månad (fast avgift)
            "power_tariff": 3.5,     # kr/kW/månad (effektavgift)
            "energy_tax": 0.54875,   # kr/kWh (energiskatt 2025)
            "vat_rate": 0.25,        # 25% moms
        }
    
    def get_last_update(self) -> Optional[datetime]:
        """Returnera tidpunkt för senaste uppdatering."""
        return self._last_update

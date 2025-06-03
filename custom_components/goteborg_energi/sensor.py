"""Sensorer för Göteborgs Energi elpriser."""
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

# Konstant för valuta (SEK)
CURRENCY_KRONA = "SEK"

_LOGGER = logging.getLogger(__name__)

from .const import (
    DOMAIN,
    SENSOR_CURRENT_SPOT_PRICE,
    SENSOR_NEXT_HOUR_SPOT_PRICE,
    SENSOR_GRID_ENERGY_PRICE,
    SENSOR_GRID_POWER_PRICE,
    SENSOR_TOTAL_PRICE,
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sätt upp sensorer för Göteborgs Energi."""
    _LOGGER.debug("Sätter upp sensorer för Göteborgs Energi")
    
    try:
        coordinator = hass.data[DOMAIN][config_entry.entry_id]
        _LOGGER.debug("Hittade coordinator för entry %s", config_entry.entry_id)
        
        entities = [
            GoteborgEnergiSpotPriceSensor(coordinator, SENSOR_CURRENT_SPOT_PRICE, "Nuvarande Elpris"),
            GoteborgEnergiSpotPriceSensor(coordinator, SENSOR_NEXT_HOUR_SPOT_PRICE, "Nästa Timmes Elpris"),
            GoteborgEnergiGridPriceSensor(coordinator, SENSOR_GRID_ENERGY_PRICE, "Elnätsavgift Energi"),
            GoteborgEnergiGridPriceSensor(coordinator, SENSOR_GRID_POWER_PRICE, "Elnätsavgift Effekt"),
            GoteborgEnergiTotalPriceSensor(coordinator, SENSOR_TOTAL_PRICE, "Totalt Elpris"),
        ]
        
        _LOGGER.debug("Skapade %d sensorer", len(entities))
        async_add_entities(entities)
        _LOGGER.info("Lyckades sätta upp %d sensorer för Göteborgs Energi", len(entities))
        
    except Exception as err:
        _LOGGER.error("Fel vid setup av sensorer: %s", err, exc_info=True)
        raise

class GoteborgEnergiBaseSensor(CoordinatorEntity, SensorEntity):
    """Basklass för Göteborgs Energi sensorer."""
    
    def __init__(self, coordinator, sensor_type: str, name: str) -> None:
        """Initiera sensorn."""
        _LOGGER.debug("Initierar sensor: %s (typ: %s)", name, sensor_type)
        try:
            super().__init__(coordinator)
            self._sensor_type = sensor_type
            self._attr_name = f"Göteborgs Energi {name}"
            self._attr_unique_id = f"goteborg_energi_{sensor_type}"
            self._attr_device_class = SensorDeviceClass.MONETARY
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_native_unit_of_measurement = f"{CURRENCY_KRONA}/{UnitOfEnergy.KILO_WATT_HOUR}"
            _LOGGER.debug("Lyckades initiera sensor: %s", self._attr_unique_id)
        except Exception as err:
            _LOGGER.error("Fel vid initiering av sensor %s: %s", name, err, exc_info=True)
            raise

class GoteborgEnergiSpotPriceSensor(GoteborgEnergiBaseSensor):
    """Sensor för spotpriser."""
    
    @property
    def native_value(self) -> Optional[float]:
        """Returnera sensorns värde."""
        if not self.coordinator.data:
            return None
        
        spot_prices = self.coordinator.data.get("spot_prices", {})
        
        if self._sensor_type == SENSOR_CURRENT_SPOT_PRICE:
            current = spot_prices.get("current")
            return current["price"] if current else None
        elif self._sensor_type == SENSOR_NEXT_HOUR_SPOT_PRICE:
            next_hour = spot_prices.get("next_hour")
            return next_hour["price"] if next_hour else None
        
        return None
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Returnera extra attribut."""
        if not self.coordinator.data:
            return {}
        
        spot_prices = self.coordinator.data.get("spot_prices", {})
        attrs = {
            "area": "SE3",
            "location": "Göteborg",
            "daily_average": spot_prices.get("daily_average"),
        }
        
        if self._sensor_type == SENSOR_CURRENT_SPOT_PRICE:
            current = spot_prices.get("current")
            if current:
                attrs["valid_from"] = current["time"].isoformat()
        elif self._sensor_type == SENSOR_NEXT_HOUR_SPOT_PRICE:
            next_hour = spot_prices.get("next_hour")
            if next_hour:
                attrs["valid_from"] = next_hour["time"].isoformat()
        
        return attrs

class GoteborgEnergiGridPriceSensor(GoteborgEnergiBaseSensor):
    """Sensor för elnätspriser."""
    
    @property
    def native_value(self) -> Optional[float]:
        """Returnera sensorns värde."""
        if not self.coordinator.data:
            return None
        
        grid_prices = self.coordinator.data.get("grid_prices", {})
        
        if self._sensor_type == SENSOR_GRID_ENERGY_PRICE:
            energy_tariff = grid_prices.get("energy_tariff", 0)
            energy_tax = grid_prices.get("energy_tax", 0)
            vat_rate = grid_prices.get("vat_rate", 0)
            # Energiavgift + energiskatt + moms
            return (energy_tariff + energy_tax) * (1 + vat_rate)
        elif self._sensor_type == SENSOR_GRID_POWER_PRICE:
            return grid_prices.get("power_tariff", 0)
        
        return None
    
    @property
    def native_unit_of_measurement(self) -> str:
        """Returnera enhet för sensorn."""
        if self._sensor_type == SENSOR_GRID_POWER_PRICE:
            return f"{CURRENCY_KRONA}/kW/månad"
        return super().native_unit_of_measurement
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Returnera extra attribut."""
        if not self.coordinator.data:
            return {}
        
        grid_prices = self.coordinator.data.get("grid_prices", {})
        
        if self._sensor_type == SENSOR_GRID_ENERGY_PRICE:
            return {
                "energy_tariff": grid_prices.get("energy_tariff"),
                "energy_tax": grid_prices.get("energy_tax"),
                "vat_rate": grid_prices.get("vat_rate"),
                "fixed_fee_monthly": grid_prices.get("fixed_fee"),
                "description": "Elnätsavgift energi inkl. energiskatt och moms"
            }
        elif self._sensor_type == SENSOR_GRID_POWER_PRICE:
            return {
                "description": "Effektavgift för villa- och företagskunder",
                "calculation": "Medel av 3 högsta timmar per månad"
            }
        
        return {}

class GoteborgEnergiTotalPriceSensor(GoteborgEnergiBaseSensor):
    """Sensor för totalt elpris (spot + nät)."""
    
    @property
    def native_value(self) -> Optional[float]:
        """Returnera totalt elpris."""
        if not self.coordinator.data:
            return None
        
        spot_prices = self.coordinator.data.get("spot_prices", {})
        grid_prices = self.coordinator.data.get("grid_prices", {})
        
        current_spot = spot_prices.get("current")
        if not current_spot:
            return None
        
        # Beräkna total kostnad per kWh
        spot_price = current_spot["price"]
        
        # Elnätsavgift (energi + skatt + moms)
        energy_tariff = grid_prices.get("energy_tariff", 0)
        energy_tax = grid_prices.get("energy_tax", 0)
        vat_rate = grid_prices.get("vat_rate", 0)
        grid_cost = (energy_tariff + energy_tax) * (1 + vat_rate)
        
        # Total kostnad (spotpris med moms + elnätsavgift)
        total_cost = (spot_price * (1 + vat_rate)) + grid_cost
        
        return round(total_cost, 4)
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Returnera extra attribut."""
        if not self.coordinator.data:
            return {}
        
        spot_prices = self.coordinator.data.get("spot_prices", {})
        grid_prices = self.coordinator.data.get("grid_prices", {})
        
        current_spot = spot_prices.get("current")
        if not current_spot:
            return {}
        
        spot_price = current_spot["price"]
        vat_rate = grid_prices.get("vat_rate", 0)
        energy_tariff = grid_prices.get("energy_tariff", 0)
        energy_tax = grid_prices.get("energy_tax", 0)
        grid_cost = (energy_tariff + energy_tax) * (1 + vat_rate)
        
        return {
            "spot_price_excl_vat": spot_price,
            "spot_price_incl_vat": round(spot_price * (1 + vat_rate), 4),
            "grid_cost_incl_vat": round(grid_cost, 4),
            "fixed_monthly_fee": grid_prices.get("fixed_fee"),
            "power_tariff": grid_prices.get("power_tariff"),
            "breakdown": {
                "spotpris": round(spot_price * (1 + vat_rate), 4),
                "elnätsavgift": round(grid_cost, 4),
                "totalt": round((spot_price * (1 + vat_rate)) + grid_cost, 4)
            }
        }

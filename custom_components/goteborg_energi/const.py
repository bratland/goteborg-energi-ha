"""Konstanter för Göteborgs Energi integration."""

DOMAIN = "goteborg_energi"
PLATFORMS = ["sensor"]

# API URLs
ELPRISET_API_URL = "https://www.elprisetjustnu.se/api/v1/prices"
RISE_GRID_API_URL = "https://elnatsavgift.se/api/v1"

# Elområde för Göteborg
ELECTRICITY_AREA = "SE3"

# Sensor namn
SENSOR_CURRENT_SPOT_PRICE = "current_spot_price"
SENSOR_NEXT_HOUR_SPOT_PRICE = "next_hour_spot_price"
SENSOR_GRID_ENERGY_PRICE = "grid_energy_price"
SENSOR_GRID_POWER_PRICE = "grid_power_price"
SENSOR_TOTAL_PRICE = "total_electricity_price"

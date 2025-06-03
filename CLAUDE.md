# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Home Assistant custom integration for Göteborg Energi electricity prices. It fetches real-time electricity spot prices for the SE3 area (Göteborg) and combines them with Göteborg Energi's grid tariffs to provide complete electricity cost information.

## Architecture

### Integration Structure
- **Domain**: `goteborg_energi` - The integration identifier for Home Assistant
- **Platform**: `sensor` - Creates sensor entities for electricity pricing data
- **Config Flow**: Simple setup flow with no required configuration parameters

### Core Components

1. **Data Coordinator** (`__init__.py`):
   - `GoteborgEnergiDataUpdateCoordinator` - Manages hourly data updates
   - Fetches both spot prices and grid prices via the API class
   - Update interval: 1 hour

2. **API Client** (`api.py`):
   - `GoteborgEnergiAPI` - Handles external data fetching
   - Spot prices from `elprisetjustnu.se` API for SE3 area
   - Grid prices are currently static values (placeholder for future RISE API integration)
   - Returns structured data with current/next hour prices and daily averages

3. **Sensors** (`sensor.py`):
   - 5 sensor entities created per integration instance
   - Base class `GoteborgEnergiBaseSensor` with common attributes
   - Specialized classes for spot prices, grid prices, and total calculations

### Sensor Types

| Sensor | Class | Purpose |
|--------|-------|---------|
| Current Spot Price | `GoteborgEnergiSpotPriceSensor` | Real-time spot price |
| Next Hour Spot Price | `GoteborgEnergiSpotPriceSensor` | Next hour's spot price |
| Grid Energy Price | `GoteborgEnergiGridPriceSensor` | Grid tariff + energy tax + VAT |
| Grid Power Price | `GoteborgEnergiGridPriceSensor` | Monthly power tariff (kr/kW/month) |
| Total Price | `GoteborgEnergiTotalPriceSensor` | Complete cost calculation |

## Key Implementation Details

### Price Calculation Logic
The total electricity price combines:
- Spot price (with 25% VAT)
- Grid energy tariff + energy tax (with 25% VAT)
- Power tariff is separate (monthly fee)

### Data Flow
1. Coordinator triggers hourly updates
2. API fetches spot prices from external API
3. Grid prices retrieved from static configuration
4. Sensors calculate and expose final values
5. All prices in SEK (Swedish Krona) per kWh

### Error Handling
- API failures are logged but don't crash the integration
- Missing data returns `None` for sensor values
- Coordinator includes retry logic via Home Assistant's base class

## Development Notes

### Language
- All code comments and logging are in Swedish
- User-facing names and descriptions are in Swedish
- Integration targets Swedish market (Göteborg specifically)

### External Dependencies
- No external Python packages required (uses only Home Assistant built-ins)
- Depends on `elprisetjustnu.se` API availability
- Future integration planned with RISE API for dynamic grid prices

### Testing
This integration has no automated tests. When making changes, verify manually by:
1. Installing in Home Assistant development environment
2. Checking that all 5 sensors are created
3. Verifying sensor values update hourly
4. Checking Home Assistant logs for API errors
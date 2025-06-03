# Göteborgs Energi Elpriser - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![Version](https://img.shields.io/github/v/release/bratland/goteborg-energi-ha)](https://github.com/bratland/goteborg-energi-ha/releases)
[![License](https://img.shields.io/github/license/bratland/goteborg-energi-ha)](LICENSE)

En Home Assistant-integration som visar kompletta elpriser för Göteborg genom att kombinera spotpriser från öppna API:er med Göteborgs Energis elnätstavgifter.

## 🏠 Översikt

Denna integration ger dig full insyn i dina elkostnader i Göteborg genom att:
- 📊 Hämta realtids-spotpriser för SE3 (Göteborg)
- ⚡ Inkludera Göteborgs Energis elnätstavgifter  
- 💰 Beräkna den totala kostnaden per kWh
- 🔄 Visa allt som lättförståeliga sensorer i Home Assistant

## 📊 Funktioner

- **Realtidspriser**: Aktuellt och nästa timmes spotpris
- **Elnätsavgifter**: Energi- och effektavgifter från Göteborg Energi
- **Totalkostnad**: Din verkliga kostnad per kWh (inkl. skatter)
- **Automatisk uppdatering**: Hämtar ny data varje timme
- **Historisk data**: Spara och analysera pristrender

## 🔌 Installation via HACS (Rekommenderas)

1. Öppna **HACS** i Home Assistant
2. Gå till **Integrationer**
3. Klicka på **⋮** → **Anpassade förråd**
4. Lägg till: `https://github.com/bratland/goteborg-energi-ha`
5. Kategori: **Integration**
6. Sök efter "**Göteborgs Energi Elpriser**" och installera
7. Starta om Home Assistant
8. Lägg till integrationen via **Inställningar** → **Enheter & tjänster**

## 📈 Sensorer som skapas

| Sensor | Beskrivning | Enhet | Uppdatering |
|--------|-------------|-------|-------------|
| `sensor.goteborgs_energi_nuvarande_elpris` | Aktuellt spotpris | kr/kWh | Varje timme |
| `sensor.goteborgs_energi_nasta_timmes_elpris` | Nästa timmes spotpris | kr/kWh | Varje timme |
| `sensor.goteborgs_energi_elnatsavgift_energi` | Elnätsavgift + energiskatt + moms | kr/kWh | Statisk |
| `sensor.goteborgs_energi_elnatsavgift_effekt` | Effektavgift för villor | kr/kW/månad | Statisk |
| `sensor.goteborgs_energi_totalt_elpris` | Total kostnad per kWh | kr/kWh | Varje timme |

## 🏡 Användningsexempel

### Smart billaddning
```yaml
automation:
  - alias: "Smart billaddning"
    trigger:
      - platform: numeric_state
        entity_id: sensor.goteborgs_energi_totalt_elpris
        below: 1.20  # kr/kWh
    condition:
      - condition: state
        entity_id: device_tracker.min_bil
        state: 'home'
    action:
      - service: switch.turn_on
        entity_id: switch.billaddare
      - service: notify.mobile_app
        data:
          message: "Billaddning startad - elpris: {{ trigger.to_state.state }} kr/kWh"
```

### Värmepumpoptimering
```yaml
automation:
  - alias: "Optimera värmepump"
    trigger:
      - platform: state
        entity_id: sensor.goteborgs_energi_totalt_elpris
    action:
      - choose:
          - conditions:
              - condition: numeric_state
                entity_id: sensor.goteborgs_energi_totalt_elpris
                below: 1.00
            sequence:
              - service: climate.set_temperature
                entity_id: climate.varmepump
                data:
                  temperature: 23  # Högre temp vid lågt pris
          - conditions:
              - condition: numeric_state
                entity_id: sensor.goteborgs_energi_totalt_elpris
                above: 2.00
            sequence:
              - service: climate.set_temperature
                entity_id: climate.varmepump
                data:
                  temperature: 20  # Lägre temp vid högt pris
```

### Prisnotifikationer
```yaml
automation:
  - alias: "Prisnotifikationer"
    trigger:
      - platform: numeric_state
        entity_id: sensor.goteborgs_energi_nuvarande_elpris
        below: 0.50  # Lågt pris
      - platform: numeric_state
        entity_id: sensor.goteborgs_energi_nuvarande_elpris
        above: 2.00  # Högt pris
    action:
      - service: notify.mobile_app
        data:
          title: >
            {% if trigger.to_state.state | float < 0.50 %}
            💚 Lågt elpris!
            {% else %}
            ⚡ Högt elpris!
            {% endif %}
          message: >
            Elpriset är nu {{ trigger.to_state.state }} kr/kWh.
            {% if trigger.to_state.state | float < 0.50 %}
            Perfekt tid för tvättmaskin, billaddning etc.
            {% else %}
            Undvik större elförbrukning om möjligt.
            {% endif %}
```

## 📊 Dashboard-exempel
```yaml
type: entities
title: Elpriser Göteborg
entities:
  - entity: sensor.goteborgs_energi_nuvarande_elpris
    name: "Nu"
  - entity: sensor.goteborgs_energi_nasta_timmes_elpris
    name: "Nästa timme"
  - entity: sensor.goteborgs_energi_totalt_elpris
    name: "Totalkostnad"
  - type: divider
  - entity: sensor.goteborgs_energi_elnatsavgift_energi
    name: "Elnätsavgift"
  - entity: sensor.goteborgs_energi_elnatsavgift_effekt
    name: "Effektavgift"
```

## 🔧 Tekniska detaljer

### Datakällor
- **Spotpriser**: [elprisetjustnu.se API](https://www.elprisetjustnu.se/elpris-api)
- **Elnätspriser**: Göteborgs Energi officiella tariffer
- **Energiskatt**: 54,875 öre/kWh (2025)
- **Moms**: 25%

### Uppdateringsschema
- **Spotpriser**: Hämtas varje timme från elprisetjustnu.se
- **Elnätspriser**: Statiska värden baserat på Göteborgs Energis tariffer
- **Totalkostnad**: Beräknas automatiskt när spotpris ändras

### Begränsningar
- Spotpriser för morgondagen publiceras vanligtvis kl 13
- Elnätspriser är hårdkodade och uppdateras vid nya versioner
- API-beroende - fungerar bara med internetanslutning

## 🐛 Felsökning

### Sensorer visar inga värden
1. Kontrollera internet-anslutning
2. Verifiera att `elprisetjustnu.se` är tillgängligt
3. Kontrollera Home Assistant-loggar för felmeddelanden

### API-fel
```
ERROR (MainThread) [custom_components.goteborg_energi.api] Fel vid hämtning av spotpriser: 404
```
Detta kan hända om dagens prisdata inte är tillgänglig ännu. Morgondagens priser publiceras vanligtvis kl 13.

## 👥 Bidra

1. Forka repositoryt
2. Skapa en feature branch (`git checkout -b feature/amazing-feature`)
3. Commit dina ändringar (`git commit -m 'Add amazing feature'`)
4. Pusha till branchen (`git push origin feature/amazing-feature`)
5. Öppna en Pull Request

## 📄 Licens

Detta projekt är licensierat under MIT License - se [LICENSE](LICENSE) filen för detaljer.

## ⚠️ Disclaimer

Denna integration är inte officiellt godkänd av Göteborg Energi. All data hämtas från offentligt tillgängliga API:er. Använd på egen risk.

## 🙏 Tack

- [elprisetjustnu.se](https://www.elprisetjustnu.se/) för det öppna API:et
- Göteborg Energi för transparenta tariffer
- Home Assistant community för inspiration

---

**Gillar du denna integration?** ⭐ Ge den en stjärna på GitHub!

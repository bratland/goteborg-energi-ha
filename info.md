# Göteborgs Energi Elpriser

En Home Assistant integration som visar elpriser för Göteborg genom att kombinera spotpriser från öppna API:er med lokala elnätstavgifter.

## 🏠 Vad gör integrationen?

- **📊 Spotpriser**: Hämtar timpriser för SE3 (Göteborg) från elprisetjustnu.se
- **⚡ Elnätsavgifter**: Inkluderar Göteborgs Energis tariffer och svenska skatter
- **💰 Totalkostnad**: Beräknar din verkliga kostnad per kWh
- **🔄 Automatisk uppdatering**: Uppdateras varje timme
- **📈 Historisk data**: Visar dagsgenomsnitt och trender

## 📊 Sensorer som skapas

| Sensor | Beskrivning | Enhet |
|--------|-------------|-------|
| `goteborg_energi_nuvarande_elpris` | Aktuellt spotpris | kr/kWh |
| `goteborg_energi_nasta_timmes_elpris` | Nästa timmes spotpris | kr/kWh |
| `goteborg_energi_elnatsavgift_energi` | Elnätsavgift + energiskatt + moms | kr/kWh |
| `goteborg_energi_elnatsavgift_effekt` | Effektavgift för villor | kr/kW/månad |
| `goteborg_energi_totalt_elpris` | Total kostnad per kWh | kr/kWh |

## 🚀 Användningsexempel

### Smart billaddning
```yaml
automation:
  - alias: "Ladda bil vid lågt pris"
    trigger:
      - platform: numeric_state
        entity_id: sensor.goteborg_energi_totalt_elpris
        below: 1.20
    action:
      - service: switch.turn_on
        entity_id: switch.billaddare
```

### Prisnotifikationer
```yaml
automation:
  - alias: "Notifiering lågt elpris"
    trigger:
      - platform: numeric_state
        entity_id: sensor.goteborg_energi_nuvarande_elpris
        below: 0.50
    action:
      - service: notify.mobile_app
        data:
          message: "Elpriset är bara {{ trigger.to_state.state }} kr/kWh - dags att tvätta!"
```

## 💡 Datakällor

- **Spotpriser**: [elprisetjustnu.se](https://www.elprisetjustnu.se/elpris-api) (öppet API)
- **Elnätspriser**: Göteborgs Energi officiella tariffer 2025
- **Skatter**: Svenska energiskatter för 2025

## 🔧 Installation

1. Installera via HACS
2. Starta om Home Assistant  
3. Lägg till integrationen via **Inställningar** → **Enheter & tjänster**
4. Sök efter "Göteborgs Energi Elpriser"

## 📍 För vem passar detta?

- Göteborgare som vill optimera sin elförbrukning
- Elbilsägare som vill ladda när det är billigast
- Alla som vill förstå sina verkliga elkostnader
- Home Assistant-entusiaster i SE3-området

## ⚠️ Notering

Denna integration är inte officiellt godkänd av Göteborg Energi. All data hämtas från offentligt tillgängliga API:er.

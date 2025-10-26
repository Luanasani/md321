# Projekt 321 – Erweiterung: Automatischer Light/Dark-Mode

Diese Erweiterung ergänzt das bestehende verteilte System um einen automatischen Wechsel zwischen Light- und Dark-Mode auf Basis der gemessenen Umgebungshelligkeit. Die Beleuchtungswerte werden vom BH1750-Lichtsensor erfasst, per MQTT verteilt, über Prometheus als Metrik bereitgestellt, in Grafana visualisiert und steuern schließlich die Web-Oberfläche in Echtzeit.

## Architekturüberblick

```
BH1750 → Sensor-API → MQTT-Broker → Prometheus → Grafana → Web-UI
```

1. **Sensor-API** (Raspberry Pi):
   - Liest den BH1750-Lichtsensor im Sekundenrhythmus aus.
   - Veröffentlicht die Lux-Werte auf dem MQTT-Topic `mondaymorning/sensors/light`.
   - Stellt die Messwerte zusätzlich über den HTTP-Endpunkt `http://<pi>:8080/metrics` im Prometheus-Format bereit.
2. **MQTT-Broker (Mosquitto)**: Empfängt die Sensordaten und stellt sie für weitere Konsumenten (z. B. Web-UI) bereit.
3. **Prometheus**: Greift alle 5 Sekunden auf die Sensor-API zu und speichert die Metrik `light` sowie ergänzende Sensorwerte (Temperatur, Luftfeuchte, Distanz).
4. **Grafana**: Visualisiert den Messverlauf. Ein Dashboard kann auf Basis der Prometheus-Datenquelle erstellt werden (Panel-Typ „Time series“, Query `light`).
5. **Web-UI**: Verwendet das MQTT-Topic, um den aktuellen Lux-Wert zu erhalten und zwischen Light- und Dark-Mode zu wechseln. Ein Initialaufruf der Sensor-API liefert Startwerte, damit die Oberfläche sofort reagiert.

## Komponenten starten

### MQTT-Broker

```bash
docker compose up -d  # im Projektwurzelverzeichnis
```

### Sensor-API

```bash
cd sensor-api
sudo docker compose up --build
```

> 💡 Durch den `privileged`-Modus erhält der Container Zugriff auf die I²C-Schnittstelle des Raspberry Pi.

### Monitoring-Stack

```bash
cd system-monitoring
docker compose up -d
```

Prometheus ist anschließend unter `http://<host>:9090`, Grafana unter `http://<host>:3000` erreichbar. Im Prometheus-Target-Tab sollte `sensor-api` als neuer Job sichtbar sein.

## Nutzung in der Web-UI

- Öffne `dashboard/index.html` über einen lokalen Webserver oder hoste die Datei z. B. via `python -m http.server`.
- Stelle sicher, dass der Browser den MQTT-Websocket unter `ws://<broker-host>:9001` erreicht.
- Die Oberfläche zeigt den aktuellen Lux-Wert, den letzten Empfangszeitpunkt und ändert das Farbschema automatisch. Über den Link „In Grafana ansehen“ gelangt man direkt zur Visualisierung.

## Anpassungen & Grenzwerte

- Der Schwellenwert für den Dark-Mode liegt bei **150 Lux** und kann in `dashboard/index.html` (`LIGHT_THRESHOLD`) angepasst werden.
- Bei Auslesefehlern des BH1750 (z. B. fehlende Verkabelung) werden im Log entsprechende Hinweise ausgegeben; die letzte erfolgreiche Messung bleibt verfügbar und wird weiterhin für Prometheus- und MQTT-Clients bereitgestellt.

## Validierung

- Prüfe im Prometheus Web-UI (`http://<host>:9090/graph`) die Metrik `light`.
- Richte in Grafana ein Panel mit der Query `light` ein und beobachte die automatischen Umschaltungen der Web-UI bei veränderten Lichtverhältnissen.


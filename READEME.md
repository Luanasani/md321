# Projekt 321 – Erweiterung: Automatischer Light/Dark-Mode

Diese Erweiterung ergänzt das bestehende verteilte System um einen automatischen Wechsel zwischen Light- und Dark-Mode auf Basis der gemessenen Umgebungshelligkeit. Die Beleuchtungswerte werden vom BH1750-Lichtsensor erfasst, per MQTT verteilt, über Prometheus als Metrik bereitgestellt, in Grafana visualisiert und steuern schließlich die Web-Oberfläche in Echtzeit.

## Architekturüberblick

```
BH1750 → Sensor-API → MQTT-Broker → Prometheus → Grafana → Web-UI
```

1. **Sensor-API** (Raspberry Pi unter `192.168.1.129`):
   - Liest den BH1750-Lichtsensor im Sekundenrhythmus aus.
   - Veröffentlicht die Lux-Werte auf dem MQTT-Topic `mondaymorning/sensors/light`.
   - Stellt die Messwerte zusätzlich über den HTTP-Endpunkt `http://<pi>:8080/metrics` im Prometheus-Format bereit.
2. **MQTT-Broker (Mosquitto)**: Empfängt die Sensordaten und stellt sie für weitere Konsumenten (z. B. Web-UI) bereit.
3. **Prometheus**: Greift alle 5 Sekunden auf die Sensor-API zu und speichert die Metrik `light` sowie ergänzende Sensorwerte (Temperatur, Luftfeuchte, Distanz).
4. **Grafana**: Visualisiert den Messverlauf. Ein Dashboard kann auf Basis der Prometheus-Datenquelle erstellt werden (Panel-Typ „Time series“, Query `light`).
5. **Web-UI**: Verwendet das MQTT-Topic, um den aktuellen Lux-Wert zu erhalten und zwischen Light- und Dark-Mode zu wechseln. Ein Initialaufruf der Sensor-API liefert Startwerte, damit die Oberfläche sofort reagiert.

## Komponenten starten

> 💡 Für alle Docker-Kommandos muss der Benutzer Mitglied der `docker`-Gruppe sein oder die Befehle mit `sudo` ausführen.

### MQTT-Broker

```bash
# aus dem Projektwurzelverzeichnis
sudo docker compose up -d
```

### Sensor-API

```bash
cd sensor-api
# optional: andere Broker-Adresse per Umgebungsvariable setzen
sudo MQTT_BROKER_HOST=192.168.1.129 MQTT_BROKER_PORT=1883 docker compose up --build
```

> 💡 Durch den `privileged`-Modus erhält der Container Zugriff auf die I²C-Schnittstelle des Raspberry Pi.

### Monitoring-Stack

```bash
cd system-monitoring
sudo docker compose up -d
```

Prometheus ist anschließend unter `http://<host>:9090`, Grafana unter `http://<host>:3000` erreichbar. Im Prometheus-Target-Tab sollte `sensor-api` als neuer Job sichtbar sein.
Passe bei Bedarf in `system-monitoring/prometheus/prometheus.yaml` die Zieladresse des Raspberry Pi (`192.168.1.129:8080`) an.

## Nutzung in der Web-UI

- Öffne `dashboard/index.html` über einen lokalen Webserver oder hoste die Datei z. B. via `python -m http.server`.
- Stelle sicher, dass der Browser den MQTT-Websocket unter `ws://192.168.1.129:9001` erreicht. Über den Query-Parameter `?host=<ziel>`
  lässt sich bei Bedarf ein anderer Host setzen, z. B. `http://localhost:8000/index.html?host=192.168.1.129`.
- Die Oberfläche zeigt den aktuellen Lux-Wert, den letzten Empfangszeitpunkt und ändert das Farbschema automatisch. Über den Link „In Grafana ansehen“ gelangt man direkt zur Visualisierung.
- Standardmäßig greift die Web-UI auf den Host `192.168.1.129` zu. Eine Anpassung ist sowohl über den Query-Parameter als auch direkt im
  Skript (`DEFAULT_HOST` in `dashboard/index.html`) möglich.

## Anpassungen & Grenzwerte

- Der Schwellenwert für den Dark-Mode liegt bei **150 Lux** und kann in `dashboard/index.html` (`LIGHT_THRESHOLD`) angepasst werden.
- MQTT-Broker-Adresse und -Port der Sensor-API lassen sich über die Umgebungsvariablen `MQTT_BROKER_HOST` und `MQTT_BROKER_PORT`
  anpassen (Standard: `192.168.1.129:1883`).
- Bei Auslesefehlern des BH1750 (z. B. fehlende Verkabelung) werden im Log entsprechende Hinweise ausgegeben; die letzte erfolgreiche Messung bleibt verfügbar und wird weiterhin für Prometheus- und MQTT-Clients bereitgestellt.

## Validierung

### Prometheus-Metriken abfragen

1. Öffne das Web-UI unter `http://<host>:9090/graph`.
2. Wähle oben den Reiter **Graph** aus.
3. Trage im Feld **Expression** den Metriknamen `light` ein und klicke auf **Execute**.
4. Über **Graph** oder **Console** kannst du dir den aktuellen Wert sowie den Verlauf anzeigen lassen.

> ℹ️ Weitere Metriken der Sensor-API (z. B. `sensor_temperature_celsius` oder `sensor_humidity_percent`) lassen sich auf die gleiche Weise prüfen.

### Grafana-Dashboard aufrufen

1. Rufe `http://<host>:3000` im Browser auf.
2. Melde dich mit Benutzername `admin` und Passwort `admin` an (Grafana fordert beim ersten Login zur Änderung des Passworts auf).
3. Lege ein neues Dashboard an oder importiere ein vorhandenes; füge ein Panel vom Typ **Time series** hinzu und verwende als Query `light`.
4. Über den Zeitraum-Selector oben rechts kannst du den Betrachtungszeitraum anpassen, um z. B. Hell-/Dunkelwechsel sichtbar zu machen.

> 🔐 Ändere das Admin-Passwort nach dem ersten Login oder hinterlege einen sicheren Wert über `GF_SECURITY_ADMIN_PASSWORD` im Compose-File.

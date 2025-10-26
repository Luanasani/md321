# Individuelle Erweiterung – Interaktiver Sensor-Showcase (Joy-Pi)
**Autor:** Luanasani  
**Modul:** 321 – Verteilte Systeme  
**Projekt:** Erweiterung eines bestehenden Systems durch echte Sensorintegration

---

## 🎯 Ziel der Erweiterung
Ziel ist es, **Temperatur**, **Luftfeuchtigkeit**, **Helligkeit** und **Bewegung** real zu messen und die Werte **in Echtzeit auf der Konsole** darzustellen.

---

## ⚙️ Technischer Aufbau

### Hardware
| Sensor | Typ | Anschluss | Beschreibung |
|---------|------|-----------|---------------|
| **DHT11** | Temperatur & Luftfeuchte | GPIO 4 | Erfasst Raumtemperatur und Luftfeuchtigkeit |
| **BH1750** | Lichtsensor | I²C (Adresse 0x5C) | Misst Umgebungshelligkeit (Lux) |
| **PIR-Sensor** | Bewegung | GPIO 16 | Erkennt Bewegungen im Raum |

### Software
- Programmiersprache: **Python 3**
- Bibliotheken:
  - `adafruit_dht` – liest den DHT11-Sensor  
  - `smbus2` – Kommunikation über I²C (BH1750)  
  - `RPi.GPIO` – Zugriff auf GPIO-Pins  
- Plattform: **Raspberry Pi OS (Bookworm)**  
- Hardware: **Joy-Pi mit Raspberry Pi 4**

---

## ⚙️ Setup-Anleitung

### 1️⃣ Voraussetzungen
- Raspberry Pi 4 (oder 3B+) mit Joy-Pi-Board  
- Raspberry Pi OS (Bookworm) installiert  
- Internetverbindung aktiv  

### 2️⃣ Projekt vorbereiten
```bash
# Projektordner erstellen
mkdir ~/md321
cd ~/md321

### 3️⃣ Abhängigkeiten installieren
```bash
sudo apt update
sudo apt install python3-pip python3-smbus libgpiod2 -y
pip install adafruit-circuitpython-dht smbus2 RPi.GPIO
```
> 💡 Wenn du eine Meldung wie „externally-managed-environment“ bekommst, nutze:
> ```bash
> pip install --break-system-packages adafruit-circuitpython-dht smbus2 RPi.GPIO
> ```

⚠️ Hinweis:
Der Parameter --break-system-packages erlaubt das manuelle Installieren zusätzlicher Bibliotheken außerhalb der Systemverwaltung.
Diese Option ist hier unbedenklich, da sie nur für die Python-Sensorbibliotheken benötigt wird.
Alternativ kann eine virtuelle Umgebung (python3 -m venv .venv) verwendet werden.

### 4️⃣ Joy-Pi vorbereiten
- **Schalter S5 = ON** (aktiviert den DHT11-Sensor)  
- Sensoren frei (nicht blockiert oder verdeckt)  
- Joy-Pi eingeschaltet  

### 5️⃣ Programm starten

```bash
python3 sensor_showcase.py
```
💡 Hinweis: Stelle sicher, dass die Datei sensor_showcase.py im Ordner sensor-api liegt und du dich auch in diesem Verzeichnis befindest.

Erwartete Ausgabe:
```
[20:01:13] Sensorrunde 2
✅ Temperatur: 24.5 °C – Temperatur im Wohlfühlbereich.
⚠️ Luftfeuchtigkeit: 29.0 % – Luft zu trocken.
⚠️ Helligkeit: 27.5 Lux – Licht an? Es ist dunkel.
🚨 Bewegung: 100 % – Bewegung erkannt!
```
Beenden mit **Strg + C** – GPIOs werden automatisch bereinigt.

---

## 🧠 Erkenntnisse / Learnings

- Ich habe gelernt, wie Sensoren direkt über **GPIO- und I²C-Schnittstellen** angebunden werden.  
- Ich verstehe, wie man **Timing- und Prüfsummenfehler** beim DHT11 erkennt und löst.  
- Ich habe ein stabiles **Echtzeitsystem** aufgebaut, das Sensorwerte zuverlässig ausgibt.  
- Ich weiß, wie ich Daten künftig in **Prometheus, Grafana oder MQTT-Systeme** integrieren kann.  

---

## 💡 Probleme & Lösungen (einfach erklärt)
| Problem | Ursache | Lösung |
|----------|----------|---------|
| **DHT11:** falsche Werte | Sensor zu früh ausgelesen | Pause + Adafruit-Bibliothek |
| **BH1750:** keine Luxwerte | falscher I²C-Befehl | korrigiert auf `(0x20, 2 Bytes)` |
| **PIR:** daueraktiv | zu empfindlich |
| **Startfehler:** keine Messung | Sensoren noch nicht bereit | 2 Sekunden Verzögerung eingefügt |

---

## 📈 Erweiterungsmöglichkeiten
- Integration mit **Prometheus & Grafana** zur grafischen Darstellung  
- **MQTT-Schnittstelle** für verteilte Systeme  
- Automatischer **Light/Dark-Mode** basierend auf Helligkeit  
---

## ✅ Fazit
Diese Erweiterung verwandelt die Simulation in ein **reales Sensorsystem mit echten Messwerten**.  
Das Projekt zeigt erfolgreich:
- stabile Sensorintegration auf dem Raspberry Pi  
- Fehlerbehandlung  
- klare Struktur und sauberen Python-Code  

---
## Git-Repo (Files)
https://github.com/Luanasani/md321.git


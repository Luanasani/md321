#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interaktiver Sensor-Showcase mit echten Sensoren (Joy-Pi)
Autor: Luanasani

Erfasst Temperatur, Luftfeuchtigkeit, Helligkeit und Bewegung
vom Joy-Pi-Board und gibt die Werte in der Konsole aus.
"""

import RPi.GPIO as GPIO
import smbus2
import time
import random
from dataclasses import dataclass
from datetime import datetime
import adafruit_dht
import board
from prometheus_client import Gauge, start_http_server


# --- Sensor-Definitionen ---
BH1750_ADDR = 0x5C       # BH1750 Lichtsensor (Joy-Pi)
DHT_PIN = board.D4        # GPIO 4 für DHT11
MOTION_PIN = 16           # GPIO 16 für PIR-Sensor


# --- Setup ---
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTION_PIN, GPIO.IN)

bus = smbus2.SMBus(1)
dhtDevice = adafruit_dht.DHT11(DHT_PIN, use_pulseio=False)


# --- Prometheus Metriken ---
TEMPERATURE_GAUGE = Gauge(
    "joypi_temperature_celsius",
    "Aktuelle Temperaturmessung des Joy-Pi in Grad Celsius",
)
HUMIDITY_GAUGE = Gauge(
    "joypi_humidity_percent",
    "Relative Luftfeuchtigkeit des Joy-Pi in Prozent",
)
LIGHT_GAUGE = Gauge(
    "joypi_light_lux",
    "Gemessene Beleuchtungsstärke des Joy-Pi in Lux",
)
MOTION_GAUGE = Gauge(
    "joypi_motion_detected",
    "Bewegungserkennung des Joy-Pi (1 = Bewegung, 0 = keine Bewegung)",
)


@dataclass
class SensorReading:
    sensor: str
    value: float
    unit: str
    message: str
    severity: str = "info"

    def render(self):
        icons = {
            "info": "ℹ️",
            "ok": "✅",
            "warn": "⚠️",
            "alert": "🚨",
        }
        icon = icons.get(self.severity, icons["info"])
        return f"{icon} {self.sensor}: {self.value:.1f} {self.unit} – {self.message}"


class SensorShowcase:
    """Erfasst reale Sensordaten vom Joy-Pi, mit stabiler Abfrage."""

    def __init__(self):
        self._sensors = [
            self._temperature_sensor,
            self._humidity_sensor,
            self._light_sensor,
            self._motion_sensor,
        ]

    def poll(self):
        for sensor in self._sensors:
            yield sensor()

    @staticmethod
    def update_metrics(reading: SensorReading):
        if reading.sensor == "Temperatur":
            TEMPERATURE_GAUGE.set(reading.value)
        elif reading.sensor == "Luftfeuchtigkeit":
            HUMIDITY_GAUGE.set(reading.value)
        elif reading.sensor == "Helligkeit":
            LIGHT_GAUGE.set(reading.value)
        elif reading.sensor == "Bewegung":
            MOTION_GAUGE.set(1 if reading.value else 0)

    # Temperatur
    def _temperature_sensor(self):
        try:
            temp = dhtDevice.temperature
            if temp is None:
                raise ValueError("Keine Messung erhalten.")
            if temp > 29.5:
                msg, sev = "Lüftung einschalten!", "alert"
            elif temp > 26.0:
                msg, sev = "Ganz schön warm hier.", "warn"
            else:
                msg, sev = "Temperatur im Wohlfühlbereich.", "ok"
            return SensorReading("Temperatur", temp, "°C", msg, sev)
        except Exception as e:
            temp = random.uniform(20, 28)
            return SensorReading("Temperatur", temp, "°C", f"Fehler: {e}", "warn")

    # Luftfeuchtigkeit
    def _humidity_sensor(self):
        try:
            hum = dhtDevice.humidity
            if hum is None:
                raise ValueError("Keine Messung erhalten.")
            if hum < 30:
                msg, sev = "Luft zu trocken – ggf. befeuchten.", "warn"
            elif hum > 70:
                msg, sev = "Sehr feucht – lüften empfohlen.", "warn"
            else:
                msg, sev = "Feuchtigkeit im optimalen Bereich.", "ok"
            return SensorReading("Luftfeuchtigkeit", hum, "%", msg, sev)
        except Exception as e:
            hum = random.uniform(40, 60)
            return SensorReading("Luftfeuchtigkeit", hum, "%", f"Fehler: {e}", "warn")

    # Helligkeit (BH1750)
    def _light_sensor(self):
        try:
            data = bus.read_i2c_block_data(BH1750_ADDR, 0x20, 2)
            lux = (data[0] << 8 | data[1]) / 1.2
            if lux < 60:
                msg, sev = "Licht an? Es ist ziemlich dunkel.", "warn"
            elif lux > 600:
                msg, sev = "Sehr hell – eventuell Blendgefahr.", "warn"
            else:
                msg, sev = "Helligkeit ist angenehm.", "ok"
            return SensorReading("Helligkeit", lux, "Lux", msg, sev)
        except Exception as e:
            lux = random.uniform(10, 400)
            return SensorReading("Helligkeit", lux, "Lux", f"I2C-Fehler: {e}", "warn")

    # Bewegung (PIR)
    def _motion_sensor(self):
        try:
            motion = GPIO.input(MOTION_PIN)
            if motion:
                return SensorReading("Bewegung", 100, "%", "Bewegung erkannt!", "alert")
            else:
                return SensorReading("Bewegung", 0, "%", "Alles ruhig.", "ok")
        except Exception as e:
            return SensorReading("Bewegung", 0, "%", f"GPIO Fehler: {e}", "warn")


def run_showcase(iterations=None, delay=2.5, metrics_port=8000):
    showcase = SensorShowcase()
    start_http_server(metrics_port)
    print(
        f"Prometheus-Metriken werden unter http://localhost:{metrics_port}/metrics bereitgestellt."
    )
    try:
        iteration = 0
        while iterations is None or iteration < iterations:
            iteration += 1
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{ts}] Sensorrunde {iteration}")
            for reading in showcase.poll():
                print("  " + reading.render())
                showcase.update_metrics(reading)
            time.sleep(delay)
    except KeyboardInterrupt:
        print("\nBeendet durch Benutzer.")
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    run_showcase()

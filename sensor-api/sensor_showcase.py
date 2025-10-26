"""Interactive sensor showcase.

This module extends the sensor demo setup with a simple event loop that
simulates readings from a couple of physical sensors.  It can be executed on
any machine without Raspberry Pi hardware but still gives immediate visual
feedback on the console.  The goal is to keep the workflow lightweight: start
it, and something happens right away.

Usage::

    python3 sensor_showcase.py --iterations 10 --delay 1.5

The script prints colourful status lines for the virtual temperature, light and
motion sensors and highlights unusual values.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import argparse
import random
import time
from typing import Callable, Iterable, List


@dataclass
class SensorReading:
    """Single sensor reading that can be printed on the console."""

    sensor: str
    value: float
    unit: str
    message: str
    severity: str = "info"

    def render(self) -> str:
        """Return a human friendly representation with a small icon."""

        icons = {
            "info": "ℹ️",
            "ok": "✅",
            "warn": "⚠️",
            "alert": "🚨",
        }
        icon = icons.get(self.severity, icons["info"])
        return f"{icon} {self.sensor}: {self.value:.1f} {self.unit} – {self.message}"


class SensorShowcase:
    """Generate playful readings for a couple of sensors."""

    def __init__(self) -> None:
        # Each callable returns a SensorReading instance.
        self._sensors: List[Callable[[], SensorReading]] = [
            self._temperature_sensor,
            self._light_sensor,
            self._motion_sensor,
        ]

    def poll(self) -> Iterable[SensorReading]:
        """Yield one reading per configured sensor."""

        for sensor in self._sensors:
            yield sensor()

    @staticmethod
    def _temperature_sensor() -> SensorReading:
        value = random.uniform(19.0, 31.5)
        if value > 29.5:
            severity = "alert"
            message = "Lüftung einschalten!"
        elif value > 26.0:
            severity = "warn"
            message = "Ganz schön warm hier."
        else:
            severity = "ok"
            message = "Temperatur im Wohlfühlbereich."
        return SensorReading("Temperatur", value, "°C", message, severity)

    @staticmethod
    def _light_sensor() -> SensorReading:
        value = random.uniform(10.0, 750.0)
        if value < 60.0:
            severity = "warn"
            message = "Licht an? Es ist ziemlich dunkel."
        elif value > 600.0:
            severity = "warn"
            message = "Sehr hell – eventuell Blendgefahr."
        else:
            severity = "ok"
            message = "Helligkeit ist angenehm."
        return SensorReading("Helligkeit", value, "Lux", message, severity)

    @staticmethod
    def _motion_sensor() -> SensorReading:
        value = random.random()
        if value > 0.8:
            severity = "alert"
            message = "Bewegung erkannt! Sicherheitscheck durchführen."
        elif value > 0.4:
            severity = "ok"
            message = "Leichte Aktivität im Raum."
        else:
            severity = "ok"
            message = "Alles ruhig."
        return SensorReading("Bewegung", value * 100, "%", message, severity)


def run_showcase(iterations: int, delay: float) -> None:
    """Run the demo loop with the given number of iterations."""

    showcase = SensorShowcase()
    for _ in range(iterations):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{timestamp}] Sensorrunde")
        for reading in showcase.poll():
            print("  " + reading.render())
        time.sleep(delay)


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Starte die Sensor-Demo-Schleife.")
    parser.add_argument(
        "--iterations",
        type=int,
        default=5,
        help="Wie oft eine Sensorrunde ausgeführt wird (Standard: 5).",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Wartezeit zwischen zwei Runden in Sekunden (Standard: 2.0).",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    run_showcase(args.iterations, args.delay)

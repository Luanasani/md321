from http.server import BaseHTTPRequestHandler, HTTPServer
from time import sleep
import threading
import json
from typing import Any, Dict

import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, reason_code, properites):
    print(f'Connected to MQTT Broker with result {reason_code}')
    # client.subscribe('$SYS/#')


def on_message(client, userdata, msg: object):
    print(msg.topic + ' ' + str(msg.payload))


mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect('172.17.0.1', 1883, 60)

from air_sensor import AirSensor
from light_sensor import LightSensor
from distance_sensor import DistanceSensor


airSensor = AirSensor()
lightSensor = LightSensor()
distanceSensor = DistanceSensor()


host = '0.0.0.0'
port = 8080


latest_values: Dict[str, Any] = {
    'light': None,
    'distance': None,
}
latest_values_lock = threading.Lock()


def _cache_value(sensor: str, value: Any) -> Any:
    with latest_values_lock:
        latest_values[sensor] = value
    return value


def _get_cached_value(sensor: str):
    with latest_values_lock:
        return latest_values.get(sensor)


def get_light_value() -> float:
    cached_value = _get_cached_value('light')
    if cached_value is not None:
        return cached_value

    try:
        light_value = round(lightSensor.readLight(), 2)
    except Exception as exc:  # pylint: disable=broad-except
        print(f'Failed to read light sensor: {exc}')
        raise

    return _cache_value('light', light_value)


class Server(BaseHTTPRequestHandler):
    def sendJSON(self, object: object, code: int = 200):
        self.send_response(code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Vary', 'Origin')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(object).encode())


    def do_GET(self):
        if self.path == '/':
            air = airSensor.readAir()
            try:
                light_value = get_light_value()
            except Exception:
                light_value = None

            with latest_values_lock:
                distance_value = latest_values.get('distance')

            response: Dict[str, Any] = {
                'status': 'Ok',
                'light': light_value,
                'air': air.__dict__,
            }

            if distance_value is not None:
                response['distance'] = distance_value

            self.sendJSON(response)
            return

        if self.path == '/metrics':
            air = airSensor.readAir()
            try:
                light_value = get_light_value()
            except Exception:
                light_value = 'nan'

            with latest_values_lock:
                distance_value = latest_values.get('distance')

            metrics_lines = [
                '# HELP light measured light intensity in lux',
                '# TYPE light gauge',
                f'light {light_value}',
                '# HELP air_temperature measured temperature in celcius',
                '# TYPE air_temperature gauge',
                f'air_temperature {air.temperature}',
                '# HELP air_humidity measured humidity in percent',
                '# TYPE air_humidity gauge',
                f'air_humidity {air.humidity}',
            ]

            if distance_value is not None:
                metrics_lines.extend([
                    '# HELP distance measured distance to obstacle in centimeters',
                    '# TYPE distance gauge',
                    f'distance {distance_value}',
                ])

            response = '\n'.join(metrics_lines)
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', '*')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.send_header('Vary', 'Origin')
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(response.encode())
            mqtt_client.publish('serverPi/metrics', 'requested', qos=2)


def readLightSensor(delay: float = 5):
    while True:
        try:
            lux = round(lightSensor.readLight(), 2)
            print(f'Light intensity: {lux} lux')
            _cache_value('light', lux)
            mqtt_client.publish('mondaymorning/sensors/light', lux, qos=2)
        except Exception as exc:  # pylint: disable=broad-except
            print(f'Unable to read from BH1750 sensor: {exc}')
        sleep(delay)


def readDistanceSensor(delay: float = 1):
    while True:
        try:
            distance = distanceSensor.read()
            print(f'Distance: {distance} cm')
            _cache_value('distance', distance)
            mqtt_client.publish('mondaymorning/sensors/distance', distance, qos=2)
        except Exception as exc:  # pylint: disable=broad-except
            print(f'Unable to read distance sensor value: {exc}')
        sleep(delay)

def main():
    webServer = HTTPServer((host, port), Server)
    print(f'Server started and listen to {host}:{port}')

    distanceSensorThread = threading.Thread(target=readDistanceSensor, args=(0.3,), daemon=True)
    lightSensorThread = threading.Thread(target=readLightSensor, args=(2,), daemon=True)
    distanceSensorThread.start()
    lightSensorThread.start()

    try:
        mqtt_client.loop_start()
        mqtt_client.publish('mondaymorning/up', 'true', qos=2)
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print('Server stopped.')

if __name__ == '__main__':
    main()

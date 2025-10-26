from http.server import BaseHTTPRequestHandler, HTTPServer
from time import sleep
import threading
import json

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
            self.sendJSON({
                'status': 'Ok',
                'light': lightSensor.readLight(),
                'air': air.__dict__
            })

        if self.path == '/metrics':
            air = airSensor.readAir()
            response = f'\
# HELP light measured light intensity in lux\n\
# TYPE light gauge\n\
light {lightSensor.readLight()}\n\
# HELP air_temperature measured temperature in celcius\n\
# TYPE air_temperature gauge\n\
air_temperature {air.temperature}\n\
# HELP air_humidity measured humidity in percent\n\
# TYPE air_humidity gauge\n\
air_humidity {air.humidity}'
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', '*')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.send_header('Vary', 'Origin')
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(response.encode())
            mqtt_client.publish('serverPi/metrics', 'requested', qos=2)

def readDistanceSensor(delay: float = 1):
    while True:
        distance = distanceSensor.read()
        print(f'Distance: {distance} cm')
        mqtt_client.publish('mondaymorning/sensors/distance', distance, qos=2)
        sleep(delay)

def main():
    webServer = HTTPServer((host, port), Server)
    print(f'Server started and listen to {host}:{port}')

    distanceSensorThread = threading.Thread(target=readDistanceSensor, args=(0.3,), daemon=True)
    distanceSensorThread.start()

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
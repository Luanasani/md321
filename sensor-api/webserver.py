from http.server import BaseHTTPRequestHandler, HTTPServer

from air_sensor import AirSensor

airSensor = AirSensor()

host = '0.0.0.0'
port = 8080

class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        values = airSensor.readAir()
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(bytes(f'Temperature: {values.temperature}°C Humidity: {values.humidity}%', 'utf-8'))

def main():
    webServer = HTTPServer((host, port), Server)
    print(f'Server started and listen to {host}:{port}')

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print('Server stopped.')

if __name__ == '__main__':
    main()
from time import sleep
import RPi.GPIO as GPIO
import threading
import dht11

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.cleanup()
    
# read data using pin 14

class AirSensor():
    def update(self):
        while True:
            readout = self.instance.read()
            valid = readout.is_valid()
            if valid:  # read until valid values
                print(f'Temperature: {readout.temperature}°C Humidity: {readout.humidity}%')
                self.result = readout
            else:
                sleep(2)

    def __init__(self):
        self.instance = dht11.DHT11(pin = 7)
        self.result = self.instance.read()
        print(self.result.__dict__)

        threading.Thread(target=self.update, daemon=True).start()
    
    def readAir(self):
        return self.result

 
from time import sleep

from air_sensor import AirSensor

airSensor = AirSensor()

while True:
    result = airSensor.readAir()
    print(result.__dict__)
    sleep(5)
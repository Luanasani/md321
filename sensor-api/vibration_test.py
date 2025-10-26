import RPi.GPIO as GPIO
import time

# Pin für den Buzzer (BOARD-Modus = physikalisch Pin 33 = GPIO13)
buzzer_pin = 13

# Töne in Frequenz (Hz)
notes = {
    'C': 523,
    'D': 587,
    'E': 659,
    'F': 698,
    'G': 784,
    'A': 880,
    'B': 988,
    'C_high': 1047,
    'D_high': 1175,
    'E_high': 1319,
    ' ': 0  # Pause
}

# Melodie (Teil von „Ode an die Freude“)
melody = [
    'E', 'E', 'F', 'G',
    'G', 'F', 'E', 'D',
    'C', 'C', 'D', 'E',
    'E', 'D', 'D', ' '
]

# Dauer jeder Note (Sekunden)
note_duration = 0.3

# Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(buzzer_pin, GPIO.OUT)

# PWM-Objekt erstellen
pwm = GPIO.PWM(buzzer_pin, 440)  # Initialfrequenz
pwm.start(0)

try:
    for note in melody:
        freq = notes[note]
        if freq == 0:
            pwm.ChangeDutyCycle(0)
        else:
            pwm.ChangeFrequency(freq)
            pwm.ChangeDutyCycle(200)  # 50% Duty für hörbaren Ton
        time.sleep(note_duration)
        pwm.ChangeDutyCycle(0)
        time.sleep(0.05)  # kurze Pause zwischen Noten

finally:
    pwm.stop()
    GPIO.cleanup()

#!/usr/bin/python3
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
import random
import board, busio
import adafruit_character_lcd.character_lcd_i2c as character_lcd

# --- LCD Setup ---
lcd_columns = 16
lcd_rows = 2
i2c = board.I2C()
lcd = character_lcd.Character_LCD_I2C(i2c, lcd_columns, lcd_rows, address=0x21)
lcd.clear()

# --- Buzzer Setup ---
buzzer_pin = 18  # BCM Pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzer_pin, GPIO.OUT)

# --- Button Matrix Setup ---
class ButtonMatrix():
    def __init__(self):
        self.buttonIDs = [[4,3,2,1],[8,7,6,5],[12,11,10,9],[16,15,14,13]]
        self.rowPins = [13,15,29,31]
        self.columnPins = [33,35,37,22]

        for i in range(len(self.rowPins)):
            GPIO.setup(self.rowPins[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        for j in range(len(self.columnPins)):
            GPIO.setup(self.columnPins[j], GPIO.OUT)
            GPIO.output(self.columnPins[j], 1)

    def get_pressed_button(self):
        for j in range(len(self.columnPins)):
            GPIO.output(self.columnPins[j],0)
            for i in range(len(self.rowPins)):
                if GPIO.input(self.rowPins[i]) == 0:
                    GPIO.output(self.columnPins[j],1)
                    time.sleep(0.2)  # Entprellung
                    return self.buttonIDs[i][j]
            GPIO.output(self.columnPins[j],1)
        return None

# --- Spiel Setup ---
matrix = ButtonMatrix()
score = 0
rounds = 5

try:
    lcd.message = "Zielschießen Spiel\nBereit..."
    time.sleep(2)
    lcd.clear()

    for rnd in range(1, rounds+1):
        target_button = random.choice(sum(matrix.buttonIDs, []))  # zufälliger Button
        lcd.clear()
        lcd.message = f"Runde {rnd}/{rounds}\nDrück: {target_button}"
        
        pressed = None
        while pressed != target_button:
            pressed = matrix.get_pressed_button()
            if pressed is not None and pressed != target_button:
                # Falscher Tastendruck → Buzzer
                GPIO.output(buzzer_pin, True)
                time.sleep(0.2)
                GPIO.output(buzzer_pin, False)
                lcd.clear()
                lcd.message = f"Falsch!\nRichtige: {target_button}"
                time.sleep(1)
                lcd.clear()
                lcd.message = f"Runde {rnd}/{rounds}\nDrück: {target_button}"

        # Richtiger Tastendruck
        score += 1
        lcd.clear()
        lcd.message = f"Richtig!\nPunkt: {score}"
        time.sleep(1)

    lcd.clear()
    lcd.message = f"Spiel vorbei!\nPunkte: {score}/{rounds}"
    time.sleep(5)

except KeyboardInterrupt:
    lcd.clear()
    lcd.message = "Abgebrochen"
finally:
    GPIO.cleanup()
    lcd.clear()

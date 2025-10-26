#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import random
import RPi.GPIO as GPIO
import board, busio
import adafruit_character_lcd.character_lcd_i2c as character_lcd
from adafruit_ht16k33.segments import Seg7x4

# --- I2C Setup ---
i2c = board.I2C()
# 7-Segment Display
seg_display = Seg7x4(i2c, address=0x70)
seg_display.fill(0)
# LCD Display
lcd_columns = 16
lcd_rows = 2
lcd = character_lcd.Character_LCD_I2C(i2c, lcd_columns, lcd_rows, address=0x21)
lcd.clear()

# --- GPIO Setup ---
buzzer_pin = 18
vibration_pin = 27
button_pins = [5, 6, 13, 19]  # Taster für Zahlen 0-3

GPIO.setup(buzzer_pin, GPIO.OUT)
GPIO.setup(vibration_pin, GPIO.OUT)
for pin in button_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# --- Funktionen ---
def buzzer_beep(times=1, duration=0.2):
    for _ in range(times):
        GPIO.output(buzzer_pin, True)
        time.sleep(duration)
        GPIO.output(buzzer_pin, False)
        time.sleep(0.1)

def vibrate(duration=0.5):
    GPIO.output(vibration_pin, True)
    time.sleep(duration)
    GPIO.output(vibration_pin, False)

def show_number_7seg(number):
    seg_display.fill(0)
    str_num = str(int(number)).rjust(4)
    for i, char in enumerate(str_num):
        seg_display[i] = char if char != ' ' else ' '
    seg_display.show()

def show_lcd_message(message):
    lcd.clear()
    lcd.message = message

# --- Spiel-Logik ---
try:
    show_lcd_message("Drücke STRG+C\nzum Stoppen")
    time.sleep(2)
    
    while True:
        # Zufällige Zahl auswählen
        number = random.randint(0, 3)
        show_lcd_message(f"Drücke Zahl:\n{number}")
        start_time = time.time()

        pressed = False
        while not pressed:
            for i, pin in enumerate(button_pins):
                if GPIO.input(pin):
                    reaction_time = time.time() - start_time
                    if i == number:
                        # richtig gedrückt
                        show_lcd_message(f"Richtig!\n{reaction_time:.2f}s")
                        show_number_7seg(reaction_time)
                    else:
                        # falsch gedrückt
                        show_lcd_message("FALSCH!")
                        buzzer_beep(2, 0.2)
                        vibrate(0.5)
                        show_number_7seg(0)
                    pressed = True
                    time.sleep(1)
                    break

except KeyboardInterrupt:
    lcd.clear()
    lcd.message = "Spiel beendet"
finally:
    GPIO.cleanup()
    seg_display.fill(0)
    seg_display.show()
    lcd.clear()

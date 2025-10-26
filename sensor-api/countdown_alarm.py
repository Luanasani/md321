import time
import RPi.GPIO as GPIO
import board, busio
import adafruit_character_lcd.character_lcd_i2c as character_lcd

# --- GPIO Setup ---
GPIO.setmode(GPIO.BCM)
light_pin = 27
GPIO.setup(light_pin, GPIO.IN)

# --- LCD Setup ---
lcd_columns = 16
lcd_rows = 2
i2c = board.I2C()
lcd = character_lcd.Character_LCD_I2C(i2c, lcd_columns, lcd_rows, address=0x21)
lcd.clear()

try:
    while True:
        light = GPIO.input(light_pin)  # 1 = hell, 0 = dunkel
        
        lcd.clear()
        if light:  # hell
            lcd.message = "Modus: HELL\nBitte schatten!"
        else:  # dunkel
            lcd.message = "Modus: DUNKEL\nAlles OK"
        
        time.sleep(2)

except KeyboardInterrupt:
    lcd.clear()
finally:
    GPIO.cleanup()
    lcd.clear()

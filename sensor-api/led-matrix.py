#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# License: https://github.com/rm-hull/luma.led_matrix/blob/master/LICENSE.rst

import time
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.legacy import show_message
from luma.core.legacy.font import proportional, CP437_FONT

def main(cascaded=1, block_orientation=0, rotate=0):
    # Matrix-Gerät erstellen
    serial = spi(port=0, device=0, gpio=noop())  # Achte auf 'device=0' statt 1
    device = max7219(serial, cascaded=cascaded, block_orientation=block_orientation, rotate=rotate)

    print("[-] Matrix initialized")

    msg = "Hallo Welt"
    print("[-] Printing: %s" % msg)

    show_message(device, msg, fill="white", font=proportional(CP437_FONT), scroll_delay=0.1)

if __name__ == "__main__":
    main()

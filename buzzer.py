#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
A Buzzer implementation.
"""

import time
import RPi.GPIO as GPIO

BUZZER_ON_INTERVAL = 500
BUZZER_OFF_INTERVAL = 5000
MAX_BUZZ_DIVIDER = 50

class Buzzer:
    """Represents a Buzzer connected to the system"""

    def __init__(self, pin):
        self.pin = pin
        self.is_buzzing = False
        self.buzzing_state = False
        self.in_state_since = -1
        self.is_low_active = True
        self.buzz_off_divider = 1

        GPIO.setup(self.pin, GPIO.OUT)

    def enable_buzzer(self):
        """Turns the buzzer on"""

        if self.is_low_active:
            GPIO.output(self.pin, GPIO.LOW)
        else:
            GPIO.output(self.pin, GPIO.HIGH)

    def disable_buzzer(self):
        """Turns the buzzer off"""

        if self.is_low_active:
            GPIO.output(self.pin, GPIO.HIGH)
        else:
            GPIO.output(self.pin, GPIO.LOW)

    def set_buzzing(self, state):
        """Changes the buzzing state"""

        self.buzzing_state = state
        self.is_buzzing = state

    def update(self):
        """Buzzes the Buzzer in a certain interval"""

        if self.buzzing_state:
            now = time.time()

            buzzer_interval = BUZZER_OFF_INTERVAL / self.buzz_off_divider
            if self.is_buzzing:
                buzzer_interval = BUZZER_ON_INTERVAL

            if (now - self.in_state_since) > buzzer_interval:
                self.in_state_since = now
                self.buzz_off_divider += 1
                if self.buzz_off_divider > MAX_BUZZ_DIVIDER:
                    self.set_buzzing(false)
                if self.is_buzzing:
                    self.disable_buzzer()
                else:
                    self.enable_buzzer()
        else:
            self.disable_buzzer()

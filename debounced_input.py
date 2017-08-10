#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
A debounced input implementation.
"""

import RPi.GPIO as GPIO

class DebouncedInput:
    """Represents a GPIO input that is debounced"""

    def __init__(self, pin):
        self.pin = pin
        self.current_value = -1
        self.input_counter = 0
        self.needed_inputs_to_change = 5
        self.check_interval = 0.5
        self.time_since_last_check = 0

        GPIO.setup(self.pin, GPIO.IN)

    def check(self):
        """Check the state of the input"""

        result = False

        new_value = GPIO.input(self.pin)

        if self.current_value != new_value:
            self.input_counter += 1
            if self.input_counter > self.needed_inputs_to_change:
                result = True
                self.current_value = new_value
        else:
            self.input_counter = 0

        return result

    def has_changed(self, delta_time):
        """Returns True if the button state has changed"""

        result = False

        self.time_since_last_check = self.time_since_last_check + delta_time
        if self.time_since_last_check < 0 or self.time_since_last_check > self.check_interval:
            self.time_since_last_check = 0

            result = self.check()


        return result

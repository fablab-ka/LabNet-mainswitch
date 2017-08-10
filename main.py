#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Lab switch controller
"""

import time
import logging
import requests

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! " +
          "This is probably because you need superuser privileges. "+
          "You can achieve this by using 'sudo' to run your script")

from debounced_input import DebouncedInput
from buzzer import Buzzer

LOG_FILENAME = "/var/log/labnet_mainswitch.log"
SWITCH_PIN = 14
PEN_SWITCH_PIN = 15
BUZZER_PIN = 18
LABNET_URL = "http://192.168.1.6"
STATE_API_URL = "http://192.168.1.6:3000"
STATE_API_HEADERS = {'clientId': 'supersecret'}
CHECKS_PER_SECOND = 60


class Main:
    """Main handles in- and output signals for the LabSwitch installation."""

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        self.switch_input = DebouncedInput(SWITCH_PIN)
        self.pen_switch_input = DebouncedInput(PEN_SWITCH_PIN)
        self.buzzer = Buzzer(BUZZER_PIN)

        logging.basicConfig(
            filename=LOG_FILENAME,
            format='%(asctime)s %(message)s',
            level=logging.DEBUG)

    @classmethod
    def send_update(cls, state):
        """send a state update to the API."""

        try:
            requests.get(LABNET_URL + "/api/" + state)

            if state == "lab/on":
                requests.post(STATE_API_URL, json={"is_open": True}, headers=STATE_API_HEADERS)
            else:
                requests.post(STATE_API_URL, json={"is_open": False}, headers=STATE_API_HEADERS)
        except requests.exceptions.RequestException as ex:
            logging.info("http request failed:")
            logging.error(ex)
        else:
            logging.info("http request succeeded: " + state)

    @classmethod
    def toggle_lab(cls, state):
        """Toggle the state lab/on -> lab/off or lab/off -> lab/on."""

        if state == 0:
            Main.send_update("lab/off")
        else:
            Main.send_update("lab/on")

    def loop(self, delta_time):
        """Executes one iteration of the loop"""

        self.buzzer.update()

        if self.switch_input.has_changed(delta_time):
            Main.toggle_lab(self.switch_input.current_value)

            self.buzzer.set_buzzing(True)

        if self.pen_switch_input.has_changed(delta_time):
            self.buzzer.set_buzzing(False)

    def run(self):
        """Starts the main loop."""

        logging.info("daemon started")

        last_check_time = -1

        while True:
            current_time = time.time()
            delta_time = current_time - last_check_time
            last_check_time = current_time

            self.loop(delta_time)

            sleep_time = 1./CHECKS_PER_SECOND - (current_time - last_check_time)
            if sleep_time > 0:
                time.sleep(sleep_time)


if __name__ == "__main__":
    Main().run()

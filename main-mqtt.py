#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Lab switch controller mqtt
"""

import time
import logging
import paho.mqtt.client as mqtt

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
MQTT_HOST = "http://felicia.flka.space"
MQTT_PORT = 1883
CHECKS_PER_SECOND = 60

TOPIC_POLL = "/FLKA/system/switch/poll"
TOPIC_PUBLISH = "/FLKA/system/switch/stat"


class Main:
    """Main handles in- and output signals for the LabSwitch installation."""

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        self.switch_input = DebouncedInput(SWITCH_PIN)
        self.buzzer = Buzzer(BUZZER_PIN)

        logging.basicConfig(
            filename=LOG_FILENAME,
            format='%(asctime)s %(message)s',
            level=logging.DEBUG)

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(MQTT_HOST, MQTT_PORT, 60)

    def on_message(self, client, userdata, msg):
        print ("Message received: " + msg.topic + " " + str(msg.payload))

        value = "ON"
        if self.switch_input.current_value == 0:
            value = "OFF"

        try:
            client.publish(TOPIC_PUBLISH, payload=value)
        except Exception as ex:
            logging.info("mqtt publish failed:")
            logging.error(ex)


    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        client.subscribe(TOPIC_POLL)

    def send_update(self):
        """send a state update to the API."""

        try:
            self.client.publish(TOPIC_PUBLISH, payload=self.switch_input.current_value)
        except Exception as ex:
            logging.info("http request failed:")
            logging.error(ex)

    def loop(self, delta_time):
        """Executes one iteration of the loop"""

        self.buzzer.update()

        if self.switch_input.has_changed(delta_time):
            self.send_update()

            self.buzzer.set_buzzing(True)

        if self.pen_switch_input.has_changed(delta_time):
            self.buzzer.set_buzzing(False)

    def run(self):
        """Starts the main loop."""

        logging.info("daemon started")

        last_check_time = -1

        self.client.loop_start()

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

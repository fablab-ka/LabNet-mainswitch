#!/usr/bin/python

import sys
import requests
import RPi.GPIO as GPIO
import time

switch_pin = 14
switch_delay = 0.5
prev_input = -1
labnet_url = "http://labnet.lab.flka.de"

GPIO.setmode(GPIO.BCM)
GPIO.setup(switch_pin,GPIO.IN)

def query_api(arg):
  try:
    requests.get(labnet_url + "/api/" + arg)
  except requests.exceptions.RequestException as e:
    print "http request failed:"
    print e
  else:
    print "http request succeeded: " + arg
  return

def toggle_lab(state):
  if ( state == 0 ):
    query_api("lab/off")
  else:
    query_api("lab/on")
  return

print "daemon started"

while True:
  input = GPIO.input(switch_pin)  
  if ( prev_input != input ):
    toggle_lab(input)
    prev_input = input
  time.sleep(switch_delay)



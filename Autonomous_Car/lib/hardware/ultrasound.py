#!/usr/bin/env python3
#coding: utf-8
#
# Author: PALACIOS Nicolas
#


# ======================================================================
# Imports
# ======================================================================
import sys
import time

import RPi.GPIO as GPIO

from lib.config import Config
import logging as log; log.basicConfig(level=log.DEBUG)



# ======================================================================
# Class
# ======================================================================
class Ultrasound(object):
	# ==================================================================
	# Constants
	# ==================================================================
	def CONFIG_FILE(self):
		return "/home/pi/projet/lib/hardware/ultrasound.conf"


	# ==================================================================
	# Primitives
	# ==================================================================
	def __init__(self):
		config = Config(self.CONFIG_FILE())
		self.trigger_pin = 16
		self.echo_pin = 18

		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(self.trigger_pin, GPIO.OUT)
		GPIO.setup(self.echo_pin, GPIO.IN)

		# waiting for settle
		time.sleep(1)


	# def __del__(self):
	# 	GPIO.cleanup(self.trigger_pin)
	# 	GPIO.cleanup(self.echo_pin)



	# ==================================================================
	# Methods
	# ==================================================================
	def get_distance(self):
		''' return distance in centimeters '''
		# log.debug("Ultrasound: computing distance.")
		GPIO.output(self.trigger_pin, GPIO.HIGH)
		time.sleep(0.00001)
		GPIO.output(self.trigger_pin, GPIO.LOW)
		pulse_start_time = None
		pulse_end_time   = None
		while ((pulse_start_time == None) or (pulse_end_time == None)):
			while(GPIO.input(self.echo_pin) == 0):
				pulse_start_time = time.time()
			while(GPIO.input(self.echo_pin) == 1):
				pulse_end_time = time.time()
			time.sleep(0.00001)
		pulse_duration = pulse_end_time - pulse_start_time
		distance = round(pulse_duration * 17150, 2)

		return distance


# ======================================================================
# Main
# ======================================================================
def main():
	if(len(sys.argv) < 3):
		log.error("Usage: python3 ultrasound.py trigger_pin echo_pin")
		sys.exit(1)
	print(Ultrasound(int(sys.argv[1]), int(sys.argv[2])).get_distance())


# Execution or import
if(__name__ == "__main__"):
	main()
	sys.exit(0)

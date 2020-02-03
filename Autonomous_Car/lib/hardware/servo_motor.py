#! /usr/bin/env python3
# coding: utf-8
#
# Author:
#


# ======================================================================
# Imports
# ======================================================================
import sys
import time

import lib.hardware.PCA9685 as pca9685

import logging as log; log.basicConfig(level=log.DEBUG)

# ======================================================================
# Constants
# ======================================================================


# ======================================================================
# Global variables
# ======================================================================


# ======================================================================
# Class
# ======================================================================
class Servo_motor(object):
	#===================================================================
	# Constants
	#===================================================================


	# ==================================================================
	# Static variables
	# ==================================================================
	_pwm = pca9685.PWM(bus_number=1)


	# ==================================================================
	# Primitives
	# ==================================================================
	def __init__(self, channel, default_pwm, min_pwm, max_pwm, offset=0):
		self.channel 	= channel
		self.value 		= default_pwm + offset
		self.min_pwm 	= min_pwm + offset
		self.max_pwm	= max_pwm + offset
		self._pwm.write(self.channel, 0, self.value)


	# ==================================================================
	# Methods
	# ==================================================================
	def set_value(self, value):
		if(value <= self.max_pwm and value >= self.min_pwm):
			self._pwm.write(self.channel, 0, value)
		else:
			log.error("Servo_motor: set_value: Invalid value.")


	def increase_x(self, value=10):
		if(self.value != self.max_pwm):
			if(self.value + value >= self.max_pwm):
				self.value = self.max_pwm
			else:
				self.value += value
			self._pwm.write(self.channel, 0, self.value)


	def decrease_x(self, value=10):
		if(self.value != self.min_pwm):
			if(self.value - value <= self.min_pwm):
				self.value = self.min_pwm
			else:
				self.value -= value
			self._pwm.write(self.channel, 0, self.value)


# ======================================================================
# Main
# ======================================================================
def main():
	print("### Servo_motor ###")


# Execution or import
if(__name__ == "__main__"):
	main()
	sys.exit(0)

#! /usr/bin/env python3
# coding: utf-8
#
# Author: Palacios Nicolas inspired by SunFounder
#


# ======================================================================
# Imports
# ======================================================================
import sys
import time

import lib.hardware.servo_motor as servo_motor

from lib.config import Config
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
class Direction(object):
	#===================================================================
	# Constants
	#===================================================================
	def CONFIG_FILE(self):
		return "/home/pi/projetM2/Autonomous_Car/lib/hardware/direction.conf"

	def LEFT_PWM(self):
		return int(self._config.get("left_pwm", 320))
		# return 320
	def HOME_PWM(self):
		return int(self._config.get("home_pwm", 427))
		# return 427
	def RIGHT_PWM(self):
		return int(self._config.get("right_pwm", 500))
		# return 500
	def OFFSET(self):
		offset = self._config.get("offset")
		if offset == None:
			self._config.set("offset", 0)
			self._config.save()
			return 0
		return int(offset)


	# ==================================================================
	# Static variables
	# ==================================================================
	_config = None


	# ==================================================================
	# Primitives
	# ==================================================================
	def __init__(self):
		self._config = Config(self.CONFIG_FILE())

		self.servo = servo_motor.Servo_motor(channel=int(self._config.get("channel", "0")),
			default_pwm=self.HOME_PWM(), min_pwm=self.LEFT_PWM(),
			max_pwm=self.RIGHT_PWM(), offset=self.OFFSET())

		self.atr_home = self.HOME_PWM()
		self.offset = self.OFFSET()

	# ==================================================================
	# Private Methods
	# ==================================================================
	def map_angle(self, x, in_min, in_max, out_min, out_max):
		return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


	#TODO delete if not needed here for straight movement test
	def set_value(self, value = 427):
		self.servo.set_value(value + self.offset)
	# ==================================================================
	# Methods
	# ==================================================================
	def turn_left(self):
		self.servo.set_value(self.LEFT_PWM() + self.offset)

	def home(self):
		log.debug("set_val: " + str(self.atr_home + self.offset))
		self.servo.set_value(self.atr_home + self.offset)
		# if self.atr_home == self.HOME_PWM():
		# 	self.atr_home += 5
		# else:
		# 	self.atr_home -= 5

	def turn_right(self):
		self.servo.set_value(self.RIGHT_PWM() + self.offset)

	def turn(self, angle):
		angle = self.map_angle(angle, 0, 255, self.LEFT_PWM()+self.offset, self.RIGHT_PWM()+self.offset)
		self.servo.set_value(int(angle))
		log.debug("angle set to: " + str(int(angle))
			+ ", Home: " + str(self.HOME_PWM()))


# ======================================================================
# Main
# ======================================================================
def main():
	print("### Direction ###")
	dir = Direction()

	dir.turn_left()
	time.sleep(1)
	dir.home()
	time.sleep(1)
	dir.turn_right()
	time.sleep(1)
	dir.home()


# Execution or import
if(__name__ == "__main__"):
	main()
	sys.exit(0)

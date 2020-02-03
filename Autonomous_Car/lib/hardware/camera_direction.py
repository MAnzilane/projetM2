#! /usr/bin/env python3
# coding: utf-8
#
# Author: Palacios Nicolas
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
class Camera_direction(object):
	#===================================================================
	# Constants
	#===================================================================
	def CONFIG_FILE(self):
		return "/home/pi/projet/lib/hardware/camera_direction.conf"

	def HOME_X_PWM(self):
		return int(self._config.get("home_x_pwm"))
	def HOME_Y_PWM(self):
		return int(self._config.get("home_y_pwm"))
	def HALF_LEFT_PWM(self):
		return int(self._config.get("half_left_pwm"))
	def LEFT_PWM(self):
		return int(self._config.get("left_pwm"))
	def HALF_RIGHT_PWM(self):
		return int(self._config.get("half_right_pwm"))
	def RIGHT_PWM(self):
		return int(self._config.get("right_pwm"))
	def UP_PWM(self):
		return int(self._config.get("up_pwm"))
	def DOWN_PWM(self):
		return int(self._config.get("down_pwm"))


	# ==================================================================
	# Static variables
	# ==================================================================
	_config = None


	# ==================================================================
	# Primitives
	# ==================================================================
	def __init__(self):
		self._config = Config(self.CONFIG_FILE())

		self.servo_x = servo_motor.Servo_motor(channel=int(self._config.get("channel_x")),
			default_pwm=self.HOME_X_PWM(), min_pwm=self.LEFT_PWM(),
			max_pwm=self.RIGHT_PWM())
		self.servo_y = servo_motor.Servo_motor(channel=int(self._config.get("channel_y")),
			default_pwm=self.HOME_Y_PWM(), min_pwm=self.DOWN_PWM(),
			max_pwm=self.UP_PWM())


	# ==================================================================
	# Methods
	# ==================================================================
	def see_straight(self):
		self.servo_x.set_value(self.HOME_X_PWM())
		self.servo_y.set_value(self.HOME_Y_PWM())


	def see_straight_x(self):
		self.servo_x.set_value(self.HOME_X_PWM())


	def see_straight_y(self):
		self.servo_y.set_value(self.HOME_Y_PWM())


	def see_left(self):
		# inverted servo
		self.servo_x.set_value(self.RIGHT_PWM())


	def see_half_left(self):
		# inverted servo
		self.servo_x.set_value(self.HALF_RIGHT_PWM())


	def see_right(self):
		# inverted servo
		self.servo_x.set_value(self.LEFT_PWM())


	def see_half_right(self):
		# inverted servo
		self.servo_x.set_value(self.HALF_LEFT_PWM())


	def see_above(self):
		self.servo_y.set_value(self.UP_PWM())



	def see_above_left(self):
		# inverted servo
		self.servo_x.set_value(self.HALF_RIGHT_PWM())
		self.servo_y.set_value(self.UP_PWM())

	def see_above_right(self):
		self.servo_x.set_value(self.HALF_LEFT_PWM())
		self.servo_y.set_value(self.UP_PWM())

	def see_below(self):
		self.servo_y.set_value(self.DOWN_PWM())


	def see_below_left(self):
		self.servo_x.set_value(self.HALF_RIGHT_PWM())
		self.servo_y.set_value(self.DOWN_PWM())

	def see_below_right(self):
		self.servo_x.set_value(self.HALF_LEFT_PWM())
		self.servo_y.set_value(self.DOWN_PWM())


	def set_value(self, value, servo):
		if(servo == 'x'):
			self.servo_x.set_value(value)
		elif(servo == 'y'):
			self.servo_y.set_value(value)
		else:
			log.error("Camera_direction: set_value: value servo motor choosen.")


# Execution or import
if(__name__ == "__main__"):
	print("No main defined.")
	sys.exit(0)

#! /usr/bin/env python3
# coding: utf-8
#
# Author: Couzon Florent
#


# ======================================================================
# Imports
# ======================================================================
import logging as log; log.basicConfig(level=log.DEBUG)
import sys
from lib.hardware.dc_motor import DC_Motor
import time

from lib.config import Config

# ======================================================================
# Constants
# ======================================================================


# ======================================================================
# Global variables
# ======================================================================


# ======================================================================
# Class
# ======================================================================
class Wheel_Motors(object):
	#===================================================================
	# Constants
	#===================================================================
	def START_SPEED(self):
		return 60

	def CONFIG_FILE(self):
		return "/home/pi/projet/lib/hardware/dc_motor.conf"

	# ==================================================================
	# Static variables
	# ==================================================================


	# ==================================================================
	# Primitives
	# ==================================================================
	def __init__(self):

		config = Config(self.CONFIG_FILE())

		self.left_wheel    = DC_Motor(int(config.get("motor_left_0", "11")),
			int(config.get("motor_left_1", "12")),
			int(config.get("speed_channel_left", "4")))

		self.right_wheel   = DC_Motor(int(config.get("motor_right_0", "13")),
			int(config.get("motor_right_1", "15")),
			int(config.get("speed_channel_right", "5")))

		#strange behavior, need a first operation to run the next ones
		self.set_speed(self.START_SPEED())

	# ==================================================================
	# Methods
	# ==================================================================
	def set_speed(self, speed):
		self.left_wheel.set_speed(speed)
		self.right_wheel.set_speed(speed)

	def stop(self):
		self.left_wheel.stop()
		self.right_wheel.stop()

	def forward_speed(self, speed=None):
		self.left_wheel.forward_speed(speed)
		self.right_wheel.forward_speed(speed)

	def backward_speed(self, speed=None):
		self.left_wheel.backward_speed(speed)
		self.right_wheel.backward_speed(speed)

	def rotate_speed_right(self, speed=None):
		self.left_wheel.backward_speed(speed)
		self.right_wheel.forward_speed(speed)

	def rotate_speed_left(self, speed=None):
		self.left_wheel.forward_speed(speed)
		self.right_wheel.backward_speed(speed)


# ======================================================================
# Main
# ======================================================================
def test_wheel_motors():
	wheel_motors = Wheel_Motors()

	wheel_motors.forward_speed()
	time.sleep(3)

	wheel_motors.rotate_speed_left(100)
	time.sleep(6)

	wheel_motors.rotate_speed_right(100)
	time.sleep(6)

	wheel_motors.backward_speed(60)
	time.sleep(3)

	wheel_motors.forward_speed()
	time.sleep(6)

	wheel_motors.stop()

def test_speed():
	while(1):
		wheel_motors = Wheel_Motors()
		speed = int(input("give a speed value, -1 to stop"))
		if speed == -1:
			wheel_motors.stop()
			sys.exit(0)
		wheel_motors.forward_speed(speed)
		time.sleep(1)
		wheel_motors.stop()

def main():
	test_wheel_motors()

# Execution or import
if(__name__ == "__main__"):
	main()
	sys.exit(0)

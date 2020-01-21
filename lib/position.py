# !/usr/bin/env python3
# coding: utf-8
#
# Author:
#



# ======================================================================
# Imports
# ======================================================================
import logging as log; log.basicConfig(level=log.DEBUG)
from lib.hardware.enum_types import Direction_State
import math
import time


# ======================================================================
# Constants
# ======================================================================


# ======================================================================
# Global variables
# ======================================================================


# ======================================================================
# Class
# ======================================================================
class Position(object):

	#===================================================================
	# Constants
	#===================================================================


	# ==================================================================
	# Static variables
	# ==================================================================


	# ==================================================================
	# Primitives
	# ==================================================================
	def __init__(self, config):
		self.x = 0
		self.y = 0
		self.angle = 0
		self.start_time = None
		self.speed_value = None
		self.speed = None
		self.config = config


	def __str__ (self) :
		return "Position : (" + str(self.x) + "; " + str(self.y) + ") - angle = " + str(self.angle) + "°"


	# ==================================================================
	# Private methods
	# ==================================================================


	# ==================================================================
	# Methods
	# ==================================================================
	def start(self, speed_value, state):
		if self.start_time != None:
			self.stop()
		self.start_time = time.time()
		self.speed_value = speed_value
		self.speed = .31 * speed_value
		self.state = state

	def stop(self):
		if self.start_time != None:
			elapsed_time = time.time() - self.start_time
			distance = self.speed * elapsed_time

			self.angle += self.relativeAngle(elapsed_time)
			self.angle = self.angle % 360

			self.x += distance * math.cos(self.angle / 360 * 2 * math.pi)
			self.y += distance * math.sin(self.angle / 360 * 2 * math.pi)

			log.debug(str(self))
			self.start_time = None
		else:
			log.debug("already stoped")

	def relativeAngle(self, elapsed_time, direction = None):
		ref_speed = None
		ref_time = None
		if direction == None:
			direction = self.state

		if direction == Direction_State.RIGHT:
			ref_speed = int(self.config.get("right_speed", 60))
			ref_time = float(self.config.get("right_time", 1.))
		elif direction == Direction_State.LEFT:
			ref_speed = -int(self.config.get("left_speed", 60))
			ref_time = float(self.config.get("left_time", 1.))
		elif direction == Direction_State.STRAIGHT:
			return 0
		else:
			log.debug("unkown direction_state : " + str(self.state))
			return 0

		D = ref_speed * ref_time
		d = self.speed_value * elapsed_time
		log.debug("relative angle : " + str(d * 90 / D))
		return d * 90 / D


	def computeAngleTime(self, required_angle, speed = None, direction = None):
		ref_speed = None
		ref_time = None
		relativeAngle = None
		if direction == None:
			direction = self.state

		if direction == Direction_State.RIGHT:
			ref_speed = int(self.config.get("right_speed", 60))
			ref_time = float(self.config.get("right_time", 1.))
			relativeAngle = self.angle - required_angle % 360
			log.debug("relativeAngle : " + str(relativeAngle))
			if relativeAngle < 0 :
				relativeAngle = 360 + relativeAngle
				log.debug("correct relativeAngle : " + str(relativeAngle))
		elif direction == Direction_State.LEFT:
			ref_speed = int(self.config.get("left_speed", 60))
			ref_time = -float(self.config.get("left_time", 1.))
			relativeAngle = required_angle - self.angle % 360
			log.debug("relativeAngle : " + str(relativeAngle))
			if relativeAngle < 0 :
				relativeAngle = 360 + relativeAngle
				log.debug("correct relativeAngle : " + str(relativeAngle))
		elif direction == Direction_State.STRAIGHT:
			return 0
		else:
			log.debug("unkown direction_state : " + str(self.state))
			return 0

		if speed == None:
			speed = self.speed_value

		D = ref_speed * ref_time
		d = relativeAngle / 90 * D
		log.debug("d : " + str(d))

		return d / self.speed_value



	def set_angle(self, angle):
		pass


# ======================================================================
# Main
# ======================================================================
def main():
	pass

# Execution or import
if(__name__ == "__main__"):
	sys.exit(0)

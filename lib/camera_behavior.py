#! /usr/bin/env python3
# coding: utf-8
#
# Author:
#


# ======================================================================
# Imports
# ======================================================================
import sys

import lib.hardware.camera_direction as camera_direction_i
import lib.hardware.camera as camera_i
import lib.image_processing as image_processing_i

import logging as log; log.basicConfig(level=log.DEBUG)


# ======================================================================
# Class
# ======================================================================
class Camera_Behavior(object):
# ==================================================================
	# Primitives
	# ==================================================================
	def __init__(self):
		self.image_processing	= image_processing_i.Image_Processing(camera_i.Camera())
		self.camera_direction	= camera_direction_i.Camera_direction()
	# ==================================================================
	# Methods
	# ==================================================================
	def is_color_detected(self, color):
		detected_color = self.image_processing.major_color()
		log.debug("\tdetected color: " + str(detected_color))
		if (detected_color == None) or (detected_color != color):
			return False
		else:
			return True

	def get_frame(self):
		return self.image_processing.camera.get_frame()


# Execution or import
if(__name__ == "__main__"):
	sys.exit(0)

#! /usr/bin/env python3
# coding: utf-8
#
# Author:
#


# ======================================================================
# Imports
# ======================================================================
import sys

import cv2

import lib.hardware.camera_direction as cam_dir

import logging as log; log.basicConfig(level=log.DEBUG)


# ======================================================================
# Class
# ======================================================================
class Camera(object):
# ==================================================================
	# Primitives
	# ==================================================================
	def __init__(self):
		self.capture = cv2.VideoCapture(-1)


	# ==================================================================
	# Methods
	# ==================================================================
	def get_frame(self):
		ret, frame = self.capture.read()
		return frame


# Execution or import
if(__name__ == "__main__"):
	sys.exit(0)

# !/usr/bin/env python3
# coding: utf-8
#
# Author: Palacios Nicolas
#


# ======================================================================
# Imports
# ======================================================================
import sys

import cv2
import numpy as np

from lib.config import Config

import logging as log; log.basicConfig(level=log.DEBUG)


# ======================================================================
# Class
# ======================================================================
class Image_Processing(object):
	#===================================================================
	# Static variables
	#===================================================================
	_config = None


	#===================================================================
	# Constants
	#===================================================================
	def CONFIG_FILE(self):
		return "/home/pi/projet/lib/image_processing.conf"

	def DISPARITY_THRESHOLD(self):
		return int(self._config.get("disparity_threshold"))
	def DISPARITY_CPT(self):
		return int(self._config.get("disparity_cpt"))
	def BLACK_THRESHOLD(self):
		return int(self._config.get("black_threshold"))
	def WHITE_THRESHOLD(self):
		return int(self._config.get("white_threshold"))

	def COLORS(self):
		return {
			"red1":[0,20],
			"orange":[20,40],
			"yellow":[40,80],
			"green":[80,160],
			"cyan":[160,200],
			"blue":[200,260],
			"magenta":[260,330],
			"red2":[330,360]
			}


	# ==================================================================
	# Primitives
	# ==================================================================
	def __init__(self, camera):
		self._config = Config(self.CONFIG_FILE())
		self.camera = camera


	# ==================================================================
	# Private methods
	# ==================================================================
	def detect_major_color(self, image):
		# origin image to HSV
		hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

		hue = hsv_image[:,:,0]
		disparity_cpt=0
		i = j = 0

		while(i < image.shape[0]):
			while(j < image.shape[1]-1):
				if(abs(int(hue[i][j]) - int(hue[i][j+1])) > self.DISPARITY_THRESHOLD()):
					disparity_cpt += 1
				j+=1
			i+=1

		log.debug("image_processing: detect_major_color: disparity_cpt: " + str(disparity_cpt))

		mean = cv2.mean(hsv_image)
		if(image.dtype == "uint8"):
			if(mean[1] <= self.WHITE_THRESHOLD()):
				return "white"
			if(mean[2] <= self.BLACK_THRESHOLD()):
				return "black"
			if(disparity_cpt > self.DISPARITY_CPT()):
				log.warning("image_processing: detect_major_color: too much disparity.")
				return None

			for color in self.COLORS():
				val = 2*mean[0]
				if(val >= self.COLORS()[color][0] and val <= self.COLORS()[color][1]):
					if(color == "red1" or color == "red2"):
						color = "red"
					return color


	# ==================================================================
	# Methods
	# ==================================================================
	def major_color(self):
		img = self.camera.get_frame()

		# keeping the center of the image only
		# color = self.detect_major_color(img[160:320, 213:427])
		# return color
		try:
			return self.detect_major_color(img[160:320, 213:427])
		except:
			log.error("image_processing: major_color: unable to get frame.")
			return None


# Execution or import
if(__name__ == "__main__"):
	sys.exit(0)

# !/usr/bin/env python3
# coding: utf-8
#
# Author: Palacios Nicolas
#


# ======================================================================
# Imports
# ======================================================================
import sys
import time
import signal
import string

import serial

import pynmea2

import logging as log; log.basicConfig(level=log.DEBUG)


# ======================================================================
# Class
# ======================================================================
class NEO_6M(object):
	# ==================================================================
	# Primitives
	# ==================================================================
	def __init__(self, port="/dev/ttyAMA0", baudrate=9600, timeout=0.5):
		self.port = port
		self.serial = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)


	# ==================================================================
	# Private methods
	# ==================================================================
	def get_line(self):
		cpt=0
		while(True):
			new_line = False

			try:
				line = self.serial.readline().decode("utf-8")
				new_line = True
				cpt=0
			except:
				log.info("NEO-6M: get_line: loading...")
				cpt += 1
				if(cpt > 3):
					return None

			if(new_line):
				if(line[0:6] == "$GPGGA"):
					log.debug("NEO_6M:get_line: GPGGGA found")
					msg = pynmea2.parse(line)
					return msg

			time.sleep(0.5)


	# ==================================================================
	# Methods
	# ==================================================================
	def get_latitude(self, msg=None):
		if(msg == None):
			msg = self.get_line()
		else:
			return msg.lat
		return None

	def get_longitude(self, msg=None):
		if(msg == None):
			msg = self.get_line()
		else:
			return msg.lon
		return None


	def get_data(self):
		msg = self.get_line()
		return (self.get_latitude(msg), self.get_longitude(msg))


# ======================================================================
# Main
# ======================================================================


# Execution or import
if(__name__ == "__main__"):
	gps = NEO_6M()
	while(True):
		print(gps.get_data())
	sys.exit(0)

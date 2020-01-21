#! /usr/bin/env python3
# coding: utf-8
#
# Author:
#


# ======================================================================
# Imports
# ======================================================================
import json
import logging as log; log.basicConfig(level=log.DEBUG)
from pathlib import Path
import sys
import os

# ======================================================================
# Constants
# ======================================================================


# ======================================================================
# Global variables
# ======================================================================


# ======================================================================
# Class
# ======================================================================
class Config(object):
	#===================================================================
	# Constants
	#===================================================================

	# ==================================================================
	# Static variables
	# ==================================================================


	# ==================================================================
	# Primitives
	# ==================================================================
	def __init__(self, file_name = "/home/pi/projet/robot.conf", *args, **kwargs):
		# log.debug(str(args) + " espace " + str(kwargs))
		self.file_name = file_name

		if self.exist():
			self.load()
		elif self.exist_default():
			self.load(self.file_name.rsplit('.', 1)[0] + ".default")


		if len(args) != 0:
			for key, val in args[0].items():
				self.set(key, val)
		if len(kwargs) != 0:
			for key, val in kwargs.items():
				self.set(key, val)

	def __del__(self):
		try :
			self.save()
		except Exception as e :
			pass
	# ==================================================================
	# Methods
	# ==================================================================
	def set(self, attribute, value):
		if attribute != "file_name":
			setattr(self, attribute, value)

	def get(self, attribute, default = None):
		if attribute != "file_name":
			value = getattr(self, attribute, default)
			if value == default:
				self.set(attribute, default)
			return value
		return default

	def load(self, file = None):
		if file == None:
			file = self.file_name
		with open(file, 'r') as f:
			dict = json.load(f)
			for key, val in dict.items():
				# log.debug("key: %s, val: %s" % (key, str(val)))
				self.set(key, val)

	def save(self):
		with open(self.file_name, 'w') as f:
			dict = self.__dict__
			file_name = self.file_name
			del dict["file_name"]
			log.debug("Saving " + str(dict) + " to " + file_name)
			json.dump(dict, f)
			self.file_name = file_name

	def exist(self):
		path = Path(self.file_name)
		return path.is_file()

	def exist_default(self):
		path = Path(self.file_name.rsplit('.', 1)[0] + ".default")
		return path.is_file()

# ======================================================================
# Main

def main():
	d = Config("auto_pilot.conf")
	#c.save()

	print (d.__dict__)

# Execution or import
if(__name__ == "__main__"):
	main()
	sys.exit(0)

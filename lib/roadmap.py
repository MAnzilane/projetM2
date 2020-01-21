# !/usr/bin/env python3
# coding: utf-8
#
# Author: Palacios Nicolas
#


# ======================================================================
# Imports
# ======================================================================
import sys

import queue

import logging as log; log.basicConfig(level=log.DEBUG)


# ======================================================================
# Class
# ======================================================================
class Roadmap(object):
	#===================================================================
	# Constants
	#===================================================================
	def FILE_PATH(self):
		return "roadmaps/"


	# ==================================================================
	# Primitives
	# ==================================================================
	def __init__(self, file=None):
		if(file != None):
			self.load(file)
		else:
			self.actions = queue.Queue()


	# ==================================================================
	# Methods
	# ==================================================================
	def load(self, file):
		with open(self.FILE_PATH() + str(file), "r") as f:
			tokens = []
			for line in f:
				if(line[0] != '#' and line[0] != '\n'):
					tokens.append(line)

			self.actions = queue.Queue()
			i=0
			while(i < len(tokens)):
				self.actions.put((str(tokens[i][0]), int(tokens[i+1]), int(tokens[i+2])))
				i+=3


	def read(self):
		if(not self.is_empty()):
			return self.actions.get()
		else:
			print("actions queue empty.")
			return None


	def is_empty(self):
		return self.actions.empty()


# Execution or import
if(__name__ == "__main__"):
	sys.exit(0)

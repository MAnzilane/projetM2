# !/usr/bin/env python3
# coding: utf-8
#
# Author: Palacios Nicolas
# Descr: intercommunication between two robots (one master one slave)
#


# ======================================================================
# Imports
# ======================================================================
import sys
import time
import queue
import threading

import socket
import json

import logging as log; log.basicConfig(level=log.DEBUG)


# ======================================================================
# Class
# ======================================================================
class Intercom(object):
	#===================================================================
	# Constants
	#===================================================================
	def BUFFER_SIZE(self):
		return 1024


	# ==================================================================
	# Primitives
	# ==================================================================
	def __init__(self, ip, port, is_master):
		self.is_master	= is_master
		self.connected 	= False
		self.sync 		= False
		self.sock 		= socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		if (self.is_master):
			self.addr = (ip, port)
			# self.client_socket
			# self.addr_connected
			# self.addr_connected
			self.sock.bind(("0.0.0.0", self.addr[1]))
			self.sock.listen(5)

		else:
			self.addr_to_connect 	= (ip, port)
			self.sync 				= False
			self.actions 			= queue.Queue()


	# ==================================================================
	# Private methods
	# ==================================================================
	def wait_for_connection(self):
		log.debug("intercom: Waiting for connection")
		self.client_socket, self.addr_connected = self.sock.accept()
		self.connected = True
		log.debug("intercom: " + str(self.addr_connected) + " connected")


	def connect_to_master(self):
		log.debug("intercom: Trying to connect to master @ " + str(self.addr_to_connect))
		try:
			self.sock.connect(self.addr_to_connect)
			self.connected = True
			log.debug("intercom: connected to master")
		except:
			log.error("intercom:connect_to_master: unable to connect to master")


	def receive_action(self):
		''' receive and put in the queue '''
		log.debug("intercom: receive_action")
		while(True):
			data = ''
			data = self.sock.recv(self.BUFFER_SIZE()).decode()
			log.debug("intercom:receive_action: \"" + str(data) + "\" received")
			try:
				data = json.loads(data)
			except:
				log.warning("intercom:receive_action: json.loads(data) failed")
			if(data['ACTION'] == 'sync'):
				self.sync = not self.sync
				log.debug("intercom:receive_action: sync mode: " + str(self.sync))
			elif (self.sync):
				self.actions.put(data)


	# ==================================================================
	# Methods
	# ==================================================================
	def run(self):
		if (self.is_master):
			self.wait_for_connection()

		else:
			self.connect_to_master()
			while(not self.connected):
				self.connect_to_master()
				time.sleep(5)
			self.receive_action()


	def forward(self, msg):
		log.debug("intercom: forwarding \"" + str(msg) + "\"")
		self.client_socket.send(msg.encode())


# Execution or import
if(__name__ == "__main__"):
	sys.exit(0)

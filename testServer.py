#! /usr/bin/env python3
# coding: utf-8

import json
import signal
import socket
import sys
import threading

#GLOBAL PARAMETERS
ipHost = "localhost"

class NotConnected(Exception):
	pass

class Client(object):
	ip = None
	port = None
	socket = None

	def __init__(self, ip = "localhost", port = 34000, socket = None):
		self.ip = ip
		self.port = port
		self.socket = socket

	def __str__(self):
		return self.ip + ":" + str(self.port) + (" " if self.connected() else " not ") + "connected"

	def __eq__(self, other):
		return self.ip == other.ip and self.port == other.port

	def connected(self):
		if self.socket == None :
			return False
		return True

	def connect(self):
		if not self.connected() :
			client = (str(self.ip), self.port)
			print(self.port)
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				self.socket.connect(client)
			except Exception as e:
				print("[Client - connect()] Exception : " + str(e))
				self.socket = None
				return -1
				# raise NotConnected
			return 0
		return 1

	def send(self, msg):
		if self.connected() :
			try:
				self.socket.send(msg)
				return 0
			except Exception as e:
				self.socket = None
				print("[Client - send()] Exception : " + str(e))
				return -1
		else :
			return 1


class Server(object):
	client_list = []
	sensor_list = []

	interval = None
	timer = None

	socket = None
	broadcastUDPPort = None
	portServer = None

	portTCP = None
	socketTCP = None
	threadTCP = None


	def __init__(self, serverTCPPort = 3000, interval = 3, broadcastUDPPort = 50000):
		self.interval = interval
		self.broadcastUDPPort = broadcastUDPPort
		self.serverTCPPort = serverTCPPort
		self.listenTCP()

	def listenTCP(self):
		self.socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socketTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socketTCP.bind((ipHost, self.serverTCPPort))
		print("Start listening on TCP port", self.serverTCPPort)
		while True:
			self.socketTCP.listen()
			client_socket, address = self.socketTCP.accept()
			print("New client", address)
			while(True):
				try:
					response = client_socket.recv(1024).decode()
				except Exception as e:
					print(self.str() + "[Client - listenTCP] Exception :", e)
				print("Receive : " + response)
				if(response == "STOP"):
					break
			client_socket.close()

	def TCPListener(self):
		self.threadTCP = threading.Thread(target = self.listenTCP)
		self.threadTCP.start()

def main():
	serv = Server()

if(__name__ == "__main__"):
	main()
	sys.exit(0)

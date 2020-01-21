#! /usr/bin/env python3
# coding: utf-8



# ======================================================================
# Imports
# ======================================================================
import os
import sys
import time
import threading
import json

import RPi.GPIO as GPIO

from socket import *

from lib.pilot import Pilot
from lib.auto_pilot import Auto_Pilot
from lib.hardware.direction import Direction
import lib.hardware.enum_types as enum
import intercom

import logging as log; log.basicConfig(level=log.DEBUG)


# ======================================================================
# Constants
# ======================================================================
busnum = 1          # Edit busnum to 0, if you uses Raspberry Pi 1 or 0

HOST = "0.0.0.0"           # The variable of HOST is null, so the function bind( ) can be bound to all valid addresses.
PORT = 31000
BUFSIZ = 1024      				# Size of the buffer

# ======================================================================
# Global variables
# ======================================================================


# ======================================================================
# Class
# ======================================================================
class Server(object):

	def __init__(self, master_or_slave):
		self.tcpCliSock = None
		self.pilot = Pilot()
		log.debug("server: init: Pilot ok")

		self.tcpSerSock = socket(AF_INET, SOCK_STREAM)
		self.tcpSerSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		self.auto_pilot = Auto_Pilot(self.pilot)
		self.start_time = None

		ADDR = (HOST, PORT)
		self.tcpSerSock.bind(ADDR)
		self.tcpSerSock.listen(5)

		#TODO suppress when test angle finish
		self.test_angle_direction = self.pilot.direction.HOME_PWM()

		if (master_or_slave == "master"):
			is_master = True
		elif (master_or_slave == "slave"):
			is_master = False
		else:
			log.error("server: master or slave only")
		self.intercom = intercom.Intercom("192.168.172.1", PORT+1, is_master)

		self.intercom_t = threading.Thread(target=self.intercom.run)
		self.intercom_t.start()
		self.thread_scenario_running = False


	#===================================================================
	# Constants
	#===================================================================


	# ==================================================================
	# Static variables
	# ==================================================================


	# ==================================================================
	# Primitives
	# ==================================================================

	# ==================================================================
	# Private methods
	# ==================================================================
	def action(self, data):
		try:
			if data['ACTION'] == 'forward':
				log.debug('pilot moving forward')
				self.pilot.forward_speed()

			elif data['ACTION'] == 'backward':
				log.debug('recv backward cmd')
				self.pilot.backward_speed()

			elif data['ACTION'] == 'left':
				log.debug('recv left cmd')
				self.pilot.turn_left()

			elif data['ACTION'] == 'right':
				log.debug('recv right cmd')
				self.pilot.turn_right()

			"""Angle calibration commands"""
			################################
			if data['ACTION'] == 'forward_angle':
				log.debug('pilot moving forward')
				self.pilot.forward_speed()
				self.start_time = time.time()

			elif data['ACTION'] == 'stop_angle':
				log.debug('recv stop_angle cmd')
				if self.start_time != None:
					elapsed_time = time.time() - self.start_time
					self.start_time = None
					self.pilot.set_90(elapsed_time)
				self.pilot.stop()

			elif data['ACTION'] == 'left++':
				# self.test_angle_direction -= 5
				# self.pilot.set_value(self.test_angle_direction)
				# log.debug("Angle value set: " + str(self.test_angle_direction))
				self.pilot.turn_left()

			elif data['ACTION'] == 'right++':
				# self.test_angle_direction += 5
				# self.pilot.set_value(self.test_angle_direction)
				# log.debug("Angle value set: " + str(self.test_angle_direction))
				self.pilot.turn_right()
			##################################

			elif data['ACTION'] == 'left90':
				# self.test_angle_direction -= 5
				# self.pilot.set_value(self.test_angle_direction)
				# log.debug("Angle value set: " + str(self.test_angle_direction))
				self.auto_pilot.go_left90()

			elif data['ACTION'] == 'right90':
				# self.test_angle_direction += 5
				# self.pilot.set_value(self.test_angle_direction)
				# log.debug("Angle value set: " + str(self.test_angle_direction))
				self.auto_pilot.go_right90()

			elif data['ACTION'] == 'go_home':
				if self.thread_scenario_running:
					self.auto_pilot.reset()
				else:
					self.thread_scenario_running = True
				threading.Thread(target=self.auto_pilot.scenario_return_to_zero).start()
				# self.auto_pilot.scenario_return_to_zero()

			elif data['ACTION'] == 'home_angle_test':
				self.test_angle_direction = self.pilot.direction.HOME_PWM()
				log.debug("Angle value set: " + str(self.test_angle_direction))
				self.pilot.go_straight()

			elif data['ACTION'] =='home':
				log.debug('recv home cmd')
				self.pilot.go_straight()

			elif data['ACTION'] == 'stop':
				log.debug('recv stop cmd')
				self.pilot.stop()

			elif data['ACTION'] == 'auto_pilot':
				log.debug('auto_pilot move and avoid')
				if self.thread_scenario_running:
					self.auto_pilot.reset()
				else:
					self.thread_scenario_running = True
				threading.Thread(target=self.auto_pilot.scenario_move_and_avoid).start()
				# self.auto_pilot.scenario_move_and_avoid()

			elif data['ACTION'] == 'reset':
				log.debug('Reset')
				self.auto_pilot.reset()
				# self.pilot.reset()
				log.debug('Stop')

			elif data['ACTION'] == 'updateroadmaps':
				for item in os.listdir('./roadmaps'):
					itemToSend = item.split('.')[0]
					itemToSend = "roadmaps=" + itemToSend + '\n'
					log.debug("Send : ")
					log.debug(itemToSend)
					self.tcpCliSock.send(itemToSend.encode())

			elif (data['ACTION'] == 'set_roadmap'):# Change the speed
				log.debug(data)
				roadmap = data["VALUE"] + ".txt"
				if self.thread_scenario_running:
					self.auto_pilot.reset()
				else:
					self.thread_scenario_running = True
				#TODO FAire des tests pour check le roadmap
				threading.Thread(target=self.auto_pilot.scenario_read_roadmap, args=[roadmap, ]).start()
				# self.auto_pilot.scenario_read_roadmap(roadmap)

			elif (data['ACTION'] == 'line'):# Change the speed
				log.debug(data)
				time_var = data['VALUE']
				try:
					time_var = int(time_var)
					if(time_var > 0):
						if self.thread_scenario_running:
							self.auto_pilot.reset()
						else:
							self.thread_scenario_running = True
						threading.Thread(target=self.auto_pilot.scenario_straight_line_time, args=[time_var, ]).start()
						# self.auto_pilot.scenario_straight_line_time(time_var)
				except:
					log.debug('Error: time =' + str(time_var))

			elif(data['ACTION'] == 'offset+'):
				offset = self.pilot.direction.OFFSET()
				self.set_offset(offset+1)
				self.pilot.go_straight()

			elif(data['ACTION'] == 'offset-'):
				offset = self.pilot.direction.OFFSET()
				self.set_offset(offset-1)
				self.pilot.go_straight()

			elif data['ACTION'] == 'rotate_left':
				self.pilot.rotate_speed_left(102)

			elif data['ACTION'] == 'rotate_right':
				self.pilot.rotate_speed_right(102)

			elif (data['ACTION'] == 'set_speed'):# Change the speed
				log.debug(data)
				speed = data['VALUE']
				try:
					speed = int(speed)
					if(speed < 24):
						speed = 24
					if(speed > 100):
						speed = 100
					self.pilot.set_speed(speed)
				except:
					log.error('Error: speed =' + str(speed))

			elif data['ACTION'] == 'set_forward':
				log.debug('data =' + str(data))
				spd = data['VALUE']
				try:
					spd = int(spd)
					self.pilot.forward_speed(spd)
				except:
					log.error('Error speed =' + str(spd))

			elif data['ACTION'] == 'set_backward':
				log.debug('data =' + str(data))
				spd = data['VALUE']
				try:
					spd = int(spd)
					self.pilot.backward_speed(spd)
				except:
					log.error('ERROR, speed ='  + str(spd))

			elif data['ACTION'] == 'set_angle':
				log.debug('data =' + str(data))
				angle = data['VALUE']
				try:
					angle = int(angle)
					self.pilot.direction.turn(angle)
				except:
					log.error('ERROR, angle =' + str(angle))

			elif data['ACTION'] == 'speedtime':
				log.debug('data = ' + str(data))
				t = data['TIME']
				speed = data['VALUE']
				try:
					t = int(t)
					speed = int(speed)
					if self.thread_scenario_running:
						self.auto_pilot.reset()
					else:
						self.thread_scenario_running = True
					threading.Thread(target=self.auto_pilot.scenario_test_speed, args=[t, speed, ]).start()
					# self.auto_pilot.scenario_test_speed(t, speed)
				except:
					log.error('ERROR non int, data = ' + str(data))

			elif data['ACTION'] == 'color':
				log.debug('data = ' + str(data))
				color = data['VALUE']
				if self.thread_scenario_running:
					self.auto_pilot.reset()
				else:
					self.thread_scenario_running = True
				threading.Thread(target=self.auto_pilot.scenario_find_color, args=[color,]).start()

			elif(data['ACTION']) == 'sync':
				log.debug('data = ' + str(data))

			else:
				log.error('Command Error! Cannot recognize command: ' + str(data))

			pass
		except Exception as e:
			log.debug(str(e) + ": " + str(data))


	def calibrate(self):
		nok = True
		offset = self.pilot.direction.OFFSET()
		while nok:

			invalid_offset = True
			while invalid_offset :
				# TODO receive msg from app
				offset_inc_str = input("offset : ")
				# with int(offset_inc_str) as offset_inc:
				try:
					offset_inc = int(offset_inc_str)
					offset += offset_inc
					invalid_offset = False
				except Exception as e:
					log.debug(str(e))

			self.set_offset(offset)

			# TODO receive msg from app
			trying = input("do u want to test bro ? ")
			if trying == 'o' or trying == 'y':
				self.pilot.go_straight()
				self.pilot.forward_speed(70)
				time.sleep(2)

			# TODO receive msg from app
			valid = input("ok ? ")
			if valid == 'o' or valid == 'y':
				nok = False

	def set_offset(self, offset):
		self.pilot.direction._config.set("offset", offset)
		del self.pilot.direction
		self.pilot.direction = Direction()


	def check_queue(self):
		log.debug("server: check_queue")
		# var_cond
		while(True):
			if(not self.intercom.actions.empty()):
				action = self.intercom.actions.get()
				log.debug("server:check_queue: next action : " + str(action))
				self.action(action)
			time.sleep(0.1)


	# ==================================================================
	# Public methods
	# ==================================================================
	def run(self):
		if(not self.intercom.is_master):
			self.check_queue_t = threading.Thread(target=self.check_queue)
			self.check_queue_t.start()

		while True:
			log.debug('Waiting for connection...')

			self.tcpCliSock, addr = self.tcpSerSock.accept()
			log.debug('...connected from :' + str(addr))

			while True:
				data = ''
				data = self.tcpCliSock.recv(BUFSIZ).decode()    # Receive data sent from the client.
				try:
					data_b = json.loads(data)
				except:
					log.error('Error: JSON load : ' + str(data))

				if(not data):
					break

				if(self.intercom.is_master and self.intercom.connected):
					self.intercom.forward(data)

				self.action(data_b)
				log.debug("Send : " + str(self.pilot.position))
				self.tcpCliSock.send(str(self.pilot.position).encode())

			self.tcpCliSock.close()

		self.tcpSerSock.close()


# ======================================================================
# Main
# ======================================================================
def main():
	if (len(sys.argv) != 2):
		log.error("server: Usage: python3 server.py master|slave")
		sys.exit(1)

	serveur = Server(str(sys.argv[1]))
	serveur.run()

# Execution or import
if(__name__ == "__main__"):
	main()
	sys.exit(0)

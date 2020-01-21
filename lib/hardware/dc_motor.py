#!/usr/bin/env python3
#coding: utf-8
#
# Author: Couzon Florent
#Code highly inspired by
#https://github.com/sunfounder/Sunfounder_Smart_Video_Car_Kit_for_RaspberryPi
#


# ======================================================================
# Imports
# ======================================================================
import logging as log; log.basicConfig(level=log.DEBUG)
import time

import RPi.GPIO as GPIO
import lib.hardware.PCA9685 as pca9685
import lib.config as config_i


# ======================================================================
# Constants
# ======================================================================


# ======================================================================
# Global variables
# ======================================================================


# ======================================================================
# Class
# ======================================================================
class DC_Motor(object):
	#===================================================================
	# Constants
	#===================================================================
	def CONFIG_FILE(self):
		return "/home/pi/projet/lib/hardware/dc_motor.conf"

	def SPEED_MULTIPLIER(self):
		return 40

	def FORWARD(self):
		return True

	def BACKRWARD(self):
		return False

	# ==================================================================
	# Static variables
	# ==================================================================


	# ==================================================================
	# Primitives
	# ==================================================================
	def __init__(self, pin_motor_A, pin_motor_B, channel_speed, speed=50,
		busnum=None):
		config            = config_i.Config(self.CONFIG_FILE())

		self.pin_motor_A         = pin_motor_A
		self.pin_motor_B         = pin_motor_B
		self.channel_speed       = channel_speed
		self.speed               = int(config.get("start_speed", "60"))

		if busnum == None:
			self.pwm = pca9685.PWM()
		else:
			self.pwm = pca9685.PWM(bus_number=busnum)

		self.pwm.frequency = int(config.get("start_frequency", "60"))

		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BOARD)

		GPIO.setup(self.pin_motor_A, GPIO.OUT)
		GPIO.setup(self.pin_motor_B, GPIO.OUT)

	# ==================================================================
	# Private methods
	# ==================================================================
	def motor_activation(self, direction):
		# log.debug("motor activ dir: " + str(direction))
		if direction == True:
			GPIO.output(self.pin_motor_A, GPIO.LOW)
			GPIO.output(self.pin_motor_B, GPIO.HIGH)
		elif direction == False:
			GPIO.output(self.pin_motor_A, GPIO.HIGH)
			GPIO.output(self.pin_motor_B, GPIO.LOW)
		else:
			log.debug("Config Error")

	# ==================================================================
	# Methods
	# ==================================================================
	def set_speed(self, speed):
		log.debug("speed: " + str(speed))
		self.speed = speed
		speed *= self.SPEED_MULTIPLIER()
		# log.debug("speed is: " + str(speed))
		self.pwm.write(self.channel_speed, 0, speed)

	def forward_speed(self, speed=None):
		# log.debug("speed start fct forward: self.speed: " + str(self.speed)
		# 	+ ", speed: " + str(speed))
		if speed != None:
			self.set_speed(speed)
		else:
			self.set_speed(self.speed)
		self.motor_activation(self.FORWARD())

	def backward_speed(self, speed=None):
		# log.debug("speed start fct bacward: self.speed: " + str(self.speed)
		# 	+ ", speed: " + str(speed))
		if speed != None:
			self.set_speed(speed)
		else:
			self.set_speed(self.speed)
		self.motor_activation(self.BACKRWARD())

	def stop(self):
		GPIO.output(self.pin_motor_A, GPIO.LOW)
		GPIO.output(self.pin_motor_B, GPIO.LOW)

# ======================================================================
# Main
# ======================================================================


# Execution or import
if(__name__ == "__main__"):
	sys.exit(0)

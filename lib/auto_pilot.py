#! /usr/bin/env python3
# coding: utf-8
#
# Author:
#


# ======================================================================
# Imports
# ======================================================================
import logging as log; log.basicConfig(level=log.DEBUG)
import sys, os

from lib.hardware.ultrasound import Ultrasound

import threading, multiprocessing
import time

import lib.camera_behavior as camera_behavior_i
import lib.hardware.enum_types as enum
import lib.roadmap as roadmap_i
import lib.hardware.neo6m as gps_i
from lib.config import Config

import math
# ======================================================================
# Constants
# ======================================================================


# ======================================================================
# Global variables
# ======================================================================


# ======================================================================
# Class
# ======================================================================
class Auto_Pilot(object):
	#===================================================================
	# Constants
	#===================================================================
	def CONFIG_FILE(self):
		return "/home/pi/projet/lib/auto_pilot.conf"

	def SPEED_SCENARIO_MOVE_AND_AVOID(self):
		return int(self.config.get("speed_scenario_move_and_avoid"))
		# return 80

	def IMPACT_DISTANCE(self):
		return int(self.config.get("impact_distance"))
		# return 25

	def CHECK_OBJ_INTERVAL(self):
		return float(self.config.get("check_obj_interval"))
		# return 0.2

	def TIME_CHECK_BLOCKED(self):
		return float(self.config.get("time_check_blocked"))
		# return 2

	def AVOIDING_TIME(self):
		return float(self.config.get("avoiding_time"))
		# return 1.2

	def ROUTINE_UNBLOCK_TIMING_1(self):
		return float(self.config.get("routine_unblock_timing_1"))
		# return 1

	def ROUTINE_UNBLOCK_TIMING_2(self):
		return float(self.config.get("routine_unblock_timing_2"))
		# return 1

	def GPS_PERIOD(self):
		''' in seconds '''
		return float(self.config.get("gps_period"))
		# return 5

	def COLOR_CHECK_FREQUENCY(self):
		return 1

	def SPEED_FIND_COLOR(self):
		return 70
	# ==================================================================
	# Static variables
	# ==================================================================


	# ==================================================================
	# Primitives
	# ==================================================================
	def __init__(self, pilot, ultrasound = None, camera_behavior = None, roadmap_file = None):
		self.config                	= Config(self.CONFIG_FILE())
		self.pilot                 	= pilot
		self.condition             	= threading.Condition()
		self.condition_roadmap     	= threading.Condition()
		self.terminated            	= False
		self.sought_routine        	= enum.Sought_Routine.NONE
		self.is_blocked            	= False
		self.notified              	= False
		self.routine_running       	= enum.Routine_Running.NONE
		self.last_routine_run      	= None
		self.sought_GPS_pos        	= (None, None)
		self.distance              	= None
		self.thread_check_obstacle 	= None
		self.sought_color 			= None

		if ultrasound == None :
			self.ultrasound = Ultrasound()
		else :
			self.ultrasound = ultrasound
		self.gps 				   = gps_i.NEO_6M()

		if camera_behavior == None:
			self.camera_behavior = camera_behavior_i.Camera_Behavior()
		else:
			self.camera_behavior = camera_behavior

		self.t1 					= None
		self.t2						= None
		self.t3						= None
		self.t4					    = None
		self.thread_check_obstacle	= None
		self.thread_check_blocked	= None
		self.thread_gps_routine		= None

	# ==================================================================
	# Private methods
	# ==================================================================

	def happy_camera(self):
		timing = 0.12
		self.camera_behavior.camera_direction.see_below_left()
		self.loop_thread_waiting(timing)
		if self.terminated:
			return
		self.camera_behavior.camera_direction.see_left()
		self.loop_thread_waiting(timing)
		if self.terminated:
			return
		self.camera_behavior.camera_direction.see_above_left()
		self.loop_thread_waiting(timing)
		if self.terminated:
			return
		self.camera_behavior.camera_direction.see_above()
		self.loop_thread_waiting(timing)
		if self.terminated:
			return
		self.camera_behavior.camera_direction.see_above_right()
		self.loop_thread_waiting(timing)
		if self.terminated:
			return
		self.camera_behavior.camera_direction.see_right()
		self.loop_thread_waiting(timing)
		if self.terminated:
			return
		self.camera_behavior.camera_direction.see_below_right()
		self.loop_thread_waiting(timing)
		if self.terminated:
			return
		self.camera_behavior.camera_direction.see_below()
		self.loop_thread_waiting(timing)
		if self.terminated:
			return
		self.camera_behavior.camera_direction.see_straight()
		self.loop_thread_waiting(timing)

	# =============================================================
	# Threads creation
	# =============================================================
	def start_routine_thread(self):
		self.t1 = threading.Thread(
			target=self.routine_thread).start()

	def start_unblock(self):
		self.t2 = self.thread_unblock = threading.Thread(
			target=self.routine_unblock).start()

	def start_avoid(self):
		self.t3 =  self.thread_avoid = threading.Thread(
			target=self.avoid_routine).start()

	def start_check_obstacle(self):
		self.thread_check_obstacle = self.thread_check_obstacle = threading.Thread(
			target=self.obstacle_check_routine)
		self.thread_check_obstacle.start()

	def start_check_blocked(self):
		self.thread_check_blocked = threading.Thread(
			target=self.check_blocked).start()

	def start_gps_routine(self):
		self.thread_gps_routine = threading.Thread(
			target=self.gps_routine).start()

	def start_find_color_routine(self):
		self.t4 = threading.Thread(target=self.find_color_routine).start()

	# =============================================================
	# Notify variable condition
	# =============================================================
	def notify_condition(self, routine):
		self.sought_routine = routine
		with self.condition:
			self.notified = True
			self.condition.notify_all()

	# =============================================================
	# Permanent Routines
	# =============================================================
	def obstacle_check_routine(self):
		while(not self.terminated):
			self.distance = self.ultrasound.get_distance()
			log.debug("I'm checking obstacles dist: " + str(self.distance))
			#if the car is blocked
			if (self.is_blocked):
				self.is_blocked = False
				self.notify_condition(enum.Sought_Routine.UNBLOCK)
			#if the car is close to an object and not unblocking itself
			elif (self.distance < self.IMPACT_DISTANCE()):
				if (self.routine_running != enum.Routine_Running.UNBLOCKING):
					self.notify_condition(enum.Sought_Routine.AVOID)
			#if nothing is running wake up the roadmap
			elif(self.routine_running == enum.Routine_Running.NONE):
				self.notify_roadmap()
			self.loop_thread_waiting(self.CHECK_OBJ_INTERVAL())
		log.debug("obstacle_check_routine terminating")

	def check_blocked(self):
		while(self.distance == None):
			self.loop_thread_waiting(0.1)
		old_distance = self.distance
		self.loop_thread_waiting(self.TIME_CHECK_BLOCKED())
		while(not self.terminated):
			if(abs(self.distance - old_distance) < 6):
				self.is_blocked = True
			else:
				self.is_blocked = False
			old_distance = self.distance
			self.loop_thread_waiting(self.TIME_CHECK_BLOCKED())
		log.debug("check_blocked terminated")

	def gps_routine(self):
		log.debug("auto_pilot: GPS")
		while(not self.terminated):
			data = self.gps.get_data()
			if(data[0] == None or data[1] == None):
				data = (0.0, 0.0)
			log.debug("\t\tgps: lat:" + str(data[0]) + ", long:" + str(data[1]))
			self.loop_thread_waiting(self.GPS_PERIOD())
		log.debug("gps_routine terminated")

	def routine_thread(self):
		skip_wait = False
		while (not self.terminated):
			if (not skip_wait):
				with self.condition:
					self.condition.wait()
			else:
				skip_wait = False
			if self.sought_routine == enum.Sought_Routine.AVOID:
				self.sought_routine = enum.Sought_Routine.NONE
				avoid_return = self.avoid_routine()
				if (avoid_return == "rerun_something"):
					skip_wait = True
			elif self.sought_routine == enum.Sought_Routine.UNBLOCK:
				self.sought_routine = enum.Sought_Routine.NONE
				unblock_return = self.routine_unblock()
				if(unblock_return == "rerun_something"):
					skip_wait = True
		if self.sought_routine == enum.Sought_Routine.STOP:
			self.sought_routine = enum.Sought_Routine.NONE
			self.pilot.reset()
			log.debug("routine_thread enum.Sought_Routine.STOP")
		log.debug("routine_thread terminating")

	def find_color_routine(self):
		log.debug("find_color_routine start")
		while(not self.terminated):
			if self.camera_behavior.is_color_detected(self.sought_color):
				log.debug("We are arrived, we found the color: " + self.sought_color)
				self.pilot.reset()
				self.happy_camera()
				self.terminated = True
			else:
				self.loop_thread_waiting(self.COLOR_CHECK_FREQUENCY())
		self.reset()
		log.debug("find_color_routine terminated")

	# ==================================
	# permanent routine wait method
	# ==================================
	def loop_thread_waiting(self, time_wait):
		t0 = time.time()
		remaining_time = time_wait
		while(remaining_time > 0):
			with self.condition:
				self.condition.wait(remaining_time)
			if self.terminated:
				return
			else:
				remaining_time = time_wait - (time.time() - t0)
		return

	# =============================================================
	# Temporary Routine
	# =============================================================
	def avoid_routine(self):
		log.debug("									avoid_routine start")
		self.routine_running = enum.Routine_Running.AVOIDING
		avoiding_time = self.AVOIDING_TIME()
		self.pilot.set_speed(69)
		self.pilot.turn_left()
		ret_value = self.wait_notify_avoid(avoiding_time * 0.8)
		if (ret_value != "keep_going"):
			return ret_value

		self.pilot.turn_right()
		ret_value = self.wait_notify_avoid((avoiding_time * 2.9) * 0.8)
		if (ret_value != "keep_going"):
			return ret_value

		self.pilot.turn_left()
		ret_value = self.wait_notify_avoid((avoiding_time * 1.1) * 0.8)
		if (ret_value != "keep_going"):
			return ret_value

		self.end_avoid_routine()
		return "normal ending"

	# ==================================
	# wait method
	# ==================================
	def wait_notify_avoid(self, avoiding_time):
		t0 = time.time()
		remaining_time = avoiding_time
		while(remaining_time > 0):
			with self.condition:
				self.condition.wait(remaining_time)
			if self.terminated:
				self.end_avoid_routine()
				return "rerun_something"
			elif self.notified:
				self.notified = False
				self.end_avoid_routine()
				if (self.sought_routine == enum.Sought_Routine.NONE):
					return "let go"
				else:
					return "rerun_something"
			else:
				remaining_time = avoiding_time - (time.time() - t0)
		return "keep_going"

	# ==================================
	# closure method
	# ==================================
	def end_avoid_routine(self):
		self.last_routine_run = "avoid"
		self.pilot.go_straight()
		self.pilot.set_speed(80)
		#if a routine ends give the lead back to roadmap
		if self.routine_running == enum.Routine_Running.NONE:
			self.notify_roadmap()
		self.routine_running = enum.Routine_Running.NONE
		log.debug("									avoid_routine end")

	# =============================================================
	#  Temporary Routine
	# =============================================================
	def routine_unblock(self):
		log.debug("				routine_unblock start")
		self.is_blocked = False
		self.routine_running = enum.Routine_Running.UNBLOCKING

		if (self.last_routine_run == "unblock"):
			self.pilot.forward_speed()
		else:
			self.pilot.backward_speed()
		ret_value = self.wait_notify_unblock(self.ROUTINE_UNBLOCK_TIMING_1())
		if (ret_value != "keep_going"):
			return ret_value

		if (self.last_routine_run == "unblock"):
			self.pilot.turn_left()
		else:
			self.pilot.turn_right()
		ret_value = self.wait_notify_unblock(self.ROUTINE_UNBLOCK_TIMING_2())
		if (ret_value != "keep_going"):
			return ret_value

		self.end_routine_unblock()
		return "routine_unblock normal ending"

	# ==================================
	# wait method
	# ==================================
	def wait_notify_unblock(self, time_wait):
		t0 = time.time()
		remaining_time = time_wait
		while(remaining_time > 0):
			with self.condition:
				self.condition.wait(remaining_time)
			if self.terminated:
				self.end_routine_unblock()
				return "rerun_something"
			else:
				remaining_time = time_wait - (time.time() - t0)
		return "keep_going"

	# ==================================
	# closure method
	# ==================================
	def end_routine_unblock(self):
		self.pilot.go_straight()
		self.pilot.forward_speed()
		self.routine_running = enum.Routine_Running.NONE

		#if stuck + last one was unblock => unblock_nb2 =>
		# 2 unblock routine before me
		if (self.last_routine_run == "unblock"):
			self.last_routine_run = "unblock_nb2"
		else:
			self.last_routine_run = "unblock"
		#if a routine ends give the lead back to roadmap
		if self.routine_running == enum.Routine_Running.NONE:
			self.notify_roadmap()
		log.debug("				routine_unblock end")

	# =============================================================
	# Temporary Routine
	# =============================================================
	def avoid_routine(self):
		log.debug("									avoid_routine start")
		self.routine_running = enum.Routine_Running.AVOIDING
		avoiding_time = self.AVOIDING_TIME()
		self.pilot.turn_left()
		ret_value = self.wait_notify_avoid(avoiding_time * 0.8)
		if (ret_value != "keep_going"):
			return ret_value

		self.pilot.turn_right()
		ret_value = self.wait_notify_avoid((avoiding_time * 2.9) * 0.8)
		if (ret_value != "keep_going"):
			return ret_value

		self.pilot.turn_left()
		ret_value = self.wait_notify_avoid((avoiding_time * 1.1) * 0.8)
		if (ret_value != "keep_going"):
			return ret_value

		self.end_avoid_routine()
		return "normal ending"

	# ==================================
	# wait method
	# ==================================
	def wait_notify_avoid(self, avoiding_time):
		t0 = time.time()
		remaining_time = avoiding_time
		while(remaining_time > 0):
			with self.condition:
				self.condition.wait(remaining_time)
			if self.terminated:
				self.end_avoid_routine()
				return "rerun_something"
			elif self.notified:
				self.notified = False
				self.end_avoid_routine()
				if (self.sought_routine == enum.Sought_Routine.NONE):
					return "let go"
				else:
					return "rerun_something"
			else:
				remaining_time = avoiding_time - (time.time() - t0)
		return "keep_going"

	# ==================================
	# closure method
	# ==================================
	def end_avoid_routine(self):
		self.last_routine_run = "avoid"
		self.pilot.go_straight()
		#if a routine ends give the lead back to roadmap
		if self.routine_running == enum.Routine_Running.NONE:
			self.notify_roadmap()
		self.routine_running = enum.Routine_Running.NONE
		log.debug("									avoid_routine end")


	# =============================================================
	#  Roadmap
	# =============================================================
	def notify_roadmap(self):
		with self.condition_roadmap:
			self.condition_roadmap.notify()

	def wait_and_interrupt(self, action_type, action_duration):
		log.debug("wait_and_interrupt start, duration: " + str(action_duration))
		if (action_duration > 0):
			sum_time_spent = 0.0
			t0 = time.time()
			#sleep but can receive avoid or unblock
			with self.condition_roadmap:

				remaining_time = action_duration - sum_time_spent
				while (remaining_time > 0):
					log.debug("wait 1, remaining_time: " + str(remaining_time))
					self.condition_roadmap.wait(remaining_time)
					sum_time_spent += time.time() - t0
					t0 = time.time()
					if(int(sum_time_spent) >= action_duration):
						return
					#if stop order don't avoid obstacles or smth else
					if (action_type != 'S'):
						sum_time_spent += time.time() - t0
						log.debug("wait 2, sum_time_spent: " +
							str(sum_time_spent))
						self.condition_roadmap.wait()
						t0 = time.time()
					remaining_time = action_duration - sum_time_spent

	# =============================================================
	#  GPS
	# =============================================================
	def get_GPS_pos(self):
		data = self.gps.get_data()
		if(data[0] == None or data[1] == None):
			data = (0.0, 0.0)
		log.debug("gps_data: " + str(data))
		return data

	def half_turn(self):
		self.pilot.backward_speed(70)
		self.pilot.turn_left()
		time.sleep(2.2)
		self.pilot.forward_speed(70)
		self.pilot.turn_right()
		time.sleep(2.2)
		self.pilot.reset()


	def camera_reset(self):
		self.camera_behavior.camera_direction.see_straight()

	def reset_args(self):
		self.terminated            	= False
		self.sought_routine        	= enum.Sought_Routine.NONE
		self.is_blocked            	= False
		self.notified              	= False
		self.routine_running       	= enum.Routine_Running.NONE
		self.last_routine_run      	= None
		self.sought_GPS_pos        	= (None, None)
		self.distance              	= None
		self.thread_check_obstacle 	= None
		self.sought_color 			= None
		self.t1 					= None
		self.t2						= None
		self.t3						= None
		self.t4					    = None
		self.thread_check_obstacle	= None
		self.thread_check_blocked	= None
		self.thread_gps_routine		= None

	# ==================================================================
	# Methods
	# ==================================================================

	def reset(self):
		self.terminated = True
		self.notify_condition(enum.Sought_Routine.STOP)
		self.pilot.reset()
		self.camera_reset()

		if self.t1 != None:
			self.t1.join()
		if self.t2 != None:
			self.t2.join()
		if self.t3 != None:
			self.t3.join()
		if self.t4 != None:
			self.t4.join()
		if self.thread_check_obstacle != None:
			self.thread_check_obstacle.join()
		if self.thread_check_blocked != None:
			self.thread_check_blocked.join()
		if self.thread_gps_routine != None:
			self.thread_gps_routine.join()
		self.pilot.reset()
		self.camera_reset()
		self.reset_args()
		log.debug("end of reset")

	def go_left90(self):
		self.stop()
		self.turn_left()
		spd = int(self.config.get("left_speed", 60))
		tps = float(self.config.get("left_time", 1.))
		log.debug("45° : " + str(spd) + "; "  + str(tps))
		self.forward_speed(spd)
		self.loop_thread_waiting(tps)
		if self.terminated:
			return
		self.stop()

	def go_right90(self):
		self.stop()
		self.turn_right()
		self.forward_speed(int(self.config.get("right_speed", 60)))
		self.loop_thread_waiting(float(self.config.get("right_time", 1.)))
		if self.terminated:
			return
		self.stop()

	def scenario_straight_line_time(self, time_wait):
		self.pilot.forward_speed()
		self.loop_thread_waiting(time_wait)
		self.pilot.reset()

	def scenario_move_and_avoid(self):
		self.start_routine_thread()
		self.start_check_blocked()
		self.start_check_obstacle()
		self.start_gps_routine()
		self.pilot.forward_speed(self.SPEED_SCENARIO_MOVE_AND_AVOID())
		self.thread_check_obstacle.join()

	def scenario_read_roadmap(self, file):
		roadmap = roadmap_i.Roadmap()
		roadmap.load(file)
		action = roadmap.read()
		first = True
		while action != None:
			print(str(action))
			(action_type, speed_angle, action_duration) = action
			if speed_angle == 0:
				speed_angle = None
			if (action_type == 'F'):
				self.pilot.forward_speed(speed_angle)
			elif (action_type == 'B'):
				self.pilot.backward_speed(speed_angle)
			elif (action_type == 'H'):
				self.pilot.go_straight()
			elif (action_type == 'L'):
				self.pilot.turn_left()
			elif (action_type == 'R'):
				self.pilot.turn_right()
			elif (action_type == 'T'):
				if (speed_angle == None):
					log.debug("Error scenario_read_roadmap, angle not defined")
					raise
				self.pilot.turn(speed_angle)
			elif (action_type == 'E'):
				self.reset()
			elif (action_type == 'S'):
				self.pilot.stop()
			if first:
				self.start_routine_thread()
				self.start_check_blocked()
				self.start_check_obstacle()
				first = False
			self.wait_and_interrupt(action_type, action_duration)
			action = roadmap.read()
		self.pilot.reset()

	def scenario_find_color(self, sought_color = "blue"):
		self.sought_color = sought_color
		self.start_routine_thread()
		self.start_check_blocked()
		self.start_check_obstacle()
		self.start_find_color_routine()
		self.pilot.forward_speed(self.SPEED_FIND_COLOR())
		self.thread_check_obstacle.join()

	def sceanario_return_to_zero(self):
		p = {x:self.pilot.position.x, y:self.pilot.position.y}
		angle = math.atan(p.y / p.x) - math.pi
		distance = math.sqrt(p.x ** 2 + p.y ** 2)
		log.debug("distance : " + str(distance) + " - angle : " + str(angle))
		self.pilot.reset()


# ======================================================================
# Not fonctionnal
# ======================================================================

	#go in diagonale => have the same value:
	# |prev_x_diff - new_diff_x| == |prev_y_diff - new_diff_y|
	def scenario_go_to_GPS_pos(self, sought_position):
		self.sought_GPS_pos = sought_position
		speed_wanted = 70
		x_dest = self.sought_GPS_pos[0]
		y_dest = self.sought_GPS_pos[1]
		prev_x_diff = None
		prev_y_diff = None
		# previous_mvt = [None] * 4
		arrived = False
		while(not arrived and not self.terminated):
			x_closer = False
			y_closer = False
			self.pilot.stop()
			(x_tmp, y_tmp) = self.get_GPS_pos()
			self.pilot.forward_speed()
			log.debug("gps_pos found: " + str((x_tmp,y_tmp)))
			if (x_tmp == ""):
				x = 0.0
				y = 0.0
			else:
				(x, y) = (float(x_tmp), float(y_tmp))
			# (x, y) = (float(x), float(y))
			log.debug("gps_pos found: " + str((x,y)))
			# (x, y) = (float(x), float(y))
			new_diff_x = x_dest - x
			new_diff_y = y_dest - y
			diff_delta = .00003
			if 	((-diff_delta <= new_diff_x and new_diff_x <= diff_delta) and
				(-diff_delta <= new_diff_y and new_diff_y <= diff_delta)):
				log.info("destination reached (" + str(new_diff_x) + ";" + str(new_diff_y) + ")")
				arrived = True
			else:
				if(prev_x_diff == None):
					self.pilot.forward_speed(speed_wanted)
				else:
					if (prev_x_diff > new_diff_x):
						log.info("getting closer x")
						x_closer = True
						#we are getting closer to the sought x
					if (prev_y_diff > new_diff_y):
						log.info("getting closer y")
						y_closer = True
						#we are getting closer to the sought y
					if (x_closer and y_closer):
						log.info("both closer")
						pass
					elif (not x_closer) and (not y_closer):
						log.info("go half turn")
						self.half_turn()
						self.pilot.forward_speed(speed_wanted)
					elif (not x_closer) or (not y_closer):
						log.info("one closer")
						self.pilot.turn_right()
						time.sleep(1)
						self.pilot.go_straight()
						time.sleep(1)

				time.sleep(2)
		log.debug("I'm arrived at: wanted pos, my pos: " )
		self.reset()



# ======================================================================
# Main
# ======================================================================


def main():
	#tests in test_flo.py
	pass

# Execution or import
if(__name__ == "__main__"):
	main()
	sys.exit(0)

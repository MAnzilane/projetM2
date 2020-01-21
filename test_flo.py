#! /usr/bin/env python3
# coding: utf-8
#
# Author: Couzon Florent
#


# ======================================================================
# Imports
# ======================================================================
import logging as log; log.basicConfig(level=log.DEBUG)
import sys, os, signal
import time
import threading
import multiprocessing

import lib.pilot as pilot_i
import lib.hardware.ultrasound as ultrasound_i
import lib.hardware.wheel_motors as wheel_motors_i
import lib.auto_pilot as auto_pilot_i
# ======================================================================
# Main
# ======================================================================
global pilot
global auto_pilot
pilot = None
auto_pilot = None

def test_auto_pilot(auto_pilot):
	pilot = auto_pilot.pilot

	log.debug("Test Pilot:")

	log.debug("Move forward at speed 70 for 2 sec.")
	pilot.forward_speed(70)
	time.sleep(2)

	log.debug("Turn left for 2 sec.")
	pilot.turn_left()
	time.sleep(2)

	log.debug("Go straight for 2 sec.")
	pilot.go_straight()
	time.sleep(2)

	log.debug("Turn right for 2 sec.")
	pilot.turn_right()
	time.sleep(2)

	log.debug("Change speed to 100 for 2 sec.")
	pilot.set_speed(100)
	time.sleep(2)

	log.debug("Stop the car 1 sec.")
	pilot.stop()
	time.sleep(1)

	log.debug("Go backward at speed 70 for 2 sec.")
	pilot.backward_speed(70)
	time.sleep(2)

	log.debug("Turn left for 2 sec.")
	pilot.turn_left()
	time.sleep(2)

	log.debug("Rotate left for 2 sec.")
	pilot.rotate_speed_left(100)
	time.sleep(2)

	log.debug("Rotate right for 2 sec.")
	pilot.rotate_speed_right(100)
	time.sleep(2)

	pilot.stop()


def test_go_straight():
	o_pilot = pilot_i.Pilot()
	o_pilot.forward_speed(60)
	for i in range(100):
		time.sleep(0.1)
		o_pilot.go_straight()
	o_pilot.stop()

def test_auto_pilot_2():
	global auto_pilot
	auto_pilot = auto_pilot_i.Auto_Pilot(pilot_i.Pilot(),
		ultrasound_i.Ultrasound())
	while(1):
		auto_pilot.start()
		time.sleep(2)

def test_auto_pilot():
	global auto_pilot
	auto_pilot = auto_pilot_i.Auto_Pilot(pilot_i.Pilot(),
		ultrasound_i.Ultrasound())

	auto_pilot_i.test_auto_pilot(auto_pilot)

def test_bug():
	global auto_pilot
	auto_pilot = auto_pilot_i.Auto_Pilot(pilot_i.Pilot(),
		ultrasound_i.Ultrasound())
	while(1):
		auto_pilot.pilot.turn_left()
		auto_pilot.pilot.turn_right()
		time.sleep(0.01)



def test_avoid_obstacle():
	global auto_pilot
	auto_pilot = auto_pilot_i.Auto_Pilot(pilot_i.Pilot(),
		ultrasound_i.Ultrasound())
	auto_pilot.scenario_move_and_avoid()



def test_pilot_angle():
	global pilot
	pilot = pilot_i.Pilot()
	pilot.turn(100)
	time.sleep(1)
	pilot.turn(170)
	time.sleep(1)
	pilot.turn(200)
	time.sleep(1)
	pilot.turn(110)
	time.sleep(1)

def test_scenario_read_roadmap():
	global auto_pilot
	auto_pilot = auto_pilot_i.Auto_Pilot(pilot_i.Pilot(),
		ultrasound_i.Ultrasound())
	auto_pilot.scenario_read_roadmap("simple_roadmap.txt")

def handler(param1, param2):
	global auto_pilot
	global pilot
	if pilot != None:
		pilot.reset()
	if auto_pilot != None:
		auto_pilot.reset()

def timer_test():
	t0 = time.time()
	time.sleep(2)
	t1 = time.time()
	print("time" + str(t1-t0))

def test_direction():
	global auto_pilot
	auto_pilot = auto_pilot_i.Auto_Pilot(pilot_i.Pilot(),
		ultrasound_i.Ultrasound())
	pilot = auto_pilot.pilot
	while(1):
		val = input("f,t, h, s to stop\n")
		if val == "f":
			pilot.forward_speed(80)
		elif val == "t":
			val = int(input("give angle:\n"))
			pilot.turn(val)
		elif val == "s":
			pilot.reset()
			return
		elif val == "h":
			auto_pilot.half_turn()

def test_kill_multi_process():
	global auto_pilot
	auto_pilot = auto_pilot_i.Auto_Pilot(pilot_i.Pilot())
	threading.Thread(target=auto_pilot.scenario_move_and_avoid).start()
	time.sleep(5)
	auto_pilot.reset()
	log.debug("reset sent")
	# auto_pilot.pilot.reset()

def test_find_color(color):
	global auto_pilot
	auto_pilot = auto_pilot_i.Auto_Pilot(pilot_i.Pilot())
	t = threading.Thread(target=auto_pilot.scenario_find_color, args=[color,])
	t.start()
	t.join()
	log.debug("end of test")

def test_scenar_go_straight():
	global auto_pilot
	auto_pilot = auto_pilot_i.Auto_Pilot(pilot_i.Pilot())
	t = threading.Thread(target=auto_pilot.scenario_straight_line_time, args=[6,])
	t.start()
	t.join()



def test_gps_only():
	global auto_pilot
	auto_pilot = auto_pilot_i.Auto_Pilot(pilot_i.Pilot())
	t = threading.Thread(target=auto_pilot.sceanario_gps_only)
	t.start()
	t.join()

def test_gps_to_pos():
	global auto_pilot
	auto_pilot = auto_pilot_i.Auto_Pilot(pilot_i.Pilot())
	t = threading.Thread(target=auto_pilot.scenario_go_to_GPS_pos, args=[(4333.66814, 00127.95310),])
	t.start()
	t.join()

def main():
	signal.signal(signal.SIGINT, handler)
	# pilot.test_pilot()
	# test_go_straight()
	# test_auto_pilot_2()
	# wheel_motors_i.test_speed()
	test_avoid_obstacle()
	# test_pilot_angle()
	# test_scenario_read_roadmap()
	# timer_test()
	# test_direction()
	# test_kill_multi_process()
	# test_find_color("red")
	# test_scenar_go_straight()
	# test_speed_wait(5, 100)
	# test_gps_only()
	# test_gps_to_pos()

# Execution or import
if(__name__ == "__main__"):
	main()
	sys.exit(0)

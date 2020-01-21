#! /usr/bin/env python3
# coding: utf-8
#
# Author: Palacios Nicolas
#

import sys
import time
import signal
import threading

import lib.hardware.ultrasound as us
import lib.hardware.wheel_motors as wheel_motors_i
import lib.hardware.direction as dir
import lib.hardware.camera as cam
import lib.hardware.camera_direction as cam_dir

import lib.pilot as pilot_i
import lib.auto_pilot as auto_pilot_i

import lib.roadmap as rm
import lib.image_processing as iproc


global pilot, auto_pilot
pilot = auto_pilot = None


def handler(param1, param2):
	global pilot, auto_pilot
	if(pilot != None):
		pilot.reset()
	if(auto_pilot != None):
		auto_pilot.reset()

roadmap_file="simple_roadmap.txt"
def test_roadmap():
	print("### test_roadmap ###")
	roadmap = rm.Roadmap()
	roadmap.load(roadmap_file)
	for i in range(6):
		print(roadmap.read())


def test_cam_dir():
	print("### test_cam_dir ###")
	c_dir = cam_dir.Camera_direction()
	while(True):
		# c_dir.see_above_right()
		# c_dir.see_below_left()
		c_dir.see_above()
		time.sleep(0.1)
		c_dir.see_below()
		time.sleep(0.1)


def test_camera():
	print("### test_camera ###")
	c = cam.Camera()


def equive():
	pil = pilot_i.Pilot()
	ap = auto_pilot_i.Auto_Pilot(pil)

	ap.pilot.forward_speed(70)
	time.sleep(5)
	ap.pilot.turn_left()
	time.sleep(1)
	ap.pilot.turn_right()
	time.sleep(2)
	ap.pilot.turn_left()
	time.sleep(1)
	ap.pilot.go_straight()
	time.sleep(5)

	ap.pilot.stop()

def test_avoid_obstacle():
	auto_pilot = auto_pilot_i.Auto_Pilot(pilot_i.Pilot())
	auto_pilot.scenario_move_and_avoid()


def test_gps():
	print("### GPS ###")
	global auto_pilot
	auto_pilot = auto_pilot_i.Auto_Pilot(pilot_i.Pilot())
	auto_pilot.sceanario_gps_only()


def test_iproc():
	print("### test_iproc ###")

	while(True):
		ip = iproc.Image_Processing(cam.Camera())
		print(ip.major_color())
		time.sleep(0.5)


def test_us():
	print("### Ultrasound ###")
	u = us.Ultrasound()
	print(u.get_distance())


def test_direction():
	auto_pilot = auto_pilot_i.Auto_Pilot(pilot_i.Pilot(),
		us.Ultrasound())
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


def test_auto_pilot():
	print("### auto_pilot ###")

	global auto_pilot
	auto_pilot = auto_pilot_i.Auto_Pilot(pilot_i.Pilot())
	auto_pilot.scenario_move_and_avoid()


def test_scenar_go_straight():
	global auto_pilot
	auto_pilot = auto_pilot_i.Auto_Pilot(pilot_i.Pilot())
	t = threading.Thread(target=auto_pilot.scenario_straight_line_time, args=[6,])
	t.start()
	t.join()


def main():
	print("### nico_test ###")
	signal.signal(signal.SIGINT, handler)
	# test_roadmap()
	test_cam_dir()
	# test_avoid_obstacle()
	# test_camera()
	# test_iproc()
	# test_us()
	# test_gps()
	# test_direction()
	# test_auto_pilot()
	# test_scenar_go_straight()


if(__name__ == "__main__"):
	main()
	sys.exit(0)

import time
import math

from lib.pilot import Pilot
from lib.hardware.ultrasound import Ultrasound
from constants import UP, DOWN, LEFT, RIGHT, NORTH, SOUTH, WEST, EAST


pilot = Pilot()
ultrasound = Ultrasound()


def forward():
    global pilot
    pilot.forward_speed(60)
    for i in range(14):
        time.sleep(0.1)
        pilot.go_straight()
    pilot.reset()


def left():
    global pilot
    for i in range(32):
        time.sleep(0.1)
        pilot.rotate_speed_left(100)
    pilot.reset()


def right():
    global pilot
    for i in range(32):
        time.sleep(0.1)
        pilot.rotate_speed_right(100)
    pilot.reset()


def stop():
    global pilot
    pilot.stop()


map_action_direction = {
                            UP: {NORTH: [], EAST: [left], WEST: [right], SOUTH: [right, right]},
                            RIGHT: {NORTH: [right], EAST: [], WEST: [right, right], SOUTH: [left]},
                            LEFT: {NORTH: [left], EAST: [right, right], WEST: [], SOUTH: [right]},
                            DOWN: {NORTH: [right, right], EAST: [right], WEST: [left], SOUTH: []}
                       }

actions = [UP, DOWN, LEFT, RIGHT]
directions = [NORTH, SOUTH, WEST, EAST]
current_direction = SOUTH


def update_position(action):
    global current_direction, ultrasound
    direction = current_direction
    for f in map_action_direction[action][direction]:
        f()
    current_direction = directions[actions.index(action)]
    return ultrasound.get_distance()


def euclidean_distance(x_1, y_1, x_2, y_2):
    return math.sqrt((x_2 - x_1) ** 2 + (y_2 - y_1) ** 2)

import logging as log

import sys
import time

from lib.hardware.direction import Direction
from lib.hardware.wheel_motors import Wheel_Motors
import lib.hardware.enum_types as enum
from lib.position import Position
from lib.config import Config

log.basicConfig(level=log.DEBUG)


class Pilot(object):

    def CONFIG_FILE(self):
        return "/home/pi/projet/lib/pilot.conf"

    def __init__(self):

        self.wheel_motors = Wheel_Motors()
        self.direction = Direction()
        self.config = Config(self.CONFIG_FILE())
        self.position = Position(self.config)
        self.mvt_state = enum.Mvt_State.IDLE
        self.direction_state = enum.Direction_State.STRAIGHT

    # TODO delete if not needed here for straight movement test
    def set_value(self, value=427):
        self.direction_state = enum.Direction_State.MANUALLY_SET
        self.direction.set_value(value)

    def forward_speed(self, speed=None):
        self.mvt_state = enum.Mvt_State.FORWARD
        self.wheel_motors.forward_speed(speed)
        self.position.stop()
        if speed == None:
            self.position.start(self.wheel_motors.left_wheel.speed, self.direction_state)
        else:
            self.position.start(speed, self.direction_state)

    def backward_speed(self, speed=None):
        self.mvt_state = enum.Mvt_State.BACKWARD
        self.wheel_motors.backward_speed(speed)
        self.position.stop()
        if speed == None:
            self.position.start(-self.wheel_motors.left_wheel.speed, self.direction_state)
        else:
            self.position.start(-speed, self.direction_state)

    def turn(self, angle):
        self.direction.turn(angle)

    def turn_right(self):
        self.direction_state = enum.Direction_State.RIGHT
        self.direction.turn_right()
        if self.mvt_state == enum.Mvt_State.BACKWARD or self.mvt_state == enum.Mvt_State.FORWARD:
            self.position.start(self.wheel_motors.left_wheel.speed, self.direction_state)

    def turn_left(self):
        self.direction_state = enum.Direction_State.LEFT
        self.direction.turn_left()
        if self.mvt_state == enum.Mvt_State.BACKWARD or self.mvt_state == enum.Mvt_State.FORWARD:
            self.position.start(self.wheel_motors.left_wheel.speed, self.direction_state)

    def go_straight(self):
        self.direction_state = enum.Direction_State.STRAIGHT
        self.direction.home()
        if self.mvt_state == enum.Mvt_State.BACKWARD or self.mvt_state == enum.Mvt_State.FORWARD:
            self.position.start(self.wheel_motors.left_wheel.speed, self.direction_state)

    def set_90(self, time):
        if self.direction_state == enum.Direction_State.RIGHT:
            self.config.set("right_speed", self.wheel_motors.left_wheel.speed)
            self.config.set("right_time", time)
        elif self.direction_state == enum.Direction_State.LEFT:
            self.config.set("left_speed", self.wheel_motors.left_wheel.speed)
            self.config.set("left_time", time)
        self.config.save()

    def set_speed(self, speed):
        self.wheel_motors.set_speed(speed)
        self.position.start(self.wheel_motors.left_wheel.speed, self.direction_state)

    def stop(self):
        self.mvt_state = enum.Mvt_State.IDLE
        self.wheel_motors.stop()
        self.position.stop()

    def reset(self):
        self.position.stop()
        self.mvt_state = enum.Mvt_State.IDLE
        self.direction_state = enum.Direction_State.STRAIGHT
        self.stop()
        self.go_straight()

    def rotate_speed_right(self, speed=None):
        self.mvt_state = enum.Mvt_State.ROTATE
        self.wheel_motors.rotate_speed_right(speed)

    def rotate_speed_left(self, speed=None):
        self.mvt_state = enum.Mvt_State.ROTATE
        self.wheel_motors.rotate_speed_left(speed)


# Execution or import
if __name__ == "__main__":
    sys.exit(0)

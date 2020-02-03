import time
import math
import sys
import signal
import time
import json
import logging
import math
import numpy as np
import paho.mqtt.client as mqtt

from lib.pilot import Pilot
from lib.hardware.ultrasound import Ultrasound
from constants import UP, DOWN, LEFT, RIGHT, NORTH, SOUTH, WEST, EAST, ERROR_ESTIMATION, SOUTH_VALUE, NORTH_VALUE, WEST_VALUE, EAST_VALUE, MAX_SPEED, MIN_SPEED, SPEED_DECAY


MQTT_SERVER = "192.168.43.21"
MQTT_PORT = 1883

MQTT_BASE_TOPIC = "Direction"

MQTT_QOS = 0

MQTT_USER = ""
MQTT_PASSWORD = ""

client = None
log = None
shutdown = False
iteration = 0
compass_value = 0.0

pilot = Pilot()
ultrasound = Ultrasound()


def is_inside_circular_interval(value, left_bound, right_bound):
    if left_bound < right_bound:
        return left_bound <= value <= right_bound
    elif left_bound > right_bound:
        return value >= left_bound or value <= right_bound


# CTRL+C handler
def ctrlc_handler(signum, frame):
    global shutdown

    log.info("<CTRL + C> action detected...")
    shutdown = True
    stop()
    # Stop monitoring
    stop_monitoring()


# Stop the monitoring
def stop_monitoring():
    global client

    log.info("Shutdown : Stop MQTT operations")
    client.unsubscribe(MQTT_BASE_TOPIC)
    client.disconnect()
    client.loop_stop()
    del client


def on_connect(client, userdata, flags, rc):
    log.info("Connected with result code : %d" % rc)
    if rc == 0:
        log.info("Subscribing to topic : %s" % MQTT_BASE_TOPIC)
        client.subscribe(MQTT_BASE_TOPIC)


def on_message(client, userdata, msg):
    global compass_value

    payload = json.loads(msg.payload.decode("utf-8"))
    # log.debug("Received message " + json.dumps(payload) + " on topic " + msg.topic + " with QoS " + str(msg.qos))
    compass_value = float(payload)
    # print("Compass", compass_value)


def on_publish(client, userdata, mid):
    log.debug("MID : " + str(mid) + " published !")


def on_subscribe(mosq, obj, mid, granted_qos):
    log.debug("Subscribed : " + str(mid) + " " + str(granted_qos))


def on_log(mosq, obj, level, string):
    log.debug(string)


def get_orientation():
    global compass_value

    if is_inside_circular_interval(float(compass_value), float((NORTH_VALUE - ERROR_ESTIMATION) % 360), float((NORTH_VALUE + ERROR_ESTIMATION) % 360)):
        return NORTH
    elif is_inside_circular_interval(float(compass_value), float((SOUTH_VALUE - ERROR_ESTIMATION) % 360), float((SOUTH_VALUE + ERROR_ESTIMATION) % 360)):
        return SOUTH
    elif is_inside_circular_interval(float(compass_value), float((WEST_VALUE - ERROR_ESTIMATION) % 360), float((WEST_VALUE + ERROR_ESTIMATION) % 360)):
        return WEST
    elif is_inside_circular_interval(float(compass_value), float((EAST_VALUE - ERROR_ESTIMATION) % 360), float((EAST_VALUE + ERROR_ESTIMATION) % 360)):
        return EAST
    else:
        return None


def forward():
    global pilot

    pilot.forward_speed(60)
    for i in range(26):
        time.sleep(0.1)
        pilot.go_straight()
    pilot.reset()


def left():
    global pilot, compass_value

    direction = get_direction()
    target = None
    if direction == NORTH:
        target = WEST
    elif direction == WEST:
        target = SOUTH
    elif direction == SOUTH:
        target = EAST
    elif direction == EAST:
        target = NORTH
    else:
        print("Error")
        # target = direction

    decay = np.arange(0, 1, SPEED_DECAY)
    i = 0

    while get_orientation() != target:
        if i < len(decay):
            pilot.rotate_speed_right(MAX_SPEED - int(decay[i] * (MAX_SPEED - MIN_SPEED)))
            i += 1
        else:
            pilot.rotate_speed_right(MIN_SPEED)

    pilot.reset()


def right():
    global pilot, compass_value

    direction = get_direction()
    target = None
    if direction == NORTH:
        target = EAST
    elif direction == EAST:
        target = SOUTH
    elif direction == SOUTH:
        target = WEST
    elif direction == WEST:
        target = NORTH
    else:
        print("Error")
        # target = direction

    decay = np.arange(0, 1, SPEED_DECAY)
    i = 0

    while get_orientation() != target:
        if i < len(decay):
            pilot.rotate_speed_left(MAX_SPEED - int(decay[i] * (MAX_SPEED - MIN_SPEED)))
            i += 1
        else:
            pilot.rotate_speed_left(MIN_SPEED)

    pilot.reset()


def stop():
    global pilot

    pilot.stop()


def update_position(action):
    global current_direction, ultrasound

    direction = current_direction
    for f in map_action_direction[action][direction]:
        f()
    current_direction = directions[actions.index(action)]
    return ultrasound.get_distance()


def get_direction():
    global current_direction

    return current_direction


def euclidean_distance(x_1, y_1, x_2, y_2):
    return math.sqrt((x_2 - x_1) ** 2 + (y_2 - y_1) ** 2)


map_action_direction = {
                            UP: {NORTH: [], EAST: [left], WEST: [right], SOUTH: [right, right]},
                            RIGHT: {NORTH: [right], EAST: [], WEST: [right, right], SOUTH: [left]},
                            LEFT: {NORTH: [left], EAST: [right, right], WEST: [], SOUTH: [right]},
                            DOWN: {NORTH: [right, right], EAST: [right], WEST: [left], SOUTH: []}
                       }

actions = [UP, DOWN, LEFT, RIGHT]
directions = [NORTH, SOUTH, WEST, EAST]
current_direction = SOUTH


def main():
    global client, compass_value, iteration

    # Trap CTRL + C (kill -2)
    signal.signal(signal.SIGINT, ctrlc_handler)

    # MQTT setup
    client = mqtt.Client(clean_session=True, userdata=None)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    client.enable_logger(log)
    if len(MQTT_USER) != 0 and len(MQTT_PASSWORD) != 0:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    client.connect(MQTT_SERVER, MQTT_PORT, 60)
    client.loop_start()

    while not shutdown:
        if iteration == 0:
            print("Iteration", iteration)
            left()
            time.sleep(10)
            iteration += 1
        elif iteration == 1:
            print("Iteration", iteration)
            right()
            time.sleep(10)
            iteration += 1
        elif iteration == 2:
            print("Iteration", iteration)
            left()
            time.sleep(10)
            iteration += 1
        elif iteration == 3:
            print("Iteration", iteration)
            right()
            time.sleep(10)
            iteration += 1
        # pass
        # value = get_orientation()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout)
    log = logging.getLogger()

    log.setLevel(logging.INFO)

    main()


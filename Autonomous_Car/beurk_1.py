import signal
import json
import paho.mqtt.client as mqtt
from threading import Thread, Lock
import sys
import select
import time
import numpy as np

import lib.pilot as pilot_i
from control_car import get_direction
from constants import UP, DOWN, LEFT, RIGHT, NORTH, SOUTH, WEST, EAST, ERROR_ESTIMATION


MQTT_SERVER = "192.168.43.21"
MQTT_PORT = 1883

MQTT_BASE_TOPIC = "Direction"

MQTT_QOS = 0

MQTT_USER = ""
MQTT_PASSWORD = ""

client = None
log = None
shutdown = False
SGH = None
compass_value = 0.0
SOUTH_VALUE = 187.76
NORTH_VALUE = (SOUTH_VALUE + 180) % 360
WEST_VALUE = (SOUTH_VALUE + 90) % 360
EAST_VALUE = (SOUTH_VALUE + 270) % 360


def is_inside_circular_interval(value, left_bound, right_bound):
    if left_bound < right_bound:
        return left_bound <= value <= right_bound
    elif left_bound > right_bound:
        return value >= left_bound or value <= right_bound

# ------------------------------------------------------------------------------
# ____________________________________GLOBALS_PARAMETERS________________________


hundler_gest = Lock()


#
# d'une feuille A4 a une autre
# speed = 60 ?/s
# temps = 0.1 s
def go_one_step():
    o_pilot = pilot_i.Pilot()
    o_pilot.forward_speed(60)
    for i in range(26):
        time.sleep(0.1)
        o_pilot.go_straight()
    o_pilot.reset()


def left():
    global pilot
    pilot = pilot_i.Pilot()
    # get target
    d = get_direction()
    target = None
    if d == NORTH:
        target = WEST
    elif d == WEST:
        target = SOUTH
    elif d == SOUTH:
        target = EAST
    elif d == EAST:
        target = NORTH
    else:
        print("ERROR")
        # target = d

    decay = np.arange(0, 1, 0.001)
    i = 0

    pilot.turn(90)

    while get_orientation() != target:
        # a = datetime.datetime.now()
        if i < len(decay):
            pilot.rotate_speed_left(100 - int(decay[i] * 10))
            i += 1
        else:
            pilot.rotate_speed_left(90)
        # time.sleep(0.1)
        # b = datetime.datetime.now()
        # print("Time", (b - a).microseconds)

    pilot.reset()


def right():
    global pilot
    pilot = pilot_i.Pilot()
    d = get_direction()
    target = None
    if d == NORTH:
        target = EAST
    elif d == EAST:
        target = SOUTH
    elif d == SOUTH:
        target = WEST
    elif d == WEST:
        target = NORTH
    else:
        print("ERROR")
        # target = d

    # for i in range(10):
    #     pilot.rotate_speed_left(70)
    #     print(get_orientation())
    # pilot.reset()

    decay = np.arange(0, 1, 0.001)
    i = 0

    while get_orientation() != target:
        if i < len(decay):
            pilot.rotate_speed_right(100 - int(decay[i] * 10))
            i += 1
        else:
            pilot.rotate_speed_right(90)
        # time.sleep(0.1)

    pilot.reset()


def pStop():
    pilot = pilot_i.Pilot()
    pilot.stop()


# ------------------------------------------------------------------------------
# ____________________________________THD_SRV_HDLR______________________________
class Server_GestionHundler(Thread):
    # Server Gestion definition
    # self    : curent prompt
    # lock    : to manage the scr shared
    def __init__(self, lock):
        Thread.__init__(self)
        self.lock = lock
        self.stop = True

    # ________________________________________________________
    # Stop thread
    def serverCmmandStopLoop(self):
        with self.lock:
            self.stop = False
            print('stop = ', self.stop)

    # _______________________________________________________
    # Server gestion
    def run(self):
        print("COMMANDE TO MANAGE THE SERVER : \n")
        print("#############################################")
        print("################### HELP ####################")
        print("h    : affiche les commande")
        print("g    : demmander une cle dans le cercle")
        print("p    : inserer une valeur dans le cercle")
        print("s    : afficher le status du noeud")
        print("st   : afficher les atistiques ")
        print("#############################################")
        print('Enter CMD : ')
        while self.stop:
            input = select.select([sys.stdin], [], [], 1)[0]  # template to have a  keyboard listener
            if input:  # non bloking methode
                v = sys.stdin.readline().rstrip()
                if v == "q" or v == "Q":
                    break
                elif v == "h" or v == "H":
                    print("COMMANDE TO MANAGE THE SERVER : \n")
                    print("#############################################")
                    print("################### HELP ####################")
                    print("h    : affiche les commande")
                    print("g    : demmander une cle dans le cercle")
                    print("p    : inserer une valeur dans le cercle")
                    print("s    : afficher le status du noeud")
                    print("st   : afficher les atistiques ")
                    print("#############################################")
                elif v == "s" or v == "S":
                    go_one_step()
                elif v == "a":
                    left()
                elif v == "z":
                    right()
                elif v == "x":
                    pStop()
                else:
                    print('entry : ', v)
                print('Enter CMD : ')


# CTRL+C handler
def ctrlc_handler(signum, frame):
    global shutdown
    shutdown = True
    # Stop monitoring
    stop_monitoring()


# Stop the monitoring
def stop_monitoring():
    global client, SGH

    client.unsubscribe(MQTT_BASE_TOPIC)
    client.disconnect()
    client.loop_stop()
    SGH.serverCmmandStopLoop()

    del client


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(MQTT_BASE_TOPIC)


def on_message(client, userdata, msg):
    global compass_value
    payload = json.loads(msg.payload.decode("utf-8"))
    # compass_value = float(payload)
    # print("Compass", compass_value)
    compass_value = float(payload)


def on_publish(client, userdata, mid):
    pass


def on_subscribe(mosq, obj, mid, granted_qos):
    pass


def on_log(mosq, obj, level, string):
    pass


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


"""def get_orientation():
    global compass_value

    if is_inside_circular_interval(float(compass_value), float(NORTH_VALUE), float(EAST_VALUE)):
        return NORTH
    elif is_inside_circular_interval(float(compass_value), float(EAST_VALUE), float(SOUTH_VALUE)):
        return EAST
    elif is_inside_circular_interval(float(compass_value), float(SOUTH_VALUE), float(WEST_VALUE)):
        return SOUTH
    elif is_inside_circular_interval(float(compass_value), float(WEST_VALUE), float(NORTH_VALUE)):
        return WEST
"""


def main():
    global client, SGH

    # Trap CTRL + C (kill -2)
    signal.signal(signal.SIGINT, ctrlc_handler)

    # MQTT setup
    client = mqtt.Client(clean_session=True, userdata=None)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    if len(MQTT_USER) != 0 and len(MQTT_PASSWORD) != 0:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    client.connect(MQTT_SERVER, MQTT_PORT, 60)
    client.loop_start()

    SGH = Server_GestionHundler(hundler_gest)
    SGH.start()

    while not shutdown:
        pass


if __name__ == "__main__":

    main()


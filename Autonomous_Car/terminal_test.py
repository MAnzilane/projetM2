from threading import Thread, Lock
import logging
import sys
import select

import time

import lib.pilot as pilot_i
import lib.hardware.ultrasound as ultrasound_i
import lib.hardware.wheel_motors as wheel_motors_i

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
    for i in range(14):
        time.sleep(0.1)
        o_pilot.go_straight()
    o_pilot.reset()


def left():
    global pilot
    pilot = pilot_i.Pilot()
    for i in range(32):
        time.sleep(0.1)
        pilot.rotate_speed_left(100)
    pilot.reset()


def right():
    global pilot
    pilot = pilot_i.Pilot()
    for i in range(32):
        time.sleep(0.1)
        pilot.rotate_speed_right(100)
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
    def __init__(self, lock, log):
        Thread.__init__(self)
        self.lock = lock
        self.log = log
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


# ------------------------------------------------------------------------------
# ____________________________________MAIN_FUNCTION_____________________________

# Logging setup
logging.basicConfig(filename='node.log', filemode='a',
                    format="[%(asctime)s][%(module)s:%(funcName)s:%(lineno)d][%(levelname)s] %(message)s")
log = logging.getLogger()
print("\n[DBG] DEBUG mode activated ... ")
log.setLevel(logging.DEBUG)
# log.setLevel(logging.INFO)
SGH = Server_GestionHundler(hundler_gest, log)
SGH.start()

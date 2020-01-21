#! /bin/sh

ifconfig wlan0 down
iwconfig wlan0 mode Ad-Hoc test
iwconfig essid RaspberryPiNetwork
iwconfig key "Raspberry"

exit 0

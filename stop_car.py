#! /usr/bin/env python3
# coding: utf-8
#
# Author: Couzon Florent
#


# ======================================================================
# Imports
# ======================================================================
import logging as log; log.basicConfig(level=log.DEBUG)
import sys

import lib.pilot as pilot

# ======================================================================
# Main
# ======================================================================



def main():
	obj_pilot = pilot.Pilot()
	obj_pilot.stop()
	obj_pilot.go_straight()

# Execution or import
if(__name__ == "__main__"):
	main()
	sys.exit(0)

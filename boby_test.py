#! /usr/bin/env python3
# coding: utf-8
#
# Author: Palacios Nicolas
#

import sys
from time import sleep

from lib.position import Position


def main():
	p = Position()
	p.stop()
	p.start(60)
	sleep(3)
	p.stop()



if(__name__ == "__main__"):
	main()
	sys.exit(0)

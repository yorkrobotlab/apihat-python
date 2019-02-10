#!/usr/bin/python
# YRL028 - APIHAT - Python 3 API Version 0.1
#
# Functions for communicating with the ATMega328P [Arduino]
#
# James Hilder, York Robotics Laboratory, Feb 2019

import logging, threading, time, random, os, smbus2                             #General Python imports
import settings as s

i2c_bus = smbus2.SMBus(s.ARDUINO_BUS)                                           #The Arduino is attached to i2c_10

def write_message(message):
    i2c_bus.write_i2c_block_data(s.ARDUINO_ADDRESS, 0, message)

#Command line test [will run when arduino.py is run directly]
if __name__ == "__main__":
 logger = logging.getLogger()
 logger.setLevel(logging.DEBUG)
 write_message([72,73])
 os._exit(1)

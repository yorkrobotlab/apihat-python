#!/usr/bin/python
# YRL028 - APIHAT - Python 3 API Version 0.1
#
# Functions for communicating with the ATMega328P [Arduino]
#
# James Hilder, York Robotics Laboratory, Feb 2019

import logging, threading, time, random, os, smbus2                             #General Python imports
from smbus2 import i2c_msg
import settings as s

i2c_bus = smbus2.SMBus(s.ARDUINO_BUS)                                           #The Arduino is attached to i2c_10

def write_message(register,message):
    i2c_bus.write_i2c_block_data(s.ARDUINO_ADDRESS, register, message)

#Command line test [will run when arduino.py is run directly]
if __name__ == "__main__":
 logger = logging.getLogger()
 logger.setLevel(logging.DEBUG)
 #message = i2c_bus.read_i2c_block_data(s.ARDUINO_ADDRESS, 0, 6)
 i2c_bus.write_byte(s.ARDUINO_ADDRESS,0)
 msg = i2c_msg.read(s.ARDUINO_ADDRESS,6)
 i2c_bus.i2c_rdwr(msg)
 logging.info(list(msg))
 time.sleep(0.5)

 i2c_bus.write_byte(s.ARDUINO_ADDRESS,1)
 msg = i2c_msg.read(s.ARDUINO_ADDRESS,4)
 i2c_bus.i2c_rdwr(msg)
 list_m = list(msg)
 long_val = (list_m[0] << 24) + (list_m[1] << 16) + (list_m[2] << 8) + list_m[3]
 logging.info(long_val)
 time.sleep(0.5)

 i2c_bus.write_byte(s.ARDUINO_ADDRESS,2)
 msg = i2c_msg.read(s.ARDUINO_ADDRESS,4)
 i2c_bus.i2c_rdwr(msg)
 logging.info(list(msg))
 time.sleep(0.5)

 time.sleep(.5)
 write_message(0,[72,73])
 time.sleep(.500)
 write_message(0,[72,79])
 time.sleep(.500)
 os._exit(1)

#!/usr/bin/python
# YRL028 - APIHAT - Python 3 API Version 0.3
#
# Functions for communicating with the YRL031 Dual H-Bridge Driver PCB
#
# James Hilder, York Robotics Laboratory, May 2019

import logging, threading, time, random, os, smbus2                             #General Python imports
from smbus2 import i2c_msg
import settings as s

i2c_bus = smbus2.SMBus(s.YRL031_BUS)                                            #If PCB is mounted on top of APIHAT use bus 10 [i2c_7]

def bytes_to_signed_long(list_m):
 long_val = (list_m[0] << 24) + (list_m[1] << 16) + (list_m[2] << 8) + list_m[3]
 if(long_val >= 2147483648): long_val -= 4294967296
 return long_val

def set_motor_speeds(speed1,speed2):
    i2c_bus.write_i2c_block_data(s.YRL031_ADDRESS,7,[speed1+128,speed2+128])
    # set_motor_1_speed(speed1)
    # set_motor_2_speed(speed2)

def set_motor_1_speed(speed):
    i2c_bus.write_byte_data(s.YRL031_ADDRESS, 5, speed+128)

def set_motor_2_speed(speed):
    i2c_bus.write_byte_data(s.YRL031_ADDRESS, 6, speed+128)

def write_message(register,message):
    i2c_bus.write_i2c_block_data(s.YRL031_ADDRESS, register, message)

def read_encoder(register):
    try:
      i2c_bus.write_byte(s.YRL031_ADDRESS,register)
      msg = i2c_msg.read(s.YRL031_ADDRESS,4)
      i2c_bus.i2c_rdwr(msg)
      return bytes_to_signed_long(list(msg))
    except OSError:
      logging.error("Error reading i2c encoder message from YRL031")
      return 0

#Command line test [will run when yrl031.py is run directly]
if __name__ == "__main__":
 logger = logging.getLogger()
 logger.setLevel(logging.DEBUG)
 set_motor_1_speed(0)
 enc_1_count = read_encoder(1)
 enc_1_odo = read_encoder(3)
 enc_2_count = read_encoder(2)
 enc_2_odo = read_encoder(4)
 logging.info("Left %d [%d] | Right %d [%d]" % (enc_1_count,enc_1_odo,enc_2_count,enc_2_odo))
 os._exit(1)

#!/usr/bin/python
# YRL028 - APIHAT - Python 3 API Version 0.2
#
# Functions for communicating with the ATMega328P [Arduino]
#
# James Hilder, York Robotics Laboratory, Mar 2019

import logging, threading, time, random, os, smbus2                             #General Python imports
from smbus2 import i2c_msg
import settings as s

i2c_bus = smbus2.SMBus(s.ARDUINO_BUS)                                           #The Arduino is attached to i2c_10

def bytes_to_signed_long(list_m):
 long_val = (list_m[0] << 24) + (list_m[1] << 16) + (list_m[2] << 8) + list_m[3]
 if(long_val >= 2147483648): long_val -= 4294967296
 return long_val

def tone(frequency):
    msb = int(frequency / 256)
    lsb = int(frequency % 256)
    print("MSB %d  LSB %d" % (msb,lsb))
    i2c_bus.write_i2c_block_data(s.ARDUINO_ADDRESS,8,[msb,lsb])

def stop_tone():
    tone(0)
    
def set_motor_speeds(speed1,speed2):
    i2c_bus.write_i2c_block_data(s.ARDUINO_ADDRESS,7,[speed1+128,speed2+128])
    # set_motor_1_speed(speed1)
    # set_motor_2_speed(speed2)

def set_motor_1_speed(speed):
    i2c_bus.write_byte_data(s.ARDUINO_ADDRESS, 5, speed+128)

def set_motor_2_speed(speed):
    i2c_bus.write_byte_data(s.ARDUINO_ADDRESS, 6, speed+128)

def write_message(register,message):
    i2c_bus.write_i2c_block_data(s.ARDUINO_ADDRESS, register, message)

def read_encoder(register):
    try:
      i2c_bus.write_byte(s.ARDUINO_ADDRESS,register)
      msg = i2c_msg.read(s.ARDUINO_ADDRESS,4)
      i2c_bus.i2c_rdwr(msg)
      return bytes_to_signed_long(list(msg))
    except OSError:
      logging.error("Error reading i2c encoder message from Arduino")
      return 0

#Command line test [will run when arduino.py is run directly]
if __name__ == "__main__":
 logger = logging.getLogger()
 logger.setLevel(logging.DEBUG)
 enc_1_count = read_encoder(1)
 enc_1_odo = read_encoder(3)
 enc_2_count = read_encoder(2)
 enc_2_odo = read_encoder(4)
 logging.info("Left %d [%d] | Right %d [%d]" % (enc_1_count,enc_1_odo,enc_2_count,enc_2_odo))
 tone(250)
 time.sleep(0.5)
 tone(300)
 time.sleep(0.5)
 tone(6000)
 time.sleep(0.5)
 stop_tone()
 os._exit(1)

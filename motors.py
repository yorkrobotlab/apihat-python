#!/usr/bin/python
# YRL028 - APIHAT - Python 3 API Version 0.1
#
# Functions for the i2c based motor drivers
#
# James Hilder, York Robotics Laboratory, Feb 2019

import settings as s
import smbus2, logging
import time, sys, os

silent = False

i2c = smbus2.SMBus(s.MOTORS_BUS)                                                #The motor drivers are attached to i2c_7

#Check requested speed ranges from -1 to 1
def check_bounds(speed):
  if speed > 1.0: return 1.0
  if speed < -1.0: return -1.0
  return speed

#Convert speed from [0.0-1.0] into adjusted integer
#We can set speed from range 6 (0.48V) to 63 (5.08V)
def get_integer_speed(speed):
  return int(abs ( speed * 56 ) + 6)

#Write the byte values to both motor drivers using I2C
def write_motor_bytes(motor_1_byte, motor_2_byte):
  i2c.write_byte_data(s.MOTOR1_ADDRESS, 0, motor_1_byte)
  i2c.write_byte_data(s.MOTOR2_ADDRESS, 0, motor_2_byte)

#Move forwards, speed -1.0 to 1.0, zero will put in coast
def forwards(speed):
  check_bounds(speed)
  motor1_byte = 0
  motor2_byte = 0
  if speed == 0:
    if not silent:
        logging.info("Setting both motors to coast")
  else:
    integer_speed = get_integer_speed(speed)
    if speed < 0:
        if not silent:
            logging.info("Setting speed to {} [{}V] backwards".format(integer_speed,(0.08 * integer_speed)))
        motor1_byte = ( integer_speed << 2 ) + 1
        motor2_byte = ( integer_speed << 2) + 2
    else:
        if not silent:
            logging.info("Setting speed to {} [{}V] forwards".format(integer_speed,(0.08 * integer_speed)))
        motor1_byte = ( integer_speed << 2 ) + 2
        motor2_byte = ( integer_speed << 2) + 1
  write_motor_bytes(motor1_byte,motor2_byte)

#Move backwards, speed -1.0 to 1.0, zero will put in coast
def backwards(speed):
  forwards(-speed)

def set_motor_speeds(motor1_speed,motor2_speed):
  set_motor1_speed(motor1_speed)
  set_motor2_speed(motor2_speed)

#Set motor 1 speed to given, speed -1.0 to 1.0, zero will put in coast
def set_motor1_speed(speed):
  check_bounds(speed)
  byte = 0
  if speed == 0:
    if not silent:
        logging.info("Setting motor 1 to coast")
  else:
    integer_speed = get_integer_speed(speed)
    if speed < 0:
        if not silent:
            logging.info("Setting motor 1 speed to {} [{}V] backwards".format(integer_speed,(0.08 * integer_speed)))
        byte = ( integer_speed << 2 ) + 1
    else:
        if not silent:
            logging.info("Setting motor 1 speed to {} [{}V] forwards".format(integer_speed,(0.08 * integer_speed)))
        byte = ( integer_speed << 2 ) + 2
  i2c.write_byte_data(s.MOTOR1_ADDRESS, 0, byte)

#Set motor 2 speed to given, speed -1.0 to 1.0, zero will put in coast
def set_motor2_speed(speed):
  check_bounds(speed)
  byte = 0
  if speed == 0:
    if not silent:
        logging.info("Setting motor 2 to coast")
  else:
    integer_speed = get_integer_speed(speed)
    if speed < 0:
        if not silent:
            logging.info("Setting motor 2 speed to {} [{}V] backwards".format(integer_speed,(0.08 * integer_speed)))
        byte = ( integer_speed << 2 ) + 2
    else:
        if not silent:
            logging.info("Setting motor 2 speed to {} [{}V] forwards".format(integer_speed,(0.08 * integer_speed)))
        byte = ( integer_speed << 2 ) + 1
  i2c.write_byte_data(s.MOTOR2_ADDRESS, 0, byte)

#Turn on spot
def turn(speed):
  set_motor1_speed(speed)
  set_motor2_speed(-speed)

#Coast both motors
def coast():
  forwards(0)

#Brake motor 1
def brake_motor1():
  byte = 0x03  # IN1 & IN2 both high = brake
  if not silent:
    logging.info("Setting motor 1 to brake")
  i2c.write_byte_data(s.MOTOR1_ADDRESS, 0, byte)

#Brake motor 2
def brake_motor2():
  byte = 0x03  # IN1 & IN2 both high = brake
  if not silent:
    logging.info("Setting motor 2 to brake")
  i2c.write_byte_data(s.MOTOR2_ADDRESS, 0, byte)

#Brake both motors
def brake():
  brake_motor1()
  brake_motor2()

#Test code
if __name__ == "__main__":
 for big in range(0, 10):
  for step in range (0, 10):
    turn(0.65)
    time.sleep(0.07)
    brake()
    time.sleep(0.1)
  turn(-0.59)
  #1 Second per 90 degrees at speed 0.59
  time.sleep(0.66)
  brake()
  time.sleep(0.1)
 os._exit(1)

# H-Bridge Logic
#
# Motors use DRV8830 (Left = 0x62, Right = 0x60)
#
# IN1  IN2  OUT1  OUT2  FUNCTION
# 0    0    Z     Z     Standby/coast
# 0    1    L     H     Reverse
# 1    0    H     L     Forward
# 1    1    H     H     Brake
#
# Vset 5..0 control voltage (ie speed).  voltage = 0.08 x Vset
# Min value 0x06 (000110) = 0.48V
# Max value 0x3F (111111) = 5.06V
#
# Register 0 is control register, Register 1 is fault register
# Control register:
# Vset[5] Vset[4] Vset[3] Vset[2] Vset[1] Vset[0] In2 In1

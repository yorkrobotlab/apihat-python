#!/usr/bin/python
# YRL028 - APIHAT - Python 3 API Version 0.1
#
# Functions for the YRL015 Switch Board
#
# James Hilder, York Robotics Laboratory, Feb 2019

import smbus2 #I2C function
import settings as s
from threading import Timer
import time, logging

GPIO_ADDRESS = s.SWITCH_GPIO_ADDRESS        # I2C Address of PCA9555 GPIO Expander on YRL015 Switch Board
GPIO_I2CBUS = s.SWITCH_BUS                  # The YRL015 switch is connected I2C_9 [7th output of switch]

# On YRL028, GPIO 25(pin 22) is interrupt in
# IO0-0 : IO0-3  4-WAY DIP SWITCH [I]
# IO0-4 : IO0-7  NAV SWITCH U-D-L-R [I]
# IO1-0          NAV SWITCH CENTER [I]
# IO1-1          PUSH BUTTON [I]
# IO1-2          PUSH BUTTON LED [O]
# IO1-3 : IO1-6  4-WAY DIP LEDS [O]
# IO1-7          POWER BUTTON LED [O]

BLINK_LIMIT = 9 # Number of half-cycles for LED blink
BLINK_DELAY = 0.03 # The delay in seconds between blink states

animation_count_power = 0
animation_count_user = 0
output_byte = 0
i2c = smbus2.SMBus(GPIO_I2CBUS)

def update_output(new_output_byte):
  OUTPUT_PORT = 0x03
  global output_byte
  output_byte = new_output_byte
  i2c.write_byte_data(GPIO_ADDRESS, OUTPUT_PORT, output_byte)

def one_blink_power_led():
  global animation_count_power
  animation_count_power = BLINK_LIMIT - 1
  blink_power_led()

def one_blink_user_led():
  global animation_count_user
  animation_count_user = BLINK_LIMIT - 1
  blink_user_led()

def blink_power_led():
  global animation_count_power
  if animation_count_power % 2 == 1:
    update_output(output_byte & 0x7F)
  else:
    update_output(output_byte | 0x80)
  animation_count_power += 1
  if animation_count_power > BLINK_LIMIT:
    animation_count_power = 0
  else:
    t = Timer(BLINK_DELAY, blink_power_led)
    t.start()

def blink_user_led():
  global animation_count_user
  if animation_count_user % 2 == 1:
    update_output(output_byte & 0xFB)
  else:
    update_output(output_byte | 0x04)
  animation_count_user += 1
  if animation_count_user > BLINK_LIMIT:
    animation_count_user = 0
  else:
    t = Timer(BLINK_DELAY, blink_user_led)
    t.start()

def setup_gpio():
  CONFIG_REGISTERS = 0x14
  i2c.write_byte_data(GPIO_ADDRESS, 0x04, 0xFF)
  i2c.write_byte_data(GPIO_ADDRESS, 0x05, 0x03)
  i2c.write_byte_data(GPIO_ADDRESS, 0x06, 0xFF)
  i2c.write_byte_data(GPIO_ADDRESS, 0x07, 0x03)


#Return [long] value for input registers
def read_input_registers():
  return (i2c.read_word_data(GPIO_ADDRESS, 0x00) & 0x3FF)

#Return [nibble] value for 4-way dip-switch
def read_dip_switch():
   return read_input_register % 8

def set_dip_leds(nibble):
   update_output((output_byte & 0x87) + (nibble << 3))

def init():
    setup_gpio()

def detect():
  try:
    i2c.read_byte(GPIO_ADDRESS)
    init()
    return True
  except IOError:
    logging.debug("No YRL015 switch board detected at address 0x%X on bus i2c_%d" % (GPIO_ADDRESS,GPIO_I2CBUS))
    return False

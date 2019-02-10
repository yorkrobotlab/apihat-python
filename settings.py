#!/usr/bin/python
# YRL028 - APIHAT - Python 3 API Version 0.1
#
# Settings and constants file
#
# James Hilder, York Robotics Laboratory, Feb 2019

import logging,sys

# Set the Python logging level; recommend INFO for deployment and DEBUG for debugging
LOGGING_MODE = logging.INFO
#LOGGING_MODE = logging.DEBUG

DISPLAY_ROTATED         = True                                                  #Set to true if the OLED module is rotated to flip image
SENSOR_PORT_LIST        = [3,4,5]                                               #The I2C ports which will be scanned for sensors

POLL_PERIOD             = 1.0                                                   #Period (seconds) at which to update sensor readings

ENABLE_BATTERY_MONITOR    = True                                                #If enabled core.py will display visual+audible warnings when battery low
BATTERY_CRITICAL_SHUTDOWN = True                                                #If enabled, system will shutdown when Vbatt<BATTERY_SHUTDOWN_VOLTAGE
BATTERY_LOW_VOLTAGE = 10.2
BATTERY_CRITICAL_VOLTAGE = 9.2
BATTERY_SHUTDOWN_VOLTAGE = 8.9

# The following settings are only used when a YRL015 switch board is NOT connected
ENABLE_DEMO_MODE        = False
ENABLE_STATS_MODE       = False
ENABLE_AUTOSENSE_MODE   = True



# The following are things you are less likely to want to change on the YRL028 setup...
OLED_BUS                = 8                                                     #The bus which the OLED module is attached to [i2c_8 on YRL028]
LED_DRIVER_BUS          = 9                                                     #The bus which the TCA6507 LED driver is attached to [i2c_9 on YRL028]
SWITCH_BUS              = 9                                                     #The bus which the YRL015 switch board is attached to [i2c_9 on YRL028]
SWITCH_INTERRUPT_PIN    = 25                                                    #The GPIO pin connected to interrupt out of YRL015 switch board
SWITCH_GPIO_ADDRESS     = 0x20                                                  #I2C Address of GPIO expender on YRL015 switch board
ADC_BUS                 = 9                                                     #The bus which the ADS7830 ADC is connected to [i2c_9 on YRL028]
ADC_ADDRESS             = 0x48                                                  #The I2C address for the ADS7830
MOTORS_BUS              = 7                     
MOTOR1_ADDRESS          = 0x60
MOTOR2_ADDRESS          = 0x62

# The following are I2C and register addresses and other parameters for the YRL013 and YLR019 sensor boards
GRIDEYE_ADDRESS         = 0x69
GAS_SENSOR_GPIO_ADDRESS = 0x41
GAS_SENSOR_ADC_ADDRESS  = 0x23
HUMIDITY_SENSOR_ADDRESS = 0x27
SENSOR_LED_ADDRESS_1    = 0x6A                                                  # I2C Address of the TLC59116 LED Driver on the YRL019 Sensor
SENSOR_LED_ADDRESS_2    = 0x69
TOF_SENSOR_ADDRESS      = 0x29                                                  # I2C Address of the VL53L0X Time-of-flight Sensor
IR_ADDRESS 	            = 0x60                                                  # I2C Address of the VCNL4040 IR Sensor
SENSOR_ADC_ADDRESS      = 0x4d                                                  # I2C Address of the MCP3221 ADC
EPROM_ADDRESS           = 0x50                                                  # I2C Address of the EEPROM
COLOUR_ADDRESS          = 0x10                                                  # I2C Address of the VEML6040 Colour Sensor
ALS_CONF_REG            = 0x00
PS_CONF1_REG            = 0x03
PS_CONF3_REG            = 0x04
PS_DATA_REG             = 0x08
ALS_DATA_REG            = 0x09
WHITE_DATA_REG          = 0x0A
RED_REGISTER 	        = 0x08
GREEN_REGISTER 	        = 0x09
BLUE_REGISTER 	        = 0x0A
WHITE_REGISTER 	        = 0x0B
WHITE_BYTE 	            = 0x40
COMMAND_BYTE 	        = 0x04
COLOUR_SENSOR_SENSITIVITY = 0x00                                                #Range 0 - 5 [40ms, 0.25168 lux/count  to 1280ms,
NOISE_FLOOR = 4000

# The locations for the sensor and system file logs
system_datafilename="/ramdisk/system.csv"
sensor_datafilename="/ramdisk/sensor"

def init():
    global use_built_in_dip_functions
    global initial_led_brightness
    global max_brightness
    global sensor_list
    global default_poll_period
    use_built_in_dip_functions = True                                             #Enable to use the built-in functions for the DIP switches
    sensor_list = []
    initial_led_brightness = 0.3                                                  #Multiplied by max_brightness
    max_brightness = 0.3                                                          #Brightness limit for LEDs.  Range 0-1.  1 is very bright and may cause power\heat issues if not used carefully...
    default_poll_period = POLL_PERIOD
    logger = logging.getLogger()
    logger.setLevel(LOGGING_MODE)

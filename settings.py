#!/usr/bin/python
# YRL028 - APIHAT - Python 3 API Version 0.3
#
# Settings and constants file
#
# James Hilder, York Robotics Laboratory, May 2019

import logging,sys

VERSION_STRING="0.03.190501"
# Set the Python logging level; recommend INFO for deployment and DEBUG for debugging
LOGGING_MODE = logging.INFO
#LOGGING_MODE = logging.DEBUG

ENABLE_PROGRAMS = True
DEFAULT_PROGRAM = None
AUDIO_VOLUME = 90
AUDIO_FILEPATH = "wav"
PROGRAM_FILEPATH = "user_programs"
ENABLE_ROBOT_TAB = True                                                         #Enable if a robot sensor model and motor model is defined to enable components in DASH server

# Define the robot sensors for DASH server, list of list of 4 elements: sensor ID, sensor type, theta, +-view angle

# Sensor model for original black robot
# ROBOT_SENSOR_MODEL = [
#     ['analog-1','2y0a21',48,14],
#     ['analog-2','2y0a21',18,14],
#     ['analog-3','2y0a21',312,14],
#     ['analog-4','2y0a21',342,14]
# ]

# Sensor model for AARM robot
ROBOT_SENSOR_MODEL = [
    ['analog-1','2y0a21',315,14],
    ['analog-2','2y0a21',345,14],
    ['analog-3','2y0a21',15,14],
    ['analog-4','2y0a21',45,14]
]

# The following settings are applicable if a YRL031 dual H-bridge driver board is attached
YRL031_HBRIDGE_BOARD    = True                                                  #If enabled system will expect to find a YRL031 high-current H-bridge board attached to one of the i2c busses
YRL031_BUS              = 6                                                     #The I2C port to which the h-bridge board is attached.  Use port 10 [i2c_7] if the PCB is directly mounted on the APIHAT.
YRL031_ADDRESS          = 0x58                                                  #Default configured address = 0x58

# The automatic fan program requires a 5V fan to be attached to i2c motor 2.
ENABLE_FAN_PROGRAM      = True                                                  #If enabled, core.py will control motor 2 speed relevant to PCB, CPU and where applicable YRL031 temperature
FAN_PROGRAM_BASE_SPEED  = 0.40                                                  #Minimum PWM speed for fan; too low may stall
FAN_PROGRAM_BASE_PCB_TEMP = 28                                                  #PCB Temperature in C at which fan will start to spin
FAN_PROGRAM_BASE_CPU_TEMP = 45                                                  #CPU Temperature in C at which fan will start to spin
FAN_PROGRAM_BASE_YRL031_TEMP = 45                                               #YRL031 Temperature in C at which fan will start to spin (if attached)
FAN_PROGRAM_DELTA = 20                                                          #The range of temperature at which fan will reach top speed
FAN_PROGRAM_HYSTERESIS = 2                                                      #The drop in temperature below base at which fan will stop

DISPLAY_ROTATED         = True                                                  #Set to true if the OLED module is rotated to flip image
SENSOR_PORT_LIST        = [3,4,5]                                               #The I2C ports which will be scanned for sensors

POLL_PERIOD             = 1.0                                                   #Period (seconds) at which to update sensor readings

ENABLE_BATTERY_MONITOR    = True                                                #If enabled core.py will display visual+audible warnings when battery low
BATTERY_CRITICAL_SHUTDOWN = True                                                #If enabled, system will shutdown when Vbatt<BATTERY_SHUTDOWN_VOLTAGE
BATTERY_LOW_VOLTAGE = 10.2                                                      #Voltage at which low voltage warning given
BATTERY_CRITICAL_VOLTAGE = 9.2                                                  #Voltage at which critical voltage warning given
BATTERY_SHUTDOWN_VOLTAGE = 8.9                                                  #Enforced shutdown voltage

# The following settings are only used when a YRL015 switch board is NOT connected
ENABLE_DEMO_MODE        = False
ENABLE_STATS_MODE       = False
ENABLE_AUTOSENSE_MODE   = True
SHOW_HOSTNAME		= True

# The following are things you are less likely to want to change on the YRL028 setup...
OLED_BUS                = 8                                                     #The bus which the OLED module is attached to [i2c_8 on YRL028]
LED_DRIVER_BUS          = 9                                                     #The bus which the TCA6507 LED driver is attached to [i2c_9 on YRL028]
SWITCH_BUS              = 9                                                     #The bus which the YRL015 switch board is attached to [i2c_9 on YRL028]
SWITCH_INTERRUPT_PIN    = 25                                                    #The GPIO pin connected to interrupt out of YRL015 switch board
SWITCH_GPIO_ADDRESS     = 0x20                                                  #I2C Address of GPIO expender on YRL015 switch board
ADC_BUS                 = 9                                                     #The bus which the ADS7830 ADC is connected to [i2c_9 on YRL028]
ADC_ADDRESS             = 0x48                                                  #The I2C address for the ADS7830
MOTORS_BUS              = 7
ARDUINO_BUS             = 10
ARDUINO_ADDRESS         = 0x57
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
program_request_filename="/ramdisk/progrequest"
program_info_filename="/ramdisk/proginfo"
program_state_filename="/ramdisk/progstate"
camera_request_filename="/ramdisk/camerarequest"


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

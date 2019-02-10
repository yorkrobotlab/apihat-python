#!/usr/bin/python

# YRL027 Sensor commands
#
# Contains a class [Sensor] which is assigned to one of the switch i2c busses, assumes either a YRL013 or YRL019 sensor or gas\environment sensor.
#
# Single port version; for multi-port revert to adapted Hexaberry code
#
# James Hilder, York Robotics Laboratory, Jan 2019

import VL53L0X, led, settings as s                                              #YRL027 library files
import numpy as np                                                              #Numpy
import math, logging, time, os, sys                                             #General Python imports
from collections import namedtuple
from ctypes import *
import smbus2                                                                   #Assume DTO-level i2c switch implementation [ie port 0 = i2c_3 etc]

MAX_BRIGHTNESS = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]


#sensor_bus = smbus2.SMBus(SENSOR_BUS)

class Sensor:
    def write_values_to_csv_string(self):
        ret = ""
        if(self.has_tof) : ret = ret + "%d," % (self.read_tof_distance())
        if(self.has_alp) :
            alp_values = self.read_alp_sensor()
            ret = ret + "%d,%d,%d," % (alp_values[0],alp_values[1],alp_values[2])
        if(self.has_colour) :
            col_values = self.read_colour_sensor()
            ret = ret + "%d,%d,%d,%d," % (col_values[0],col_values[1],col_values[2],col_values[3])
        if(self.has_adc) :
            ret = ret + "%d," % (self.read_corrected_adc_value())
        if(self.has_gas_sensor) :
            gas_values = self.read_gas_sensor()
            ret = ret + "%d,%d,%d,%d," % (gas_values[0],gas_values[1],gas_values[2],gas_values[3])
        if(self.has_humidity_sensor) :
            humidity_values = self.read_humidity_sensor()
            ret = ret + "%2.2f,%2.2f," % (humidity_values[0],humidity_values[1])
        return ret

    def get_export_list(self):
        ret = []
        if self.has_tof: ret.append("TOF")
        if self.has_alp: ret.append("ALP")
        if self.has_colour: ret.append("COLOUR")
        if self.has_adc: ret.append("IR ADC")
        if self.has_gas_sensor: ret.append("GAS ADC")
        if self.has_gas_sensor_gpio: ret.append("GAS GPIO")
        if self.has_humidity_sensor: ret.append("HUMIDITY")
        if self.has_led: ret.append("LED")
        return ret

    def get_csv_header_string(self):
        ret = ""
        if(self.has_tof) : ret = ret + "TOF,"
        if(self.has_alp) : ret = ret + "ALS:IR PROX,ALS:LIGHT,ALS:WB,"
        if(self.has_colour) : ret = ret + "RED,GREEN,BLUE,WHITE,"
        if(self.has_adc) : ret = ret + "IR,"
        if(self.has_gas_sensor) : ret = ret + "GAS0,GAS1,GAS2,GAS3,"
        if(self.has_humidity_sensor) : ret = ret + "HUMIDITY,TEMPERATURE,"
        return ret

    def read_humidity_sensor(self):
        self.sensor_bus.write_quick(s.HUMIDITY_SENSOR_ADDRESS)
        humidity_data = self.sensor_bus.read_i2c_block_data (s.HUMIDITY_SENSOR_ADDRESS, 0 , 4 ) # Read 4 bytes of data
        humidity = ( ( ( float )(( humidity_data [ 0 ] % 64 ) << 8 ) + humidity_data [ 1 ] ) / 163.82 )
        temperature = ((( float ) (( humidity_data [ 2 ] << 6 ) + ( humidity_data [ 3 ] >> 2 )) / 16382 ) * 165 ) - 40
        return [humidity,temperature]

    def read_gas_sensor(self):
        return [self.read_ad7998_adc(0),self.read_ad7998_adc(1),self.read_ad7998_adc(2),self.read_ad7998_adc(3)]

    def init_gas_sensor_gpio(self):
        self.sensor_bus.write_byte_data(s.GAS_SENSOR_GPIO_ADDRESS, 0x03, 0xF0) # Register 3 = Config, 0=output

    def read_gas_sensor_gpio(self):
        return self.sensor_bus.read_byte_data(s.GAS_SENSOR_GPIO_ADDRESS, 0x01) #Register 1 = Output Port

    def write_gas_sensor_gpio(self,byte_data):
        self.sensor_bus.write_byte_data(s.GAS_SENSOR_GPIO_ADDRESS, 0x01, byte_data)

    def printout_sensors(self):
      if not self.has_sensors: logging.info("No sensors detected on bus i2c_%d",self.SENSOR_BUS)
      else:
          logging.info("SENSORS DETECTED ON BUS i2c_%d:",self.SENSOR_BUS)
          if(self.has_tof):    logging.info         ("VL53L0X Time-of-flight sensor [address 0x%X]" % s.TOF_SENSOR_ADDRESS)
          if(self.has_alp):    logging.info         ("VCNL4040 IR ALP sensor        [address 0x%X]" % s.IR_ADDRESS)
          if(self.has_led):    logging.info         ("TLC59116 LED driver           [address 0x%X]" % self.SENSOR_LED_ADDRESS)
          if(self.has_colour): logging.info         ("VEML6040 colour sensor        [address 0x%X]" % s.COLOUR_ADDRESS)
          if(self.has_adc):    logging.info         ("MCP3221 ADC analog IR sensor  [address 0x%X]" % s.ADC_ADDRESS)
          if(self.has_gas_sensor): logging.info     ("AD7998 ADC gas sensor         [address 0x%X]" % s.GAS_SENSOR_ADC_ADDRESS)
          if(self.has_gas_sensor_gpio): logging.info("PCA9536 GPIO expander for gas [address 0x%X]" % s.GAS_SENSOR_GPIO_ADDRESS)
          if(self.has_humidity_sensor): logging.info("Honeywell Humidity sensor     [address 0x%X]" % s.HUMIDITY_SENSOR_ADDRESS)

    def set_sensor_pwm_brightness(self,brightness):
        relative = brightness * s.max_brightness * 255
        if relative > 255: relative = 255
        if relative < 0: relative = 0
        self.sensor_bus.write_byte_data(self.SENSOR_LED_ADDRESS, 0x12, int(relative))

    def set_sensor_rgb_pwm_init(self):
      self.sensor_bus.write_i2c_block_data(self.SENSOR_LED_ADDRESS, 0x95, [0xFF,0xFF,0xFF] )

    def setup_sensor_led_driver(self):
      logging.debug("Setting up LED driver for sensor")
      mode1_byte = 0
      self.sensor_bus.write_byte_data(self.SENSOR_LED_ADDRESS, 0x00, mode1_byte)
      self.sensor_bus.write_i2c_block_data(self.SENSOR_LED_ADDRESS, 0x82, MAX_BRIGHTNESS)
      self.set_sensor_pwm_brightness(s.initial_led_brightness)
      self.set_sensor_rgb_pwm_init()

    def set_sensor_rgb_pwm_off(self):
      self.sensor_bus.write_i2c_block_data(self.SENSOR_LED_ADDRESS, 0x86, [0,0,0,0,0,0,0,0,0,0,0,0])

    def set_sensor_colour_individual(self,index_0,index_1,index_2,index_3):
      if index_0 < 0 or index_0 > len(led.user_colour_array) or index_1 < 0 or index_1 > len(led.user_colour_array) or index_2 < 0 or index_2 > len(led.user_colour_array) or index_3 < 0 or index_3 > len(led.user_colour_array) or sensor < 0 or sensor > 5:
        logging.warning("Requested value outside range; ignoring.")
      else:
        logging.debug("Setting sensor top LEDs to R:%02X G:%02X B:%02X" % (led.user_colour_array[index_0][0],led.user_colour_array[index_0][1],led.user_colour_array[index_0][2]))
      self.sensor_bus.write_i2c_block_data(self.SENSOR_LED_ADDRESS, 0x86, [led.user_colour_array[index_0][2],led.user_colour_array[index_0][1],led.user_colour_array[index_0][0],led.user_colour_array[index_1][2],led.user_colour_array[index_1][1],led.user_colour_array[index_1][0],led.user_colour_array[index_2][2],led.user_colour_array[index_2][1],led.user_colour_array[index_2][0],led.user_colour_array[index_3][2],led.user_colour_array[index_3][1],led.user_colour_array[index_3][0]] )

    def set_sensor_colour_solid(self,index):
      if index < 0 or index > len(led.user_colour_array):
        logging.warning("Requested value outside range; ignoring.")
      else:
        logging.debug("Setting sensor top LEDs to R:%02X G:%02X B:%02X" % (led.user_colour_array[index][0],led.user_colour_array[index][1],led.user_colour_array[index][2]))
      self.sensor_bus.write_i2c_block_data(self.SENSOR_LED_ADDRESS, 0x86, [led.user_colour_array[index][2],led.user_colour_array[index][1],led.user_colour_array[index][0],led.user_colour_array[index][2],led.user_colour_array[index][1],led.user_colour_array[index][0],led.user_colour_array[index][2],led.user_colour_array[index][1],led.user_colour_array[index][0],led.user_colour_array[index][2],led.user_colour_array[index][1],led.user_colour_array[index][0]] )

    def set_sensor_colour_rgb(self,red,green,blue):
      if red < 0 or red > 255 or green < 0 or green > 255 or blue < 0 or blue > 255:
        logging.warning("Requested value outside range; ignoring.")
      else:
        logging.debug("Setting sensor top LEDs to [R%02X G%02X B%02X]" % (red, green, blue))
      self.sensor_bus.write_i2c_block_data(self.SENSOR_LED_ADDRESS, 0x86, [blue,green,red,blue,green,red,blue,green,red,blue,green,red] )

    def init_tof_sensor(self):
      logging.info("Initialising VL53L0X TOF sensor (using external library)")
      #Enable bus
      return self.tof_sensor.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

    def read_tof_distance(self):
      logging.debug("Reading VL53L0X TOF sensor (using external library)")
      #Enable bus
      ret_val = self.tof_sensor.get_distance()
      if ret_val < 0: ret_val = 999
      return ret_val

    #Initialise the VCNL4040 IR Sensor
    def init_alp_sensor(self):
      logging.debug("Initialising VCNL4040 IR sensor at address 0x%X" % s.IR_ADDRESS)
      #Write 0x00 to ALS_CONF [80ms int. time, interrupt disable, power on]
      self.sensor_bus.write_byte_data(s.IR_ADDRESS, s.ALS_CONF_REG, 0x00)
      #Write 0x0E to PS_CONF1 [1/40 DC, 8T Integration (Max), Power On)
      #Write 0x08 to PS_CONF2 [16 bit, int. disable)
      self.sensor_bus.write_i2c_block_data(s.IR_ADDRESS, s.PS_CONF1_REG, [0x0E,0x08])
      #Write 0x0C to PS_CONF3 [Active force mode, trigger 1 cycle]
      #Write 0x07 to PS_MS [white channel enabled, 200ma current]
      self.sensor_bus.write_i2c_block_data(s.IR_ADDRESS, s.PS_CONF3_REG, [0x0C,0x07])

    def read_corrected_adc_value(self):
      word = self.sensor_bus.read_word_data(s.SENSOR_ADC_ADDRESS,0)
      #Word is byte shifted
      corrected = s.NOISE_FLOOR - (((word & 255) << 8) + (word >> 8))
      if(corrected < 0): corrected = 0
      return corrected

    def read_ad7998_adc(self, input):
        add_byte = 0x80 + (input << 4) # Mode 2 [sample-on-write] operation on AD7998
        return self.read_reg(s.GAS_SENSOR_ADC_ADDRESS,add_byte)

    def read_reg(self,i2c_address, register_address):
      word = self.sensor_bus.read_i2c_block_data(i2c_address,register_address,2)
      return (word[1] << 8) + (word[0])

    def read_colour_sensor(self):
      return [self.read_reg(s.COLOUR_ADDRESS,s.RED_REGISTER),self.read_reg(s.COLOUR_ADDRESS,s.GREEN_REGISTER),self.read_reg(s.COLOUR_ADDRESS,s.BLUE_REGISTER),self.read_reg(s.COLOUR_ADDRESS,s.WHITE_REGISTER)]

    def read_alp_sensor(self):
      return [self.read_reg(s.IR_ADDRESS,s.PS_DATA_REG), self.read_reg(s.IR_ADDRESS,s.ALS_DATA_REG), self.read_reg(s.IR_ADDRESS, s.WHITE_DATA_REG)]

    def detect_i2c_device(self,i2c_address):
      try:
        self.sensor_bus.read_byte(i2c_address)
        return True
      except IOError:
        logging.debug("No I2C device detected at address 0x%X" % (i2c_address))
        return False

    def init_colour_sensor(self):
      #Command register of VEML6040 [address 0x00]
      #[ 0  IT2 IT1 IT0 0 TRIG AF SD]
      # IT2-0 Itegration Time	[ 40 - 80- 160 - 320 - 640 - 1280ms ]  40=000
      # TRIG  Trigger (manual mode)
      # AF    Auto\manual force mode
      # SD    Chip shutdown
      config_byte = 0x00 + (s.COLOUR_SENSOR_SENSITIVITY << 4) #40ms integration, auto
      #config_byte=0x44
      self.sensor_bus.write_byte_data(s.COLOUR_ADDRESS, 0x00, config_byte)

    def init_colour_sensor_oneshot(self):
      config_byte = 0x02 + (s.COLOUR_SENSOR_SENSITIVITY << 4) #Selected integration, force mode, no trigger
      self.sensor_bus.write_byte_data(s.COLOUR_ADDRESS, 0x00, config_byte)

    def one_shot_illuminated_colour_test_init(self):
      led.set_sensor_pwm_brightness(1)
      init_colour_sensor_oneshot(self)

    def one_shot_illuminated_colour_test(self):
      #Enable leds
      led.set_sensor_colour_solid(7)
      config_byte = 0x06 # 40ms integration, force mode, trigger
      self.sensor_bus.write_byte_data(s.COLOUR_ADDRESS, 0x00, config_byte)
      time.sleep(0.04)
      led.set_sensor_colour_solid(0)
      return read_colour_sensor()

    def two_shot_illuminated_colour_test(self):
      #Disable leds
      led.set_sensor_colour_solid(0)
      config_byte = 0x06 # 40ms integration, force mode, trigger
      self.sensor_bus.write_byte_data(s.COLOUR_ADDRESS, 0x00, config_byte)
      time.sleep(0.05)
      dark_colour = self.read_colour_sensor()
      led.set_sensor_colour_solid(7)
      config_byte = 0x06 # 40ms integration, force mode, trigger
      self.sensor_bus.write_byte_data(s.COLOUR_ADDRESS, 0x00, config_byte)
      time.sleep(0.05)
      light_colour = self.read_colour_sensor()
      return [dark_colour,light_colour]

    def __init__(self,i2c_bus):
        self.has_sensors = False
        self.SENSOR_BUS = i2c_bus
        self.sensor_bus = smbus2.SMBus(self.SENSOR_BUS)
        self.tof_sensor = VL53L0X.VL53L0X()
        self.SENSOR_LED_ADDRESS = 0 # Work-around for server expecting a value even if driver not present...
        logging.debug("Starting sensor detection on i2c_%d" % self.SENSOR_BUS)
        if self.detect_i2c_device(s.SENSOR_LED_ADDRESS_1):
            self.SENSOR_LED_ADDRESS = s.SENSOR_LED_ADDRESS_1
            logging.debug("TLC59116 LED driver detected at address  0x%X " % self.SENSOR_LED_ADDRESS)
            self.setup_sensor_led_driver()
            self.has_led = True
        elif self.detect_i2c_device(s.SENSOR_LED_ADDRESS_2):
            self.SENSOR_LED_ADDRESS = s.SENSOR_LED_ADDRESS_2
            logging.debug("TLC59116 LED driver detected at address  0x%X " % self.SENSOR_LED_ADDRESS)
            self.setup_sensor_led_driver()
            self.has_led = True
        else: self.has_led = False
        if self.detect_i2c_device(s.IR_ADDRESS):
            logging.debug("VCNL4040 IR sensor detected at address  0x%X " % s.IR_ADDRESS)
            self.init_alp_sensor()
            self.has_alp = True
        else: self.has_alp = False
        self.has_tof = False
        if self.detect_i2c_device(s.TOF_SENSOR_ADDRESS):
            logging.debug("VL53L0X TOF sensor detected at address  0x%X " % s.TOF_SENSOR_ADDRESS)
            if self.init_tof_sensor(): self.has_tof = True
        try:
            self.init_colour_sensor()
            logging.debug("VEML6040 colour sensor detected at address  0x%X " % s.COLOUR_ADDRESS)
            self.has_colour = True
        except IOError:
            logging.debug("No colour sensor detected at address 0x%X " % s.COLOUR_ADDRESS)
            self.has_colour = False
        try:
          self.sensor_bus.read_word_data(s.ADC_ADDRESS,0)
          logging.debug("MCP3221 analog:digital converter detected at address 0x%X " % s.ADC_ADDRESS)
          self.has_adc = True
        except IOError:
          logging.debug("No ADC device detected at address 0x%X" % (s.ADC_ADDRESS))
          self.has_adc = False
        if self.detect_i2c_device(s.GAS_SENSOR_GPIO_ADDRESS):
            self.has_gas_sensor_gpio = True
            self.init_gas_sensor_gpio()
            logging.debug("PCA9536 GPIO Expander detected at address 0x%X " % s.GAS_SENSOR_GPIO_ADDRESS)
        else: self.has_gas_sensor_gpio = False
        if self.detect_i2c_device(s.GAS_SENSOR_ADC_ADDRESS):
            self.has_gas_sensor = True
            logging.debug("AD7998 ADC converter (gas sensor) detected at address 0x%X" % (s.GAS_SENSOR_ADC_ADDRESS))
        else: self.has_gas_sensor = False
        if self.detect_i2c_device(s.HUMIDITY_SENSOR_ADDRESS):
            self.has_humidity_sensor = True
            logging.debug("HIH8120 Humidity sensor detected at address 0x%X" % (s.HUMIDITY_SENSOR_ADDRESS))
        else: self.has_humidity_sensor = False
        if self.has_tof or self.has_alp or self.has_led or self.has_colour or self.has_adc or self.has_gas_sensor_gpio or self.has_gas_sensor or self.has_humidity_sensor: self.has_sensors = True

def ir_value_to_distance(ir_value):
  #Curve fit using a * x ^ b curve fit
  #a=1392  b=-0.5487
  if ir_value == 0: return 999
  return 1392 * pow(ir_value, -0.5487)

def get_rgb_from_single_csv(rgb_array):
  sum = float(rgb_array[0]+rgb_array[1]+rgb_array[2])
  ratios=[rgb_array[0]/sum,rgb_array[1]/sum,rgb_array[2]/sum]


def get_rgb_from_colour_sensor_values(cvs):
  noise = 16
  d = [max(0,cvs[1][0]-cvs[0][0]-noise),max(0,cvs[1][1]-cvs[0][1]-noise),max(0,cvs[1][2]-cvs[0][2]-noise)]
  max_dif = max(d)
  s = float((d[0]+d[1]+d[2]))
  if s < 1: s = 1.0
  #print s
  dif = [(d[0]/s),(d[1]/s),(d[2]/s)]
  #print dif
  p_mul = 1.0
  brightness = min(255,(s-1) * 2)
  if max(dif) > 0: p_mul = 1.0 / max(dif)
  dif[:] = [((dv * p_mul) ** 2) for dv in dif]
  #print dif
  dec_dif = [int(brightness * dif[0]),int(brightness * dif[1]),int(brightness*dif[2])]
  return dec_dif

def get_rgb_from_xy_and_brightness(x, y, bri=1):
        XYPoint = namedtuple('XYPoint', ['x', 'y'])
        # From Philips Hue library
        # We do this to calculate the most accurate color the given light can actually do.
        xy_point = XYPoint(x, y)
        #if not self.check_point_in_lamps_reach(xy_point):
        #    # Calculate the closest point on the color gamut triangle
        #    # and use that as xy value See step 6 of color to xy.
        #    xy_point = self.get_closest_point_to_point(xy_point)
        # Calculate XYZ values Convert using the following formulas:
        Y = bri
        X = (Y / xy_point.y) * xy_point.x
        Z = (Y / xy_point.y) * (1 - xy_point.x - xy_point.y)
        return get_rgb_from_XYZ([X,Y,Z])

def get_rgb_from_XYZ(XYZ):
        X=XYZ[0]
        Y=XYZ[1]
        Z=XYZ[2]
        # Convert to RGB using Wide RGB D65 conversion
        r = X * 1.656492 - Y * 0.354851 - Z * 0.255038
        g = -X * 0.707196 + Y * 1.655397 + Z * 0.036152
        b = X * 0.051713 - Y * 0.121364 + Z * 1.011530
        # Apply reverse gamma correction
        r, g, b = map(
            lambda x: (12.92 * x) if (x <= 0.0031308) else ((1.0 + 0.055) * pow(x, (1.0 / 2.4)) - 0.055),
            [r, g, b]
        )
        # Bring all negative components to zero
        r, g, b = map(lambda x: max(0, x), [r, g, b])
        # If one component is greater than 1, weight components by that value.
        max_component = max(r, g, b)
        if max_component > 1:
            r, g, b = map(lambda x: x / max_component, [r, g, b])
        r, g, b = map(lambda x: int(x * 255), [r, g, b])
        # Convert the RGB values to your color object The rgb values from the above formulas are between 0.0 and 1.0.
        return ([r, g, b])

#Convert the value from the green register (closely matched to human eye curve) to lux value [based on VEML6040 design guides]
def convert_colour_sensor_lux(green_val):
  lux_mul = [0.25168,0.12584,0.06292,0.03146,0.01573,0.007865]
  return green_val * lux_mul[COLOUR_SENSOR_SENSITIVITY]

#Convert the RGB colour sensor values into a corrected colour temperature (CCT) value and x-y coordinate values for the CIE1931 colour space [based on VEML6040 design guides]
def calculate_cct_colour_sensor(cs_values):
  corr_coeff = np.array([[0.048403, 0.183633, -0.253589],[0.022916,0.176388,-0.183205],[-0.077436,0.124541,0.032081]])
  cs_rgb = np.array([cs_values[0],cs_values[1],cs_values[2]])
  XYZ = np.matmul(corr_coeff,cs_rgb)
  x= XYZ[0]/np.sum(XYZ)
  y= XYZ[1]/np.sum(XYZ)
  #Calculate CCT
  n = (x - 0.3320) / (y - 0.1858)
  cct = (449 * n * n * n) + (3525 * n * n) + (6823.3 * n) + 5520.33
  return ([XYZ[0],XYZ[1],XYZ[2],x,y,cct])

adc_bus = smbus2.SMBus(s.ADC_BUS)

def read_pcb_temp():
    #Temperature sensor is MCP9701AT-E/TT connected to channel 5 of ADC
    return (0.5 * read_adc(5)) - 20.5

def read_voltage():
    #Bat_ref is ADC channel 4
    #Vin routed through 499K:100K PD, Vref=2.5V
    #(100/599) * adc * (2.5/255) = 0.001637
    return 0.057843 * read_adc(4)

def read_adc(channel):
    channel_values = [0x88,0xC8,0x98,0xD8,0xA8,0xE8,0xB8,0xF8]
    adc_bus.write_byte(s.ADC_ADDRESS,channel_values[channel])
    return adc_bus.read_byte(s.ADC_ADDRESS)

def detect_sensors():
    sensor_list = s.SENSOR_PORT_LIST
    logging.info("Searching for sensors on ports %s" % sensor_list)
    active_list = []
    for bus_ix in sensor_list:
        sensor = Sensor(bus_ix)
        if sensor.has_sensors: active_list.append(sensor)
        sensor.printout_sensors()
    return active_list

#Test code
if __name__ == "__main__":
 s.init()
 logging.info("Sensor test code")
 #active_list = detect_sensors()
 #while True:
     # for sensor in active_list:
     #   print("Reading i2c_%d:" % sensor.SENSOR_BUS)
     #   if sensor.has_gas_sensor_gpio: print(sensor.read_gas_sensor_gpio())
     #   if sensor.has_led: sensor.set_sensor_colour_rgb(128,0,0)
     #   if sensor.has_colour: print(sensor.read_colour_sensor())
     #   if sensor.has_alp: print(sensor.read_alp_sensor())
     #   if sensor.has_tof: print(sensor.read_tof_distance())
     #   time.sleep(0.5)
 while True:
     print ("PCB Temperature: %f" % (read_pcb_temp()))
     # for x in range(8):
     #     print("%d " % (read_adc(x)),end=" "),
     # print (" Voltage:%f" % (read_voltage()))
     time.sleep(0.3)
 os._exit(1)

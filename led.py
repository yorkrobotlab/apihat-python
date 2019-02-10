#!/usr/bin/python
# YRL028 - APIHAT - Python 3 API Version 0.1
#
# Functions for the TCA6507 LED driver
#
# James Hilder, York Robotics Laboratory, Feb 2019

import logging, threading, time, random, os, smbus2                             #General Python imports
import settings as s
import patterns
import numpy as np                                                              #Numpy
from threading import Timer

BODY_LED_ADDRESS = 0x45                                                         #I2C Address of TCA6507 LED Driver [drives LEDs on rim of PCB]
body_bus = smbus2.SMBus(s.LED_DRIVER_BUS)                                       #The TCA6507 is attached to i2c_10

initial_led_brightness = 0.5
max_brightness = 1.0
animation_step = 0                                                              #Holds the current step index for the sensor led animation
animation_step_body = 0                                                         #Holds the current step index for the body led animation
stepped_animation = []                                                          #Holds the current stepped animation command set
toggle_step = False                                                             #Used to alternate top:bottom body LEDs in stepped animations
leds_off = False
sensor_animation_running = False
sensor_animation_mode = 0
sensor_animation_step = 0
sensor_animation_steptime = 0.2
LED_ADDRESS = 0x45                                                              #I2C Address of TCA6507 LED Driver [drives LEDs on main PCB]
LED_SUBBUS  = 7                                                                 #TCA6507 connected to sub-bus 7 of I2C SWITCH
LED_REGISTER = 0x10                                                             #Auto-increment from register 0 on TCA6507

def generate_random_colours():                                                  #Define 3 randomly generated colours
  if random.random() > 0.5 : colour_1=[1,generate_random_colour()]
  else: colour_1=[1,pick_random_colour()]
  if random.random() > 0.5 : colour_2=[2,generate_contrast_colour(colour_1[1])]
  elif random.random() > 0.5 : colour_2=[2,pick_random_colour()]
  elif random.random() > 0.5 : colour_2=[2,generate_random_colour()]
  else: colour_2=[2,generate_complement_colour(colour_1[1])]
  if random.random() > 0.5 : colour_3=[3,generate_complement_colour(colour_1[1])]
  elif random.random() > 0.5 : colour_3=[3,pick_random_colour()]
  elif random.random() > 0.5 : colour_3=[3,generate_random_colour()]
  else: colour_3=[3,generate_contrast_colour(colour_1[1])]
  return [5,[colour_1,colour_2,colour_3]]

def dim_colours(gen):                                                           #Divide brightness of colour array by 2
   colour_1=[1,[gen[1][0][1][0]>>1,gen[1][0][1][1]>>1,gen[1][0][1][2]>>1]]
   colour_2=[2,[gen[1][1][1][0]>>1,gen[1][1][1][1]>>1,gen[1][1][1][2]>>1]]
   colour_3=[3,[gen[1][2][1][0]>>1,gen[1][2][1][1]>>1,gen[1][2][1][2]>>1]]
   ret=[5,[colour_1,colour_2,colour_3]]
   return ret

def generate_random_colour():                                                   #Generate a random (2-out-of-3) colour
  primary_brightness =  (random.random() * 0.5) + 0.5
  complement_brightness = random.random()
  index=[0,1,2]
  random.shuffle(index)
  ret_val=[0,0,0]
  ret_val[index[0]]=int(primary_brightness * 255)
  ret_val[index[1]]=int(complement_brightness * 255)
  return ret_val

def pick_random_colour():                                                       #Pick a random 'core' colour
  brightness =  (random.random() * 0.5) + 0.5
  col = random.randint(0,8)
  if col==0: return [int (0x00 * brightness), int (0x00 * brightness), int (0x00 * brightness)]  # Black
  if col==1: return [int (0xff * brightness), int (0x00 * brightness), int (0x00 * brightness)]  # Red
  if col==2: return [int (0x00 * brightness), int (0xff * brightness), int (0x00 * brightness)]  # Green
  if col==3: return [int (0x00 * brightness), int (0x00 * brightness), int (0xff * brightness)]  # Blue
  if col==4: return [int (0xff * brightness), int (0xff * brightness), int (0x00 * brightness)]  # Yellow
  if col==5: return [int (0x00 * brightness), int (0xff * brightness), int (0xff * brightness)]  # Cyan
  if col==6: return [int (0xff * brightness), int (0x00 * brightness), int (0xff * brightness)]  # Magenta
  return [int (0xff * brightness),int (0xff * brightness),int (0xff * brightness)]  # White

def generate_contrast_colour(rgb_colour_array):                                 #Generate a colour that contrast (ie opposite on colour wheel) to supplied colour
  max_val = max(rgb_colour_array)
  return [max_val - rgb_colour_array[0], max_val - rgb_colour_array[1], max_val - rgb_colour_array[2]]

def generate_complement_colour(rgb_colour_array):                               #Generate a colour that complements (ie close on colour wheel) to supplied colour
  red =   min(255,int((rgb_colour_array[0] + random.randint(0,10))  * (random.random() + 0.5)))
  green = min(255,int((rgb_colour_array[1] + random.randint(0,10))  * (random.random() + 0.5)))
  blue  = min(255,int((rgb_colour_array[2] + random.randint(0,10))  * (random.random() + 0.5)))
  return [red,green,blue]

def shift_list(l, n):
  return l[n:] + l[:n]

def get_random_animation(seed_value):                                           #Either randomly select a predefined, or generate a new random pattern, with 50% probability
  random.seed(seed_value)
  if random.random() > 0.5: return generate_random_animation(random.randint(0,1000000))
  return random.choice(patterns.stepped_animations)

def generate_body_animation(seed_value,colours):                                #Generate a random new animation sub-pattern for the body LEDs
  logging.debug("Generating new random body animation for seed %d" % seed_value)
  random.seed(seed_value)
  rhythm=random.choice(patterns.body_led_patterns)
  side_mode=random.randint(0,3)
  each_subbeat=random.choice([True,False])
  oneshot=random.choice([True,False])
  pulse=random.choice([True,False])
  triangle=random.choice([True,False])
  slow=random.choice([True,False])
  return [rhythm,colours[0][1],colours[1][1],colours[2][1],side_mode,each_subbeat,oneshot,pulse,triangle,slow]

def generate_random_animation(seed_value):                                      #Generate a random new animation pattern for the sensor and body LEDs
  logging.debug("Generating new random animation for seed %d" % seed_value)
  random.seed(seed_value)
  colours = generate_random_colours()                                           #Add this to first routines to define random custom colours
  body_animation=generate_body_animation(random.randint(0,10000),colours[1])
  logging.debug("Body      : %s " % body_animation)
  logging.debug("Colours   : %s " % colours)
  steps_mode = random.randint(0,2)
  logging.debug("Steps Mode: %s " % steps_mode)
  fade = True
  if random.random() > 0.7 : fade=False
  logging.debug("Fade      : %s " % fade)
  number_of_steps = (1 << steps_mode)
  logging.debug("No. Steps : %d " % number_of_steps)
  beat_delay = max(0,(2 * random.randint(0,2) - 1))
  logging.debug("Beat Delay: %d "% beat_delay)
  colour_range_low = 1
  colour_range_high = 3
  if random.random() > 0.5:
    colour_range_low = 0
  elif random.random() > 0.5:
    colour_range_high = 7
  logging.debug("Col Range : %d to %d" % (colour_range_low, colour_range_high))
  alt_mode = random.randint(0,4)
  logging.debug("Alt Mode  : %d" % alt_mode)
  sequence_1 = [random.randint(colour_range_low,colour_range_high),random.randint(colour_range_low,colour_range_high),random.randint(colour_range_low,colour_range_high),random.randint(colour_range_low,colour_range_high)]
  if alt_mode == 0: sequence_2 = [random.randint(colour_range_low,colour_range_high),random.randint(colour_range_low,colour_range_high),random.randint(colour_range_low,colour_range_high),random.randint(colour_range_low,colour_range_high)]
  if alt_mode == 1:
      sol_col = random.randint(0,7)
      sequence_2 = [sol_col,sol_col,sol_col,sol_col]
  if alt_mode == 2: sequence_2 = [sequence_1[1],sequence_1[0],sequence_1[3],sequence_1[2]]
  if alt_mode == 3: sequence_2 = [sequence_1[3],sequence_1[2],sequence_1[1],sequence_1[0]]
  if alt_mode == 4: sequence_2 = [sequence_1[2],sequence_1[3],sequence_1[0],sequence_1[1]]
  if sequence_2 == sequence_1: sequence_2=[1,1,1,1]
  logging.debug("Sequence 1: %s " % sequence_1)
  logging.debug("Sequence 2: %s " % sequence_2)
  sensor_mode = random.choice(patterns.sensor_mode_patterns)
  logging.debug("Sensor md : %s " % sensor_mode)
  add_complement = random.choice([True,False])
  animation=[]
  add_colour = True
  for sensor_mode_steps in sensor_mode:
    logging.debug("Sensor mode steps: %s " % sensor_mode_steps)
    for step in range(number_of_steps):
      animation_line = []
      sub_line = []
      if add_colour:
        animation_line.append(colours)
        add_colour=False
      element=[sensor_mode_steps[0]]
      draft_cell = sequence_1
      if steps_mode == 1:  draft_cell = sequence_2
      if steps_mode == 2:  draft_cell = shift_list(sequence_1,step)
      element.append(draft_cell)
      sub_line.append(element)
      logging.debug("Element 1: %s", element)
      if len(sensor_mode_steps)==2:
        element_2=[sensor_mode_steps[1]]
        draft_cell = sequence_2
        if steps_mode == 1: draft_cell = sequence_1
        if steps_mode == 2: draft_cell = shift_list(sequence_2,step)
        element_2.append(draft_cell)
        logging.debug("Element 2: %s", element_2)
        sub_line.append(element_2)
      command = [4,sub_line]
      line=animation_line
      line.append(command)
      logging.debug("Adding line: %s" % line)
      animation.append(line)
      q_colours = list(colours)
      for delays in range(beat_delay):
        if fade:
          q_colours=dim_colours(q_colours)
          k_line = []
          k_line.append(q_colours)
          k_line.append(command)
          logging.debug("Adding line: %s" % k_line)
          animation.append(k_line)
        else: animation.append([[-1,0]])
  logging.debug("Animation: %s" % animation)
  return ['Seed:%d' % seed_value,body_animation,animation]


def set_predefined_stepped_animation(index):
   animation = patterns.stepped_animations[index]
   set_stepped_animation(animation)

def set_stepped_animation(animation):
   global animation_step
   global stepped_animation
   global leds_off
   global animation_step_body
   global toggle_step
   leds_off = False
   animation_step = 0
   animation_step_body = 0
   toggle_step = False
   stepped_animation = animation

def next_step_body(body_animation):
   global animation_step_body
   global toggle_step
   if len(body_animation) == 10:
     rhythm = body_animation[0]
     rhy_length = len(rhythm)
     cols=[body_animation[1],body_animation[2],body_animation[3]]
     side_mode = body_animation[4]
     each_subbeat = body_animation[5]
     if not each_subbeat: rhy_length = rhy_length * 2
     oneshot = body_animation[6]
     pulse = body_animation[7]
     triangle = body_animation[8]
     slow = body_animation[9]
     if each_subbeat or animation_step_body % 2 == 0:                           #Only animate every other step if each_subbeat is false....
        index = animation_step_body
        if not each_subbeat: index = index >> 1
        top = False
        bottom = False
        colour = cols[rhythm[index] - 1]
        if side_mode==0: bottom = True
        if side_mode==1: top = True
        if side_mode==2:
            bottom = True
            top = True
        if rhythm[index] > 0:
            if side_mode==3:
                if not toggle_step: top = True
                else: bottom = True
                toggle_step = not toggle_step
            if len(colour)==1:
                if colour[0] == 0: colour = generate_random_colour()
                elif colour[0] == 1: colour = pick_random_colour()
                set_colour_rgb(colour, top, bottom, oneshot, pulse, triangle, slow)
        animation_step_body += 1
        if animation_step_body >= rhy_length: animation_step_body = 0
   else:  logging.warning("Body LED animation invalidly formed, ignoring")

def next_step():
   global animation_step
   if len(stepped_animation) == 3:
     animation_name = stepped_animation[0]
     body_animation = stepped_animation[1]
     next_step_body(body_animation)
     animation = stepped_animation[2]
     animation_length = len(animation)
     current = animation[animation_step]
     logging.debug("Stepped Animation Routine: Step %d of %d" % (animation_step, animation_length))
     logging.debug("Current [%d elements]: %s " % (len(current),current))
     for current_element in current:
       mode = current_element[0]
       logging.debug("Element mode: %s String: %s " % (mode,current_element))   #Do nothing if mode = -1
       if mode == 0 and not leds_off:			                                #mode 0 = turn off leds
          leds_off = True
          turn_off_all_sensor_leds()
       if mode == 1: set_all_sensor_brightness(current_element[1])	            #mode 1 = set brightness
       if mode == 2: randomise_all_sensor_leds(current_element[1])              #mode 2 = randomise
       if mode == 3:                                                            #mode 3 = set solid colour
         for sets in current_element[1]:
           for sensor in sets[0]:
              if len(sets[1])==1: set_sensor_colour_solid(sensor,sets[1][0])
              if len(sets[1])==3: set_sensor_colour_rgb(sensor,sets[1][0],sets[1][1],sets[1][2])
       if mode == 4:                                                            #mode 4 = set individual colour
         for sets in current_element[1]:
           logging.debug("Sensor array %s Data array %s" % (sets[0],sets[1]))
           for sensor in sets[0]:
              if len(sets[1])==4: set_sensor_colour_individual(sensor,sets[1][0],sets[1][1],sets[1][2],sets[1][3])
       if mode == 5:
         for sets in current_element[1]:
           logging.debug("Setting colour %s to %s" % (sets[0],sets[1]))
           set_user_colour(sets[0],sets[1])
     animation_step += 1
     if animation_step >= len(animation): animation_step = 0
   else:  logging.warning("Animation invalidly formed, ignoring")

def reset_default_colours():
    global user_colour_array
    user_colour_array=[[0,0,0],[0xFF,0,0],[0xAA,0xAA,0],[0,0xFF,0],[0,0xAA,0xAA],[0,0,0xFF],[0xAA,0,0xAA],[0xFF,0xFF,0xFF],[10,0,0],[0,10,0],[0,0,10]]

def set_user_colour(index,rgb_array):
    global user_colour_array
    user_colour_array[index]=rgb_array

def timed_animation(index, time):
    timer = Timer(time, stop_animation)
    animation(index)
    timer.start()

def animation(index):
    logging.debug("Playing animation index %d" % index)
    body_bus.write_i2c_block_data(LED_ADDRESS, LED_REGISTER, patterns.body_animations[index][1])

def stop_animation():
    animation(0)

def set_colour_rgb(rgb_array, top = True, bottom = True, oneshot = False, pulse = True, triangle = True, slow = False):
  sorted_index_vals = np.argsort(rgb_array).tolist()
  sorted_index = [0,0,0]
  ix=0x11
  if slow: ix=0x22
  for i in range(3):
    sorted_index[sorted_index_vals[i]] = i
  if rgb_array[sorted_index.index(1)] > 0:                                      #Check if middle value is greater than zero
    ratio = rgb_array[sorted_index.index(0)] / float(rgb_array[sorted_index.index(1)])
    if pulse and not oneshot:                                                   #If pulse is true we can bodge a 3-colour system; in oneshot mode all colours use blink pattern so this wont work
      if ratio > 0.9:
         rgb_array[sorted_index.index(0)] = rgb_array[sorted_index.index(1)]
         sorted_index[sorted_index.index(0)]=1
      if ratio < 0.2: sorted_index[sorted_index.index(0)]=-1
    else:
      if ratio > 0.75:                                                          #Otherwise, if 3rd colour is within 75% of second colour, show it, else don't.
         rgb_array[sorted_index.index(0)] = rgb_array[sorted_index.index(1)]
         sorted_index[sorted_index.index(0)]=1
      else: sorted_index[sorted_index.index(0)]=-1
    ratio_array = [0.75,0.667,0.5,0.333,0.25]
    relative_duty = ratio_array.index(min(ratio_array, key=lambda x:abs(x-ratio)))
  else:
    sorted_index[sorted_index.index(0)] = -1
    sorted_index[sorted_index.index(1)] = -1
  message=[0,0,0,0,0,0,0,0,0,0x0F,0]                                            #Just hardcoded for quickness
  if oneshot:
    message=[0,0,0,0,ix,0,0,0xFF,0,0x0F,0x88]
    if triangle:
      message[3]=ix
      message[5]=ix
    if pulse:
      message[6]=ix
  cols=["Red","Green","Blue"]
  led_mask = 0
  if top: led_mask += 1
  if bottom: led_mask += 8
  for col in range(3):
    logging.debug("Setting %s value" % cols[col])
    mode = sorted_index[col]
    power = rgb_array[col] >> 4
    if mode == 0: power = rgb_array[sorted_index.index(1)] >> 4
    if power < 1: mode = -1
    if mode == 0:
      if slow:
        on_time_array = [96,64,32,32,32]
        off_time_array = [32,32,32,64,96]
      else:
        on_time_array = [96,64,32,32,32]
        off_time_array = [32,32,32,64,96]
      message[0] = message[0] + (led_mask << col)                               #Turn on bank 1 following blink pattern for colour [111]
      message[1] = message[1] + (led_mask << col)
      message[2] = message[2] + (led_mask << col)
      if triangle:
        message[3] = on_time_array[relative_duty]
        message[5] = off_time_array[relative_duty]
      else:
        message[4] = on_time_array[relative_duty]
        message[6] = off_time_array[relative_duty]
        message[7] = off_time_array[relative_duty]
    if mode == 1:
      if oneshot: message[2] = message[2] + (led_mask << col)                   #Turn on bank 1 max pwm for colour [110]
      message[0] = message[0] + (led_mask << col)
      message[1] = message[1] + (led_mask << col)
      message[8] = message[8] + (power << 4)
    if mode == 2:                                                               #Turn on bank 0 max pwm for colour [010]
      if oneshot: message[2] = message[2] + (led_mask << col)
      message[1] = message[1] + ( led_mask << col)
      message[8] = message[8] + power
  body_bus.write_i2c_block_data(LED_ADDRESS, LED_REGISTER, message)

def set_right_colour_solid(index):
  if index < 0 or index > len(patterns.solid_colours):
    logging.warning("Requested colour outside range; ignoring.")
  else:
    logging.debug("Setting right LED to %s" % patterns.solid_colours[index][0])
    body_bus.write_i2c_block_data(LED_ADDRESS, LED_REGISTER, [0x00,0x00,patterns.solid_colours[index][1],0x44,0x44,0x44,0x44,0xFF,0x0F,0x8B])

def set_left_colour_solid(index):
  if index < 0 or index > len(patterns.solid_colours):
    logging.warning("Requested colour outside range; ignoring.")
  else:
    logging.debug("Setting left LED to %s" % patterns.solid_colours[index][0])
    body_bus.write_i2c_block_data(LED_ADDRESS, LED_REGISTER, [0x00,0x00,patterns.solid_colours[index][2],0x44,0x44,0x44,0x44,0xFF,0x0F,0x8B])

def set_right_colour_pulse(index,speed=0x04):                                     #Speed range 0 to 8
  if index < 0 or index > len(patterns.solid_colours):
    logging.warning("Requested colour outside range; ignoring.")
  else:
    logging.debug("Setting right LED to pulse %s" % patterns.solid_colours[index][0])
    body_bus.write_i2c_block_data(LED_ADDRESS, LED_REGISTER, [0x00,patterns.solid_colours[index][1],patterns.solid_colours[index][1],speed,speed<<1,speed,speed,speed,0xFF,0x0F,0x11])

def set_left_colour_pulse(index,speed=0x04):                                  #Speed range 0 to 15
  if index < 0 or index > len(patterns.solid_colours):
    logging.warning("Requested colour outside range; ignoring.")
  else:
    logging.debug("Setting left LED to pulse %s" % patterns.solid_colours[index][0])
    body_bus.write_i2c_block_data(LED_ADDRESS, LED_REGISTER, [0x00,patterns.solid_colours[index][2],patterns.solid_colours[index][2],speed,speed<<1,speed,speed,speed,0xFF,0x0F,0x11])

def set_colour_pulse(index,speed=0x04):                                         #Speed range 0 to 15
  if index < 0 or index > len(patterns.solid_colours):
    logging.warning("Requested colour outside range; ignoring.")
  else:
    logging.debug("Setting LEDs to pulse %s" % patterns.solid_colours[index][0])
    body_bus.write_i2c_block_data(LED_ADDRESS, LED_REGISTER, [0x00,patterns.solid_colours[index][1]+patterns.solid_colours[index][2],patterns.solid_colours[index][1]+patterns.solid_colours[index][2],speed,speed<<1,speed,speed,speed,0xFF,0x0F,0x11])


def set_colour_solid(index):
  if index < 0 or index > len(patterns.solid_colours):
    logging.warning("Requested colour outside range; ignoring.")
  else:
    logging.debug("Setting LEDs to %s" % patterns.solid_colours[index][0])
    body_bus.write_i2c_block_data(LED_ADDRESS, LED_REGISTER, [0x00,0x00,patterns.solid_colours[index][1]+patterns.solid_colours[index][2],0x44,0x44,0x44,0x44,0xFF,0x0F,0x8B])

reset_default_colours()

#Command line test [will run when led.py is run directly]
if __name__ == "__main__":
 logger = logging.getLogger()
 logger.setLevel(logging.DEBUG)
 #generate_random_animation(0)
 #for i in range(3):
 #  rgb=[random.randint(0,15)*16,random.randint(0,15)*16,random.randint(0,15)*16]
 #  print "RGB: %s" % rgb
 #  set_colour_rgb(rgb,triangle=True, pulse=False, slow=True)
 #  time.sleep(0.5)
 set_left_colour_pulse(3);
 time.sleep(1);
 set_left_colour_solid(0);
 set_right_colour_solid(1);
 time.sleep(1);
 set_right_colour_pulse(5);
 time.sleep(1);
 set_right_colour_solid(0);
 os._exit(1)


# LED Driver TI TCA6507 [On bus #9 on APIHAT]
# http://www.ti.com/lit/ds/symlink/tca6507.pdf
# Note left led = LED 2, right led = LED 1
# Port 0: LED_1_RED
# Port 1: LED_1_GREEN
# Port 2: LED_1_BLUE
# Port 3: LED_2_RED
# Port 4: LED_2_GREEN
# Port 5: LED_2_BLUE

# Registers:
# 0x00: Select0 [BANK1/PWM1 Characteristics]
# 0x01: Select1 [BANK0/PWM0 Characteristics]
# 0x02: Select2 [LED ON with Select0\1 Characteristics]
# 0x03: Fade-ON Register [Split C7:C4 = Bank 1 C3:C0 = Bank 0]
# 0x04: Fully-ON Register [Split C7:C4 = Bank 1 C3:C0 = Bank 0]
# 0x05: Fade-OFF Register [Split C7:C4 = Bank 1 C3:C0 = Bank 0]
# 0x06: Fully-OFF Register 1 [Split C7:C4 = Bank 1 C3:C0 = Bank 0]
# 0x07: Fully-OFF Register 2 [Split C7:C4 = Bank 1 C3:C0 = Bank 0]
# 0x08: Brightness [Split C7:C4 = Bank 1 C3:C0 = Bank 0]
# 0x09: One-Shot \ Master Intensity

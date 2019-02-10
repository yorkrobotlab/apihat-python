#!/usr/bin/python

# YRL027 Demo Routine - Stripped from Hexaberry Code
# James Hilder, York Robotics Laboratory, Jan 2019

import settings, switch, display,audio, led, sensors, speech, patterns         #YRL027 library imports
import time, logging, sys, threading, math

from threading import Timer
from os import listdir
from os.path import isfile, join

voice_output = False
menu_level = 0
menu_started = False
read_sensor = False
level_0_selection = 0
level_1_selection = 0
led_selection = 0
animation_selection = 0
sensor_mode_selection = 0
poll_sensor = 0
sampling = False
stepped_animation_running = False
seed = 0
display_text = None

level_0_items = ["Lights","Parrot"]
level_0_audio_files = ['wav/lights.wav','wav/parrot.wav']
level_1_items = [
   ["Top","Bottom","Top & Bottom"],
   [""]]
sensor_modes = ["IR","TOF","FUS"]

def setup_demo():
        #Build the lists based on the built list of sensors
        for sensor in settings.sensor_list:
            adjusted_bus = sensor.SENSOR_BUS - 2  # Makes i2c_3=Sensor 1, i2c_7=Sensor 5
            sensor_name = "Sensor %d" % adjusted_bus
            level_0_items.append(sensor_name)
            level_0_audio_files.append("wav/sensor%d.wav" % adjusted_bus)
            level_1_items[0].append(sensor_name)
            level_1_items.append(["IR-R:","AMB:","WB:","RED:","GRN:","BLUE:","WHT:","IR-D:","TOF-D"])

def update_selection():
  global menu_started
  menu_started = True
  if menu_level == 0:
    display.one_line_text(level_0_items[level_0_selection])
    play_audio(level_0_audio_files[level_0_selection])
  if menu_level == 1:
    line_1 = level_0_items[level_0_selection]
    if level_0_selection == 0:                                                  #LED menu
       if level_1_selection == 0 : led.set_top_colour_solid(led_selection)
       elif level_1_selection == 1 : led.set_bottom_colour_solid(led_selection)
       elif level_1_selection == 2 : led.set_colour_solid(led_selection)
       else : settings.sensor_list[level_1_selection-3].set_sensor_colour_solid(led_selection)
    if display_text != None: display.two_line_text(line_1,display_text)
    else: display.two_line_text(line_1,"")

def switch_handler(current_cursor, previous_cursor):
  global level_0_selection, level_1_selection, led_selection, menu_level, read_sensor, display_text, sampling, sensor_mode_selection, seed
  display_text = None                                                           # Display text holds a string to write on the display on update
  if not menu_started:
    update_selection()                                                          # Do not respond to very first nav. stroke but update display...
  else:
    dir_push = (current_cursor & 0x10) - (previous_cursor & 0x10)
    dir_up = (current_cursor & 0x08) - (previous_cursor & 0x08)
    dir_down = (current_cursor & 0x04) - (previous_cursor & 0x04)
    dir_left = (current_cursor & 0x01) - (previous_cursor & 0x01)
    dir_right = (current_cursor & 0x02) - (previous_cursor & 0x02)

    if dir_push > 0:
      logging.debug("Push Pressed")
      if menu_level == 0:
        if level_0_selection == 1:                                              #Parrot mode - sample speech
          logging.info("Starting audio recording")
          sampling = True
          led.animation(2)
          speech.start_recording()
        else:
          menu_level = 1
          level_1_selection = 0
          display_text = level_1_items[level_0_selection][level_1_selection]
          if level_0_selection > 1:
              read_sensor = True
      else:
        if menu_level == 1:
            read_sensor = False
            menu_level = 0
        level_1_selection = 0
        led.set_colour_solid(0)
      update_selection()

    if dir_up > 0 and not sampling:
      logging.debug("Up Pressed")
      if menu_level == 0:
        level_0_selection -= 1
        if level_0_selection < 0:
          level_0_selection = len(level_0_items) - 1
        update_selection()
      if menu_level == 1:
          level_1_selection += 1
          if level_1_selection >= len(level_1_items[level_0_selection]): level_1_selection = 0
      display_text = level_1_items[level_0_selection][level_1_selection]
      update_selection()

    if dir_down > 0 and not sampling:
      logging.debug("Down Pressed")
      if menu_level == 0:
        level_0_selection += 1
        if level_0_selection == len(level_0_items):
          level_0_selection = 0
        update_selection()
      if menu_level == 1:
          level_1_selection -= 1
          if level_1_selection < 0: level_1_selection = len(level_1_items[level_0_selection]) - 1
      if level_1_selection >= 0: display_text = level_1_items[level_0_selection][level_1_selection]
      update_selection()

    if dir_right > 0 and not sampling:
      logging.debug("Right Pressed")
      if menu_level == 1:
        if level_0_selection == 0:                                              #LED mode
          led_selection += 1
          if led_selection >= len(patterns.solid_colours): led_selection = 0
          display_text = patterns.solid_colours[led_selection][0]
          update_selection()

    if dir_left > 0 and not sampling :
      logging.debug("Left Pressed")
      if menu_level == 1:
        if level_0_selection == 0:                                              #LED mode
          led_selection -= 1
          if led_selection < 0: led_selection = len(patterns.solid_colours)-1
          display_text = patterns.solid_colours[led_selection][0]
          update_selection()

    if dir_push < 0:
      logging.debug("Push Released")
      if sampling:
        sampling = False
        led.timed_animation(3,0.5)
        message = speech.end_recording()
        audio.say(message)

    if dir_up < 0:
      logging.debug("Up Released")

    if dir_down < 0:
      logging.debug("Down Released")

    if dir_right < 0:
      logging.debug("Right Released")

    if dir_left < 0:
      logging.debug("Left Released")

def set_voice_output(vo):
  global voice_output
  voice_output = vo
  logging.debug("Voice output set to %s" % voice_output )

def play_audio(file):
  if voice_output:
    audio.play_audio_file_background(file)

def start_demo():
  global menu_started
  global menu_level
  play_audio('wav/demomode_on.wav')
  logging.debug("STARTING DEMO")
  display.one_line_text("Demo On")
  menu_started = False
  menu_level = 0
  level_0_selection = 0

def stop_demo():
  global read_sensor
  read_sensor = False
  play_audio('wav/demomode_off.wav')
  display.one_line_text("Demo Off")

def demo_sensor_thread():
  global display_text
  while True:
    if read_sensor:
      if level_1_selection < 3 or level_1_selection == 7:
        ir_sensor_data = settings.sensor_list[level_0_selection-2].read_alp_sensor()
        settings.sensor_list[level_0_selection-2].init_alp_sensor()
        logging.debug("IR Sensor Read - IR:%d ALS:%d WB:%d" % (ir_sensor_data[0],ir_sensor_data[1],ir_sensor_data[2]))
        if level_1_selection < 3 : display_text = "%s %d" % (level_1_items[level_0_selection][level_1_selection],ir_sensor_data[level_1_selection])
        if level_1_selection == 7 : display_text = "%s  %03dmm" % (level_1_items[level_0_selection][level_1_selection],(int) (sensors.ir_value_to_distance(ir_sensor_data[0])))
      if level_1_selection > 2 and level_1_selection < 7:
        colour_sensor_data = settings.sensor_list[level_0_selection-2].read_colour_sensor()
        logging.debug("Colour Sensor Read - R:%d G:%d B:%d W:%d" % (colour_sensor_data[0],colour_sensor_data[1],colour_sensor_data[2],colour_sensor_data[3]))
        display_text = "%s %d" % (level_1_items[level_0_selection][level_1_selection],colour_sensor_data[level_1_selection - 3])
      if level_1_selection == 8:
        display_text = "%s %03dmm" % (level_1_items[level_0_selection][level_1_selection],settings.sensor_list[level_0_selection-2].read_tof_distance())
      update_selection()
    time.sleep(0.1)

def start_demo_threads():
  t=threading.Thread(target=demo_sensor_thread)
  t.start()

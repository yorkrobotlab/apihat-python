#!/usr/bin/python
# YRL028 - APIHAT - Python 3 API Version 0.1
#
# Main program
#
# James Hilder, York Robotics Laboratory, Feb 2019


import logging, sys
import settings

settings.init()

import RPi.GPIO as GPIO, threading, subprocess, time, pickle, os
import display, led, demo, audio, speech, utils, sensors, switch                #YRL028 Imports
from threading import Timer
from subprocess import call
from queue import *
from user_programs import *

data_poll_period = settings.default_poll_period    # Default sensor\system status polling period in seconds

logging.info("YRL028 Core Functions Python File - Ver  %s" % (settings.VERSION_STRING))

PROG_NOT_RUNNING = 0
PROG_INITIALISED = 1
PROG_RUNNING     = 2
PROG_PAUSED      = 3
program_name = None
program_state = PROG_NOT_RUNNING
demo_mode_enabled = False
demo_mode_active = False
stats_mode_enabled = False
autosense_mode_enabled = False
switch_interrupt = False
status_interrupt = False
power_interrupt = False
previous_switch_state = 0
battery_warning_state = 0                                                       # Used so we don't repeatedly give battery low warnings

GPIO.setmode(GPIO.BCM)
GPIO.setup(settings.SWITCH_INTERRUPT_PIN,GPIO.IN,pull_up_down=GPIO.PUD_UP)

def switch_interrupt_active(pin):
  global switch_interrupt
  switch_interrupt = True

def default_dip_switch_change_handler(current_dip_state,previous_dip_state):
  global demo_mode_enabled, stats_mode_enabled, speech_mode_enabled, autosense_mode_enabled
  #The DIP switch has changed state...
  logging.info('DIP Switch state altered')
  if current_dip_state & 1 == 1 and previous_dip_state & 1 == 0:
    demo_mode_enabled = True
    logging.info("Demo mode enabled")
    demo.start_demo()
  if current_dip_state & 1 == 0 and previous_dip_state & 1 == 1:
    demo_mode_enabled = False
    logging.info("Demo mode disabled")
    demo.stop_demo()
  if current_dip_state & 2 == 2 and previous_dip_state & 2 == 0:
    stats_mode_enabled = True
    logging.info("Stats mode enabled")
  if current_dip_state & 2 == 0 and previous_dip_state & 2 == 2:
    stats_mode_enabled = False
    logging.info("Stats mode disabled")
  if current_dip_state & 4 == 4 and previous_dip_state & 4 == 0:
    demo.set_voice_output(True)
    logging.info("Audio enabled")
  if current_dip_state & 4 == 0 and previous_dip_state & 4 == 4:
    demo.set_voice_output(False)
    logging.info("Audio disabled")
  if current_dip_state & 8 == 8 and previous_dip_state & 8 == 0:
    autosense_mode_enabled = True
    logging.info("Data polling thread enabled")
  if current_dip_state & 8 == 0 and previous_dip_state & 8 == 8:
    autosense_mode_enabled = False
    logging.info("Data polling thread disabled")

def switch_interrupt_handler():
  global previous_switch_state, switch_interrupt
  current_switch_state = switch.read_input_registers()
  #Check if the switches have changed state (false interrupts eg bounce possible...)
  if previous_switch_state != current_switch_state:
    #logging.debug(current_switch_state)
    current_dip_state = current_switch_state % 16
    previous_dip_state = previous_switch_state % 16
    if current_dip_state != previous_dip_state:
      #DIP switch has been changed...
      logging.debug('DIP switch changed')
      switch.set_dip_leds(current_dip_state)
      if settings.use_built_in_dip_functions:
        default_dip_switch_change_handler(current_dip_state,previous_dip_state)
      #else :   # Add non-default code here...
    current_cursor_state = (current_switch_state & 0x1F0) >> 4
    previous_cursor_state = (previous_switch_state & 0x1F0) >> 4
    if current_cursor_state != previous_cursor_state:
      #Navigation switch has been changed...
      logging.debug('Navigation switch changed')
      if demo_mode_enabled:
        demo.switch_handler(current_cursor_state, previous_cursor_state)
    current_user_button_state = (current_switch_state & 0x200) >> 9
    previous_user_button_state = (previous_switch_state & 0x200) >> 9
    if current_user_button_state != previous_user_button_state:
      logging.debug('User button changed')
      #if speech_mode_enabled:
      #speech.switch_handler(current_user_button_state)
    previous_switch_state = current_switch_state
  switch_interrupt = False

update_stats = False
update_sensors = False
update_battery_monitor = False

def stats_thread():
  global update_stats
  while handler_running:
    if stats_mode_enabled and not demo_mode_enabled:
      update_stats = True
    time.sleep(1)

poll_s_since_epoch = 0
next_poll_s = 0

def battery_thread():
   global update_battery_monitor
   while handler_running:
       time.sleep(2)
       update_battery_monitor = True

def data_thread():
   global update_sensors
   while handler_running:
       if autosense_mode_enabled:
           update_sensors = True
       time.sleep(0.05)
       sleep_period = next_poll_s - time.time()
       if sleep_period < 0.01: sleep_period = data_poll_period
       #print (sleep_period)
       time.sleep(sleep_period)

def update_data_files():
    global poll_s_since_epoch, next_poll_s
    #Do autosense polling
    poll_s_since_epoch = time.time()
    next_poll_s = poll_s_since_epoch + data_poll_period
    logging.info("Polling system state and sensors at %f" % poll_s_since_epoch)
    system_datafile=open(settings.system_datafilename,"a+")
    system_datafile.write("%f,%s\n" % (poll_s_since_epoch,utils.dynamic_values_to_csv()))
    system_datafile.close()
    for sensor in settings.sensor_list:
        sensor_datafile=open("%s%d.csv" % (settings.sensor_datafilename,(sensor.SENSOR_BUS-2)),"a+")
        sensor_datafile.write("%f,%s\n" % (poll_s_since_epoch,sensor.write_values_to_csv_string()))
        sensor_datafile.close()

def write_headers():
    logging.info("Writing new system data file at %s" % settings.system_datafilename)
    system_datafile=open(settings.system_datafilename,"w")
    system_datafile.write("system-time,%s\n" % utils.dynamic_values_to_csv_header())
    system_datafile.close()
    export_sensor_list=[]
    for sensor in settings.sensor_list:
        export_sensor_list.append(["%d" % (sensor.SENSOR_BUS-2),sensor.get_export_list(),sensor.SENSOR_LED_ADDRESS])
        sensor_datafile=open("%s%d.csv" % (settings.sensor_datafilename,(sensor.SENSOR_BUS-2)),"w")
        sensor_datafile.write("system-time,%s\n" % (sensor.get_csv_header_string()))
        sensor_datafile.close()
    with open("%slist.pickle" % settings.sensor_datafilename, "wb") as pickler:
        pickle.dump(export_sensor_list,pickler)

shutdown_timer = None
audio.setup_audio()
GPIO.add_event_detect(settings.SWITCH_INTERRUPT_PIN , GPIO.FALLING, switch_interrupt_active)

#Intro bits
audio.play_audio_file("wav/apihat.wav")
display.init_display()
led.timed_animation(3,4)
display.display_image_file("images/yrl-white.pbm")
time.sleep(0.6)
display.display_image_file("images/yrl028-black.pbm")
time.sleep(0.1)
display.display_image_file("images/yrl028-white.pbm")
time.sleep(0.2)
display.display_image_file("images/apihat-black.pbm")
time.sleep(0.1)
display.display_image_file("images/apihat-white.pbm")
time.sleep(0.8)
#Detect if switch attached; if not, display IP address, else start demo threads
has_switch = switch.detect()

if not has_switch:
    display.two_line_text_wrapped("IP Address:",utils.get_ip())
    time.sleep(1)
    demo_mode_enabled = settings.ENABLE_DEMO_MODE;
    stats_mode_enabled = settings.ENABLE_STATS_MODE;
    autosense_mode_enabled = settings.ENABLE_AUTOSENSE_MODE;


settings.sensor_list = sensors.detect_sensors();
write_headers()

if has_switch:
    demo.setup_demo()
    demo.start_demo_threads()

handler_running = True
t=threading.Thread(target=stats_thread)
t.start()
battery_monitor_thread = threading.Thread(target=battery_thread)
data_polling_thread = threading.Thread(target=data_thread)
data_polling_thread.start()
if(settings.ENABLE_BATTERY_MONITOR): battery_monitor_thread.start()
time.sleep(0.5)

#Run the switch interrupt handler to set current states
if has_switch: switch_interrupt_handler()

def shutdown():
    logging.critical("Battery voltage critically low, shutting down.")
    time.sleep(0.5)
    os.system("shutdown")

def initialise_user_program():
    global program_state
    program_state = PROG_RUNNING
    eval(program_name+".initialise_program()")
    utils.write_prog_state_info("Program %s started" % program_name)

def pause_user_program():
    global program_state
    if(program_state == PROG_RUNNING):
        program_state = PROG_PAUSED
        eval(program_name+".set_display('PAUSED')")
        utils.write_prog_state_info("Program %s paused" % program_name)
    elif(program_state == PROG_PAUSED):
        program_state = PROG_RUNNING
        eval(program_name+".set_display('')")
        utils.write_prog_state_info("Program %s resumed" % program_name)


def stop_user_program():
    global program_state
    program_state = PROG_NOT_RUNNING
    eval(program_name+".stop_program()")
    utils.write_prog_state_info("Program %s stopped" % program_name)

def program_loop():
    global program_name, program_state
    #Check if we have a program request filename
    if(os.path.isfile(settings.program_request_filename)):
        #File exists: First stop currently running program (if one exists).  Then read the file, delete it and set state to NOT_RUNNING
        if(program_state > PROG_NOT_RUNNING): stop_user_program()
        with open(settings.program_request_filename, 'r') as req_file: program_name = (req_file.read())
        logging.info("New program request: %s " % program_name)
        program_state = PROG_NOT_RUNNING
        utils.write_prog_state_info("Program %s requested" % program_name)
        os.remove(settings.program_request_filename)
    else:
        if(os.path.isfile(settings.program_state_filename)):
            #State file exists: Read then delete file
            with open(settings.program_state_filename, 'r') as req_file: state = (req_file.read())
            if(state == "START" and program_name != None): initialise_user_program()
            if(state == "STOP" and program_name != None): stop_user_program()
            if(state == "PAUSE" and program_name != None): pause_user_program()
            os.remove(settings.program_state_filename)
        #Check if we have a program state request filename etc...
        if(program_state == PROG_RUNNING): eval(program_name+".program_loop()")


def handler_loop():
  global update_stats, update_sensors, update_battery_monitor, battery_warning_state, program_name, program_state
  while handler_running:
    if settings.ENABLE_PROGRAMS: program_loop()
    if switch_interrupt:
      if has_switch: switch_interrupt_handler()
    if update_stats:
      display.display_stats()
      update_stats = False
    if update_sensors:
      update_data_files()
      update_sensors = False
    if update_battery_monitor:
      voltage = sensors.read_voltage()
      if(voltage < settings.BATTERY_SHUTDOWN_VOLTAGE and settings.BATTERY_CRITICAL_SHUTDOWN): shutdown()
      if(voltage < settings.BATTERY_CRITICAL_VOLTAGE and battery_warning_state != 1):
          battery_warning_state = 1
          led.animations(8)
          display.warning("BATTERY EMPTY")
          audio.play_audio_file("wav/batterycriticallylow.wav")
      elif (voltage < settings.BATTERY_LOW_VOLTAGE and battery_warning_state != 2):
          battery_warning_state = 2
          display.warning("BATTERY LOW")
          audio.play_audio_file("wav/batterylow.wav")
      if(battery_warning_state != 0 and voltage>(settings.BATTERY_LOW_VOLTAGE + 0.3)):
          battery_warning_state = 0
      update_battery_monitor = False
    time.sleep(0.001)

handler_loop()

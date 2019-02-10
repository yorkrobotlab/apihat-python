#!/usr/bin/python

import threading
import logging
import os
import signal
import subprocess
import speech_recognition as sr
import time
#import led
import display

# Hexaberry Python i2c Interface - Speech Recognition (using Google API)

p = None
r = sr.Recognizer()
stop_recording = False
is_recording = False

def switch_handler(user_button_state):
  if user_button_state == True:
    logging.info("Starting audio recording")
    #led.animation(2)
    start_recording()
  else:
    logging.info("Stopping audio recording")
    #led.timed_animation(3,0.5)
    end_recording()

def start_recording():
   global p, stop_recording
   end_recording = False
   record_st = 'arecord -D dmic_sv -q -c 2 -d 6 -r 16000 -f S32_LE -t wav /ramdisk/temp.wav'
   p = subprocess.Popen(record_st,stdout=subprocess.PIPE, shell=True,preexec_fn=os.setsid)

def end_recording():
   global r
   os.killpg(os.getpgid(p.pid),signal.SIGTERM) # Kill the arecord process
   with sr.AudioFile('/ramdisk/temp.wav') as source:
      audio = r.record(source) # Read entire file
   # recognize speech using Google Speech Recognition
   try:
      google_response = r.recognize_google(audio)
      logging.info("Response: " + google_response)
      display.display_string(google_response)
   except sr.UnknownValueError:
      #led.timed_animation(8,1)
      logging.info("Google Speech Recognition could not understand audio")
      return ""
   except sr.RequestError as e:
      #led.timed_animation(8,1)
      logging.info("Could not request results from Google Speech Recognition service; {0}".format(e))
      return ""
   return google_response

#Command line test [will run when speech.py is run directly]
if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging.info("YRL027 Speech Recognition Test")
    display.init_display()
    switch_handler(True)
    time.sleep(2)
    switch_handler(False)
    os._exit(1)
#display_image_file('images/hexaberry_white.pbm')
#display_stats()

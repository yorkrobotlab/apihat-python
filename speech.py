#!/usr/bin/python
# YRL028 - APIHAT - Python 3 API Version 0.4
#
# Speech recognition functions  (using Google API)
#
# James Hilder, York Robotics Laboratory, June 2019

import threading
import logging
import os
import signal
import subprocess
import settings
import speech_recognition as sr
import time
import display

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
   record_st = 'arecord -D dmic_sv -q -c 2 -d 6 -r 16000 -f S32_LE -t wav ' + settings.speech_filename
   p = subprocess.Popen(record_st,stdout=subprocess.PIPE, shell=True,preexec_fn=os.setsid)

def end_recording():
   global r
   os.killpg(os.getpgid(p.pid),signal.SIGTERM) # Kill the arecord process
   if os.path.isfile(settings.speech_filename):
           with sr.AudioFile(settings.speech_filename) as source:
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
   else:
       logging.error("Audio file %s not found - check OS error messages." % settings.speech_filename)
       return ""

#Command line test [will run when speech.py is run directly]
if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging.info("YRL028 Speech Recognition Test")
    display.init_display()
    switch_handler(True)
    time.sleep(2)
    switch_handler(False)
    os._exit(1)
#display_image_file('images/hexaberry_white.pbm')
#display_stats()

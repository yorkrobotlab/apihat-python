#!/usr/bin/python
# YRL028 - APIHAT - Python 3 API Version 0.1
#
# Functions for audio output
#
# James Hilder, York Robotics Laboratory, Feb 2019

import RPi.GPIO as GPIO, threading, logging, subprocess, os, time, settings
from queue import *

AUDIO_ON = 16   #Audio Enable attached to GPIO 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(AUDIO_ON,GPIO.OUT,initial=GPIO.LOW)

audio_volume_string = "100%"

q=Queue()
running_process = None
audio_killed = False

def audio_queue_thread():
  global audio_killed
  logging.debug("Audio Queue Thread started")
  while True :
    while not q.empty():
      #Purge all but most recent item in audio queue
      while q.qsize() > 1:
        next_function=q.get()
        q.task_done()
      next_function = q.get()
      func = next_function[0]
      args = next_function[1:]
      logging.debug("Handling next audio job from queue: %s %s" % (func.__name__ ,args , ))
      audio_killed = False
      unmute()
      func(*args)
      while not audio_killed and running_process.poll() is None: time.sleep(0.01)
      logging.debug("Audio task finished - muting audio")
      q.task_done()
      mute()
    time.sleep(0.01)

def set_volume(volume):
  subprocess.call(["amixer","-q","sset","PCM,0","%d%%" % (volume)])  #Set audio_volume_string to 96 for 100%

def start_audio_thread():
  audio_thread.start()

def setup_audio():
  set_volume(settings.AUDIO_VOLUME)
  mute()
  start_audio_thread()

def kill_audio():
  global audio_killed
  global running_process
  if not running_process is None:
    if running_process.poll() is None:
      logging.info("Killing audio process %d" % running_process.pid)
      running_process.kill()
    audio_killed = True
    running_process = None

def mute():
  GPIO.output(AUDIO_ON,GPIO.LOW)


def unmute():
  GPIO.output(AUDIO_ON,GPIO.HIGH)

def IF_say(message):
  subprocess.call(["espeak",message])

def IF_play_audio_file(file):
  global running_process
  filename,ext=os.path.splitext(file)
  #print ext
  if ext=='.mp3': running_process = subprocess.Popen(["mpg123","-q",file])
  else:  running_process = subprocess.Popen(["aplay","-q",file])

def say(message):
   q.put((IF_say,message))

def play_audio_file(file):
   q.put((IF_play_audio_file,file))

def play_audio_file_background(file):
  t=threading.Thread(target=play_audio_file,args=(file,))
  t.start()

audio_thread=threading.Thread(target=audio_queue_thread)

#Command line test [will run when audio.py is run directly]
if __name__ == "__main__":
 setup_audio()
 play_audio_file("wav/yrl028.wav")
 time.sleep(1.3)
 kill_audio()
 time.sleep(0.4)
 play_audio_file("wav/apihat.wav")
 time.sleep(0.85)
 kill_audio()
 time.sleep(1)
 os._exit(1)

#!/bin/bash
arduino --upload --port /dev/ttyUSB0 --board arduino:avr:pro:cpu=8MHzatmega328 --verbose-upload yrl028_arduino.ino 

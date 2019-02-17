# Blank example user program for APIHAT Python library
#
# User programs should have a "_apihat.py" suffix, be placed in the "user_programs" folder and contain the following functions:
#
# set_display()         :  Displays the program name and an additional message (eg "PAUSED") on the OLED
# initalise_program()   :  Run once when program is requested or restarted
# program_loop()        :  Run every loop of the main core program.  Avoid having blocking or unduly long to run code here...
# stop_program()        :  Run once when the program is stopped (and also when a new program is about to be loaded).  Should ideally reset motors, display and leds to an off state....

import logging,settings, motors, led, sensors, display, switch, time
program_name = "BLANK PROGRAM"
start_time = 0
loop_period = 0.2 #Target period in seconds for each run of loop

def set_display(message):
    display.two_line_text_wrapped(program_name,message)

def initialise_program():
    global start_time
    set_display('')
    start_time = time.time()
    logging.info("Program initialised");

def program_loop():
    global start_time
    if((time.time() - start_time) > loop_period):
        start_time = time.time()
        logging.info("Program loop");

def stop_program():
    #Clear the display, turn off LEDs, stop the motors
    display.clear()
    led.stop_animation()
    motors.coast()
    logging.info("Program stopped")

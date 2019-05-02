# Avoid obstacles user program for APIHAT Python library
#
# AARM Plate Version  02-05-2019
#
# User programs should have a "_apihat.py" suffix, be placed in the "user_programs" folder and contain the following functions:
#
# set_display()         :  Displays the program name and an additional message (eg "PAUSED") on the OLED
# initalise_program()   :  Run once when program is requested or restarted
# program_loop()        :  Run every loop of the main core program.  Avoid having blocking or unduly long to run code here...
# on_pause()            :  Run once when program is PAUSED
# on_resume()           :  Run once when program is resumed (before loop)
# stop_program()        :  Run once when the program is stopped (and also when a new program is about to be loaded).  Should ideally reset motors, display and leds to an off state....

import logging,audio,settings, motors, led, sensors, display, switch, time, random
program_name = "AVOID"
start_time = 0
init_period = 2.5 # Time to wait for init routine
loop_period = 0.05 #Target period in seconds for each run of loop
distance_threshold_low = 15 # If something is within low threshold take evasive active
distance_threshold_high = 30 # If something is within high threshold slow down, edge away
target_speed = 0.5
previous_state = -1
current_state = -2
evasion_start_time = 0
evasion_period = 0

def set_display(message):
    display.two_line_text_wrapped(program_name,message)

def initialise_program():
    global start_time
    audio.play_audio_file("wav/avoid_obstacles.wav")
    set_display('')
    start_time = time.time()
    logging.info("Program initialised");
    led.animation(7) #Purple pulse

#State: -1) Paused\stopped 0) Getting ready 1) No obstacle 2) Obstacle to left 3) Obstacle to right 4) Danger 5) Evasive action
def program_loop():
    global start_time, previous_state, evasion_start_time,evasion_period
    current_state = -1
    if(previous_state == -1):
        if((time.time() - start_time) > init_period):
            current_state = 0
    elif((time.time() - start_time) > loop_period):
        start_time = time.time()
        min_distance = 100
        min_bearing = 0
        distances = []
        count = 0
        for s_def in settings.ROBOT_SENSOR_MODEL:
            distance = sensors.get_distance(sensors.read_adc(count),s_def[1])
            count+=1
            distances.append([s_def[2],distance])
            if(distance < min_distance):
                min_distance = distance
                min_bearing = s_def[2]
        #logging.info(distances)
        if(min_distance > distance_threshold_high):
            current_state = 1;  # No obstacle
        elif(min_distance < distance_threshold_low):
            if(previous_state == 5 and (time.time()-evasion_start_time < evasion_period)): current_state = 5
            else: current_state = 4
        else:   #Distance falls between thresholds so decide if it is to left or right
            if(min_bearing > 180):  current_state = 2
            else: current_state = 3
    else: current_state = previous_state #Set current state to previous state when we haven't passed the loop period
    if(previous_state != current_state):
        logging.info("avoid_obstacles: Current state %d, previous state %d" % (current_state, previous_state))
        if(current_state==1): #No obstacle; full speed ahead!
            motors.forwards(target_speed)
            led.set_colour_solid(3) #GREEN
        if(current_state==2): #Obstacle to left, head right
            motors.set_motor_speeds(target_speed,target_speed/2)
            led.set_left_colour_pulse(1)
        if(current_state==3):
            motors.set_motor_speeds(target_speed/2,target_speed)
            led.set_right_colour_pulse(1)
        if(current_state==4):
            evasion_start_time = time.time()
            evasion_period = 0.2+(random.random())
            if(random.random()>0.6): motors.set_motor_speeds(-target_speed,target_speed)
            elif(random.random()>0.3): motors.set_motor_speeds(target_speed,-target_speed)
            else: motors.set_motor_speeds(-target_speed/2,-target_speed/2)
            led.animation(8)
            current_state=5
    previous_state = current_state

def stop_program():
    #Clear the display, turn off LEDs, stop the motors
    display.clear()
    led.stop_animation()
    motors.coast()
    logging.info("Program stopped")

def on_pause():
    #Do something when program is PAUSED
    set_display('PAUSED')
    motors.coast()
    led.animation(4) #Yellow blink
    logging.info("Program paused")

def on_resume():
    #Do something when program is resumed
    set_display('')
    global previous_state
    logging.info("Program resumed")
    previous_state = 0

#!/usr/bin/python
# YRL028 - APIHAT - Python 3 API Version 0.2
#
# Quick keyboard pilot example
#
# James Hilder, York Robotics Laboratory, Mar 2019

import curses, time
import motors,arduino
from curses import wrapper

speed = 1.0
old_c = -2
moving = False

def main(stdscr):
    global moving, old_c, speed
    # Clear screen
    stdscr.clear()
    stdscr.addstr(1,1,"YRL028 APIHAT:  Keyboard control console")
    stdscr.refresh()
    stdscr.nodelay(True) #Stops getch being a blocking call
    c = old_c
    while True:
        while(c == old_c):
            time.sleep(0.03)
            c=stdscr.getch()
        old_c = c
        if c == curses.ERR:
            if moving:
                robot_speed(0,0)
                moving = False
        elif c == ord('q'): break
        elif c == curses.KEY_UP:
            robot_speed(speed, speed)
        elif c == curses.KEY_DOWN:
            robot_speed(-speed,-speed)
        elif c == curses.KEY_LEFT:
            robot_speed(-speed,speed)
        elif c == curses.KEY_RIGHT:
            robot_speed(speed,-speed)
        stdscr.addstr(3,3,str(c))

def robot_speed(speed_l,speed_r):
    global moving
    motors.set_motor_speeds(speed_l*100,speed_r*100)
    arduino.set_motor_speeds(int(speed_l*127),int(speed_r*127))
    moving = True
    time.sleep(0.1)

wrapper(main)
# stdscr = curses.initscr() #Setup curses terminal
# curses.noecho() #Don't display keyboard input on console
# curses.cbreak() #Respond instantly [no CR]
# stdscr.keypad(True) #Allow special key shortcuts
#
# def end_curses():
#     curses.nocbreak()
#     stdscr.keypad(False)
#     curses.echo()
#     curses.endwin()

#ifndef YRL028_H
#define YRL028_H

#include <Wire.h>
#include <Math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "Arduino.h"
#include "motors.h"
#include "comms.h"
#include "piezo.h"

const boolean debug = true;
const boolean logSerialData = false;

// Robot specific paramaters
const boolean invert_motors = true;
const int motor_stall_offset = 20;

const int i2c_slave_address = 0x57;
const int power_led = A6;
const int red_led = 13;
const int green_led = 12;
const int enable_vr = 4;
const int pi_shutdown_input = A3;
const int power_button = A2;
const int buzzer = 11;              
const int battery_ref = A7;
const float battery_critical_voltage = 8.6;  //Below this voltage, hard-shutdown V.reg.

const int SWITCH_OFF = 0;
const int POWER_OFF = 1;
const int WAITING_FOR_BOOT = 2;
const int BATTERY_FLAT = 10;

//Global variables
extern volatile long enc_1_count;
extern volatile long enc_2_count;

float get_battery_voltage(void);
void check_for_shutdown(void);
boolean check_battery(void);
boolean check_switch(void);
void yrl028_setup(void);
void yrl028_loop(void);

#endif

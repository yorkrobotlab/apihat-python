// Arduino Code for YRL031 - Dual H-Bridge Driver
//
// Version 0.1 - May 2019
//
// Copyright (C) 2019 James Hilder, York Robotics Laboratory

#ifndef YRL031_H
#define YRL031_H

#include <Wire.h>
#include <Math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "Arduino.h"
#include "comms.h"
#include "motors.h"

//I2C Slave Address [Suggested = 0x58]
const int i2c_slave_address = 0x58;

const boolean debug = true;
const boolean logSerialData = false;

const int motor_stall_offset = 10;

//Global variables
extern volatile long enc_1_count;
extern volatile long enc_1_cumulative;
extern volatile long enc_2_count;
extern volatile long enc_2_cumulative;

const int led1 = 13;
const int led2 = 8;

void yrl031_setup(void);
void yrl031_loop(void);

#endif

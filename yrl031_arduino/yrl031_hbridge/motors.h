// Arduino Code for YRL031 - Dual H-Bridge Driver
//
// Version 0.1 - May 2019
//
// motors.h : Header for motor and wheel encoder functions
//
// Copyright (C) 2019 James Hilder, York Robotics Laboratory
// This is free software, with no warranty, and you are welcome to redistribute it
// under certain conditions.  See GNU GPL v3.0.

#ifndef MOTORS_H
#define MOTORS_H

#include "yrl031.h"

// Pin assignments
const int motor_1_pwm = 9;              
const int motor_1_direction = 4;                
const int motor_1_brakemode = 6;                
const int motor_2_pwm = 10;             
const int motor_2_direction = 5;               
const int motor_2_brakemode = 7;                
const int motor_1_int = 2;  //Output A of Motor 1 Encoder
const int motor_2_int = 3;  //Output A of Motor 2 Encoder
const int motor_1_dir = A0; //Output B of Motor 1 Encoder
const int motor_2_dir = A1; //Output B of Motor 2 Encoder

// Function prototypes
void setPwmFrequency(int divisor);
void set_motor_speeds(int speed1, int speed2);
void set_motor1_speed(int speed);
void set_motor2_speed(int speed);
void brake(void);
void brake_motor1(void);
void brake_motor2(void);
void stop_motors(void);
void setup_motors(void);
void enc_1_ISR(void);
void enc_2_ISR(void);
void reset_encoders(void);

#endif

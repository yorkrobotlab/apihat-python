// Arduino Code for YRL028 - APIHAT
//
// motors.h : Header for motor and wheel encoder functions
//
// Copyright (C) 2019 James Hilder, York Robotics Laboratory
// This is free software, with no warranty, and you are welcome to redistribute it
// under certain conditions.  See GNU GPL v3.0.

#ifndef MOTORS_H
#define MOTORS_H

#include "yrl028.h"

// Pin assignments
const int motor_1_pwm = 9;              // D9=12
const int motor_1_f = 5;                // D5=8
const int motor_1_r = 6;                // D6=9
const int motor_2_pwm = 10;             // D10=13
const int motor_2_f = 7;                // D7=10
const int motor_2_r = 8;                // D8=11
const int motor_1_int = 2;  //Output A of Motor 1 Encoder
const int motor_2_int = 3;  //Output A of Motor 2 Encoder
const int motor_1_dir = A0; //Output B of Motor 1 Encoder
const int motor_2_dir = A1; //Output B of Motor 2 Encoder

// Function prototypes
void setPwmFrequency(int divisor);
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

// Arduino Code for YRL028 - APIHAT
//
// motors.cpp : Source for motor and wheel encoder functions
//
// Copyright (C) 2019 James Hilder, York Robotics Laboratory
// This is free software, with no warranty, and you are welcome to redistribute it
// under certain conditions.  See GNU GPL v3.0.

#include "yrl028.h"


volatile long enc_1_count = 0;
volatile long enc_2_count = 0;
volatile long enc_1_cumulative = 0;
volatile long enc_2_cumulative = 0;

void setPwmFrequency(int divisor) {
 byte mode;
 switch(divisor) {
      case 1: mode = 0x01; break;
      case 8: mode = 0x02; break;
      case 64: mode = 0x03; break;
      case 256: mode = 0x04; break;
      case 1024: mode = 0x05; break;
      default: return;
    }
 TCCR1B = TCCR1B & 0b11111000 | mode;
}

void setup_motors(){
  setPwmFrequency(2);
  pinMode(motor_1_f, OUTPUT);
  pinMode(motor_1_r, OUTPUT);
  pinMode(motor_2_f, OUTPUT);
  pinMode(motor_2_r, OUTPUT);
  pinMode(motor_1_pwm, OUTPUT);
  pinMode(motor_2_pwm, OUTPUT);
  pinMode(motor_1_int, INPUT);
  pinMode(motor_1_dir, INPUT);
  pinMode(motor_2_int, INPUT);
  pinMode(motor_2_dir, INPUT);
  digitalWrite(motor_2_f, 0);
  digitalWrite(motor_2_r, 0);
  analogWrite(motor_2_pwm, 0);
  digitalWrite(motor_1_f, 0);
  digitalWrite(motor_1_r, 0);
  analogWrite(motor_1_pwm, 0);
  attachInterrupt(digitalPinToInterrupt(motor_1_int),enc_1_ISR,CHANGE);
  attachInterrupt(digitalPinToInterrupt(motor_2_int),enc_2_ISR,CHANGE);
}

void set_motor_speeds(int speed1, int speed2){
   set_motor1_speed(speed1);
   set_motor2_speed(speed2);
}

void set_motor1_speed(int speed) {
  if (speed > 0) {
    speed += motor_stall_offset;
    if (speed > 255)speed = 255;
    digitalWrite(motor_1_f, invert_motors);
    digitalWrite(motor_1_r, 1 - invert_motors);
    analogWrite(motor_1_pwm, speed);
  } else {
    if (speed == 0) {
      digitalWrite(motor_1_f, 0);
      digitalWrite(motor_1_r, 0);
    } else {
      speed = motor_stall_offset - speed;

      if (speed > 255)speed = 255;
      digitalWrite(motor_1_f, 1 - invert_motors);
      digitalWrite(motor_1_r, invert_motors);
      analogWrite(motor_1_pwm, speed);
    }
  }
}

void set_motor2_speed(int speed) {
  if (speed > 0) {
    speed += motor_stall_offset;
    if (speed > 255)speed = 255;
    digitalWrite(motor_2_f, 1 - invert_motors);
    digitalWrite(motor_2_r, invert_motors);
    analogWrite(motor_2_pwm, speed);
  } else {
    if (speed == 0) {
      digitalWrite(motor_2_f, 0);
      digitalWrite(motor_2_r, 0);
    } else {
      speed = motor_stall_offset - speed;
      if (speed > 255)speed = 255;
      digitalWrite(motor_2_f, invert_motors);
      digitalWrite(motor_2_r, 1 - invert_motors);
      analogWrite(motor_2_pwm, speed);
    }
  }
}

void brake_motor1() {
  digitalWrite(motor_1_f, 1);
  digitalWrite(motor_1_r, 1);
}

void brake_motor2() {
  digitalWrite(motor_2_f, 1);
  digitalWrite(motor_2_r, 1);
}
void brake() {
  brake_motor1();
  brake_motor2();
}

void stop_motors() {
  set_motor1_speed(0);
  set_motor2_speed(0);
}


void enc_1_ISR() {
  boolean a = digitalRead(motor_1_int);
  boolean b = digitalRead(motor_1_dir);
  if(a==b) enc_1_count--;
  else enc_1_count++;
  enc_1_cumulative++;
}

void enc_2_ISR() {
  boolean a = digitalRead(motor_2_int);
  boolean b = digitalRead(motor_2_dir);
  if(a==b) enc_2_count++;
  else enc_2_count--;
  enc_2_cumulative++;
}

void reset_encoders() {
  enc_1_count=0;
  enc_2_count=0;
  enc_1_cumulative=0;
  enc_2_cumulative=0;
}

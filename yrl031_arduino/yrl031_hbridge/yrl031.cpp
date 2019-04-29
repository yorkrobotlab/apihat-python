// Arduino Code for YRL031 - Dual H-Bridge Driver
//
// Version 0.1 - May 2019
//
// Copyright (C) 2019 James Hilder, York Robotics Laboratory
//
// This is free software, with no warranty, and you are welcome to redistribute it
// under certain conditions.  See GNU GPL v3.0.
//
// The YRL031 Arduino compatible microcontroller is an ATmega328P running at 8MHz [on a 3.3V supply]
//
// Choose Board = "Arduino Pro or Pro Mini" and Processor = "ATmega328P (3.3V, 8MHz)" in Tools Menu
// of Arduino IDE, or use settings in command-line script.
//


#include "yrl031.h"

unsigned long startMillis;

int power_state = 0;
int step_time_ms = 250;

void yrl031_setup() {
  // Setup serial console
  Serial.begin(57600);
  Serial.println(F("YRL031-H-Bridge Driver [Version 0.1.190430]"));

  // Setup LEDs
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
 
  Wire.begin(i2c_slave_address);
  Wire.onRequest(i2c_request_event);
  Wire.onReceive(i2c_receive_event);
  startMillis = millis();
}

boolean log_updated = false;


void yrl031_loop() {
  //Check for serial data
  check_serial_for_data();
  process_serial_data();
  process_i2c_data();
  unsigned long currentMillis = millis() - startMillis;
  if (currentMillis > step_time_ms) {
    digitalWrite(led1,!digitalRead(led1));
    digitalWrite(led2,!digitalRead(led2));
    Serial.print("TEMP:");
    Serial.print(analogRead(A7));
    //Serial.print("  CURRENT:");
    //Serial.println(analogRead(A6));
    startMillis = millis();
  }
}

// Arduino Code for YRL028 - APIHAT
//
// Copyright (C) 2019 James Hilder, York Robotics Laboratory
// This is free software, with no warranty, and you are welcome to redistribute it
// under certain conditions.  See GNU GPL v3.0.
//
//
//
//
// The YRL028 Arduino compatible microcontroller is an ATmega328P running at 8MHz [on a 3.3V supply]
//
// Choose Board = "Arduino Pro or Pro Mini" and Processor = "ATmega328P (3.3V, 8MHz)" in Tools Menu
// of Arduino IDE, or use settings in command-line script.
//
// In this version of the code, the Arduino controls the following hardware functions:
//   1.  Soft power control for main 5V supply [powering the RPi, motors, sensors etc].
//   2.  Dual H-Bridge driver
//   3.  Dual wheel encoder
//   4.  Piezo Sounder

#include "yrl028.h"

unsigned long startMillis;

int hb_period = 1000;  //Heart-beat period in ms; adjusted from 1000 to sync with Pi better
int power_state = 0;

/**
 * Return the battery voltage.  10 bit ADC, 3.3V = 1023.  Bat_ref uses 500K:100K PD: 
 */
float get_battery_voltage(){
  return analogRead(battery_ref) * 0.0193f;
}

void check_for_shutdown() {
   //Pin pi_shutdown_input will be HIGH unless shutdown has been triggered on Pi  
   if(digitalRead(pi_shutdown_input) == LOW){
    Serial.println(F("Shutdown pin LOW: Switching off regulator"));
    chime(false);
    pinMode(enable_vr, OUTPUT);
    digitalWrite(enable_vr,LOW);
    power_state = POWER_OFF;
   }
}

/**
 * Compare battery voltage to battery_critical reference.  If it is below, do a quick chime, force main V.reg off, enter an endless
 * loop blocking booting [in order to boot, the Arduino will need to be reset, but this would generally happen anyway as the battery
 * would be changed].  This state shouldn't really be reached as the R-Pi has its own battery monitoring and should shutdown at an 
 * earlier point.  A reference voltage of around 8.5V is probably a safe choice for use with 3-cell Li-Po batteries.
 */
boolean check_battery() {
    if(get_battery_voltage() < battery_critical_voltage){
      power_state = BATTERY_FLAT;
      Serial.println(F("Battery voltage critically low. Switching off regulator"));
      alert();
      hb_period = 2000; //Sets the heart-beat period to 2s
      pinMode(enable_vr, OUTPUT);
      digitalWrite(enable_vr,LOW);
      return false;      
    }
    return true;
}

boolean check_switch() {
    pinMode(enable_vr, INPUT_PULLUP);
    boolean switch_state = digitalRead(enable_vr);
    if(switch_state == LOW) {
      hb_period = 3000;
      power_state = SWITCH_OFF;
    }
    return switch_state;
}



void yrl028_setup() {
  // Setup serial console
  Serial.begin(57600); 
  Serial.println(F("YRL028-Arduino Code"));
  // Setup LEDs
  pinMode(power_led, OUTPUT);
  pinMode(red_led, OUTPUT);
  pinMode(green_led, OUTPUT);
  pinMode(pi_shutdown_input, INPUT_PULLUP);
  pinMode(power_button, INPUT_PULLUP);
  setup_motors();

  //Check state of enable_vr line; if switch is closed (off) it will read a zero
  if(check_switch()){
    power_state = WAITING_FOR_BOOT;
    if(check_battery())chime(true);
  }
  Wire.begin(i2c_slave_address);
  Wire.onRequest(i2c_request_event);
  Wire.onReceive(i2c_receive_event);
  startMillis = millis();
}

boolean log_updated = false;

void yrl028_loop() {
  //Check for serial data
  check_serial_for_data();
  process_serial_data();
  process_i2c_data();
  
  unsigned long currentMillis = millis() - startMillis;
  if(logSerialData){
    if(!log_updated){
      if(currentMillis % 100 < 5){
        Serial.print(F("Battery voltage:"));
        Serial.println(get_battery_voltage());
        log_updated = true;
      }
    }else{
      if(currentMillis % 100 > 5){
        log_updated = false;
      }
    }
  }
  //
  if(currentMillis > hb_period) currentMillis = currentMillis % hb_period; 
  switch(power_state){
    case SWITCH_OFF:
      //Blink for 20ms, once every 3 seconds
      if(digitalRead(red_led)){
         if (currentMillis > 20) digitalWrite(red_led,0);
      }else if (currentMillis < 21) digitalWrite(red_led,1);
      if(check_switch()){
        delay(20);
        if(check_battery()){
          power_state = WAITING_FOR_BOOT;
          hb_period = 1000;
        }
      }
      break;
    case POWER_OFF:
      //In POWER_OFF state we have the VR disabled; check power button. Blink for 20ms, once a second
      if(digitalRead(red_led)){
         if (currentMillis > 20) digitalWrite(red_led,0);
      }else if (currentMillis < 21) digitalWrite(red_led,1);
      if(digitalRead(power_button)==LOW){
        Serial.println("Power button pressed");
        //Running check_switch() turns enable_vr back into input, turning on power if switch is open
        if(check_switch()){
          delay(20);
          if(check_battery()){
            hb_period = 1000;
            power_state = WAITING_FOR_BOOT;
          }
        }
      }
      break;
    case WAITING_FOR_BOOT:   
      //Show heartbeat on RED led (2x20mS long flashes each 250ms, then off for half a second)  
      if(currentMillis < 500){ 
        if(digitalRead(red_led)){
           if (currentMillis % 250 > 20) digitalWrite(red_led,0);
        }else if (currentMillis % 250 < 21) digitalWrite(red_led,1);
      }
      if(check_switch()) check_battery();
      check_for_shutdown();
      break;
    case BATTERY_FLAT:
      if(currentMillis < 600){
        if(digitalRead(red_led)){
          if (currentMillis % 200 > 15) digitalWrite(red_led,0);
        }else if (currentMillis % 200 < 16) digitalWrite(red_led,1);
      }
      break;
  }
}

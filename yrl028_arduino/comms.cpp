// Arduino Code for YRL028 - APIHAT
//
// comms.cpp  : Source for i2c and serial communications
//
// Copyright (C) 2019 James Hilder, York Robotics Laboratory
// This is free software, with no warranty, and you are welcome to redistribute it
// under certain conditions.  See GNU GPL v3.0.

#include "yrl028.h"

//Serial variables
const byte numChars = 32;  //Size of serial string buffer (-1)
char received[numChars];  //Stores the received serial data
boolean new_data = false;
int parsed_value = 0;

void i2c_receive_event(int howMany) {
  Serial.println(howMany);
  while (1 < Wire.available()) { // loop through all but the last
    char c = Wire.read(); // receive byte as a character
    Serial.print(c);      
  }
  Serial.println(" - i2c data");
}

void i2c_request_event() {
  Serial.println("Request event");
}

void check_serial_for_data() {
  static byte ndx = 0;
  char endMarker = '\n';
  char rc;
  while (Serial.available() > 0 && new_data == false) {
    rc = Serial.read();
    if (rc != endMarker) {
      received[ndx] = rc;
      ndx++;
      if (ndx >= numChars) {
        ndx = numChars - 1;
      }
    }
    else {
      received[ndx] = '\0'; // terminate the string
      ndx = 0;
      new_data = true;
      Serial.print("Data received:");
      Serial.println(received);
    }
  }
}

boolean parse_integer_from_serial(int low_limit, int high_limit) {
  char * submessage = received + 1;
  int value;
  value = atoi (submessage); //Read integer from string [note this will like return 0 for invalid strings]
  if(value <= high_limit && value >= low_limit) {
    parsed_value = value;
    return true;
  }
  return false;
}

void process_serial_data() {
  if (new_data == true) {
    Serial.println("Received");
    boolean ok = true;
    boolean show_value = true;
    switch (received[0])
    {
      case 'i': Serial.print("Left:");
                Serial.print(enc_1_count);
                Serial.print("  Right:");
                Serial.print(enc_2_count);
                break;
      case 'l': if(parse_integer_from_serial(-255,255)) set_motor1_speed(parsed_value); else ok = false; break;
      case 'r': if(parse_integer_from_serial(-255,255)) set_motor2_speed(parsed_value); else ok = false; break;
      case 'f': if(parse_integer_from_serial(-255,255)) {set_motor1_speed(parsed_value);set_motor2_speed(parsed_value);} else ok = false; break;
      case 'b': brake(); show_value=false; break; //brake!
      //case 'q': toggle_user_led(); show_value=false; break;
      //case 'w': toggle_boot_led(); show_value=false; break;
      case 't': if(parse_integer_from_serial(30,10000)) tone(buzzer, parsed_value); else ok=false; break;
      case 'y': noTone(buzzer); show_value=false; break;
      case 'x': brake(); noTone(buzzer); show_value=false;  break;
      
      default: ok = false;

    }

/**
 * Serial commands:
 * 
 * l [-255 to 255]: Set left motor speed
 * r [-255 to 255]: Set right motor speed
 * f [-255 to 255]: Set both motor speeds
 * b [-----------]: Brake motors
 * q [-----------]: Toggle user LED
 * w [-----------]: Toggle boot LED
 * t [30 to 10000]: Play a tone at given frequency
 * y [-----------]: Stop playing tone
 * m [-255 to 255]: Set running mode [0 - 5 are active modes]
 * x [-----------]: Brake motors and stop active mode 
 */
 
    if (debug) {
      if(ok){
         Serial.print(F("Message: "));
         Serial.print(received[0]);
         if(show_value)Serial.print(parsed_value); 
         Serial.println();
      }else{
      Serial.print(F("ERROR: Invalid message "));
      Serial.println(received);
      }
    }
    new_data = false;
  }
}

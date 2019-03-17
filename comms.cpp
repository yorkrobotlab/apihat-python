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
char i2c_received[numChars];
char i2c_received_length = 0;
char i2c_register;
boolean new_i2c_data = false;
boolean non_displayed_i2c_data = false;

boolean new_data = false;
int parsed_value = 0;

void i2c_receive_event(int howMany) {
  //static byte ndx = 0;
  byte ndx = 0;
  i2c_register = Wire.read();
  if (howMany > 1) {
    while (Wire.available()) { // loop through all but the last
      i2c_received[ndx] = Wire.read();
      ndx++;
    }
  }
  i2c_received_length = ndx;
  new_i2c_data = true;
  non_displayed_i2c_data = true;
    switch(i2c_register){
      case 5: if(i2c_received_length == 1){
        int speed = ((int)i2c_received[0] + 128) << 1;
        if(speed > 255) speed -= 512;
        set_motor1_speed(speed);
        Serial.print("M1:");
        Serial.println(speed);
      }
        break;
      case 6: if(i2c_received_length == 1){
        int speed = ((int)i2c_received[0] + 128) << 1;
        if(speed > 255) speed -= 512;
        set_motor2_speed(speed);
        Serial.print("M2:");
        Serial.println(speed);
      }
        break;
      case 7: if(i2c_received_length == 2){
        int speed1 = ((int)i2c_received[0]+128) << 1;
        int speed2 = ((int)i2c_received[1]+128) << 1;
        if(speed1 > 255) speed1 = speed1 - 512;
        if(speed2 > 255) speed2 = speed2 - 512;
        set_motor_speeds(speed1,speed2);
        Serial.print("M1:");
        Serial.print(speed1);
        Serial.print(" M2:");
        Serial.println(speed2);        
      }
        break;
      case 8: if(i2c_received_length == 2){
        uint8_t msb = (uint8_t) i2c_received[0];
        uint8_t lsb = (uint8_t) i2c_received[1];
        //Serial.print("MSB:");
        //Serial.println(msb);
        //Serial.print("LSB:");
        //Serial.println(lsb);
        int freq = (msb * 256) + lsb;
        if((freq > 29) && (freq<10001)) tone(buzzer,freq);
        else noTone(buzzer);
        Serial.print("T:");
        Serial.println(freq);
      }
        break;
      };     
}

void process_i2c_data() {
//  if (non_displayed_i2c_data) {
//   
//    }
//    Serial.print("I2C Receive - ");
//    Serial.print(i2c_register, HEX);
//    if (i2c_received_length == 0) {
//      Serial.println(" - No data");
//    } else {
//      Serial.print(" - ");
//      Serial.print(i2c_received_length, HEX);
//      Serial.print(" [0x");
//      for (byte i = 0; i < i2c_received_length; i++) {
//        Serial.print(i2c_received[i], HEX);
//        if (i + 1 < i2c_received_length) {
//          Serial.print(",0x");
//        }
//      }
//      Serial.println("]");
//    }
//  }
  non_displayed_i2c_data = false;
}

void write_long(int32_t value){
     byte m_array[4];
     m_array[0]=(value >> 24) & 0xFF;
     m_array[1]=(value >> 16) & 0xFF;
     m_array[2]=(value >> 8) & 0xFF;
     m_array[3]=value & 0xFF;
     Wire.write(m_array,4);
}

void i2c_request_event() {
  if (!new_i2c_data || i2c_received_length > 0) {
    Serial.println("Invalid i2c request");
  } else {
    switch (i2c_register) {
      case 0: Wire.write("yrl028"); break;
      case 1: write_long(enc_1_count); break;
      case 2: write_long(enc_2_count); break;
      case 3: write_long(enc_1_cumulative); break;
      case 4: write_long(enc_2_cumulative); break;
    }
    new_i2c_data = false;
  }
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
  if (value <= high_limit && value >= low_limit) {
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
        Serial.print(" [");
        Serial.print(enc_1_cumulative);
        Serial.print("]  Right:");
        Serial.print(enc_2_count);
        Serial.print(" [");
        Serial.print(enc_2_cumulative);
        Serial.println("]");
        break;
      case 'l': if (parse_integer_from_serial(-255, 255)) set_motor1_speed(parsed_value); else ok = false; break;
      case 'r': if (parse_integer_from_serial(-255, 255)) set_motor2_speed(parsed_value); else ok = false; break;
      case 'f': if (parse_integer_from_serial(-255, 255)) {
          set_motor1_speed(parsed_value);
          set_motor2_speed(parsed_value);
        } else ok = false; break;
      case 'b': brake(); show_value = false; break; //brake!
      //case 'q': toggle_user_led(); show_value=false; break;
      //case 'w': toggle_boot_led(); show_value=false; break;
      case 't': if (parse_integer_from_serial(30, 10000)) tone(buzzer, parsed_value); else ok = false; break;
      case 'y': noTone(buzzer); show_value = false; break;
      case 'x': brake(); noTone(buzzer); show_value = false;  break;
      case 'z': reset_encoders(); break;
      default: ok = false;

    }

    /**
       Serial commands:

       i [-----------]: Display encoder values
       l [-255 to 255]: Set left motor speed
       r [-255 to 255]: Set right motor speed
       f [-255 to 255]: Set both motor speeds
       b [-----------]: Brake motors
       q [-----------]: Toggle user LED
       w [-----------]: Toggle boot LED
       t [30 to 10000]: Play a tone at given frequency
       y [-----------]: Stop playing tone
       m [-255 to 255]: Set running mode [0 - 5 are active modes]
       x [-----------]: Brake motors and stop active mode
       z [-----------]: Reset wheel encoders
    */

    if (debug) {
      if (ok) {
        Serial.print(F("Message: "));
        Serial.print(received[0]);
        if (show_value)Serial.print(parsed_value);
        Serial.println();
      } else {
        Serial.print(F("ERROR: Invalid message "));
        Serial.println(received);
      }
    }
    new_data = false;
  }
}

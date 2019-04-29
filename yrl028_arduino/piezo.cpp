// Arduino Code for YRL028 - APIHAT
//
// Version 0.1.190429
//
// piezo.cpp  : Source for piezo buzzer 
//
// Copyright (C) 2019 James Hilder, York Robotics Laboratory
// This is free software, with no warranty, and you are welcome to redistribute it
// under certain conditions.  See GNU GPL v3.0.

#include "yrl028.h"

/**
*  Play a quick intro of the Mario theme
*/
void play_mario() {
  //[E5 E5 E5 C5 E5 G5 G4]
  //  static int mario[7][3] = {{660,70,100},{660,70,200},{660,70,200},{523,70,66},{660,70,200},{784,70,350},{392,70,400}};
  static int mario[7][3] = {{1320, 70, 100}, {1320, 70, 200}, {1320, 70, 200}, {1046, 70, 66}, {1320, 70, 200}, {1568, 70, 350}, {784, 70, 400}};
  for (int i = 0; i < 7; i++) {
    tone(buzzer, mario[i][0], mario[i][1]);
    delay(mario[i][2]);
  }
}

/**
*  Play a upward [positive=true] or downward short 2-note chime
*/
void chime(boolean positive) {
  tone(buzzer, 1047, 50);
  delay(100);
  if (positive) tone(buzzer, 1568, 50);
  else tone(buzzer, 784, 50);
  delay(100);
}

/**
*  Play a short 1-note alert with delay
*/
void alert_note() {
  tone(buzzer, 784, 100);
  delay(300);
}

/**
*  Play a short 3-note alert chime
*/
void alert() {
  tone(buzzer, 784, 100);
  delay(300);
  tone(buzzer, 784, 100);
  delay(300);
  tone(buzzer, 784, 100);
  delay(300);
}

// Arduino Code for YRL028 - APIHAT
//
// piezo.h  : Header for piezo buzzer 
//
// Copyright (C) 2019 James Hilder, York Robotics Laboratory
// This is free software, with no warranty, and you are welcome to redistribute it
// under certain conditions.  See GNU GPL v3.0.

#ifndef PIEZO_H
#define PIEZO_H

#include "yrl028.h"

void play_mario(void);
void chime(boolean positive);
void alert(void);

#endif

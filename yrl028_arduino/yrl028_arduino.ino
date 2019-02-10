#include <Wire.h>

const int i2c_slave_address = 0x57;
const int power_led = A6;
const int red_led = 13;
const int green_led = 12;
const int enable_vr = 4;
const int pi_shutdown_input = A3;
const int power_button = A2;

const int SWITCH_OFF = 0;
const int POWER_OFF = 1;
const int WAITING_FOR_BOOT = 2;

unsigned long startMillis;

int power_state = 0;

void check_for_shutdown() {
   //Pin pi_shutdown_input will be HIGH unless shutdown has been triggered on Pi  
   if(digitalRead(pi_shutdown_input) == LOW){
    Serial.println(F("Shutdown pin LOW: Switching off regulator"));
    pinMode(enable_vr, OUTPUT);
    digitalWrite(enable_vr,LOW);
    power_state = POWER_OFF;
   }
}

boolean check_switch() {
    pinMode(enable_vr, INPUT_PULLUP);
    boolean switch_state = digitalRead(enable_vr);
    if(switch_state == LOW) power_state = SWITCH_OFF;
    return switch_state;
}

void i2c_receive_event(int howMany) {
  Serial.println(howmany);
  while (1 < Wire.available()) { // loop through all but the last
    char c = Wire.read(); // receive byte as a character
    Serial.print(c);      
  }
  Serial.println(" - i2c data");
}

void i2c_request_event() {
  Serial.println("Request event");
}

void setup() {
  // Setup serial console
  Serial.begin(57600); 
  Serial.println(F("YRL028-Arduino Code"));
  // Setup LEDs
  pinMode(power_led, OUTPUT);
  pinMode(red_led, OUTPUT);
  pinMode(green_led, OUTPUT);
  pinMode(pi_shutdown_input, INPUT_PULLUP);
  pinMode(power_button, INPUT_PULLUP);
  //Check state of enable_vr line; if switch is closed (off) it will read a zero
  if(check_switch())power_state = WAITING_FOR_BOOT;
  Wire.begin(i2c_slave_address);
  Wire.onRequest(i2c_request_event);
  Wire.onReceive(i2c_receive_event);
  startMillis = millis();
}

void loop() {
  unsigned long currentMillis = millis() - startMillis;
  if(currentMillis > 1000) currentMillis = currentMillis % 1000;
  switch(power_state){
    case SWITCH_OFF:
      if(digitalRead(red_led)){
         if (currentMillis > 20) digitalWrite(red_led,0);
      }else if (currentMillis < 21) digitalWrite(red_led,1);
      if(check_switch())power_state = WAITING_FOR_BOOT;
      break;
    case POWER_OFF:
      //In POWER_OFF state we have the VR disabled; check power button
      if(digitalRead(red_led)){
         if (currentMillis > 20) digitalWrite(red_led,0);
      }else if (currentMillis < 21) digitalWrite(red_led,1);
      if(digitalRead(power_button)==LOW){
        Serial.println("Power button pressed");
        //Running check_switch() turns enable_vr back into input, turning on power if switch is open
        if(check_switch())power_state = WAITING_FOR_BOOT;
      }
      break;
    case WAITING_FOR_BOOT:      
      if(digitalRead(red_led)){
         if (currentMillis % 250 > 20) digitalWrite(red_led,0);
      }else if (currentMillis % 250 < 21) digitalWrite(red_led,1);
      check_switch();
      check_for_shutdown();
      break;
  }
}

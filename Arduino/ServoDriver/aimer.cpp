#include "Arduino.h"
#include <Servo.h>
#include "aimer.h"
#define DEBUG true
#define DELAY true
#define HEADERBYTE 0xAA
#define MAXLOOP 100
#define PACKETLEN 4

Aimer::Aimer(Stream &_strm, int xservoPin, int yservoPin){
  // -- Setup Serial Pointer --
  strm = &_strm;

  // -- Setup Servos --
  // init
  Servo _xservo;
  Servo _yservo;
  // Assign to pointers
  xservo = &_xservo;
  yservo = &_yservo;
  // Assign pins
  xservo->attach(xservoPin);
  yservo->attach(yservoPin);
  }

void Aimer::turn(bool xdir, bool ydir){
  /*
  turn() -> void
    Turn the servo connected to servoPin in the specified direction.
    dir = true, turn right/up; dir = false, turn left/false
    Post:
      Uses xservo and yservo to move
  */

  xangle += (dir) ? 1 : -1;
  xservo->write(xangle);
  yangle + (dir) ? 1 : -1;
  yservo->write(yangle);

  }

void Aimer::sendPacket(){
  /*
  sendPacket() -> void
    Using serial, send true xangle and yangle to driver.
    Post:
      Uses UART to send serial information.*/

  // -- Build Packet -- 
  byte PACKET[4];
  // X Angle
  if (xangle > 254) {
    packet[0] = 254;
    packet[1] = xangle - 254;
    }
  else {
    packet[0] = xangle;
    packet[1] = 0;
    }
  }
  // Y Angle
  if (xangle > 254) {
    packet[2] = 254;
    packet[3] = yangle - 254;
    }
  else {
    packet[2] = yangle;
    packet[3] = 0;
    }
  

void Aimer::aim(){
  /*
  aim() -> void
    Using xgoal and ygoal, adjust move servos to that position.
    Post:
      Sends current angle back over Serial with Aimer::sendPacket()
  */

  // -- Turn servos --
  bool xdir = ((xgoal - xangle) > 0);
  bool ydir = ((ygoal - yangle) > 0);
  this->turn(xdir, ydir)

  // -- Send output over serial --
  


bool Aimer::validateHeader(){
  /*
  validateHeader() -> bool
    Validates packet header to that it matches the HEADERBYTE twice.
    Returns:
      bool - True = valid; False = invalid
  */
  if (DEBUG){ strm->println("Searching for header");}

  // -- Read UART until header byte found --
  // ~ Search for first byte ~
  byte incoming = strm->read(); 
  int i = 0;
  while (incoming != HEADERBYTE && i < MAXLOOP) {
    i++;
    // Read bytes when available
    if (strm->available() > 0) {
      incoming = strm->read();
      }
    // Move servo when waiting for byte
    else {
      Aimer::aim();  // Move
      if (DEBUG){ strm->print(".");} // Show wait durring debug
      if (DELAY){ delay(50);}
    }
    }
  // Kill if maximum loop reached
  if (i == MAXLOOP){
    return false;
    }

  // ~ Search for second byte ~
  // Wait for available byte. Move in free time.
  while (!strm->available()){
      Aimer::aim();  // Move
      if (DEBUG){ strm->print(".");} // Show wait durring debug
      if (DELAY){ delay(50);}
    }
  // Validate second byte
  if (sdtrm->read() == HEADERBYTE) {
    if (DEBUG){ strm->println("found good header");}
    return true;  // Good header
    }
  else {
    if (DEBUG){ strm->println("found bad header");}
    return false; // Bad header
    }
  }

void Aimer::getPacketData(){
  /*
  getPacketData() -> void
    Gets the contents of the packet and decodes x & y angle
  */

  // -- Read packet data off uart
  byte packetBytes[4];
  for (int i=0; i<4; i++) {
    // Update servo when waiting for packet
    while (!strm->available()){
      Aimer::aim();  // Move
      if (DEBUG){ strm->print(".");} // Show wait durring debug
      if (DELAY){ delay(50);}
    }
    
    // Add byte to packetBytes
    packetBytes[i] = strm->read();
    }

  // -- Save packet data to variables -- 
  this->xgoal = packetBytes[0] + packetBytes[1];
  this->ygoal = packetBytes[2] + packetBytes[3];
  }

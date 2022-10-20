#include <Servo.h>
#include "Arduino.h"

class Aimer
{
  
  private:
    void getPacketData(); // Reads and parses packet
    bool validateHeader(); // Finds header of a packet
    void sendPacket();  // Send position packet back over serial
    void turn(bool xdir, bool ydir)  // Turn servos in some direction

    Servo* xservo = NULL;
    Servo* yservo = NULL;
    
    int xangle = 0;  // Actual x angle
    int xgoal = 0;  // Desired x angle
    int yangle = 0;  // Actual y angle
    int ygoal = 0;  // Desired y angle
    Stream* strm = NULL; // Serial reference
  public:
    Aimer(Stream &_strm); // Constructor
    
    void update(); // Update cycle
    void available(); // If packet waiting
    void aim();
  };

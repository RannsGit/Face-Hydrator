#include <Servo.h>
#define XSERVO_PIN 3
#define YSERVO_PIN 6
#define RELAY_PIN 2
#define HEADER 0xAA
#define DEBUG true

Servo xservo;
Servo yservo;

byte incoming; // Incoming command byte
int xgoal;  // Desired x angle
int ygoal;  // Desired y angle
int xangle; // Current x angle
int yangle; // Current y angle


void goTo(Servo &servo, int real, int goal){
    /*
    goTo(servo, real, goal) -> Void

    Move servos from actual position, to desired position.
    Parameters:
        &servo (Servo)  - Servo to actuate
        real   (int)    - Actual angle of servo
        goal   (int)    - Desired angle of servo
    
    Post:
        Changes specified angle
    */

    // Determine relation between real & goal
    bool isEqual = (real == goal);
    bool isIncreasing = (real < goal);

    if (isEqual){return; } // Skip if equal

    // Increment servo
    if (isIncreasing){
        for(int i=real; i < goal; i++){
            delay(1);
            servo.write(i);
            }
    }
    else{ 
        for(int i=real; i > goal; i--){
            delay(1);
            servo.write(i);
        }
    }
}


void aim(bool axis){
    /*
    aim(axis) -> void
    Parameters:
        axis  (bool) - true = x; false = y
    Post:
      Changes servo position
    */

    // Display status over serial
    if (DEBUG){
        Serial.print((axis) ? "X Axis" : "Y Axis");
        Serial.print(" aiming from ");
        Serial.print((axis) ? xangle : yangle);
        Serial.print(" to ");
        Serial.println((axis) ? xgoal : ygoal);
    }

    // Actuate servo
    goTo(
        axis ? xservo : yservo, 
        axis ? xangle : yangle,
        axis ? xgoal  : ygoal
        );

    // Update goal
    if (axis){
        xangle = xgoal;
    }
    else{
        yangle = ygoal;
    }

}

void relay(byte rbyte){
    /*
    relay(rbyte) -> void
    Parameters:
        rbyte (byte) - Signal byte for relay.
        
    Accepted signal bytes:
        0x0E - Disconnect relay
        0xE0 - Connect relay*
        0xEE (or any other) - Continue with previous relay state

    Post: 
        Changes output of RELAY_PIN
        */
    
    if (rbyte == 0x0E){
        Serial.println("disconnect relay");
        digitalWrite(RELAY_PIN, LOW);
    }
    else if (rbyte == 0xE0){
        Serial.println("connect relay");
        digitalWrite(RELAY_PIN, HIGH);
    }
    else{
        Serial.print("Unknown byte ");
        Serial.println(rbyte, HEX);
    }
}

void setup(){
    // Start Serial
    Serial.begin(9600);

    // Initialize servos
    xservo.attach(XSERVO_PIN);
    yservo.attach(YSERVO_PIN);

    // Setup relay
    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, LOW);
}

void loop(){

    // Wait for incoming bytes
    if (Serial.available() > 0){

        // Check byte for header
        byte incoming = Serial.read();
        Serial.print("Checking byte ");
        Serial.println(incoming, HEX);

        // Read packet if header match
        if (incoming == HEADER){

            // Wait for buffer to fill to two
            while (Serial.available() < 2){
                Serial.print('.');
                delay(50);
            }

            // Get x and y angles from packet
            xgoal = Serial.read();
            ygoal = Serial.read();

            // Get relay status from packet
            byte relayIncoming = Serial.read();

            // Aim for both axes
            aim(true);
            aim(false);

            relay(relayIncoming);
        }
    }
}


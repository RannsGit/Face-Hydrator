"""
Kyle Tennison
October 24, 2022

Servo host. Using status file, send commands via serial to arduino running
ServoDriver.ino. """

import serial
import time

class ServoHost:


    PORT = "/dev/cu.usbmodem101"
    STATUSFILE = "status.txt"
    PACKET_HEADER = 0xAA

    def __init__(self):
        """Setup serial connection with arduino.
        Post: 
            May exit program! If PORT is invalid, program will exit."""
        self.previous = (0, 0)
        try:    
            self.arduino = serial.Serial(port=self.PORT, baudrate=9600)
        except serial.serialutil.SerialException:
            print("Port closed.")
            exit()


    def isUpdate(self) -> bool:
        """Check if there have been any changes in the file to avoid 
        unnecessary updates"""
        if self.previous == self.read():
            return False 
        else:
            self.previous = self.read()
            return True
    
    @classmethod
    def read(cls) -> any:
        """Get angles from file. 
            Returns:
                x, y (tuple) - Position received from file. (x & y are int)
                OR None      - If file contains some invalid value. """

        with open(cls.STATUSFILE, 'r') as file:
            contents =file.read()

            try:
                # Split csv 
                x, y = contents.split(",")
            except ValueError:
                # If not enough values are recognized
                print("ServoHost: read(): Invalid File: Cannot unpack")
                return None
            else:
                try:
                    # Convert fields to integer
                    x = int(float(x))  # Convert to float to avoid ValueError for 
                    y = int(float(y))  #    long decimal numbers.
                except ValueError:
                    # If fields contain alien type
                    print("ServoHost: read(): Invalid File: Cannot read type")
                    return None
            return x, y

        
    def send(self, b1: int, b2: int) -> None:
        """Send data to arduino.
        Parameters:
            b1 (int)    - First byte to send (NOT HEADER)
            b2 (int)    - Second byte to send"""
        packet = bytearray()
        packet.append(self.PACKET_HEADER) # Add header

        # Add bytes to packet
        packet.append(b1)
        packet.append(b2)

        # Send packet
        self.arduino.write(packet) 

        # Wait for arduino response
        time.sleep(0.01)

        while self.arduino.in_waiting != 0:
            print(self.arduino.readline().decode())

    def run(self):
        """Wait until file change, then send the updated value to arduino.
        Loops indefinitely. """
        while True:
            if self.isUpdate():
                r = self.read()
                # Skip invalid
                if r is None:
                    continue
                else:
                    b1, b2 = r
                self.send(b1, b2)
            else:
                time.sleep(0.01)

if __name__ == "__main__": 
    host = ServoHost()
    host.run()
"""
The Face Hydrator

Kyle Tennison
October 13, 2022

mainface.py:
    Runs Face Hydrator
"""

from  VideoTracker import VideoTracker
from os import path

CASC_PATH = f"{path.dirname(path.abspath(__file__))}"\
            "/haarcascade_frontalface_default.xml"
CAMERA_FOV = 54 

def main():

    v = VideoTracker(CASC_PATH, CAMERA_FOV)
    v.run()

if __name__ == "__main__": main()
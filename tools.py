"""
Misc tools for face detection.

Kyle Tennison
October 10, 2022
"""

DEBUG = True

import json
from datetime import datetime

log = open('log.txt', 'w')

def debug(note, color='') -> None:

    if not DEBUG: return

    ENDC = '\033[0m'

    code = ('', '')
    if color == "red":
        code = ('\033[91m', ENDC)
    elif color == "green":
        code = ('\033[92m', ENDC)
    elif color == "blue":
        code = ('\033[94m', ENDC)
    elif color == "yellow":
        code = ('\033[93m', ENDC)

    print(f"{code[0]}{note}{code[1]}")
    log.write(f"{datetime.now()} ->\t{note}\n")

def jsonGet(*args) -> list:
    """Get parameter from JSON.
    Arguments:
        *args: JSON keys to get
    Returns: 
        (list) Corresponding json values."""

    parameters = []

    # Load json file into dict
    jsonDict = {}
    with open("config.json", 'r') as jsonFile:
        jsonDict = json.load(jsonFile)

    # Get parameters from arguments
    for arg in args:
        try: 
            parameters.append( jsonDict[arg] )
        except KeyError: 
            raise KeyError(f"JSON parameter {arg} does not exist.")

    return parameters


class Aimer:
    
    def __init__(self, name, fov, clen) -> None:

        # Setup Camera Parameters
        self.name = name
        self.fov = fov 
        self.clen = clen

        # Display parameters
        print(
            "-"*15, "\n"
            "Aimer init\n"
            f"  - Name: {name}\n"
            f"  - Field of View: {fov}\n"
            f"  - clen: {clen}\n",
            "-"*15, "\n",
            sep=''
        )

    def get_angle(self, point):
        f = self.fov
        p = point 
        l = self.clen 

        t = (l * f - 2 * p * f) / (2 * l)

        return round(t, 2)

class Rectangle:
    def __init__(self, w=0, h=0, x=0, y=0) -> None:
        self.w = w 
        self.h = h 
        self.x = x 
        self.y = y

    def set(self, x, y, w, h):
        self.w = w
        self.h = h
        self.x = x
        self.y = y

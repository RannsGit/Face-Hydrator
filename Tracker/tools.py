"""
Misc tools for face detection.

Kyle Tennison
October 10, 2022
"""

DEBUG = True

import json
from datetime import datetime

# Open log into memory
log = open('log.txt', 'w')

def debug(note, color='') -> None:
    """Colored print for debug"""

    # Do nothing when debug is disabled
    if not DEBUG: return

    # Get color
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

    # Print with color
    print(f"{code[0]}{note}{code[1]}")

    # Log to log.txt
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


class Rectangle:
    """Stores position and size attributes for rectangular objects."""
    def __init__(self, w=0, h=0, x=0, y=0) -> None:
        self.w = w 
        self.h = h 
        self.x = x 
        self.y = y

    def set(self, x, y, w, h) -> None:
        """Bulk set attributes."""
        self.w = w
        self.h = h
        self.x = x
        self.y = y

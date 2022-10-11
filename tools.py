"""
Misc tools for face detection.

Kyle Tennison
October 10, 2022
"""

DEBUG = True


from datetime import datetime

log = open('log.txt', 'w')

def debug(note, color=''):

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
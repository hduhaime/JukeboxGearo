

# import os
# os.environ['SDL_AUDIODRIVER'] = 'pulse'

import code
import time
import threading

# pipenv shell

import serial
import pygame
import time

ser = serial.Serial('COM4', 9600, timeout=1)
time.sleep(3)
ser.flushInput()
print("Go")
try:
    while True:
        inString = input()
        ser.write(bytearray(inString, 'ascii'))


except KeyboardInterrupt:
    ser.close()
    exit(0)


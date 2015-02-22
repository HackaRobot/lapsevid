#!/usr/bin/python

# This script runs inside the RPi and listens for rover commands.
# It also takes pictures and uploads to URL.

import RPi.GPIO as GPIO
import time
import atexit
import fileinput
import re
import SocketServer
import ConfigParser
import sys
import picamera
import pqtimer

def right(duration):
    print "Right turn"
    enable()
    GPIO.output(PIN_RIGHT_FWD, False)
    GPIO.output(PIN_RIGHT_REV, False)
    GPIO.output(PIN_LEFT_FWD, True)
    GPIO.output(PIN_LEFT_REV, False)
    time.sleep(duration)
    stop()
    disable()

def forward(duration, trim = None):
    print "Forward"
    enable()
    GPIO.output(PIN_LEFT_FWD, True)
    GPIO.output(PIN_LEFT_REV, False)
    GPIO.output(PIN_RIGHT_FWD, True)
    GPIO.output(PIN_RIGHT_REV, False)
    time.sleep(duration)
    disable()

def left(duration):
    print "Left turn"
    enable()
    GPIO.output(PIN_RIGHT_FWD, True)
    GPIO.output(PIN_RIGHT_REV, False)
    GPIO.output(PIN_LEFT_FWD, False)
    GPIO.output(PIN_LEFT_REV, False)
    time.sleep(duration)
    stop()
    disable()

def reverse(duration):
    print "Reverse"
    GPIO.output(PIN_LEFT_FWD, False)
    GPIO.output(PIN_LEFT_REV, True)
    GPIO.output(PIN_RIGHT_FWD, False)
    GPIO.output(PIN_RIGHT_REV, True)
    time.sleep(duration)

def stop():
    print "Stop"
    GPIO.output(PIN_LEFT_FWD, False)
    GPIO.output(PIN_LEFT_REV, False)
    GPIO.output(PIN_RIGHT_FWD, False)
    GPIO.output(PIN_RIGHT_REV, False)

def enable():
    GPIO.output(PIN_ENABLE, True)

def disable():
    GPIO.output(PIN_ENABLE, False)

def cleanup():
    print "Cleaning up"
    GPIO.cleanup()

def snap(cam, imgfile):
    #print "Capturing to " + imgfile
    cam.capture(imgfile)

class snap_event (pqtimer.timed_event):
    def __init__(self, interval, cam):
        pqtimer.timed_event.__init__(self, "SNAPEVT", interval)
        self.cam = cam
        self.counter = 0

    def fire(self):
        print "SNAP  at ", time.time()
        imgfile = "{0}/capture{1:05}.png".format(CAPTURE_DIR, self.counter)
        snap(self.cam, imgfile)
        self.counter += 1

class crawl_event (pqtimer.timed_event):
    def __init__(self, interval, skip = 100):
        pqtimer.timed_event.__init__(self, "CRAWLEVT", interval)
        self.skip = skip
        self.counter = 0
        self.skip = skip

    def fire(self):
        global TURN
        print "CRAWL at ", time.time()
        if TURN == 0:
            forward(0.1)
        elif (self.counter % abs(TURN)) == 0:
            if TURN < 0:
                left(0.1)
            else:
                right(0.1)
        else:
            forward(0.1)

        self.counter += 1
        
######################  Begin main #################################
if len(sys.argv) != 2:
    raise RuntimeError("syntax: lapsevid.py configfile")

config = ConfigParser.RawConfigParser()
config.read(sys.argv[1])

PIN_LEFT_FWD = config.getint('RPI', 'PIN_LEFT_FWD')
PIN_RIGHT_FWD = config.getint('RPI', 'PIN_RIGHT_FWD')
PIN_LEFT_REV = config.getint('RPI', 'PIN_LEFT_REV')
PIN_RIGHT_REV = config.getint('RPI', 'PIN_RIGHT_REV')
PIN_ENABLE = config.getint('RPI', 'PIN_ENABLE')

# CAPTURE params
CAPTURE_DIR = config.get('CAPTURE', 'CAPTURE_DIR')
CAPTURE_MINS = config.getint('CAPTURE', 'CAPTURE_MINS')
VIDEO_SECONDS = config.getint('CAPTURE', 'VIDEO_SECONDS')
CRAWL_TIME = config.getfloat('CAPTURE', 'CRAWL_TIME')
FPS = config.getfloat('CAPTURE', 'FPS')
NMOVES = config.getfloat('CAPTURE', 'NMOVES')
TURN = config.getint('CAPTURE', 'TURN')

endtime = time.time() + CAPTURE_MINS * 60
crawltime = CRAWL_TIME
# 1 frame taken in this many seconds
frameperiod = CAPTURE_MINS * 60 / (VIDEO_SECONDS * FPS)
if NMOVES > 0:
    moveperiod = CAPTURE_MINS * 60 / NMOVES
else:
    moveperiod = 100000 # Some large but finite number
print "moveperiod=", moveperiod
print "frameperiod=", frameperiod

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN_LEFT_FWD, GPIO.OUT)
GPIO.setup(PIN_LEFT_REV, GPIO.OUT)
GPIO.setup(PIN_RIGHT_FWD, GPIO.OUT)
GPIO.setup(PIN_RIGHT_REV, GPIO.OUT)
GPIO.setup(PIN_ENABLE, GPIO.OUT)
atexit.register(cleanup)

timer = pqtimer.pytimer()
with picamera.PiCamera() as cam:
    cam.resolution = (1024, 768)
    cam.vflip = True
    cam.hflip = True
    evt = snap_event(frameperiod, cam)
    evt2 = crawl_event(moveperiod, 5) # Right turn every 5 moves
    timer.enqueue(evt2)
    timer.enqueue(evt)
    while time.time() < endtime:
        timer.next()

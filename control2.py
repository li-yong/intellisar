#!/usr/bin/env python
import curses
import time
import RPi.GPIO as GPIO

# Declare the GPIO settings
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(True)

PIN_EN = 40
PIN_PWM_L = 12
PIN_PWM_R = 11

PIN_R_DIR = 7
PIN_L_DIR = 15

channel_list = [PIN_EN, PIN_R_DIR, PIN_L_DIR, PIN_PWM_L,PIN_PWM_R]
GPIO.setup(channel_list, GPIO.OUT)

#20K hz
pl = GPIO.PWM(PIN_PWM_L, 20000)
pr = GPIO.PWM(PIN_PWM_R, 20000)

    
def init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(channel_list, GPIO.OUT)
    GPIO.output(channel_list, GPIO.LOW)


def speed(l,r):
    pl.stop()
    pr.stop()
    
    pl.start(l)
    pr.start(r)
    print("speed "+str(l)+str(r))




def forward(l=10,r=10):
    GPIO.output(PIN_EN, GPIO.HIGH)
    GPIO.output([PIN_L_DIR, PIN_R_DIR], GPIO.LOW)
    print("forward")
    speed(l,r)

def backward(l=10,r=10):
    GPIO.output(PIN_EN, GPIO.HIGH)
    GPIO.output([PIN_L_DIR, PIN_R_DIR], GPIO.HIGH)
    print("backward")
    speed(l,r)


def turn_left(l=30,r=30):
    GPIO.output(PIN_EN, GPIO.HIGH)
    GPIO.output(PIN_R_DIR, GPIO.LOW)
    GPIO.output(PIN_L_DIR, GPIO.HIGH)
    #time.sleep(0.5)
    #GPIO.output(PIN_EN, GPIO.LOW)
    print("turn left")
    speed(l,r)
    
def turn_right(l=30,r=30):
    GPIO.output(PIN_EN, GPIO.HIGH)
    GPIO.output(PIN_R_DIR, GPIO.HIGH)
    GPIO.output(PIN_L_DIR, GPIO.LOW)
    #time.sleep(0.5)
    #GPIO.output(PIN_EN, GPIO.LOW)
    print("turn right")
    speed(l,r)
 
def break_stop():
    pl.stop()
    pr.stop()

def detach():
    GPIO.output(PIN_EN, GPIO.LOW)

def restore():
    GPIO.cleanup()
    
def reset():
    restore()
    init()
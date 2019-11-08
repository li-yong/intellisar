#!/usr/bin/env python
import curses
import time
import RPi.GPIO as GPIO

PIN_EN = 40
PIN_PWM = 12

PIN_R_DIR = 7
PIN_L_DIR = 15


channel_list = [PIN_EN, PIN_R_DIR, PIN_L_DIR, PIN_PWM]


# Declare the GPIO settings
GPIO.setmode(GPIO.BOARD)
GPIO.setup(channel_list, GPIO.OUT)
GPIO.output(channel_list, GPIO.LOW)

p = GPIO.PWM(PIN_PWM, 100)
p.start(50) #  ==  p.ChangeDutyCycle(100)

def speed(x):
    p.stop()
    p.start(x)



def speed_100():
    p.stop()
    p.start(100)


def speed_50():
    p.stop()
    p.start(50)


def speed_10():
    p.stop()
    p.start(10)

def forward():
    GPIO.output(PIN_EN, GPIO.HIGH)
    GPIO.output([PIN_L_DIR, PIN_R_DIR], GPIO.LOW)

def backward():
    GPIO.output(PIN_EN, GPIO.HIGH)
    GPIO.output([PIN_L_DIR, PIN_R_DIR], GPIO.HIGH)

def turn_left():
    speed(30)
    GPIO.output(PIN_EN, GPIO.HIGH)
    GPIO.output(PIN_R_DIR, GPIO.LOW)
    GPIO.output(PIN_L_DIR, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(PIN_EN, GPIO.LOW)
    speed(10)
    
def turn_right():
    speed(30)
    GPIO.output(PIN_EN, GPIO.HIGH)
    GPIO.output(PIN_R_DIR, GPIO.HIGH)
    GPIO.output(PIN_L_DIR, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(PIN_EN, GPIO.LOW)
    speed(10)
 
def break_stop():
    p.stop()

def detach():
    GPIO.output(PIN_EN, GPIO.LOW)

def restore():
    GPIO.cleanup()
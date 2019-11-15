#!/usr/bin/env python
import curses
import time
import RPi.GPIO as GPIO
import logging

# Declare the GPIO settings
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(True)

PIN_EN = 40


PIN_R_DIR = 7
PIN_L_DIR = 15

channel_list = [PIN_EN, PIN_R_DIR, PIN_L_DIR]
GPIO.setup(channel_list, GPIO.OUT)

    
GPIO.setmode(GPIO.BOARD)
GPIO.setup(channel_list, GPIO.OUT)
GPIO.output(channel_list, GPIO.LOW)
print("PIN_EN "+str(PIN_EN)+" 0")

GPIO.output(PIN_EN, GPIO.HIGH)
GPIO.output([PIN_L_DIR, PIN_R_DIR], GPIO.HIGH)

en=GPIO.input(PIN_EN)
l=GPIO.input(PIN_L_DIR)
r=GPIO.input(PIN_R_DIR)
print("car EXPECT, PIN_EN "+str(PIN_EN)+":"+str(1)+" , PIN_L_DIR "+str(PIN_L_DIR)+":"+str(1)+", PIN_R_DIR "+str(PIN_R_DIR)+":"+str(1))
print("car ACTUAL, PIN_EN "+str(PIN_EN)+":"+str(en)+" , PIN_L_DIR "+str(PIN_L_DIR)+":"+str(l)+", PIN_R_DIR "+str(PIN_R_DIR)+":"+str(r))

time.sleep(5)
GPIO.cleanup()


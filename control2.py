#!/usr/bin/env python
import curses
import time
import RPi.GPIO as GPIO
import logging

# Declare the GPIO settings
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(True)

PIN_EN = 40
PIN_PWM_L = 12
PIN_PWM_R = 11

PIN_R_DIR = 7
PIN_L_DIR = 15

PIN_CAM_H = 35
PIN_CAM_V = 33


H_Low_Degree = 90-45
H_High_Degree = 90+45

V_Low_Degree = 90-45
V_High_Degree = 90+45

channel_list = [PIN_EN, PIN_R_DIR, PIN_L_DIR, PIN_PWM_L,PIN_PWM_R,PIN_CAM_H,PIN_CAM_V]

GPIO.setup(channel_list, GPIO.OUT)

#20K hz
pl = GPIO.PWM(PIN_PWM_L, 20000)
pr = GPIO.PWM(PIN_PWM_R, 20000)


logging.basicConfig(
    #filename='control2.log', filemode='w',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
    
    
    
def init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(channel_list, GPIO.OUT)
    GPIO.output(channel_list, GPIO.LOW)
    logging.info("PIN_EN "+str(PIN_EN)+" 0")



def speed(l,r):
    pl.stop()
    pr.stop()
    
    pl.start(l)
    pr.start(r)
    logging.info("speed "+str(l)+" "+str(r))




def forward(l=10,r=10):
    GPIO.output(PIN_EN, GPIO.HIGH)
    GPIO.output([PIN_L_DIR, PIN_R_DIR], GPIO.LOW)
    logging.info("forward, PIN_EN "+str(PIN_EN)+":1 , PIN_L_DIR "+str(PIN_L_DIR)+":0, PIN_R_DIR "+str(PIN_R_DIR)+":0")
    speed(l,r)

def backward(l=10,r=10):
    GPIO.output(PIN_EN, GPIO.HIGH)
    GPIO.output([PIN_L_DIR, PIN_R_DIR], GPIO.HIGH)
    logging.info("backward, PIN_EN "+str(PIN_EN)+":1 , PIN_L_DIR "+str(PIN_L_DIR)+":1, PIN_R_DIR "+str(PIN_R_DIR)+":1")
    speed(l,r)


def turn_left(l=30,r=30):
    GPIO.output(PIN_EN, GPIO.HIGH)
    GPIO.output(PIN_R_DIR, GPIO.LOW)
    GPIO.output(PIN_L_DIR, GPIO.HIGH)
    time.sleep(0.5) #90/4 = 22 degree 
    #time.sleep(1) #90 degree 
    GPIO.output(PIN_EN, GPIO.LOW)
    logging.info("turn left, PIN_EN "+str(PIN_EN)+":1 , PIN_L_DIR "+str(PIN_L_DIR)+":1, PIN_R_DIR "+str(PIN_R_DIR)+":0")
    speed(l,r)
    
def turn_right(l=30,r=30):
    GPIO.output(PIN_EN, GPIO.HIGH)
    GPIO.output(PIN_R_DIR, GPIO.HIGH)
    GPIO.output(PIN_L_DIR, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(PIN_EN, GPIO.LOW)
    logging.info("turn right, PIN_EN "+str(PIN_EN)+":1 , PIN_L_DIR "+str(PIN_L_DIR)+":0, PIN_R_DIR "+str(PIN_R_DIR)+":1")
    speed(l,r)
 
def break_stop():
    pl.stop()
    pr.stop()
    logging.info("stop")

def detach():
    GPIO.output(PIN_EN, GPIO.LOW)
    logging.info("Disabled PIN_EN "+str(PIN_EN))

def restore():
    GPIO.cleanup()
    logging.info("GPIO cleanup")
    
def reset():
    logging.info("reset")
    restore()
    init()
    
#Camera movement
def servo_pulse(serve_pin, angle):
    pulsewidth = (angle * 11) + 500
    GPIO.output(serve_pin, GPIO.HIGH)
    time.sleep(pulsewidth/1000000.0)
    GPIO.output(serve_pin, GPIO.LOW)
    time.sleep(20.0/1000-pulsewidth/1000000.0)
    
def cam_left_step():
    cam_enable()
    servo_pulse(PIN_CAM_H, 10)
        
def cam_right_step():
    cam_enable()
    servo_pulse(PIN_CAM_H, 10)
        
def cam_up_step():
    cam_enable()
    servo_pulse(PIN_CAM_V, 10)
        
def cam_down_step():
    cam_enable()
    servo_pulse(PIN_CAM_V, -10)
    
    
def cam_left():
    cam_enable()
    for pos in range(H_Low_Degree,H_High_Degree):
        servo_pulse(PIN_CAM_H, pos)
        time.sleep(0.01) 
            
def cam_right():
    cam_enable()
    for pos in reversed(range(H_Low_Degree,H_High_Degree)):
        servo_pulse(PIN_CAM_H, pos)
        time.sleep(0.01) 

def cam_h_patrol():
    #while(1):
    for i in range(1):
        cam_left()
        time.sleep(1)
        cam_right()
        time.sleep(1)

        
def cam_up():
    cam_enable()
    for pos in range(V_Low_Degree,V_High_Degree):
        servo_pulse(PIN_CAM_V, pos)
        time.sleep(0.01) 
            
def cam_down():
    cam_enable()
    #for pos in reversed(range(40,181)):
    for pos in reversed(range(V_Low_Degree,V_High_Degree)):
        servo_pulse(PIN_CAM_V, pos)
        time.sleep(0.01) 
        
def cam_v_patrol():
    #while(1):
    for i in range(1):
        cam_up()
        time.sleep(1)
        cam_down()
        time.sleep(1)         
        
def cam_stop():
    GPIO.output(PIN_CAM_H, GPIO.LOW)
    GPIO.output(PIN_CAM_V, GPIO.LOW)
                    
def cam_enable():
    pass
    #GPIO.output(PIN_CAM_H, GPIO.HIGH)
    #GPIO.output(PIN_CAM_V, GPIO.HIGH)
                    
def cam_position_reset():
    cam_enable()
    for i in range(10):
        servo_pulse(PIN_CAM_H, 90)
        servo_pulse(PIN_CAM_V, 90)
    logging.info("cam_position_reset")
           
#Libraries
import RPi.GPIO as GPIO
import time
import control2 as ctl
 
STOP_DISTANCE = 30
IS_MOVING = True
GPIO.setmode(GPIO.BOARD)

PIN_EN = 40
GPIO.setup(PIN_EN, GPIO.OUT)

#PIN_PWM_L = 12
#PIN_PWM_R = 11
#GPIO.setup(PIN_PWM_L, GPIO.OUT)
#GPIO.setup(PIN_PWM_R, GPIO.OUT)

#PIN_R_DIR = 7
#PIN_L_DIR = 15
#GPIO.setup(PIN_R_DIR, GPIO.OUT)
#GPIO.setup(PIN_L_DIR, GPIO.OUT)

######### UltraSonic sensor #######
#set GPIO Pins
GPIO_TRIGGER = 36  #physical 36, BCM 16, GPIO.27
GPIO_ECHO = 38     #physical 38, BCM 20, GPIO.28

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.output(GPIO_TRIGGER,  GPIO.LOW)

######### Infrared  sensor #######
PIN_INF_L = 29
PIN_INF_R = 31
GPIO.setup(PIN_INF_L, GPIO.IN)
GPIO.setup(PIN_INF_R, GPIO.IN)

print ("Waiting for sensor to settle")
time.sleep(2)
 
def measure():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER,  GPIO.HIGH) 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER,  GPIO.LOW)
 
    #StartTime = time.time()
    #StopTime = time.time()
   
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
        #StopTime = StartTime
        #print("echo pin == 0, start time "+str(StartTime))
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
        #print("echo pin == 1, stop time "+str(StopTime))
        
    #if (StopTime == StartTime):
    #    print("EXP: STOP=START")
    #    return(0)

 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    #print("str "+str(StartTime))
    #print("end "+str(StopTime))    
    #print("TimeElapsed "+str(TimeElapsed))    
    #print(" ")
    
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    #distance = (TimeElapsed * 34300) / 2
    distance = round(TimeElapsed * 17150, 2)
 
    return distance
    
def measure_average():

  # This function takes 3 measurements and
  # returns the average.
  #distance1=measure()
  #time.sleep(0.1)
  #distance2=measure()
  #time.sleep(0.1)
  #distance3=measure()
  #distance = distance1 + distance2 + distance3
  #distance = distance / 3
  #return distance    
  return measure()    
 
if __name__ == '__main__':
    try:
        BACKWARDING = False #whether the car is moving backwards
        
        while True:
            dist = measure_average()
            #print ("Measured Distance = %.1f cm" % dist)
            #time.sleep(0.1) 
            #time.sleep(0.5) 
            time.sleep(1) 

            if dist < STOP_DISTANCE:
                allow_straight = False
            else:
                allow_straight = True

            
            allow_turn_left = GPIO.input(PIN_INF_L);
            allow_turn_right = GPIO.input(PIN_INF_R);
            
            print(
                "allow_straight " +str(allow_straight) 
                +"  allow_turn_right " +str(allow_turn_right)
                +"  allow_turn_left " +str(allow_turn_left))
            
            if (not BACKWARDING):#moving forward
                if allow_turn_right:
                    ctl.turn_right()
                elif allow_straight:
                    ctl.forward()
                elif allow_turn_left:
                    ctl.turn_left()
                else:
                    #turn 180 degreens back.
                    ctl.backward()
                    BACKWARDING=True
            else: #moving backward
                if allow_turn_left:
                    ctl.turn_left()
                    ctl.forward()
                    BACKWARDING=False
                elif allow_turn_right:
                    ctl.turn_right()
                    ctl.forward()
                    BACKWARDING=False
                else:
                    pass


            '''
            if (not allow_straight) and IS_MOVING and (GPIO.input(PIN_EN) == 1):        
                GPIO.output(PIN_EN, GPIO.LOW)
                IS_MOVING = False
                print("less "+str(STOP_DISTANCE)+", stop")
            elif allow_straight and (not IS_MOVING) and (GPIO.input(PIN_EN) == 0):
                GPIO.output(PIN_EN, GPIO.HIGH)
                IS_MOVING = True
                print("more than "+str(STOP_DISTANCE)+", moving")
            else:
                pass
            '''
            
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
#Libraries
import RPi.GPIO as GPIO
import time
import control2 as ctl
import logging


STOP_DISTANCE = 30
IS_MOVING = True
GPIO.setmode(GPIO.BOARD)

#PIN_EN = 40
#GPIO.setup(PIN_EN, GPIO.OUT)

logging.basicConfig(
    filename='us4.log', filemode='w', 
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO, 
    datefmt='%Y-%m-%d %H:%M:%S')
    

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


def measure():
  # This function measures a distance
  MAX_TIME = 0.04 # max time waiting for response in case something is missed
  # Pulse the trigger/echo line to initiate a measurement
  GPIO.output(GPIO_TRIGGER, True)
  time.sleep(0.00001)
  GPIO.output(GPIO_TRIGGER, False)
  #ensure start time is set in case of very quick return
  start = time.time()
  timeout = start + MAX_TIME

  # set line to input to check for start of echo response
  #GPIO.setup(GPIO_ECHO, GPIO.IN) 
  while GPIO.input(GPIO_ECHO)==0:
    if (start <= timeout): # At max wait MAX_TIME sec in case missed the 0.
        start = time.time()
    else:
        logging.info("start timeout. start "+str(start)+" timeout "+str(timeout) )
        break
  
  stop = time.time()
  timeout = stop + MAX_TIME
  # Wait for end of echo response
  while GPIO.input(GPIO_ECHO)==1:
    if (stop <= timeout):
        stop = time.time()
    else:
        logging.info("stop timeout")
        break
  
  #GPIO.setup(GPIO_TRIGECHO, GPIO.OUT)
  #GPIO.output(GPIO_TRIGECHO, False)

  elapsed = stop-start
  distance = round(elapsed * 17150, 2)
  #time.sleep(0.02)
  return distance
  

#measure without timeout. Cause high CPU loading.
def measure_del():
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
  #return measure_del()    
 
if __name__ == '__main__':
    logging.info("Waiting for sensor to settle")
    time.sleep(2)
    #ctl.forward(1,1)

    try:
        BACKWARDING = 0 #whether the car is moving backwards
        FORWARDING = 1
        TURNR = 0
        TURNL = 0
        
        while True:
            dist = measure_average()
            logging.info ("Measured Distance = %.1f cm" % dist)
            time.sleep(0.1)

            if dist < STOP_DISTANCE:
                allow_straight = 0
            else:
                allow_straight = 1

            time.sleep(0.5) 
            allow_turn_left = GPIO.input(PIN_INF_L);
            allow_turn_right = GPIO.input(PIN_INF_R);
            
            logging.info(
                "allow_straight " +str(allow_straight) 
                +"  allow_turn_right " +str(allow_turn_right)
                +"  allow_turn_left " +str(allow_turn_left))
                
            logging.info("FORWARDING:"+str(FORWARDING)+" TURNL:"+str(TURNL)+" TURNR:"+str(TURNR)+" BACKWARDING:"+str(BACKWARDING))
            
            if FORWARDING:#moving forward
                if allow_straight: #keep forward 
                    if (TURNR or TURNL): #change to forward if it was from forward->turn
                        ctl.forward(1,1)
                        TURNL = 0
                        TURNR = 0
                elif allow_turn_right: #turn whenever allowed, right first. After turn, speed at 1,1
                    #tl=30,tr=30,t=0.5,al=1,ar=1
                    ctl.turn_right(30,30,2,1,1)
                    TURNR = 1; 
                elif allow_turn_left: #turn left when allowed. After turn, speed at 1,1
                    ctl.turn_left(30,30,2,1,1)
                    TURNL = 1
                else:  #was moving forward, not allow straight, right and left. Turn 180 degreens back.
                    ctl.backward(1,1)
                    BACKWARDING=1
                    FORWARDING=0
            
            if BACKWARDING: #moving backward
                if allow_turn_left:
                    time.sleep(3) #wait the robot head out of the block
                    ctl.turn_left(30,30,2,1,1)
                    ctl.forward(1,1)
                    BACKWARDING=0
                    FORWARDING=1
                elif allow_turn_right:
                    time.sleep(3) #wait the robot head out of the block
                    ctl.turn_right(30,30,2,1,1)
                    ctl.forward(1,1)
                    BACKWARDING=0
                    FORWARDING=1
                else:
                    pass
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")

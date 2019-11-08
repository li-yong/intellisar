#Libraries
import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BOARD)
#GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 36  #physical 36, BCM 16, GPIO.27
GPIO_ECHO = 38     #physical 38, BCM 20, GPIO.28

#GPIO_TRIGGER = 16  #physical 36, BCM 16, GPIO.27
#GPIO_ECHO = 20     #physical 38, BCM 20, GPIO.28

#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.output(GPIO_TRIGGER,  GPIO.LOW)

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
  distance1=measure()
  time.sleep(0.001)
  distance2=measure()
  time.sleep(0.001)
  distance3=measure()
  distance = distance1 + distance2 + distance3
  distance = distance / 3
  return distance    
 
if __name__ == '__main__':
    try:
        while True:
            dist = measure_average()
            print ("Measured Distance = %.1f cm" % dist)
            time.sleep(0.1) 
            
            #if (dist != 0):
            #    print ("Measured Distance = %.1f cm" % dist)
            #    time.sleep(1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
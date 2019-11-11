'''
    Raspberry Pi GPIO Status and Control
'''
import RPi.GPIO as GPIO
from flask import Flask, render_template, request,Response
from flask_socketio import SocketIO, send, emit

import control2 as ctl
import dht11
import time
import datetime

#rom camera_pi import Camera


app = Flask(__name__)

socketio = SocketIO(app)


#GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(True)

#define sensors GPIOs
enabler = 40 # enabler
right = 7 # right_dir
#define actuators GPIOs
left = 15  #left dir

'''
def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
'''

def readtmper():
    rtn = {
        'time': 0,
        'temp': 0,
        'humi': 0
    }
    instance = dht11.DHT11(pin=16)


    while True:
       # time.sleep(1)

        result = instance.read()

        if result.is_valid():
            itime = str(datetime.datetime.now())
            #print("Last valid input: " + itime)

            #print("Temperature: %-3.1f C" % result.temperature)
            #print("Humidity: %-3.1f %%" % result.humidity)

            rtn = {
                'time': itime,
                'temp': result.temperature,
                'humi': result.humidity
            }

            break

    return(rtn)


def readsensor():
    enablerSts = 0
    leftSts = 0
    rightSts = 0
    forwardSts = 0
    backwardSts = 0

    # Read GPIO Status
    enablerSts = GPIO.input(enabler)
    rightV= GPIO.input(right)
    leftV = GPIO.input(left)
 
           
    if(rightV == 0) and (leftV == 0) and (enablerSts ==1 ):
        forwardSts = 1        
        
    if(rightV == 1) and (leftV == 1) and (enablerSts ==1 ):
        backwardSts = 1
    
    if(rightV == 0) and (leftV == 1) and (enablerSts ==1 ):
        leftSts = 1
    
        
    if(rightV == 1) and (leftV == 0) and (enablerSts ==1 ):
        rightSts = 1
    
   
    templateData = {
      'enablerSts'  : enablerSts,
      'rightSts'  : rightSts,
      'leftSts'  : leftSts,
      'forwardSts'  : forwardSts,
      'backwardSts'  : backwardSts,
    }
    return(templateData)
    
@app.route("/temp")
def temp_index():
    templateData = readtmper()
    return render_template("temp.html", **templateData)

@socketio.on('update_event')
def on_update_event(data):
    print("server received update request.")
    templateData = readtmper()
    send(templateData)
    print("server sent update request"+str(templateData))
    emit('receiveSensorData', templateData)

@socketio.on('connect')
def on_connect():
    print("Client connected ")

'''
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
'''

@app.route("/motor")
def motor_index():
    #templateData = readsensor()
    ctl.reset()
    return  render_template('motor.html')

# The function below is executed when someone requests a URL with the actuator name and action in it:
@app.route("/<deviceName>/<action>")
def action(deviceName, action):

    if action == "fwd":
        ctl.forward()
    if action == "bwd":
        ctl.backward()
    if action == "left":
        ctl.turn_left()
    if action == "right":
        ctl.turn_right()
    if action == "stop":
        ctl.detach()
    if action == "reset":
        ctl.reset()
    if action == "speed100":
        ctl.speed(100,100)
    if action == "speed50":
        ctl.speed(50,50)
    if action == "speed10":
        ctl.speed(10,10)
    return '', 204

    #templateData = readsensor()
    #return  render_template('motor.html', **templateData)
             
@app.route("/")
def index():
    return  render_template('index.html')


if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=True)
   #socketio.run(app)

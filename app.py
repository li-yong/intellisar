'''
    Raspberry Pi GPIO Status and Control
'''
import RPi.GPIO as GPIO
from flask import Flask, render_template, request,Response,jsonify
from flask_socketio import SocketIO, send, emit

import control2 as ctl
import dht11
import time
import datetime
import logging


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



logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s', 
    level=logging.INFO,filename='app.log',
    datefmt='%Y-%m-%d %H:%M:%S')


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
            #logging.info("Last valid input: " + itime)

            #logging.info("Temperature: %-3.1f C" % result.temperature)
            #logging.info("Humidity: %-3.1f %%" % result.humidity)

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
    
@app.route("/temp0")
def temp_index0():
    templateData = readtmper()
    return render_template("temp0.html", **templateData)

@socketio.on('update_event')
def on_update_event(data):
    logging.info("server received update request.")
    templateData = readtmper()
    send(templateData)
    logging.info("server sent update request"+str(templateData))
    emit('receiveSensorData', templateData)

@socketio.on('connect')
def on_connect():
    logging.info("Client connected ")

'''
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
'''


@app.route("/test", methods=['GET', 'POST'])
def test():
   ts2 = time.time()
   ts2a = datetime.datetime.timestamp(datetime.datetime.now())
   ts2b = datetime.datetime.now()
   
   data =  request.form
   
   sequence = data['sequence']
   distance = data['distance']
   ts1 = data['ts1']
   ts1a = data['ts1a']
   ts1b = data['ts1b']

   print('sequence '+sequence)
   print('distance '+distance)
   print('ts1 '+ts1)
   print('ts1a '+ts1a)
   
   ts3 = time.time()
   ts3a = datetime.datetime.timestamp(datetime.datetime.now())
   ts3b = datetime.datetime.now()
   #rects = datetime.datetime.timestamp(datetime.datetime.now())
   delts = ts2 - float(ts1)
   
   print('I am Server. Seq '+sequence+'client sent at ts1 '+ts1+", server received at ts2 "+str(ts2)+", server responsed at ts3 "+str(ts3)+', delta ts_12 '+str(delts))
   #time.sleep(2)
   
   return jsonify({'ts1':ts1, 'ts1a':ts1a,  'ts1b':ts1b, 'ts2':ts2, 'ts3':ts3 , 'ts2a':ts2a, 'ts3a':ts3a , 'ts2b':ts2b, 'ts3b':ts3b }), 200


@app.route("/motor")
def motor_index():
    #templateData = readsensor()
    #ctl.reset()
    return  render_template('motor.html')

# The function below is executed when someone requests a URL with the actuator name and action in it:
@app.route("/<deviceName>/<action>")
def action(deviceName, action):
    if (deviceName == 'motor'):
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
    elif (deviceName=='cam'):
        if action == "up":
            ctl.cam_up()
        if action == "down":
            ctl.cam_down_step()
        if action == "left":
            ctl.cam_left()
        if action == "right":
            ctl.cam_right_step()
        if action == "stop":
            ctl.cam_stop()
        if action == "reset":
            ctl.cam_position_reset() 
        if action == "h_patrol":
            ctl.cam_h_patrol()
        if action == "v_patrol":
            ctl.cam_v_patrol()
    return '', 204

    #templateData = readsensor()
    #return  render_template('motor.html', **templateData)
             
@app.route("/")
def index():
    #return  render_template('index.html')
    return  render_template('motor.html')


@app.route("/detection")
def detection():
    # Rendered template
    return render_template('detection.html')


if __name__ == "__main__":
    logging.info("program start")
    app.run(host='0.0.0.0', port=80, debug=True)
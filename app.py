'''
    Raspberry Pi GPIO Status and Control
'''
import RPi.GPIO as GPIO
from flask import Flask, render_template, request, Response,jsonify
from flask_socketio import SocketIO, send, emit

import control2 as ctl
import dht11
import time
import datetime
import logging

import threading
from threading import Thread
import argparse
import cv2
import numpy as np
import os
import importlib.util
from util.videostream import VideoStream

# If tensorflow is not installed, import interpreter from tflite_runtime, else import from regular tensorflow
pkg = importlib.util.find_spec('tensorflow')
if pkg is None:
    from tflite_runtime.interpreter import Interpreter
else:
    from tensorflow.lite.python.interpreter import Interpreter

# Define and parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument('--modeldir', help='Directory the .tflite and labelmap files are located in. Default: model',
                    default='model')
parser.add_argument('--graph', help='Name of the .tflite file. Default: detect.tflite',
                    default='detect.tflite')
parser.add_argument('--labels', help='Name of the labelmap file. Default: labelmap.txt',
                    default='labelmap.txt')
parser.add_argument('--threshold', help='Minimum confidence threshold for displaying detected objects. Default: 0.5',
                    default=0.5)
parser.add_argument('--resolution', help='Desired resolution (WxH). If camera does not support the resolution entered, errors may occur. Default: 640x480',
                    default='640x480')
parser.add_argument('--framerate', help='Desired framerate (FPS). If camera does not support the framerate entered, errors may occur. Default: 30',
                    default=30)
parser.add_argument('--codec', help='Desired video codec (FourCC code). If FourCC code does not exist or is not supported, errors may occur. Default: X264',
                    default='X264')
args = parser.parse_args()

# Parse resolution W and H
resW, resH = list(map(int, args.resolution.split('x')))

# Initialize the output frame and a lock used to ensure thread-safe exchanges of the output frames
outputFrame = None
lock = threading.Lock()

# Boolean for toggling object detection
detection_mode = True

# Initialize Flask object
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

# Initialize VideoStream
videostream = VideoStream(resolution=(resW, resH), framerate=args.framerate, codec=args.codec).start()
time.sleep(2.0)

def object_detection():
    # Grab global references
    global videostream, outputFrame, lock, args, resW, resH, detection_mode

    # Path to .tflite file, which contains the model that is used for object detection
    PATH_TO_TFLITE = os.path.join(os.getcwd(), args.modeldir, args.graph)

    # Path to label map file
    PATH_TO_LABELMAP = os.path.join(os.getcwd(), args.modeldir, args.labels)

    # Load the label map
    with open(PATH_TO_LABELMAP, 'r') as f:
        labels = [line.strip() for line in f.readlines()]

    # If using the COCO "starter model" from https://www.tensorflow.org/lite/models/object_detection/overview
    # Have to remove '???' label
    if labels[0] == '???':
        del(labels[0])

    # Load the Tensorflow Lite model and get details
    interpreter = Interpreter(model_path=PATH_TO_TFLITE)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]

    floating_model = (input_details[0]['dtype'] == np.float32)

    input_mean = 127.5
    input_std = 127.5

    # Initialize frame rate calculation
    frame_rate_calc = 1
    freq = cv2.getTickFrequency()

    # Loop through frames from the video stream
    while True:
        if detection_mode:
            # Start timer (for calculating frame rate)
            t1 = cv2.getTickCount()

            # Grab frame from video stream
            frame1 = videostream.read()

            # Acquire frame and resize to expected shape [1xHxWx3]
            # frame = frame1.copy()
            frame = cv2.flip(frame1, -1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (width, height))
            input_data = np.expand_dims(frame_resized, axis=0)

            # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
            if floating_model:
                input_data = (np.float32(input_data) - input_mean) / input_std

            # Perform the actual detection by running the model with the image as input
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()

            # Retrieve detection results
            boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
            classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
            scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
            # num = interpreter.get_tensor(output_details[3]['index'])[0] # Total number of detected objects

            # Loop over all detections and draw detection box if confidence is above minimum threshold
            for i in range(len(scores)):
                if ((scores[i] > args.threshold) and (scores[i] <= 1.0)):
                    # Get bounding box coordinates and draw box
                    # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                    ymin = int(max(1, (boxes[i][0] * resH)))
                    xmin = int(max(1, (boxes[i][1] * resW)))
                    ymax = int(min(resH, (boxes[i][2] * resH)))
                    xmax = int(min(resW, (boxes[i][3] * resW)))
                    
                    cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

                    # Draw label
                    object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
                    label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
                    labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
                    label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                    cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
                    cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text

            # Draw detection status in top left corner of frame
            cv2.putText(frame,'Detection: ON', (1, 12), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 1, cv2.LINE_AA)
            # Draw framerate in top left corner of frame
            cv2.putText(frame,'FPS: {0:.2f}'.format(frame_rate_calc), (1, 24), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 1, cv2.LINE_AA)

            # Acquire the lock, set the output frame for generate(), and release the lock
            with lock:
                outputFrame = frame.copy()

            # Calculate framerate
            t2 = cv2.getTickCount()
            frame_rate_calc = 1 / ((t2 - t1) / freq)
        else:
            # Grab frame from video stream
            frame1 = videostream.read()
            frame = cv2.flip(frame1, -1)
            # Draw detection status in top left corner of frame
            cv2.putText(frame,'Detection: OFF', (1, 12), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 1, cv2.LINE_AA)
            # Draw framerate in top left corner of frame
            cv2.putText(frame,'FPS: {0:.2f}'.format(videostream.framerate()), (1, 24), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 1, cv2.LINE_AA)
            # Acquire the lock, set the output frame for generate(), and release the lock
            with lock:
                outputFrame = frame.copy()

def generate():
    # Grab global references to the output frame and lock variables
    global outputFrame, lock

    # Loop over frames from the output stream
    while True:
        # Wait until the lock is acquired
        with lock:
            # Check if the output frame is available, otherwise continue
            if outputFrame is None:
                continue

            # Encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode('.jpg', outputFrame)

            # Ensure frame was successfully encoded
            if not flag:
                continue

        # Yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

@app.route('/video_feed')
def video_feed():
    # Return the response generated along with the specific media type (mime type)
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

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

   #print('sequence '+sequence)
   #print('distance '+distance)
   #print('ts1 '+ts1)
   #print('ts1a '+ts1a)
   
   ts3 = time.time()
   ts3a = datetime.datetime.timestamp(datetime.datetime.now())
   ts3b = datetime.datetime.now()
   #rects = datetime.datetime.timestamp(datetime.datetime.now())
   delts = ts2 - float(ts1)
   
   #print('I am Server. Seq '+sequence+'client sent at ts1 '+ts1+", server received at ts2 "+str(ts2)+", server responsed at ts3 "+str(ts3)+', delta ts_12 '+str(delts))
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
    global detection_mode
    if (deviceName == 'motor'):
        if action == "fwd":
            ctl.forward(1,1)
        if action == "bwd":
            ctl.backward(1,1)
        if action == "left":
            ctl.turn_left(1,1)
        if action == "right":
            ctl.turn_right(1,1)
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
    elif (deviceName == 'cam'):
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
    elif (deviceName == 'detection'):
        # Toggle detection button
        if action == "toggle":
            detection_mode = not detection_mode
    return '', 204

    #templateData = readsensor()
    #return render_template('motor.html', **templateData)
             
@app.route("/")
def index():
    #return render_template('index.html')
    return render_template('motor.html')

if __name__ == "__main__":
    # Start a thread that will perform object detection
    t = threading.Thread(target=object_detection)
    t.daemon = True
    t.start()
    logging.info("Program start")
    app.run(host='0.0.0.0', port=80, debug=False, threaded=True)

# Stop videostream after Flask webserver is shut down
videostream.stop()

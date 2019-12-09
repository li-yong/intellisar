# Define VideoStream class to handle streaming of video from camera in separate processing thread
# Using a separate thread can help increase the FPS of the main pipeline

# https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/TFLite_detection_webcam.py
# https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/

import cv2
from threading import Thread

class VideoStream:
    def __init__(self, resolution=(640, 480), framerate=30, codec='X264'):
        # Initialize the PiCamera and the camera image stream
        self.stream = cv2.VideoCapture(0)

        # Set resolution
        ret = self.stream.set(3, resolution[0])
        ret = self.stream.set(4, resolution[1])

        # Set framerate
        ret = self.stream.set(cv2.CAP_PROP_FPS, framerate)

        # Specify video codec
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*codec))
            
        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()

    # Variable to control when the camera is stopped
        self.stopped = False

    def start(self):
        # Start the thread that reads frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Close camera resources
                self.stream.release()
                return

            # Otherwise, grab next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # Return the most recent frame
        return self.frame

    def stop(self):
        # Indicate that the camera and thread should be stopped
        self.stopped = True

    def framerate(self):
        # Return frame rate of camera
        return self.stream.get(cv2.CAP_PROP_FPS)
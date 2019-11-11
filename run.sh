sudo service uv4l_raspicam restart;
sleep 2;

pkill uv4l;
sleep 1;

uv4l --driver raspicam --auto-video_nr --object-detection --min-object-size 80 80 --main-classifier /usr/share/uv4l/raspicam/lbpcascade_frontalface.xml --object-detection-mode accurate_detection --width 320 --height 240 --framerate 15 --encoding h264;
sleep 2;

#curl  -o /dev/null http://localhost:8080 
#sleep 2;

#curl  -o /dev/null http://localhost:8080/stream
#sleep 2;
#curl  -o /dev/null http://localhost:8080/stream/video.mjpeg
#sleep 2;
#curl -r 0-20 -o /dev/null http://localhost:8080/stream/video.h264

sudo pkill python;
nohup python us4.py &

#sudo pkill python
sudo python app.py;


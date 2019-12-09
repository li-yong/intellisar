

#sudo service uv4l_raspicam restart;
#sleep 2;

#pkill uv4l;
#sleep 1;

#uv4l   --driver raspicam --auto-video_nr on  --object-detection --min-object-size 80 80 --main-classifier /usr/share/uv4l/raspicam/lbpcascade_frontalface.xml --object-detection-mode accurate_detection --width 640 --height 480 --framerate 5 --encoding h264;
#sleep 2;

sudo pkill python;

#nohup sudo python us4.py &

cd /home/pi/object-detection-intellisar &&  python  app.py &

cd /home/pi/intellisar && sudo python app.py


# IntelliSAR
- Raspberry Pi 4B (Raspbian Buster)
- Python 3.7
- OpenCV 4 (pip install is sufficient)
- Tensorflow 2

## OpenCV Setup
From: https://www.pyimagesearch.com/2019/09/16/install-opencv-4-on-raspberry-pi-4-and-raspbian-buster/
### Install Dependencies
```
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install build-essential cmake pkg-config
sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng-dev
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install libxvidcore-dev libx264-dev
sudo apt-get install libfontconfig1-dev libcairo2-dev
sudo apt-get install libgdk-pixbuf2.0-dev libpango1.0-dev
sudo apt-get install libgtk2.0-dev libgtk-3-dev
sudo apt-get install libatlas-base-dev gfortran
sudo apt-get install libhdf5-dev libhdf5-serial-dev libhdf5-103
sudo apt-get install libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5
sudo apt-get install python3-dev
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
sudo python3 get-pip.py
sudo rm -rf ~/.cache/pip
```
### Setup Virtual Environment
`sudo pip install virtualenv virtualenvwrapper`

Append the following lines to end of your ~/.bashrc file
```
# virtualenv and virtualenvwrapper
export WORKON_HOME=$HOME/.virtualenvs
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
source /usr/local/bin/virtualenvwrapper.sh
```
`source ~/.bashrc`

`mkvirtualenv [Insert Virtual Environment Name Here] -p python3`
### Install PiCamera API
`pip install "picamera[array]"`
### Install OpenCV
`sudo pip3 install opencv-contrib-python==4.1.0.25`

## Tensorflow Setup
```
wget https://github.com/lhelontra/tensorflow-on-arm/releases/download/v2.0.0/tensorflow-2.0.0-cp37-none-linux_armv7l.whl
sudo pip3 install --ignore-installed tensorflow-2.0.0-cp37-none-linux_armv7l.whl
rm tensorflow-2.0.0-cp37-none-linux_armv7l.whl
```

## How to Run
All dependencies should be set up in your virtual environment, so remember to enter your virtual environment with `workon [Virtual Environment Name]`

e.g. `workon intellisar`

`sudo python3 app.py`

Webserver located at http://localhost:80

### Optional Arguments
`sudo python3 app.py -h`

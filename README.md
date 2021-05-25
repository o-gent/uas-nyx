# Nyx, UAS Surrey team Peryton 2021

-> If you want to change code, make another branch and create a merge request so I can review the changes

Nyx co-ordinates the whole mission and the image recognition 

See nyx/main.py for the entry point into the program




## 1. tools & workflow

SFTP -> https://sourceforge.net/projects/winscp/ - load files to and from a remote computer over SSH

forwarding ports over SSH for jupyter notebook -> https://ljvmiranda921.github.io/notebook/2018/01/31/running-a-jupyter-notebook/
```
localuser@localhost: ssh -N -f -L localhost:YYYY:localhost:XXXX remoteuser@remotehost
```

Ardupilot SITL -> https://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html

MAVproxy, basic mavlink interface https://ardupilot.org/mavproxy/docs/getting_started/download_and_installation.html#linux

software for gimbal -> https://www.basecamelectronics.com/downloads/8bit/ use version 2.2b2

GLaDOS voice -> https://glados.c-net.org/ 

useful USB commands
```
dmesg | grep tty # list devices
ls -al /dev/serial/by-id # list USB serial devices (pixhawk...)
sudo dmesg | more # history of devices mounted etc
```


## 2. installing/compiling

Install OpenCV on raspberry pi -> https://qengineering.eu/install-opencv-4.4-on-raspberry-pi-4.html

Overclocking rpi4 -> https://magpi.raspberrypi.org/articles/how-to-overclock-raspberry-pi-4

Install OpenCV with GPU support on Jetson Nano -> https://qengineering.eu/install-opencv-4.5-on-jetson-nano.html

Install pytorch on the Nano -> https://forums.developer.nvidia.com/t/pytorch-for-jetson-version-1-7-0-now-available/72048

this command was useful first time setting up the camera:
```
v4l2-ctl --device /dev/video0 --list-formats-ext
```

serial ports are root by default use 
```
sudo usermod -a -G tty <user>
```

## 3. technical reference

EKF
- https://ardupilot.org/dev/docs/ekf2-estimation-system.html
- https://github.com/ArduPilot/ardupilot/blob/master/libraries/AP_NavEKF2/AP_NavEKF2.cpp


## 4. other downloads

The dataset can be found on the peryton teams.
The raw source for this dataset is found at https://www.sensefly.com/education/datasets/?dataset=1502


## 5. take a deep breath

Drink a beer and prepare for flying bugs

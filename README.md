# UAS image recognition for Surrey team Peryton 2021

- If you want to change code, make another branch and create a merge request so I can review the changes


See main.py for the entry point into the program

GLaDOS voice https://glados.c-net.org/ 

Install OpenCV on raspberry pi https://qengineering.eu/install-opencv-4.4-on-raspberry-pi-4.html

Overclocking rpi4 https://magpi.raspberrypi.org/articles/how-to-overclock-raspberry-pi-4

Install OpenCV with GPU support on Jetson Nano https://qengineering.eu/install-opencv-4.5-on-jetson-nano.html

forwarding ports over SSH for jupyter notebook https://ljvmiranda921.github.io/notebook/2018/01/31/running-a-jupyter-notebook/
```
localuser@localhost: ssh -N -f -L localhost:YYYY:localhost:XXXX remoteuser@remotehost
```

setting up the STL
https://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html

EKF
https://ardupilot.org/dev/docs/ekf2-estimation-system.html
https://github.com/ArduPilot/ardupilot/blob/master/libraries/AP_NavEKF2/AP_NavEKF2.cpp



use 
```
# if on linux -> apt-get install python3-opencv
pip install -r requirements.txt
```
to install the modules used. A decent amount of them are unneccesary for this project but that's what pip freeze does 🤷‍♀️

software for gimbal -> https://www.basecamelectronics.com/downloads/8bit/ use version 2.2b2


The dataset can be found on the peryton teams.
The raw source for this dataset is found at https://www.sensefly.com/education/datasets/?dataset=1502


I could organise things into modules... ideally you'd have an app module with sub modules, however this works for now

- doing this makes it harder to test individual components.. (you can't run the script directly as own module imports don't work)

- but then we could initialise global objects in __init__ which is a bit more pythonic / nice



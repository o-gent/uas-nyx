import nyx

from nyx.camera import CameraStream
from nyx.target_recognition import findCharacters

cam = CameraStream().start()

def find():
    print(findCharacters(cam.read()))


import dronekit
vehicle = dronekit.connect('/dev/ttyACM0', wait_ready=True)

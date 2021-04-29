import nyx

from nyx.camera import CameraStream
from nyx.target_recognition import findCharacters

cam = CameraStream().start()

def find():
    print(findCharacters(cam.read()))

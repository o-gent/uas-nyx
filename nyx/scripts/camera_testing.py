import time
import importlib
import os

import cv2

from nyx.recognition import camera
from nyx.utils import logger


cam = camera.CameraStream()

logger.info("started camera")
cam.start()

try:
    while True:
        t = str(time.time()).split(".")[0] + "-" + str(time.time()).split(".")[1]
        cv2.imwrite(time.strftime(f"images/%m-%d-%H:%M:%S-{t}.jpg"),cam.read()[0])
        logger.info("took image")

except KeyboardInterrupt:
    logger.info("Keyboard interupt")
    cam.stop()

except Exception as e:
    logger.info(f"Failed {e}")
    cam.stop()


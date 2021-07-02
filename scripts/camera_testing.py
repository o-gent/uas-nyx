import sys

sys.path.append("../")

import time
import importlib
import os

import cv2

from nyx import camera
from nyx.utils import logger


cam = camera.CameraStream()

logger.info("started camera")
cam.start()

try:
    while True:
        t = str(time.time()).split(".")[0]
        cv2.imwrite(time.strftime(f"%m/%d %H:%M:%S {t}"),cam.read())
        logger.info("took image")

except KeyboardInterrupt:
    logger.info("Keyboard interupt")
    cam.stop()

except Exception as e:
    logger.info(f"Failed {e}")
    cam.stop()


"""
camera backends & parameters https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html#ga023786be1ee68a9105bf2e48c700294d
CAP_DSHOW needs to be used for Windows and the ELP 13MP IMX214

VideoCapture docs https://docs.opencv.org/3.4/d8/dfe/classcv_1_1VideoCapture.html#a57c0e81e83e60f36c83027dc2a188e80

"""

import os
import platform
import time
from threading import Lock, Thread
from typing import Generator

import cv2
import numpy as np

from nyx.utils import display, logger


class CameraStream :
    """ https://gist.github.com/allskyee/7749b9318e914ca45eb0a1000a81bf56 """

    def __init__(self, src = 0, width = 320, height = 240) :
        if platform.system() == "Linux": # found that gstreamer backend doesn't work
            logger.info("using linux backend")
            
            waiting = True
            while waiting:
                try:
                    self.stream = cv2.VideoCapture("/dev/video0", cv2.CAP_V4L)
                    waiting = False
                except:
                    logger.info("camera not connected")
                    time.sleep(1)
            
            # not sure but forces it to work lol https://stackoverflow.com/questions/14011428/how-does-cv2-videocapture-changes-capture-resolution
            self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
        
        else: # Found this works for Windows
            self.stream = cv2.VideoCapture(1, cv2.CAP_DSHOW)
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 3839) # doesn't like it if you set to 3840
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
        
        (self.grabbed, self.frame) = self.stream.read()
        self.started = False
        self.read_lock = Lock()


    def start(self) :
        if self.started :
            print("already started!!")
            return None
        self.started = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self


    def update(self) :
        while self.started :
            (grabbed, frame) = self.stream.read()
            self.read_lock.acquire()
            self.grabbed, self.frame = grabbed, frame
            self.read_lock.release()


    def read(self) :
        self.read_lock.acquire()
        frame = self.frame.copy()
        self.read_lock.release()
        return frame


    def stop(self) :
        self.started = False
        self.thread.join()


    @staticmethod
    def take_image_test()-> Generator[np.ndarray, None, None]:
        """
        just return an image from file
        will be slower than the real thing as having to load from disk
        """
        files = [f for f in os.listdir('./dataset/sim_dataset/')]

        for image_name in files:
            image = cv2.imread('./dataset/sim_dataset/' + image_name)
            yield image


    def __exit__(self, exc_type, exc_value, traceback) :
        self.stream.release()


class Camera: 
    def __init__(self, debug = False):
        self.debug = debug
        
        if platform.system() == "Linux": # found that gstreamer backend doesn't work
            logger.info("using linux backend")
            self.cam = cv2.VideoCapture("/dev/video0", cv2.CAP_V4L)
            # not sure but forces it to work lol https://stackoverflow.com/questions/14011428/how-does-cv2-videocapture-changes-capture-resolution
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
        
        else: # Found this works for Windows
            self.cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 3839) # doesn't like it if you set to 3840
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
        
        # setup any camera parameters
        logger.info(self.cam.set(cv2.CAP_PROP_FPS, 25))
        logger.info(self.cam.set(cv2.CAP_PROP_BUFFERSIZE, 10))


    def take_image(self):
        ret, frame = self.cam.read()
        if self.debug:
            height, width, channels = frame.shape
            print(f"{width}, {height}")
        return frame
    

    def get_camera(self):
        return self.cam





if __name__ == "__main__":
    c = Camera(debug=True)
    l = []
    l.append(c.take_image())
    l.append(c.take_image())
    time.sleep(1)
    l.append(c.take_image())

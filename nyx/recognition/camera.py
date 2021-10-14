import os
import platform
import time
from threading import Lock, Thread
from typing import Generator, Tuple

import cv2
import numpy as np

from nyx.utils import display, logger


class CameraStream :
    """ 
    Captures a stream of images in the background
    https://gist.github.com/allskyee/7749b9318e914ca45eb0a1000a81bf56
    """

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
            
            """
            CAP_PROP_ISO_SPEED is unsupported
            CAP_PROP_WB_TEMPERATURE doesn't work?
            standard CAP_PROP_BUFFERSIZE is 4.0
            """
            
            # not sure but forces it to work lol https://stackoverflow.com/questions/14011428/how-does-cv2-videocapture-changes-capture-resolution
            self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
            self.stream.set(cv2.CAP_PROP_GAIN, 100)
            self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1) # 1 off, 3 on
            self.stream.set(cv2.CAP_PROP_EXPOSURE, 100)
            self.stream.set(cv2.CAP_PROP_AUTO_WB, 1) # 0 off, 1 on
            #self.stream.set(cv2.CAP_PROP_WB_TEMPERATURE, -0.5) # negative warm, positive cool
            #self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 1.0)
            #self.stream.set(cv2.CAP_PROP_HUE, 0)
            #self.stream.set(cv2.CAP_PROP_SATURATION,100)

        
        else: # Found this works for Windows
            self.stream = cv2.VideoCapture(1, cv2.CAP_DSHOW)
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 3839) # doesn't like it if you set to 3840
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
            #self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            self.stream.set(cv2.CAP_PROP_SETTINGS , 1)
            #self.stream.set(cv2.CAP_PROP_EXPOSURE, 0)
            #self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, -3.0)
            #self.stream.set(cv2.CAP_PROP_GAIN, 60)
        
        (self.grabbed, self.frame) = self.stream.read()
        self.started = False
        self.read_lock = Lock()
        self.time = 0


    def start(self):
        """ Begin capturing images """
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
            self.time = time.time()
            self.read_lock.release()


    def read(self) -> Tuple[np.ndarray,float]:
        """
        return the last captured frame and the time it was taken
        """
        self.read_lock.acquire()
        frame = self.frame.copy()
        self.read_lock.release()
        #print(self.stream.get(cv2.CAP_PROP_EXPOSURE))
        #print(self.stream.get(cv2.CAP_PROP_AUTO_EXPOSURE))
        return frame, self.time


    def stop(self):
        """ Stop capturing images """
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

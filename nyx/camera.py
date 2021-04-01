"""
camera backends & parameters https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html#ga023786be1ee68a9105bf2e48c700294d
CAP_DSHOW needs to be used for Windows and the ELP 13MP IMX214

VideoCapture docs https://docs.opencv.org/3.4/d8/dfe/classcv_1_1VideoCapture.html#a57c0e81e83e60f36c83027dc2a188e80

"""

from typing import Generator
import cv2
import numpy as np
import os
import time

class Camera:
    def __init__(self, debug = False):
        self.debug = debug
        self.cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        # setup any camera parameters
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 3839) # doesn't like it if you set to 3840
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
        self.cam.set(cv2.CAP_PROP_FPS, 2)


    def take_image(self):
        ret, frame = self.cam.read()
        if self.debug:
            height, width, channels = frame.shape
            print(f"{width}, {height}")
        return frame
    

    def get_camera(self):
        return self.cam


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


def display(img) -> None:
    """ display 800px wide image and wait for enter """
    img = resizeWithAspectRatio(img, width=800)
    cv2.imshow("", img)
    cv2.waitKey(0)

def resizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    """ return resized image """
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)


c = Camera(debug=True)
l = []
l.append(c.take_image())
l.append(c.take_image())
time.sleep(1)
l.append(c.take_image())
for i in l:
    display(i)
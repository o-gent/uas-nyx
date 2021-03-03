"""
not expecting this to be large
"""

import cv2
import numpy as np
import os


def initialise_camera():
    """
    first time setup of camera
    """
    pass


def take_image():
    """
    return an image from the camera
    """
    pass


def take_image_test() -> np.ndarray:
    """
    just return an image from file
    will be slower than the real thing as having to load from disk
    """
    files = [f for f in os.listdir('./dataset/sim_dataset/')]

    for image_name in files:
        image = cv2.imread('./dataset/sim_dataset/' + image_name)
        yield image

"""
not expecting this to be large
"""

import cv2
import numpy as np


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
    img = cv2.imread("test_images/field.png")
    return img

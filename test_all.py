import cv2
import matplotlib.pyplot as plt
import numpy as np

import target_recognition
from utils import display, imageOverlay


k_nearest = target_recognition.load_model()
target_recognition.k_nearest = k_nearest


def test_one():
    assert 1 == 1


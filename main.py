""" 
co-ordinate everything

- Image capture
- Dronekit
- Image recognition
- Payload calculations

track mission state
idle -> payload drop -> idle -> speed test -> area search -> finish
"""

import threading
import time

import cv2
import numpy as np

import target_recognition

target_recognition.k_nearest = target_recognition.load_model()


def take_image() -> np.ndarray:
    """ take an image from the camera and return it """
    img = cv2.imread("test_images/field.png")
    return img


def process_image(image) -> list:
    """ given an image return the colour, position, letter or none """
    result = target_recognition.findCharacters(image)
    return result


def main():
    start = time.time()
    #image = take_image()
    result = process_image(image)
    #print(time.time() - start)


if __name__ == "__main__":
    # from multi import RepeatedTimer
    image = take_image()
    # rt = RepeatedTimer(1, main)
    
    while True:
        start = time.time()
        
        main()
        
        sleep_time = 0.1 - (time.time()-start)
        print(sleep_time)
        if sleep_time < 0: print("running behind")
        time.sleep(sleep_time)

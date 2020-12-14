""" 
co-ordinate everything

- Image capture
- Dronekit
- Image recognition
- Payload calculations

track mission state
idle -> payload drop -> idle -> speed test -> area search -> finish
"""

import numpy as np
import cv2
import target_recognition


def take_image(__) -> np.ndarray:
    """ take an image from the camera and return it """
    img = cv2.imread("test_images/field.png")
    return img


def process_image(image, gps):
    """ given an image return the colour, position, letter or none """
    result = target_recognition.findCharacters(image)
    if result:
        # work out position
        pass
    
    return result


def main():
    pass


if __name__ == "__main__":
    main()

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
import multi
import time


k_nearest = target_recognition.load_model()
target_recognition.k_nearest = k_nearest


def take_image(__) -> np.ndarray:
    """ take an image from the camera and return it """
    print("image taken")
    img = cv2.imread("test_images/field.png")
    return img


def process_image(image):
    """ given an image return the colour, position, letter or none """
    print("image recieved")
    result = target_recognition.findCharacters(image)
    if result:
        # work out position
        pass
    
    return result



if __name__ == "__main__":

    results = []
    process = multi.WorkerManager(3, process_image)
    take = multi.Worker(take_image)

    take.send(1)
    while True:
        image = take.recieve()
        if image is not None:
            take.send(1)
            process.add(image)
        process.churn()
        results.append(process.get())
        time.sleep(1)


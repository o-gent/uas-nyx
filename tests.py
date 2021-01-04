import os
import time
import unittest

import cv2
import matplotlib.pyplot as plt
import numpy as np

import target_recognition
from utils import display, imageOverlay


k_nearest = target_recognition.load_model()
target_recognition.k_nearest = k_nearest

class TestImageRecognition(unittest.TestCase):

    def test_standard(self):
        files = [f for f in os.listdir('./test_images/')]
        iterations = 1

        start = time.time()

        for i in range(iterations):
            for f in files:
                img = cv2.imread('./test_images/' + f)
                print(f"found charachters {target_recognition.findCharacters(img)} in image")

        print(f"average time taken per image {(time.time() - start) / (len(files) * iterations)}")


    def test_minimum_target_size(self):
        # cycle through image widths
        overlay = cv2.imread('test_images/target.jpg')
        background = cv2.imread('test_images/field2.png')
        results=[]
        for i in range(10,300):
            img = imageOverlay(background, overlay, x=100, y=100, width=i)
            results.append(target_recognition.findCharacters(img))
        processed_results = list(map(lambda x: 1 if x == ['T'] else 0, results))

        prob = [sum(processed_results[i-10:i])/10 for i in range(10,len(processed_results))]
        prob = [0,0,0,0,0,0,0,0,0] + prob

        plt.plot(processed_results)
        #plt.plot(prob)
        plt.show()
    

    def test_parallel_processing(self):
        import multi

        def take_image(__) -> np.ndarray:
            """ take an image from the camera and return it """
            print("image taken")
            img = cv2.imread("test_images/field.png")
            return img


        def process_image(image) -> list:
            """ given an image return the colour, position, letter or none """
            print("image recieved")
            result = target_recognition.findCharacters(image)
            if result:
                # work out position
                pass
            
            return result

        results = []
        process = multi.WorkerManager(1, process_image)
        take = multi.Worker(take_image)

        take.send(1)
        start = time.time()
        
        for i in range(100):
            image = take.recieve()
            if image is not None:
                take.send(1)
                process.add(image)
            process.churn()
            results.append(process.get())

        print(time.time() - start)


if __name__ == "__main__":
    unittest.main()



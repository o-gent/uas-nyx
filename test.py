import os
import time

import cv2
import matplotlib.pyplot as plt

import target_recognition
from utils import display, imageOverlay


k_nearest = target_recognition.load_model()
target_recognition.k_nearest = k_nearest
files = [f for f in os.listdir('./test_images/')]
iterations = 1

start = time.time()

for i in range(iterations):
    for f in files:
        img = cv2.imread('./test_images/' + f)
        print(f"found charachters {target_recognition.find_characters(img)} in image")

print(f"average time taken per image {(time.time() - start) / (len(files) * iterations)}")


# cycle through image widths
overlay = cv2.imread('test_images/target.jpg')
background = cv2.imread('test_images/field2.png')
results=[]
for i in range(10,300):
    img = imageOverlay(background, overlay, x=100, y=100, width=i)
    results.append(target_recognition.find_characters(img))
processed_results = list(map(lambda x: 1 if x == ['T'] else 0, results))

prob = [sum(processed_results[i-10:i])/10 for i in range(10,len(processed_results))]
prob = [0,0,0,0,0,0,0,0,0] + prob

plt.plot(processed_results)
plt.plot(prob)
plt.show()
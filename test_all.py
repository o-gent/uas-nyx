import cv2
import matplotlib.pyplot as plt
import numpy as np
import os


def test_one():
    assert 1 == 1


def test_image_recognition():
    """ test against the dataset """
    
    import target_recognition
    
    k_nearest = target_recognition.load_model()
    target_recognition.k_nearest = k_nearest

    files = [f for f in os.listdir('./dataset/sim_dataset/')]

    results = []
    for image_name in files:
        image = cv2.imread('./dataset/sim_dataset/' + image_name)
        result = target_recognition.findCharacters(image)
        print(result)
        results.append(result)
    
    def check(x) -> list:
        try: return x[0]
        except: return []

    score = sum([1 if 'T' in check(i) else 0 for i in results])/len(results)

    print(f"{score*100}% dataset accuracy")

    assert score/len(results) > 0.95

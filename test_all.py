import math
import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
import time


def test_one():
    assert 1 == 1


def test_image_recognition_accuracy():
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


def test_image_recognition_speed():
    import target_recognition
    k_nearest = target_recognition.load_model()
    target_recognition.k_nearest = k_nearest

    files = [f for f in os.listdir('./dataset/sim_dataset/')]
    iterations = 100
    img = cv2.imread('./dataset/sim_dataset/' + files[10])
    
    start = time.time()
    for i in range(iterations):
        print(f"found charachters {target_recognition.findCharacters(img)} in image")

    print(f"average time taken per image {(time.time() - start) / (iterations)}")

    assert 1==1


def test_triangulate():
    """ """

    import target_recognition

    position = (0,0)
    target_px = (1920,1440)
    altitude = 25.0
    heading = 90

    result = target_recognition.triangulate(position, target_px, altitude, heading)
    assert(result == (0.0,0.0))
    
    target_px = (0,1440)
    heading = 0
    altitude = 1
    result = target_recognition.triangulate(position, target_px, altitude, heading)
    result = round(result[0], 3)
    assert(result == -1.192)
    
    

def test_state():
    """ """
    import state

    state.state_manager.change_state(state.PRE_FLIGHT_CHECKS)
    
    time.sleep(1) # shouldn't be taken account of
    
    state.state_manager.change_state(state.WAIT_FOR_ARM)
    state.state_manager.change_state(state.TAKE_OFF_ONE)
    state.state_manager.change_state(state.PAYLOAD_WAYPOINTS)
    state.state_manager.change_state(state.PREDICT_PAYLOAD_IMPACT)
    state.state_manager.change_state(state.DROP_BOMB)
    state.state_manager.change_state(state.CLIMB_AND_GLIDE)
    
    time.sleep(2)
    
    state.state_manager.change_state(state.LAND_ONE)
    state.state_manager.change_state(state.WAIT_FOR_CLEARANCE)
    
    time.sleep(1) # this one shouldn't be taken account of

    state.state_manager.change_state(state.TAKE_OFF_TWO)
    state.state_manager.change_state(state.SPEED_TRAIL)
    
    time.sleep(3)
    
    state.state_manager.change_state(state.AREA_SEARCH)
    state.state_manager.change_state(state.LAND_TWO)
    state.state_manager.change_state(state.NULL)

    assert(int(state.state_manager.elapsed_mission_time()) == 5)
    assert(int(state.state_time[state.CLIMB_AND_GLIDE].taken) == 2)
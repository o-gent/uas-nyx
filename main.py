""" 
co-ordinate everything

- Image capture
- Dronekit
- Image recognition
- Payload calculations

track mission state
idle -> payload drop -> idle -> speed test -> area search -> finish
"""

import functools
import threading
import time
from typing import Callable, Dict

import cv2
import dronekit
import numpy as np

import mission
import target_recognition

target_recognition.k_nearest = target_recognition.load_model()
state = ""

class States:
    PRE_FLIGHT_CHECKS = "pre_flight_checks"
    # etc etc


# to be moved
def take_image() -> np.ndarray:
    """ take an image from the camera and return it """
    img = cv2.imread("test_images/field.png")
    return img


# to be moved
def process_image(image) -> list:
    """ given an image return the colour, position, letter or none """
    result = target_recognition.findCharacters(image)
    return result


def change_state(new_state) -> str:
    """ 
    err globals but hey, otherwise would need a class for only this reason 
    maybe other reasons but probably not, fight me
    """
    global state
    
    try:
        state = new_state
        print(state)
        return state
    except:
        mission.vehicle.simple_goto(mission.vehicle.home_location)
        raise Exception("that state doesn't exist")


def target_loop(f_py=None, target_time=1.0):
    """
    base code for each state, while loop with a target time per loop
    target functions must return a bool of if they want to break the loop
    decorator with parameters 
    https://stackoverflow.com/questions/5929107/decorators-with-parameters
    """
    assert callable(f_py) or f_py is None
    def _decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            while True:
                start = time.time()    
                # run the actual function and check if break needed
                ended: bool = func(*args, **kwargs)
                if ended:
                    break
                sleep_time = target_time - (time.time()-start)
                print(sleep_time)
                if sleep_time < 0: 
                    print("running behind!!")
                    sleep_time = 0
                time.sleep(sleep_time)
            return True
        return wrapper
    return _decorator(f_py) if callable(f_py) else _decorator


@target_loop
def pre_flight_checks():
    return True


@target_loop
def wait_for_arm():
    if mission.vehicle.arm == True:
        mission.vehicle.mode = "TAKEOFF"
        change_state("wait_for_arm")
        return True
    print("waiting for arm..")
    return False


@target_loop
def take_off_one():
    return True


def payload_waypoints():
    """ this one has a single running setup phase """

    @target_loop
    def loop():
        return True

    return True


@target_loop
def predict_payload_impact():
    return True


@target_loop
def drop_bomb():
    return True


@target_loop
def climb_and_glide():
    return True


@target_loop
def land_1():
    return True


@target_loop
def wait_for_clearance():
    return True


@target_loop
def take_off_two():
    return True


@target_loop(target_time=0.2)
def speed_trial():
    image = take_image()
    result = process_image(image)
    #print(mission.vehicle.velocity)
    if False:
        return True
    return False


@target_loop
def area_search():
    return True


@target_loop
def land_2():
    return True


@target_loop
def null():
    return True
        

# State machine format
# each stage has its own loop and checks if it should transition to the next stage
states: Dict[str, Callable] = {
    'pre_flight_checks': pre_flight_checks,
    'wait_for_arm': wait_for_arm,
    'take_off_one': take_off_one,
    'payload_waypoints': payload_waypoints,
    'predict_payload_impact': predict_payload_impact,
    'drop_bomb': drop_bomb,
    'climb_and_glide': climb_and_glide,
    'land_1': land_1,
    'wait_for_clearance': wait_for_clearance,
    'take_off_two': take_off_two,
    'speed_trial': speed_trial,
    'area_search': area_search,
    'land_2': land_2,
    'null': null
}


if __name__ == "__main__":
    state = change_state('speed_trial')

    # run the current state
    while True:
        states[state]()
    

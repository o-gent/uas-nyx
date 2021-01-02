""" 
entry point for the program
co-ordinate everything

The loop format creates some issues, makes it difficut to pass in and out "global" variables
Could use a class to keep track of these things
May have to use globals..

"""

import functools
import time
from typing import Callable, Dict

import camera
import mission # contains the vehicle variable
import target_recognition
import utils
from state import * # for all the 
import state # hacky, to use the state_manager as a global


target_recognition.k_nearest = target_recognition.load_model()
logger = utils.setup_logger("main")


# could be moved
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
                #print(sleep_time)
                if sleep_time < 0: 
                    logger.log(f"{state} running behind!!")
                    sleep_time = 0
                time.sleep(sleep_time)
            return True
        return wrapper
    return _decorator(f_py) if callable(f_py) else _decorator


def pre_flight_checks() -> bool:
    """ 
    user prompt to ensure the vehicle is ready
    not a loop
    state changes:
        - wait_for_arm
    """
    return True


@target_loop
def wait_for_arm() -> bool:
    """
    check periodically for vehicle arming, proceed once observed
    state changes:
        - take_off_one
    """
    if mission.vehicle.arm == True:
        mission.vehicle.mode = "TAKEOFF"
        state.state_manager.change_state(TAKE_OFF_ONE)
        return True
    print("waiting for arm..")
    return False


@target_loop
def take_off_one():
    """
    start take-off sequence, proceed once target height reached
    state changes:
        - payload_waypoints
    """

    return True


def payload_waypoints():
    """ 
    this one has a single running setup phase
    state changes:
        - predict_payload_impact
    """

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
def land_one():
    return True


@target_loop
def wait_for_clearance():
    return True


@target_loop
def take_off_two():
    return True


@target_loop(target_time=0.2)
def speed_trial():
    image = camera.take_image_test()
    result = target_recognition.findCharacters(image)
    #print(mission.vehicle.velocity)
    if False:
        return True
    return False


@target_loop
def area_search():
    return True


@target_loop
def land_two():
    return True


@target_loop
def null():
    return True
        

# State machine format
# each stage has its own loop and checks if it should transition to the next stage
states: Dict[str, Callable] = {
    PRE_FLIGHT_CHECKS: pre_flight_checks,
    WAIT_FOR_ARM: wait_for_arm,
    TAKE_OFF_ONE: take_off_one,
    PAYLOAD_WAYPOINTS: payload_waypoints,
    PREDICT_PAYLOAD_IMPACT: predict_payload_impact,
    DROP_BOMB: drop_bomb,
    CLIMB_AND_GLIDE: climb_and_glide,
    LAND_ONE: land_one,
    WAIT_FOR_CLEARANCE: wait_for_clearance,
    TAKE_OFF_TWO: take_off_two,
    SPEED_TRAIL: speed_trial,
    AREA_SEARCH: area_search,
    LAND_TWO: land_two,
    NULL: null
}


if __name__ == "__main__":
    state.state_manager.change_state(SPEED_TRAIL)

    # run the current state
    try:
        while True:
            states[state.state_manager.state]()
    except:
        # a bruh moment for sure
        mission.vehicle.simple_goto(mission.vehicle.home_location)
        raise Exception("balls")
    
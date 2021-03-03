""" 
entry point for the program
co-ordinate everything

The loop format creates some issues, makes it difficut to pass in and out "global" variables
Could use a class to keep track of these things
May have to use globals..

"""

import functools
from os import stat
import time
from typing import Callable, Dict

from erebus.bomb_computer import drop_point
from erebus import camera, mission, state, target_recognition
from erebus import mission  # contains the vehicle variable
from erebus.utils import logger  # to configure logger
from erebus.state import *  # for all the state names

logger.info("All modules imported and ready, proceeding to main")


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
                    logger.warning(f"{state} running behind!!")
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
    # make dronekit is working correctly

    # ensure we have GPS lock

    # check if values make sense, level at 0 altitude etc

    # then do control surface checks

    state.state_manager.change_state(WAIT_FOR_ARM)
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
    logger.info("waiting for arm..")
    return False


@target_loop
def take_off_one() -> bool:
    """
    start take-off sequence, proceed once target height reached
    state changes:
        - payload_waypoints
    """
    state.state_manager.change_state(PAYLOAD_WAYPOINTS)
    return True


def payload_waypoints() -> bool:
    """ 
    this one has a single running setup phase
    state changes:
        - predict_payload_impact
    """

    @target_loop
    def loop():
        if mission.is_position_reached((0,0), 100):
            return True
        return False
    
    loop()
    state.state_manager.change_state(PREDICT_PAYLOAD_IMPACT)
    return True


@target_loop
def predict_payload_impact() -> bool:
    """ 
    use a wind speed / direction prediction to predict bomb impact
    https://ardupilot.org/dev/docs/ekf2-estimation-system.html 
    """
    wind_bearing = mission.vehicle.wind.wind_direction - mission.vehicle.heading
    # get the latest position requirement
    aim_X, aim_Y = drop_point(
        mission.TARGET_LOCATION,
        mission.vehicle.location._alt,
        mission.vehicle.groundspeed,
        mission.vehicle.wind.wind_speed,
        wind_bearing
        )
    # check how close we are to this position
    
    if mission.is_position_reached((0,0), 2):
        state.state_manager.change_state(DROP_BOMB)
        return True
    # aim to go to this position
    return False


def drop_bomb() -> bool:
    state.state_manager.change_state(CLIMB_AND_GLIDE)
    return True


@target_loop
def climb_and_glide() -> bool:
    state.state_manager.change_state(LAND_ONE)
    return True


@target_loop
def land_one() -> bool:
    state.state_manager.change_state(WAIT_FOR_CLEARANCE)
    return True


@target_loop
def wait_for_clearance() -> bool:
    state.state_manager.change_state(TAKE_OFF_TWO)
    return True


@target_loop
def take_off_two() -> bool:
    state.state_manager.change_state(SPEED_TRAIL)
    return True


def speed_trial() -> bool:
    # set up speed trail waypoints and start waypoints

    results = []

    @target_loop(target_time=0.2)
    def loop() -> bool:
        image = next(camera.take_image_test())
        result = target_recognition.findCharacters(image)
        if len(result) == 1:
            # figure out the image position
            target_position = target_recognition.triangulate(
                (mission.vehicle.location.local_frame.north, mission.vehicle.location.local_frame.east),
                result["centre"],
                mission.vehicle.location.local_frame.down,
                mission.vehicle.heading
            )
            results.append([target_position, result])
            logger.info(f"{target_position}, {result['charachter']}, {result['colour']}")
        
        if mission.is_position_reached((0,0), 5):
            return True

        if len(results) >= 3:
            # found all targets
            return True
        
        return False
    
    loop()
    state.state_manager.change_state(AREA_SEARCH)
    return True


@target_loop
def area_search() -> bool:
    state.state_manager.change_state(LAND_TWO)
    return True


@target_loop
def land_two() -> bool:
    state.state_manager.change_state(END)
    return True


@target_loop
def end() -> bool:
    mission.vehicle.armed = False
    mission.vehicle.close()
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
    END: end
}


if __name__ == "__main__":
    # run the current state
    try:
        while True:
            states[state.state_manager.state]()
    except:
        # a bruh moment for sure
        mission.vehicle.simple_goto(mission.vehicle.home_location)
        logger.critical("main loop crashed, exiting")
        raise Exception("balls")
    
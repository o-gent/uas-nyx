"""
collect the big dictionaries into one file
and manage state in a class cos it turns out you would need more globals than I thought
"""

from typing import Dict
from dataclasses import dataclass
from utils import setup_logger


logger = setup_logger("state")


# list out states as statics to prevent spelling errors
PRE_FLIGHT_CHECKS = "pre_flight_checks"
WAIT_FOR_ARM = "wait_for_arm"
TAKE_OFF_ONE = "take_off_one"
PAYLOAD_WAYPOINTS = "payload_waypoints"
PREDICT_PAYLOAD_IMPACT = "predict_payload_impact"
DROP_BOMB = "drop_bomb"
CLIMB_AND_GLIDE = "climb_and_glide"
LAND_ONE = "land_one"
WAIT_FOR_CLEARANCE = "wait_for_clearance"
TAKE_OFF_TWO = "take_off_two"
SPEED_TRAIL = "speed_trial"
AREA_SEARCH = "area_search"
LAND_TWO = "land_two"
NULL = "null"


@dataclass
class StateTiming:
    """ just makes it more intelligent than a dictionary """
    expected: int
    started: int = 0
    end: int = 0
    taken: int = 0


# state timing
# expected amount of time, time started (blank), time taken (blank)
state_time: Dict[str, StateTiming] = {
    TAKE_OFF_ONE: StateTiming(0),
    PAYLOAD_WAYPOINTS: StateTiming(0),
    PREDICT_PAYLOAD_IMPACT: StateTiming(0),
    DROP_BOMB: StateTiming(0),
    CLIMB_AND_GLIDE: StateTiming(0),
    LAND_ONE: StateTiming(0),
    
    TAKE_OFF_TWO: StateTiming(0),
    SPEED_TRAIL: StateTiming(0),
    AREA_SEARCH: StateTiming(0),
    LAND_TWO: StateTiming(0)
}

class State:
    """ keep track of timings and state and all that fun stuff """

    def __init__(self):
        self.state = ""
        self.state_time = state_time

    
    def start_timer(self):
        pass


    def pause_timer(self):
        pass


    def elapsed_mission_time(self):
        pass

    
    def change_state(self, new_state):
        """ 
        err globals but hey, otherwise would need a class for only this reason 
        maybe other reasons but probably not, fight me
        """
        
        try:
            logger.log(f"STATE CHANGE from {self.state} to {new_state}")
            self.complete_state(new_state)
            self.state = new_state
        except:
            raise Exception("that state doesn't exist")


    def complete_state(self, new_state):
        """ 
        store the time taken to complete the state
        returns the error (how far behind we are)
        """
        # get the total time up to this state
        total_time = sum([state_time[item].taken for item in state_time])
        # get the total expected time up to this state
        total_expected = 0
        for key in state_time:
            if key == self.state:
                break
            else:
                total_expected += state_time[key].expected
        
        error = total_time - total_expected # +ve bad, -ve good

        # record values
        self.state_time[self.state].end = self.elapsed_mission_time()
        self.state_time[self.state].taken = self.elapsed_mission_time() - state_time[self.state].started
        self.state_time[new_state].started = self.elapsed_mission_time()

        return error


state_manager = State()

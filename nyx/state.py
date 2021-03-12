"""
collect the big dictionaries into one file
and manage state in a class cos it turns out you would need more globals than I thought
"""

import time
from dataclasses import dataclass
from typing import Dict

from erebus.utils import logger


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
END = "end"


@dataclass
class StateTiming:
    """ just makes it more intelligent than a dictionary """
    expected: int
    started: int = 0
    end: int = 0
    taken: int = 0


# state timing
# expected amount of time, time started (blank), time taken (blank)
# if the state isn't in this list then we aren't interested in timing it
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
        self._state_time = state_time
        self.misson_time = 0
        self._timer = 0 # a timestap to calculate a time delta from
        logger.info("state object created")

    
    def start_timer(self):
        """ run again to reset the timer """
        self._timer = time.time()


    def elapsed_mission_time(self) -> float:
        """  """
        self.misson_time += time.time() - self._timer
        self.start_timer()
        return self.misson_time

    
    def change_state(self, new_state: str):
        """ 
        err globals but hey, otherwise would need a class for only this reason 
        maybe other reasons but probably not, fight me
        """
        logger.info(f"STATE CHANGE from {self.state} to {new_state}")
        self._complete_state(new_state)
        self.state = new_state


    def _complete_state(self, new_state) -> int:
        """ 
        store the time taken to complete the state
        returns the error (how far behind we are)
        """
        # assumes if it's not in the timing states then it's a non timing state
        # so doesn't handle bad input
        if self.state not in self._state_time.keys():
            self.start_timer()
            return self.error()
        else:
            pass

        # record values
        elapsed_mission_time = self.elapsed_mission_time()
        self._state_time[self.state].end = elapsed_mission_time
        self._state_time[self.state].taken = elapsed_mission_time - self._state_time[self.state].started
        if new_state in self._state_time.keys():
            self._state_time[new_state].started = elapsed_mission_time

        return self.error()


    def error(self) -> int:
        """ return how far we are off the misison target """
        # get the total time up to this state
        total_time = sum([self._state_time[item].taken for item in self._state_time])
        # get the total expected time up to this state
        total_expected = 0
        # relies on going through the dictionary in order of the state changes
        for key in self._state_time:
            if key == self.state:
                break
            else:
                total_expected += self._state_time[key].expected

        error = total_time - total_expected # +ve bad, -ve good
        return error


state_manager = State()

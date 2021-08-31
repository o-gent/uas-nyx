from nyx.autopilot.state import State, StateList
import time
from nyx.autopilot.config import load_mission_parameters

def test_state():
    """ """
    state_manager = State(load_mission_parameters())

    state_manager.change_state(StateList.PRE_FLIGHT_CHECKS)
    
    time.sleep(1) # shouldn't be taken account of
    
    state_manager.change_state(StateList.WAIT_FOR_ARM)

    state_manager.start_timer()

    state_manager.change_state(StateList.TAKE_OFF_ONE)
    state_manager.change_state(StateList.PAYLOAD_WAYPOINTS)
    state_manager.change_state(StateList.PREDICT_PAYLOAD_IMPACT)
    state_manager.change_state(StateList.CLIMB_AND_GLIDE)
    
    time.sleep(2)
    
    state_manager.change_state(StateList.LAND_ONE)
    state_manager.change_state(StateList.WAIT_FOR_CLEARANCE)
    
    time.sleep(1) # this one shouldn't be taken account of

    state_manager.change_state(StateList.TAKE_OFF_TWO)
    state_manager.change_state(StateList.SPEED_TRAIL)
    
    time.sleep(3)
    
    state_manager.change_state(StateList.AREA_SEARCH)
    state_manager.change_state(StateList.LAND_TWO)
    state_manager.change_state(StateList.END)

    assert(int(state_manager.elapsed_mission_time()) == 5)
    assert(int(state_manager._state_time[StateList.CLIMB_AND_GLIDE].taken) == 2)

if __name__ == "__main__":
    test_state()
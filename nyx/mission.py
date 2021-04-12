"""
ardupilot mission structure
you'll need the SITL installed to test this, i'd recommend using WSL 
"""

import math
import os
import time
from typing import Dict, List, Tuple

import dronekit
from dronekit import LocationGlobalRelative
from nyx.utils import logger


"""
STARTUP PROCEDURE - runs on import
"""

logger.info("connecting to vehicle")
vehicle = dronekit.connect('127.0.0.1:14550', wait_ready=True)

waiting = True
while  waiting == True:
    # force information to be fetched
    vehicle.armed = False

    try:
        if vehicle.home_location.lat != None:
            waiting = False
        else:
            pass
    except:
        logger.info("waiting for dronekit information")
        time.sleep(1)

HOME = {
    'lat': vehicle.home_location.lat, 
    'lon': vehicle.home_location.lon, 
    'alt': vehicle.home_location.alt
}

logger.info("connection complete")


"""
MISSION SPECIFICS - may change this to JSON
"""

# need to set everything since current parameters are unknown
START_PARAMETERS = {
    "TAKEOFF_ALT": 20,
}

NON_PAYLOAD_PARAMETERS: Dict[str, int] = {

}

GLIDE_PARAMETERS: Dict[str, int] = {

}

RESET_GLIDE_PARAMETERS: Dict[str, int] = {

}

SPEED_TRIAL_PARAMETERS: Dict[str, int] = {

}

PAYLOAD_WAYPOINTS = [
    (100,100,20),
    (200,200,20)
]

TARGET_LOCATION = (100,100)

CLIMB_AND_GLIDE_WAYPOINTS = [
    (0,0,0)
]

SPEED_TRAIL_WAYPOINTS = [
    (0,0,0)
]

# this needs to be figured out - need a grid pattern 
# define a polygon and the waypoints need to be generated
AREA_SEARCH = [
    (0,0,0),
    (0,0,0),
    (0,0,0),
    (0,0,0)
]


"""
UTILITIES
"""

def parameters_set(parameters: Dict[str, int]):
    """ 
    set a list of parameters during flight and make sure they have been set, needs to complete gradually 
    https://dronekit-python.readthedocs.io/en/latest/guide/vehicle_state_and_parameters.html#vehicle-state-parameters
    """
    for parameter in parameters.keys():
        # saves a bit of time if the parameter is already correct and checks param exists
        if vehicle.parameters.get(parameter) != parameters.get(parameter):
            vehicle.parameters[parameter] = parameters.get(parameter)
            while vehicle.parameters.get(parameter) != parameters.get(parameter):
                yield False
        # still need to set more parameters
        yield False
    
    # all parameters set
    return True


def grid_search(polygon):
    """ given a polygon edge, generate a waypoint path to follow """
    pass


def goto_cmd(X,Y, altitude):
    """ 
    command which accepts relative co-ordinates from the point of launch 
    tried to use MAV_FRAME_LOCAL_NED, created upload issues so that didn't work
    https://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
    conversion maybe accurate?
    TODO: https://en.wikipedia.org/wiki/Haversine_formula
    """
    lat = HOME['lat'] + Y/111111
    lon = HOME['lon'] + X/(111111 * math.cos(math.radians(HOME['lat'])))
    
    #dronekit.LocationLocal()?
    
    return dronekit.Command(0,0,0, dronekit.mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
    dronekit.mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, lat, lon, altitude)


def goto_gps_cmd(lat, long, altitude):
    """ 
    command to go to co-ords at altitude 
    https://dronekit-python.readthedocs.io/en/latest/automodule.html#dronekit.CommandSequence
    """
    return dronekit.Command(0,0,0, dronekit.mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
    dronekit.mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, lat, long, altitude)


def command(mission: List[Tuple[int,int,int]]):
    """ given a list of waypoint co-ords, upload a mission """
    # get ready
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready() 
    cmds.clear()
    # list commands
    for waypoint in mission:
        cmds.add(goto_cmd(*waypoint))
    cmds.upload() # Send commands


def takeoff():
    """ take off checks etc? """
    pass


def is_position_reached(target_position, tolerance) -> bool:
    """ given a position, have we reached it """
    pass


def release_payload():
    """ set the payload release channel to high """
    vehicle.channels.overrides = {'9': 2000}
    time.sleep(0.2)
    vehicle.channels.overrides = {}


def distance_to_current_waypoint():
    """
    Gets distance in metres to the current waypoint.
    It returns None for the first waypoint (Home location).
    https://dronekit-python.readthedocs.io/en/latest/guide/auto_mode.html
    """
    nextwaypoint=vehicle.commands.next
    if nextwaypoint ==0:
        return None
    missionitem=vehicle.commands[nextwaypoint-1] #commands are zero indexed
    lat=missionitem.x
    lon=missionitem.y
    alt=missionitem.z
    targetWaypointLocation=LocationGlobalRelative(lat,lon,alt)
    distancetopoint = get_distance_metres(vehicle.location.global_frame, targetWaypointLocation)
    return distancetopoint


def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two `LocationGlobal` or `LocationGlobalRelative` objects.

    This method is an approximation, and will not be accurate over large distances and close to the
    earth's poles. It comes from the ArduPilot test code:
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5


if __name__ == "__main__":
    # assumes SITL
    # an absolute pain but it works..
    #os.system("""powershell.exe "start wsl '/mnt/c/Users/olive/ardupilot/Tools/autotest/sim_vehicle.py -v ArduPlane'" """)
    os.system("start wsl '/mnt/c/Users/olive/ardupilot/Tools/autotest/sim_vehicle.py -v ArduPlane'")


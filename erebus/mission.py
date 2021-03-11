"""
ardupilot mission structure
you'll need the SITL installed to test this, i'd recommend using WSL 
"""

import math
import os
import time

import dronekit
from erebus.utils import logger


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

TARGET_LOCATION = (100,100)
HOME = {
    'lat': vehicle.home_location.lat, 
    'lon': vehicle.home_location.lon, 
    'alt': vehicle.home_location.alt
}

print("connection complete")


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


def command():
    """ the command list """
    # get ready
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready() 
    cmds.clear()
    # list commands
    cmds.add(goto_cmd(100,100,100))
    cmds.add(goto_cmd(-500,-1000,200))
    cmds.upload() # Send commands


def takeoff():
    """ take off checks etc? """
    pass


def is_position_reached(target_position, tolerance) -> bool:
    """ given a position, have we reached it """
    pass


if __name__ == "__main__":
    # assumes SITL
    # an absolute pain but it works..
    #os.system("""powershell.exe "start wsl '/mnt/c/Users/olive/ardupilot/Tools/autotest/sim_vehicle.py -v ArduPlane'" """)
    os.system("start wsl '/mnt/c/Users/olive/ardupilot/Tools/autotest/sim_vehicle.py -v ArduPlane'")

    command()


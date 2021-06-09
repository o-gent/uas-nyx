"""
ardupilot mission structure
you'll need the SITL installed to test this, i'd recommend using WSL 
"""

import json
import math
import os
import time
from typing import Dict, List, Tuple, Union

import dronekit
from dronekit.atributes import LocationGlobalRelative

from nyx.utils import logger


class Mission():

    def __init__(self, sim:bool):
        self.vehicle, self.home = self.connect(sim)
        self.config = self.load_mission_parameters()

    
    def load_mission_parameters(self):
        """ 
        Load the config.json file into a dictionary & validate
        """
        with open("config.json") as config_file:
            config: Dict[str, Union[Dict, List]] = json.load(config_file)

        logger.info("read parameters:")
        logger.info(config)

        return config


    def connect(self, sim:bool) -> Tuple[dronekit.Vehicle, Dict[str, int]]:
        """
        Connect to the vehicle, check information is returned then return the object and home location
        """

        logger.info("connecting to vehicle")
        if sim:
            connection_string = '127.0.0.1:14550'
        
        vehicle = dronekit.connect(connection_string, wait_ready=True)

        waiting_time = 0
        waiting = True
        while  waiting == True:
            if waiting_time > 10:
                del vehicle
                waiting_time = 0
                logger.info("connecting to vehicle again")
                vehicle = dronekit.connect(connection_string, wait_ready=True)

            try:
                # force information to be fetched
                vehicle.armed = False
                
                if vehicle.home_location.lat != None:
                    waiting = False
                else:
                    logger.info("waiting for dronekit information")
                    waiting_time += 1
            except:
                logger.info("waiting for dronekit information")
                waiting_time += 1
                time.sleep(1)

        home = {
            'lat': vehicle.home_location.lat, 
            'lon': vehicle.home_location.lon, 
            'alt': vehicle.home_location.alt
        }

        logger.info("connection complete")

        return vehicle, home


    def parameters_set(self, parameters: Dict[str, int]):
        """ 
        set a list of parameters during flight and make sure they have been set, needs to complete gradually 
        https://dronekit-python.readthedocs.io/en/latest/guide/vehicle_state_and_parameters.html#vehicle-state-parameters
        """
        for parameter in parameters.keys():
            
            # saves a bit of time if the parameter is already correct and checks param exists
            if self.vehicle.parameters.get(parameter) != parameters.get(parameter):
                self.vehicle.parameters[parameter] = parameters.get(parameter)
            
                while self.vehicle.parameters.get(parameter) != parameters.get(parameter):
                    yield False
            
            # still need to set more parameters
            yield False
        
        # all parameters set
        return True


    def grid_search(self, polygon):
        """ given a polygon edge, generate a waypoint path to follow """
        pass


    def goto_cmd(self, X,Y, altitude):
        """ 
        command which accepts relative co-ordinates from the point of launch 
        tried to use MAV_FRAME_LOCAL_NED, created upload issues so that didn't work
        https://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
        conversion maybe accurate?
        TODO: https://en.wikipedia.org/wiki/Haversine_formula
        """
        lat = self.home['lat'] + Y/111111
        lon = self.home['lon'] + X/(111111 * math.cos(math.radians(self.home['lat'])))
        
        #dronekit.LocationLocal()?
        
        return dronekit.Command(0,0,0, dronekit.mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        dronekit.mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, lat, lon, altitude)


    def goto_gps_cmd(self, lat, long, altitude):
        """ 
        command to go to co-ords at altitude 
        https://dronekit-python.readthedocs.io/en/latest/automodule.html#dronekit.CommandSequence
        """
        return dronekit.Command(0,0,0, dronekit.mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        dronekit.mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, lat, long, altitude)


    def command(self, vehicle: dronekit.Vehicle, mission: List[Tuple[int,int,int]]):
        """ given a list of waypoint co-ords, upload a mission """
        # get ready
        cmds = vehicle.commands
        cmds.download()
        cmds.wait_ready() 
        cmds.clear()
        # list commands
        for waypoint in mission:
            cmds.add(self.goto_cmd(*waypoint))
        cmds.upload() # Send commands


    def takeoff(self):
        """ take off checks etc? """
        pass


    def is_position_reached(self, target_position, tolerance) -> bool:
        """ given a position, have we reached it """
        pass


    def release_payload(self):
        """ set the payload release channel to high """
        self.vehicle.channels.overrides = {'9': 2000}
        time.sleep(0.2)
        self.vehicle.channels.overrides = {}


    def distance_to_current_waypoint(self):
        """
        Gets distance in metres to the current waypoint.
        It returns None for the first waypoint (Home location).
        https://dronekit-python.readthedocs.io/en/latest/guide/auto_mode.html
        """
        nextwaypoint=self.vehicle.commands.next
        if nextwaypoint ==0:
            return None
        missionitem=self.vehicle.commands[nextwaypoint-1] #commands are zero indexed
        lat=missionitem.x
        lon=missionitem.y
        alt=missionitem.z
        targetWaypointLocation=LocationGlobalRelative(lat,lon,alt)
        distancetopoint = self.get_distance_metres(self.vehicle.location.global_frame, targetWaypointLocation)
        return distancetopoint


    def get_distance_metres(self, aLocation1, aLocation2):
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




"""
MISSION SPECIFICS - may change this to JSON
"""

# need to set everything since current parameters are unknown
START_PARAMETERS = {
    "TAKEOFF_ALT": 20,
    "TKOFF_ROTATE_SPD": 15,
    "LEVEL_ROLL_LIMIT": 30,
    
    "USE_REV_THRUST": 0,
    "THR_MIN": 0,
    "TKOFF_THR_MAX": 75,
    
    "WP_RADIUS": 5, #TEST
    "WP_MAX_RADIUS": 0, #TEST
    "STALL_PREVENTION": 1,
    "ARSPD_FBW_MIN": 14.7,
    "ARSPD_FWB_MAX": 30,
    "FS_LONG_ACTN": 2,
    "FS_LONG_TIMEOUT": 5,
    "FS_GCS_ENABLE": 2,
    "ARSPD_USE": 1,
    "ARSPD_SKIP_CAL": 0,
    
    "BATT_MONITOR": 4,
    "BATT_CAPACITY": 3900,
    "BATT_VOLT_PIN": 2, #TEST
    "BATT_CURR_PIN": 3, #TEST
    "BATT_VOLT_MULT": 10.1,
    "BATT_AMP_PERVLT": 17,
    "BATT_LOW_VOLT": 19.8,
    "BATT_FS_LOW_ACT": 1,
    
    "LAND_SLOPE_RECALC": 2,
    "LAND_FLARE_ALT": 2,
    #TEST "LAND_PF_ALT":
    #TEST "LAND_PF_ARSPD":
    "LAND_DISARMDELAY": 10,
    "LAND_THEN_NEUTRAL": 5,
    #TEST "LAND_FLAP_PERCNT":
    "LAND_TYPE": 0,
    
    "RNGFND1_TYPE": 14,
    "RNGFND1_ORIENT": 25,
    "RNGFND_ADDR": 49,
    "RNGFND_MIN_CM": 50,
    "RNGFND_MAX_CM": 11000,
    
    "SERVO_AUTO_TRIM": 1,
    "TKOFF_ALT": 20,
    "TKOFF_LVL_PITCH": 11,
    "SOAR_ENABLE": 0,
    "TECS_SPDWEIGHT": 1,
}

NON_PAYLOAD_PARAMETERS: Dict[str, int] = {
    "TKOFF_THR_MAX": 60,
}

GLIDE_PARAMETERS: Dict[str, int] = {
    "SOAR_ENABLE": 1,
    "TECS_SPDWEIGHT": 2,
    "SOAR_VSPEED": 50,
    "SOAR_ALT_CUTOFF": 20, #confirm
    "SOAR_ALT_MIN": 0,
}

RESET_GLIDE_PARAMETERS: Dict[str, int] = {
    "SOAR_ENABLE": 0,
    "TECS_SPDWEIGHT": 1,
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

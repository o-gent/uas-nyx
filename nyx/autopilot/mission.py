"""
ardupilot mission structure
you'll need the SITL installed to test this, i'd recommend using WSL 
"""

import math
import os
import platform
import time
import csv
from typing import Dict, List, SupportsIndex, SupportsInt, Tuple, Generator, Union

import dronekit
from dronekit.atributes import LocationGlobal, LocationGlobalRelative, LocationLocal
from pymavlink import mavutil

from nyx.utils import logger


class Mission():

    def __init__(self, sim:bool, config:dict):
        (self.vehicle, self.home) = self.connect(sim)
        self.config = config


    def connect(self, sim:bool) -> Tuple[dronekit.Vehicle, Dict[str, int]]:
        """
        Connect to the vehicle, check information is returned then return the object and home location
        """

        logger.info("connecting to vehicle")
        if sim:
            logger.info("simulated vehicle")
            connection_string = '127.0.0.1:14550'
        else:
            logger.info("real vehicle")
            
            if platform.system() == "Linux":
                logger.info("on linux")
                connection_string = '/dev/ttyACM0'
            else:
                logger.info("on windows")
                connection_string = "COM"+input("enter COM number ->")

        

        vehicle = dronekit.connect(connection_string, wait_ready=True)

        waiting = True
        while waiting:
            if vehicle.armed != None:
                waiting = False
                logger.info("waiting for dronekit information")
                time.sleep(1)

        try:
            home = {
                'lat': vehicle.home_location.lat, 
                'lon': vehicle.home_location.lon, 
                'alt': vehicle.home_location.alt
            }
        except:
            logger.info("GPS not connected?")
            home = {
                'lat':0,
                'lon':0,
                'alt':0
            }

        logger.info("connection complete")

        return vehicle, home


    def parameters_set(self, parameters) -> Generator[bool, None, None]:
        """ 
        set a list of parameters during flight and make sure they have been set, needs to complete gradually 
        https://dronekit-python.readthedocs.io/en/latest/guide/vehicle_state_and_parameters.html#vehicle-state-parameters
        """

        logger.info("starting parameter setting..")
        
        for parameter in parameters.keys():
            
            # saves a bit of time if the parameter is already correct and checks param exists
            if self.vehicle.parameters.get(parameter) == None:
                logger.info(f"parameter {parameter} doesn't exist")
                continue

            else:
                condition = True

                while condition:

                    # When fetching floats from ardupilot, they will be full floats
                    # i.e we have 10.1 vs ardupilot having 10.100000381469727
                    if type(parameters.get(parameter)) == float:
                        decimal_places = str(parameters.get(parameter))[::-1].find(".")
                        if round(self.vehicle.parameters.get(parameter), decimal_places) != parameters.get(parameter):
                            condition = True
                        else:
                            condition = False
                    
                    # dronekit/ardupilot seems to report some int parameters as X.0
                    elif type(self.vehicle.parameters.get(parameter)) == int:
                        if float(self.vehicle.parameters.get(parameter)) != parameters.get(parameter):
                            condition = True
                        else:
                            condition = False

                    # if there's nothing weird going on
                    else:
                        if self.vehicle.parameters.get(parameter) != parameters.get(parameter):
                            condition = True
                        else:
                            condition = False

                    if condition:
                        logger.info(f"setting {parameter} to {parameters.get(parameter)}")
                        self.vehicle.parameters[parameter] = parameters.get(parameter)
                        time.sleep(0.1)
                    yield False


            logger.info(f"parameter {parameter} is correct")
            # still need to set more parameters
            yield False
        
        # all parameters set
        logger.info("all parameters set")
        yield True


    def grid_search(self, polygon):
        """ 
        UNIMPLIMENTED
        given a polygon edge, generate a waypoint path to follow 
        """
        pass


    def rel_waypoint(self, X, Y, relalt):
        """ 
        command which accepts relative co-ordinates from the point of launch 
        tried to use MAV_FRAME_LOCAL_NED, created upload issues so that didn't work
        https://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
        conversion maybe accurate?
        TODO: https://en.wikipedia.org/wiki/Haversine_formula
        """

        location = self.local_location(X, Y, relalt)
        lat = location.lat
        lon = location.lon
        altitude = location.alt
        
        return dronekit.Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
        mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, lat, lon, altitude)


    def waypoint(self, lat, long, altitude):
        """
        MODE 16
        command to go to co-ords at altitude 
        https://dronekit-python.readthedocs.io/en/latest/automodule.html#dronekit.CommandSequence
        """
        return dronekit.Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, lat, long, altitude)
    

    def land(self, lat, long):
        """
        MODE 21
        https://ardupilot.org/copter/docs/common-mavlink-mission-command-messages-mav_cmd.html
        """
        return dronekit.Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, 0, 0, lat, long, 0)

    
    def rel_land(self, X, Y):
        """ 
        command which accepts relative co-ordinates from the point of launch 
        """
        location = self.local_location(X, Y, 0)
        lat = location.lat
        lon = location.lon

        return self.land(lat,lon)

    
    def take_off(self, altitude):
        """
        MODE 22
        https://ardupilot.org/copter/docs/common-mavlink-mission-command-messages-mav_cmd.html
        """
        return dronekit.Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, altitude)
    

    def loiter_to_alt(self, X, Y, altitude):
        """
        MODE 31
        """
        location = self.local_location(X, Y, altitude)
        
        lat = location.lat
        lon = location.lon
        alt = location.alt
        
        return dronekit.Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_LOITER_TO_ALT, 0, 0, 0, 0, 0, 0, lat, lon, alt)


    def command(self, mission: List[dronekit.Command]):
        """ 
        given a list of commands, upload a mission and execute the mission
        """
        logger.info("Starting new mission, clearing old one")
        cmds = self.vehicle.commands
        cmds.download()
        cmds.wait_ready() 
        cmds.clear()

        logger.info(f"sending {len(mission)} waypoints to autopilot")
        for waypoint in mission:
            cmds.add(waypoint) #self.waypoint(*waypoint)
        cmds.upload() # Send commands

        logger.info("running new mission")
        self.vehicle.commands.next=0 # reset mission
        self.vehicle.mode = "AUTO" # just incase
    

    def local_location(self, X, Y, relalt) -> LocationGlobal:
        """ 
        given X, Y distances from home, return the latitude and longitude of this position 
        """
        earth_radius=6378137.0 #Radius of "spherical" earth
        #Coordinate offsets in radians
        dLat = Y/earth_radius
        dLon = X/(earth_radius*math.cos(math.pi*self.home['lon']/180))
        lat = self.home['lat'] + (dLat * 180/math.pi)
        lon = self.home['lon'] + (dLon * 180/math.pi) 
        alt = relalt #self.home['alt'] + relalt

        return LocationGlobal(lat,lon,alt)


    def is_position_reached(self, location:LocationGlobal, tolerance:int=5) -> bool:
        """ 
        given a global position, have we reached it 
        """
        distance = self.get_distance_metres(self.vehicle.location.global_frame, location)
        if  distance < tolerance: 
            logger.info(f"{location} reached")
            return True
        else:
            logger.info(f"{distance}m remaining")
            return False
    

    def is_altitude_reached(self, altitude:int, tolerance:int=5) -> bool:
        """ 
        given an altitude, check if the vehicle is at this altitude, given a tolerance
        """
        delta = abs(altitude - self.vehicle.location.global_relative_frame.alt)
        if  delta < tolerance:
            logger.info(f"{altitude} reached")
            return True
        else:
            logger.info(f"altitude target is {altitude}, delta is {delta}")
            return False


    def close_payload(self):
        """ 
        set the payload release channel to high 
        """
        # self.vehicle.channels.overrides = {'9': 2000}
        # time.sleep(0.2)
        # self.vehicle.channels.overrides = {}

        msg = self.vehicle.message_factory.command_long_encode(
            0,0,
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
            0,
            7, # servo instance number
            850, # PWM
            0,0,0,0,0 # params 3-7 not used
        )
        self.vehicle.send_mavlink(msg)


    def release_payload(self):
        """ 
        set the payload release channel to high 
        """
        # self.vehicle.channels.overrides = {'9': 2000}
        # time.sleep(0.2)
        # self.vehicle.channels.overrides = {}

        msg = self.vehicle.message_factory.command_long_encode(
            0,0,
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
            0,
            7, # servo instance number
            1300, # PWM
            0,0,0,0,0 # params 3-7 not used
        )
        self.vehicle.send_mavlink(msg)


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


    @staticmethod
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

    
    @staticmethod
    def load_waypoints(waypoint_file:str) -> List[dronekit.Command]:
        """
        Load commands from a mission planner generated waypoint file
        """
        file=open(waypoint_file,'r') 
        read=list(csv.reader(file, delimiter='\t')) # Exports to list of lists of tab seperated waypoint file using csv module
        read.pop(0) # Removes first line

        wp_parameters=['index','current_wp','coord_frame','command','param1','param2','param3','param4','lat','long','alt','auto_continue']
        waypoint_list=[]
        for waypoint in range(len(read)):   # For each row (waypoint)
            waypoint_dict={}
            for param in range(len(read[waypoint])):    # For each column (parameter)
                waypoint_dict[wp_parameters[param]]=read[waypoint][param]   # Writes parameter value and name to dict

            logger.info(f"loaded waypoint {waypoint_dict}")

            cmd = dronekit.Command(
                0, 0, 0, 
                int(waypoint_dict["coord_frame"]), int(waypoint_dict["command"]),
                0, 0,
                float(waypoint_dict["param1"]), float(waypoint_dict["param2"]), float(waypoint_dict["param3"]), float(waypoint_dict["param4"]),
                float(waypoint_dict["lat"]), float(waypoint_dict["long"]), float(waypoint_dict["alt"])
            )
            waypoint_list.append(cmd) # Appends list with dicts
        file.close()

        return waypoint_list

    
if __name__ == "__main__":
    # assumes SITL
    # an absolute pain but it works..
    #os.system("""powershell.exe "start wsl '/mnt/c/Users/olive/ardupilot/Tools/autotest/sim_vehicle.py -v ArduPlane'" """)
    os.system("start wsl '/mnt/c/Users/olive/ardupilot/Tools/autotest/sim_vehicle.py -v ArduPlane'")

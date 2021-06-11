""" 
entry point for the program
co-ordinate everything

The loop format creates some issues, makes it difficut to pass in and out "global" variables
Could use a class to keep track of these things
May have to use globals..

"""

import time
from typing import Callable, Dict

from dronekit.atributes import LocationGlobal, LocationGlobalRelative, LocationLocal

from nyx.bomb_computer import drop_point
from nyx import camera, mission, state, target_recognition
from nyx import mission  # contains the vehicle variable
from nyx.utils import logger, target_loop
from nyx.state import *  # for all the state names


class Main():

    def __init__(self, sim = True):
        self.state_manager = state.State()
        self.mission_manager = mission.Mission(sim)
        self.camera = camera.CameraStream()

        self.state_manager.change_state(PRE_FLIGHT_CHECKS)

            # each stage has its own loop and checks if it should transition to the next stage
        self.states: Dict[str, Callable] = {
            PRE_FLIGHT_CHECKS: self.pre_flight_checks,
            WAIT_FOR_ARM: self.wait_for_arm,
            TAKE_OFF_ONE: self.take_off_one,
            PAYLOAD_WAYPOINTS: self.payload_waypoints,
            PREDICT_PAYLOAD_IMPACT: self.predict_payload_impact,
            DROP_BOMB: self.drop_bomb,
            CLIMB_AND_GLIDE: self.climb_and_glide,
            LAND_ONE: self.land_one,
            WAIT_FOR_CLEARANCE: self.wait_for_clearance,
            TAKE_OFF_TWO: self.take_off_two,
            SPEED_TRAIL: self.speed_trial,
            AREA_SEARCH: self.area_search,
            LAND_TWO: self.land_two,
            END: self.end
        }
        

    def pre_flight_checks(self) -> bool:
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

        # Make sure parameters are correct
        
        parameter_setter = self.mission_manager.parameters_set(self.mission_manager.config.get("START_PARAMETERS"))
        setting_parameters = False
        while not setting_parameters:
            setting_parameters = next(parameter_setter)
            time.sleep(0.1)

        self.state_manager.change_state(WAIT_FOR_ARM)
        return True


    @target_loop
    def wait_for_arm(self) -> bool:
        """
        check periodically for vehicle arming, proceed once observed
        state changes:
            - take_off_one
        """
        if self.mission_manager.vehicle.armed == True:
            self.state_manager.change_state(TAKE_OFF_ONE)
            return True
        logger.info("waiting for arm..")
        return False


    def take_off_one(self) -> bool:
        """
        start take-off sequence, proceed once target height reached
        state changes:
            - payload_waypoints
        """
        self.mission_manager.vehicle.mode = "TAKEOFF"
        
        @target_loop
        def loop():
            if self.mission_manager.vehicle.mode != "AUTO":
                self.mission_manager.vehicle.mode = "TAKEOFF"
            if -self.mission_manager.vehicle.location.local_frame.down >=20:
                return True
            else:
                logger.info(f"takeoff status: height is {self.mission_manager.vehicle.location.local_frame.down}")

        loop()
        self.state_manager.change_state(PAYLOAD_WAYPOINTS)
        return True


    def payload_waypoints(self) -> bool:
        """ 
        this one has a single running setup phase
        state changes:
            - predict_payload_impact
        """
        # add the waypoints
        self.mission_manager.command([(400,400,40)])

        @target_loop
        def loop():
            print(f"actual location {self.mission_manager.vehicle.location.local_frame}")
            # could maybe do is final waypoint reached using the waypoint system
            if self.mission_manager.is_position_reached(self.mission_manager.local_location(400,400,40), 20):
                return True
            return False
        
        loop()
        self.state_manager.change_state(PREDICT_PAYLOAD_IMPACT)
        return True


    @target_loop
    def predict_payload_impact(self) -> bool:
        """ 
        use a wind speed / direction prediction to predict bomb impact
        https://ardupilot.org/dev/docs/ekf2-estimation-system.html 
        """
        wind_bearing = self.mission_manager.vehicle.wind.wind_direction - self.mission_manager.vehicle.heading
        # get the latest position requirement
        aim_X, aim_Y = drop_point(
            self.mission_manager.config.get("TARGET_LOCATION"),
            self.mission_manager.vehicle.location._alt,
            self.mission_manager.vehicle.groundspeed,
            self.mission_manager.vehicle.wind.wind_speed,
            wind_bearing
            )
        # check how close we are to this position
        
        if self.mission_manager.is_position_reached((0,0), 2):
            self.state_manager.change_state(DROP_BOMB)
            return True
        # aim to go to this position
        return False


    def drop_bomb(self) -> bool:
        self.state_manager.change_state(CLIMB_AND_GLIDE)
        return True


    @target_loop
    def climb_and_glide(self) -> bool:
        self.state_manager.change_state(LAND_ONE)
        return True


    @target_loop
    def land_one(self) -> bool:
        self.state_manager.change_state(WAIT_FOR_CLEARANCE)
        return True


    @target_loop
    def wait_for_clearance(self) -> bool:
        self.state_manager.change_state(TAKE_OFF_TWO)
        return True


    @target_loop
    def take_off_two(self) -> bool:
        self.state_manager.change_state(SPEED_TRAIL)
        return True


    def speed_trial(self) -> bool:
        # set up speed trail waypoints and start waypoints

        self.camera.start()

        results = []

        @target_loop(target_time=0.2)
        def loop() -> bool:
            image = next(self.camera.take_image_test())
            result = target_recognition.findCharacters(image)
            if len(result) == 1:
                # figure out the image position
                target_position = target_recognition.triangulate(
                    (self.mission_manager.vehicle.location.local_frame.north, self.mission_manager.vehicle.location.local_frame.east),
                    result["centre"],
                    self.mission_manager.vehicle.location.local_frame.down,
                    self.mission_manager.vehicle.heading
                )
                results.append([target_position, result])
                logger.info(f"{target_position}, {result['charachter']}, {result['colour']}")
            
            if self.mission_manager.is_position_reached((0,0), 5):
                return True

            if len(results) >= 3:
                # found all targets
                return True
            
            return False
        
        loop()

        self.state_manager.change_state(AREA_SEARCH)
        return True


    @target_loop
    def area_search(self) -> bool:

        self.camera.stop()

        self.state_manager.change_state(LAND_TWO)
        return True


    @target_loop
    def land_two(self) -> bool:
        self.state_manager.change_state(END)
        return True


    @target_loop
    def end(self) -> bool:
        self.mission_manager.vehicle.armed = False
        self.mission_manager.vehicle.close()
        return True


    def run(self):
        """ start the mission routine """

        logger.info("warmed up, engaging improbability drive")

        try:
            while True:
                logger.info(f"running {self.state_manager.state}")
                self.states[self.state_manager.state]()
        except:
            # a bruh moment for sure
            self.mission_manager.vehicle.simple_goto(self.mission_manager.vehicle.home_location)
            logger.critical("main loop crashed, exiting")
            raise Exception("balls")
    
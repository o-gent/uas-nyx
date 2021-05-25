""" 
entry point for the program
co-ordinate everything

The loop format creates some issues, makes it difficut to pass in and out "global" variables
Could use a class to keep track of these things
May have to use globals..

"""

import time
from typing import Callable, Dict

from nyx.bomb_computer import drop_point
from nyx import camera, mission, state, target_recognition
from nyx import mission  # contains the vehicle variable
from nyx.utils import logger, target_loop
from nyx.state import *  # for all the state names


class Main():

    def __init__(self):
        self.state_manager = state.State()
        self.mission = mission.Mission()
        self.camera = camera.CameraStream()

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

        self.state_manager.change_state(WAIT_FOR_ARM)
        return True


    @target_loop
    def wait_for_arm(self) -> bool:
        """
        check periodically for vehicle arming, proceed once observed
        state changes:
            - take_off_one
        """
        if self.mission.vehicle.armed == True:
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
        self.mission.vehicle.mode = "TAKEOFF"
        
        @target_loop
        def loop():
            if mission.vehicle.mode != "AUTO":
                mission.vehicle.mode = "TAKEOFF"
            if -mission.vehicle.location.local_frame.down >=20:
                return True
            else:
                logger.info(f"takeoff status: height is {mission.vehicle.location.local_frame.down}")

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
        

        @target_loop
        def loop():
            if mission.is_position_reached(mission.TARGET_LOCATION, 100):
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
        wind_bearing = self.mission.vehicle.wind.wind_direction - self.mission.vehicle.heading
        # get the latest position requirement
        aim_X, aim_Y = drop_point(
            mission.TARGET_LOCATION,
            self.mission.vehicle.location._alt,
            self.mission.vehicle.groundspeed,
            self.mission.vehicle.wind.wind_speed,
            wind_bearing
            )
        # check how close we are to this position
        
        if self.mission.is_position_reached((0,0), 2):
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

        results = []

        @target_loop(target_time=0.2)
        def loop() -> bool:
            image = next(self.camera.take_image_test())
            result = target_recognition.findCharacters(image)
            if len(result) == 1:
                # figure out the image position
                target_position = target_recognition.triangulate(
                    (self.mission.vehicle.location.local_frame.north, self.mission.vehicle.location.local_frame.east),
                    result["centre"],
                    self.mission.vehicle.location.local_frame.down,
                    self.mission.vehicle.heading
                )
                results.append([target_position, result])
                logger.info(f"{target_position}, {result['charachter']}, {result['colour']}")
            
            if self.mission.is_position_reached((0,0), 5):
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
        self.state_manager.change_state(LAND_TWO)
        return True


    @target_loop
    def land_two(self) -> bool:
        self.state_manager.change_state(END)
        return True


    @target_loop
    def end(self) -> bool:
        self.mission.vehicle.armed = False
        self.mission.vehicle.close()
        return True



    def run(self):
        """ start the mission routine """
        mission.connect()
        self.start()

        logger.info("ready, proceeding to main")

        try:
            while True:
                self.states[self.state_manager.state]()
        except:
            # a bruh moment for sure
            mission.vehicle.simple_goto(mission.vehicle.home_location)
            logger.critical("main loop crashed, exiting")
            raise Exception("balls")


if __name__ == "__main__":
    main = Main()
    main.run()
    
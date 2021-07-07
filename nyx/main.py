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
from pymavlink import mavutil

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
        

    def pre_flight_checks(self):
        """ 
        user prompt to ensure the vehicle is ready
        not a loop
        state changes:
            - wait_for_arm
        """
        # make dronekit is working correctly & vehicle is ready
        while self.mission_manager.vehicle.is_armable == False:
            logger.info("Vehicle initialising")
            time.sleep(1)
        logger.info("Vehicle finished initialising, proceeding")

        # Make sure parameters are correct
        parameter_setter = self.mission_manager.parameters_set(self.mission_manager.config.get("START_PARAMETERS"))
        setting_parameters = False
        while not setting_parameters:
            setting_parameters = next(parameter_setter)
            time.sleep(0.1)

        # check if values make sense, level at 0 altitude etc


        # then do control surface checks


        self.state_manager.change_state(WAIT_FOR_ARM)


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
        # upload payload mission including takeoff

        @target_loop
        def loop():
            print(f"actual location {self.mission_manager.vehicle.location.local_frame}")
            # could maybe do is final waypoint reached using the waypoint system
            if self.mission_manager.is_position_reached(self.mission_manager.local_location(400,400,40), 20):
                return True
            return False

        self.state_manager.change_state(PREDICT_PAYLOAD_IMPACT)
        return True


    def payload_waypoints(self) -> bool:
        """ 
        SKIPPED
        """
        pass


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
            # release the payload
            self.mission_manager.release_payload()

            self.state_manager.change_state(CLIMB_AND_GLIDE)
            return True

        # aim to go to this position
        self.mission_manager.vehicle.simple_goto()
        
        # haven't reached the location yet
        return False


    def drop_bomb(self):
        """ SKIPPED """
        pass


    @target_loop
    def climb_and_glide(self) -> bool:
        """ climb to 400ft over landing strip then glide and land """
        # set waypoints


        # set parameters for glide once at 400ft and in descent phase
        self.mission_manager.parameters_set(self.mission_manager.config.get("GLIDE_PARAMETERS"))


        self.state_manager.change_state(WAIT_FOR_CLEARANCE)
        return True


    @target_loop
    def land_one(self) -> bool:
        """ SKIPPED """
        self.state_manager.change_state(WAIT_FOR_CLEARANCE)
        return True


    @target_loop
    def wait_for_clearance(self) -> bool:
        # reset parameters from gliding
        self.mission_manager.parameters_set(self.mission_manager.config.get("RESET_GLIDE_PARAMETERS"))

        # wait for arm state again


        self.state_manager.change_state(TAKE_OFF_TWO)
        return True


    @target_loop
    def take_off_two(self) -> bool:
        # upload the new mission

        self.state_manager.change_state(SPEED_TRAIL)
        return True


    def speed_trial(self) -> bool:
        # set up speed trail waypoints and start waypoints

        self.camera.start()

        results = []

        @target_loop(target_time=0.2)
        def loop() -> bool:
            
            image = next(self.camera.take_image_test())
            # need to record the location of the image now


            image_results = target_recognition.find_targets(image)
            

            for result in image_results:
                # save the image
                cv2.imwrite("", image)

                # figure out the image position
                target_position = target_recognition.triangulate(
                    (self.mission_manager.vehicle.location.local_frame.north, self.mission_manager.vehicle.location.local_frame.east),
                    result.centre,
                    self.mission_manager.vehicle.location.local_frame.down,
                    self.mission_manager.vehicle.heading
                )
                result.position = target_position
                results.append(result)
                logger.info(result)
            
            if self.mission_manager.is_position_reached((0,0), 5):
                # this position should be the end of the area search
                self.camera.stop()

                # now figure out what letters are in the images while we are still flying
                for letter_image in results:
                    pass

                return True
            
            return False
        
        loop()

        self.state_manager.change_state(END)
        return True


    @target_loop
    def area_search(self) -> bool:
        """ SKIPPED """

        self.camera.stop()

        self.state_manager.change_state(LAND_TWO)
        return True


    @target_loop
    def land_two(self) -> bool:
        """ SKIPPED """
        self.state_manager.change_state(END)
        return True


    @target_loop
    def end(self) -> bool:
        logger.info("this is the end, hold your breath and count to ten")
        self.mission_manager.vehicle.armed = False
        self.mission_manager.vehicle.close()
        
        # print the mission summary
        logger.info(self)
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
    
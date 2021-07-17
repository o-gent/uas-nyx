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
import cv2

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
        # parameter_setter = self.mission_manager.parameters_set(self.mission_manager.config.get("START_PARAMETERS"))
        # setting_parameters = False
        # while not setting_parameters:
        #     setting_parameters = next(parameter_setter)
        #     time.sleep(0.1)

        self.state_manager.change_state(WAIT_FOR_ARM)


    @target_loop(target_time=2.0)
    def wait_for_arm(self) -> bool:
        """
        check periodically for vehicle arming, proceed once observed
        state changes:
            - take_off_one
        """
        if self.mission_manager.vehicle.armed == True:
            logger.info("vehicle armed, starting mission routine")
            self.state_manager.change_state(TAKE_OFF_ONE)
            return True
        time.sleep(1)
        logger.info("waiting for arm..")
        return False


    def take_off_one(self) -> bool:
        """
        start take-off sequence, proceed once target height reached
        state changes:
            - payload_waypoints
        """
        # upload payload mission including takeoff

        m = self.mission_manager.load_waypoints("./core_mission.waypoints")
        self.mission_manager.command(m)

        self.state_manager.change_state(CLIMB_AND_GLIDE)
        return True


    def payload_waypoints(self) -> bool:
        """ 
        SKIPPED
        """
        pass


    # @target_loop
    def predict_payload_impact(self):
        """ 
        SKIPPED
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
        
        # if self.mission_manager.is_position_reached((0,0), 2):
        #     # release the payload
        #     self.mission_manager.release_payload()

        #     self.state_manager.change_state(CLIMB_AND_GLIDE)
        #     return True

        # aim to go to this position
        # self.mission_manager.vehicle.simple_goto()
        
        # haven't reached the location yet
        return wind_bearing, aim_X, aim_Y


    def drop_bomb(self):
        """ SKIPPED """
        pass


    def climb_and_glide(self) -> bool:
        """ 
        climb to 400ft over landing strip then glide and land
        """

        self.times_reached = 0
        position = LocationGlobalRelative(52.780880,-0.7083570)

        @target_loop(target_time=0.2)
        def payload_release():
            global times_reached
            if self.mission_manager.is_position_reached(position):
                logger.info(f"position reached {self.times_reached} times")
                self.times_reached+=1
            if self.times_reached == 2:
                self.mission_manager.release_payload()
                return True
            logger.info("payload position not reached")
            return False
        
        @target_loop(target_time=2.0)
        def check_glide_start():
            """ once we reach gliding height, set gliding parameters """
            if self.mission_manager.is_altitude_reached(120,5):
                logger.info("altitude reached")
                
                time.sleep(5)

                # change parameters to glide
                logger.info("starting glide parameter set")
                
                parameter_setter = self.mission_manager.parameters_set(self.mission_manager.config.get("GLIDE_PARAMETERS"))
                setting_parameters = False
                while not setting_parameters:
                    setting_parameters = next(parameter_setter)
                    time.sleep(0.1)
                logger.info("parameters set")

                time.sleep(20)
                # change parmeters back
                parameter_setter = self.mission_manager.parameters_set(self.mission_manager.config.get("RESET_GLIDE_PARAMETERS"))
                setting_parameters = False
                while not setting_parameters:
                    setting_parameters = next(parameter_setter)
                    time.sleep(0.1)
                logger.info("parameters set")

                return True

            else:
                time.sleep(1)
                logger.info(f"waiting for glide altitude not at 120m, at {self.mission_manager.vehicle.location.global_relative_frame.alt}")
                try:
                    logger.info(self.predict_payload_impact())
                except:
                    logger.info("payload prediction fail")
                return False

        
        payload_release()
        check_glide_start()

        while self.mission_manager.vehicle.armed == True:
            time.sleep(1)
            logger.info("waiting for landing, currently armed")
            
        self.state_manager.change_state(WAIT_FOR_CLEARANCE)
        return True


    @target_loop
    def land_one(self) -> bool:
        """ SKIPPED """
        self.state_manager.change_state(WAIT_FOR_CLEARANCE)
        return True


    def wait_for_clearance(self) -> bool:
        # reset parameters from gliding
        logger.info("starting glide parameter RESET")
        parameter_setter = self.mission_manager.parameters_set(self.mission_manager.config.get("RESET_GLIDE_PARAMETERS"))
        setting_parameters = False
        while not setting_parameters:
            setting_parameters = next(parameter_setter)
            time.sleep(0.1)
        logger.info("parameters set")

        @target_loop(target_time=2.0)
        def wait():
            # wait for arm state again
            if self.mission_manager.vehicle.armed == True:
                logger.info("vehicle armed, starting optional mission routine")
                self.state_manager.change_state(TAKE_OFF_ONE)
                return True
            
            time.sleep(1)
            logger.info("waiting for arm..")
        
        wait()

        self.state_manager.change_state(TAKE_OFF_TWO)
        return True


    @target_loop
    def take_off_two(self) -> bool:
        # upload the new mission
        m = self.mission_manager.load_waypoints("./optional_mission.waypoints")
        self.mission_manager.command(m)

        self.state_manager.change_state(SPEED_TRAIL)
        return True


    def speed_trial(self) -> bool:
        # set up speed trail waypoints and start waypoints

        self.camera.start()

        results = []

        @target_loop(target_time=0.2)
        def loop() -> bool:
            
            image = next(self.camera.take_image_test())
            
            t = str(time.time()).split(".")[0] + "-" + str(time.time()).split(".")[1]
            cv2.imwrite(time.strftime(f"targets/%m-%d-%H:%M:%S-{t}.jpg"),image)


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

        logger.info(results)

        self.state_manager.change_state(END)
        return True


    @target_loop
    def area_search(self) -> bool:
        """ SKIPPED """

        self.state_manager.change_state(LAND_TWO)
        return True


    @target_loop
    def land_two(self) -> bool:
        """ SKIPPED """
        self.state_manager.change_state(END)
        return True


    def end(self) -> bool:
        logger.info("this is the end, hold your breath and count to ten")
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
        except KeyboardInterrupt:
            self.end()
        except:
            # a bruh moment for sure
            self.mission_manager.vehicle.simple_goto(self.mission_manager.vehicle.home_location)
            logger.critical("main loop crashed, exiting")
            raise Exception("balls")
    
import time
from typing import Callable, Dict

import cv2
from dronekit.atributes import LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil

from nyx import camera
from nyx import config
from nyx.autopilot import state, mission
from nyx.autopilot.bomb_computer import drop_point
from nyx.autopilot.state import StateList
from nyx.utils import logger, target_loop
from nyx.autopilot.config import load_mission_parameters


class Main:
    """
    Co-ordinates mission stages
    """
    
    def __init__(self, sim = True):
        """
        
        """
        self.config = load_mission_parameters()
        self.mission_manager = mission.Mission(sim, config)
        self.state_manager = state.State(config)
        self.camera = camera.CameraStream()
        
        # Dictionary of state methods, works with self.run
        self.states: Dict[str, Callable] = {
            StateList.PRE_FLIGHT_CHECKS: self.pre_flight_checks,
            StateList.WAIT_FOR_ARM: self.wait_for_arm,
            StateList.TAKE_OFF_ONE: self.take_off_one,
            StateList.PAYLOAD_WAYPOINTS: self.payload_waypoints,
            StateList.PREDICT_PAYLOAD_IMPACT: self.predict_payload_impact,
            StateList.DROP_BOMB: self.drop_bomb,
            StateList.CLIMB_AND_GLIDE: self.climb_and_glide,
            StateList.LAND_ONE: self.land_one,
            StateList.WAIT_FOR_CLEARANCE: self.wait_for_clearance,
            StateList.TAKE_OFF_TWO: self.take_off_two,
            StateList.SPEED_TRAIL: self.speed_trial,
            StateList.AREA_SEARCH: self.area_search,
            StateList.LAND_TWO: self.land_two,
            StateList.END: self.end
        }

        # start the process
        self.state_manager.change_state(StateList.PRE_FLIGHT_CHECKS)
    
    
    def run(self):
        """ 
        Run the current mission stage and manage any overall errors
        """

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
        

    def pre_flight_checks(self):
        """
        MISSION_STAGE
        
        user prompt to ensure the vehicle is ready
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
            time.sleep(0.05)

        self.state_manager.change_state(StateList.WAIT_FOR_ARM)


    @target_loop(target_time=2.0)
    def wait_for_arm(self) -> bool:
        """
        MISSION_STAGE

        check periodically for vehicle arming, proceed once observed
        """
        if self.mission_manager.vehicle.armed == True:
            logger.info("vehicle armed, starting mission routine")
            self.state_manager.change_state(StateList.TAKE_OFF_ONE)
            return True
        time.sleep(1)
        logger.info("waiting for arm..")
        return False


    def take_off_one(self):
        """
        MISSION_STAGE

        start take-off sequence, proceed once target height reached
        """
        # upload payload mission including takeoff

        m = self.mission_manager.load_waypoints("./core_mission.waypoints")
        self.mission_manager.command(m)

        self.state_manager.change_state(StateList.PAYLOAD_WAYPOINTS)


    def payload_waypoints(self):
        """ 
        MISSION_STAGE
        
        Waits until we are close to the drop location, then passes onto payload drop prediction
        """
        self.times_reached = 0
        position = LocationGlobalRelative(52.780880,-0.7083570)

        @target_loop(target_time=0.1)
        def payload_release():
            
            if self.mission_manager.is_position_reached(position,tolerance=50):
                logger.info(f"position reached {self.times_reached} times")
                self.times_reached += 1
            
            elif self.times_reached == 2:
                self.state_manager.change_state(StateList.PREDICT_PAYLOAD_IMPACT)
                return True
            
            else:
                logger.info("payload position not reached")
                return False
        
        payload_release()


    @target_loop(target_time=0.1)
    def predict_payload_impact(self) -> bool:
        """ 
        MISSION_STAGE

        use a wind speed / direction prediction to predict bomb impact
        https://ardupilot.org/dev/docs/ekf2-estimation-system.html

        Using simple_goto() will change the vehicle state to GUIDED
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
        
        drop_location = self.mission_manager.local_location(aim_X, aim_Y)

        self.mission_manager.vehicle.simple_goto(drop_location)
        
        # check how close we are to this position
        if self.mission_manager.is_position_reached(drop_location, tolerance=5):
            # release the payload
            self.mission_manager.release_payload()

            self.state_manager.change_state(StateList.CLIMB_AND_GLIDE)
            return True
        
        else:
            return False


    @target_loop(target_time=0.2)
    def climb_and_glide(self) -> bool:
        """
        MISSION_STAGE

        climb to 400ft over landing strip then glide and land
        """

        # Now need to upload the glide section of the mission
        # could maybe do this with the config file instead, as the waypoints won't be complicated
        m = self.mission_manager.load_waypoints("./glide.waypoints")
        self.mission_manager.command(m)
        
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
            self.state_manager.change_state(StateList.LAND_ONE)
            return True

        else:
            logger.info(f"waiting for glide altitude not at 120m, at {self.mission_manager.vehicle.location.global_relative_frame.alt}")
            return False


    @target_loop
    def land_one(self) -> bool:
        """ 
        MISSION_STAGE

        when the vehicle has disarmed, we have landed 
        """
        while self.mission_manager.vehicle.armed == True:
            time.sleep(1)
            logger.info("waiting for landing, currently armed")

        self.state_manager.change_state(StateList.WAIT_FOR_CLEARANCE)
        return True


    def wait_for_clearance(self):
        """
        MISSION_STAGE

        Reset parameters for next section of mission
        Then wait until vehicle is armed again
        """
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
                self.state_manager.change_state(StateList.TAKE_OFF_ONE)
                return True
            
            time.sleep(1)
            logger.info("waiting for arm..")
        
        wait()

        self.state_manager.change_state(StateList.TAKE_OFF_TWO)


    @target_loop
    def take_off_two(self) -> bool:
        """
        MISSION_STAGE
        """

        # upload the new mission
        m = self.mission_manager.load_waypoints("./optional_mission.waypoints")
        self.mission_manager.command(m)

        self.state_manager.change_state(StateList.SPEED_TRAIL)
        return True


    def speed_trial(self) -> bool:
        """
        MISSION_STAGE
        """
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

        self.state_manager.change_state(StateList.END)
        return True


    @target_loop
    def area_search(self) -> bool:
        """ SKIPPED """

        self.state_manager.change_state(StateList.LAND_TWO)
        return True


    @target_loop
    def land_two(self) -> bool:
        """ 
        MISSION_STAGE 
        """

        while self.mission_manager.vehicle.armed == True:            
            time.sleep(1)
            logger.info("waiting for landing, currently armed")

        self.state_manager.change_state(StateList.END)
        return True


    def end(self):
        """
        MISSION_STAGE
        """

        logger.info("this is the end, hold your breath and count to ten")
        self.mission_manager.vehicle.close()
        
        # print the mission summary
        logger.info(self)
        return True
    
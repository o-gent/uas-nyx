from nyx import mission
import time


mission_manager = mission.Mission(True)


input("press enter to drop payload")

self.mission_manager.release_payload()

input("press enter to attempt glide")

parameter_setter = mission_manager.parameters_set(mission_manager.config.get("GLIDE_PARAMETERS"))
setting_parameters = False
while not setting_parameters:
    setting_parameters = next(parameter_setter)
    time.sleep(0.1)
logger.info("parameters set")

time.sleep(20)

# change parmeters back
parameter_setter = mission_manager.parameters_set(mission_manager.config.get("RESET_GLIDE_PARAMETERS"))
setting_parameters = False
while not setting_parameters:
    setting_parameters = next(parameter_setter)
    time.sleep(0.1)
logger.info("parameters set")
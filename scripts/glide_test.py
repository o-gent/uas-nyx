import sys
import time
sys.path.append("../")

from nyx import mission

mission_manager = mission.Mission(True)

# parameter_setter = mission_manager.parameters_set(mission_manager.config.get("START_PARAMETERS"))
# setting_parameters = False
# while not setting_parameters:
#     setting_parameters = next(parameter_setter)
#     time.sleep(0.1)

# load in the climb mission
m = [
    mission_manager.take_off(30),
    mission_manager.rel_waypoint(300,300,40),
    mission_manager.loiter_to_alt(0,400,120)
]

mission_manager.command(m)

# now wait until mission complete
while not mission_manager.is_altitude_reached(120,5):
    time.sleep(1)
    pass

# upload the glide mission
m = [
    mission_manager.rel_land(0,0)
]

mission_manager.command(m)

# change parameters to glide
parameter_setter = mission_manager.parameters_set(mission_manager.config.get("GLIDE_PARAMETERS"))
setting_parameters = False
while not setting_parameters:
    setting_parameters = next(parameter_setter)
    time.sleep(0.1)
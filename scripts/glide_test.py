import sys
import time
sys.path.append("../")

from nyx import mission

mission_manager = mission.Mission(True)

parameter_setter = mission_manager.parameters_set(mission_manager.config.get("START_PARAMETERS"))
setting_parameters = False
while not setting_parameters:
    setting_parameters = next(parameter_setter)
    time.sleep(0.1)

while mission_manager.vehicle.armed == False:
    print("waiting for arm..")

print("loading waypoints")
# load in the climb mission
m = mission_manager.load_waypoints("./scripts/glide_test1")

mission_manager.command(m)
print("executed waypoints")

# now wait until mission complete
while not mission_manager.is_altitude_reached(80,5):
    time.sleep(1)
    print(f"not at 80m, at {mission_manager.vehicle.location.global_relative_frame.alt}")
    pass


print("uploading landing")
# upload the glide mission
m = [
    mission_manager.rel_land(0,0)
]

mission_manager.command(m)
print("glide landing executed")

# change parameters to glide
parameter_setter = mission_manager.parameters_set(mission_manager.config.get("GLIDE_PARAMETERS"))
setting_parameters = False
while not setting_parameters:
    setting_parameters = next(parameter_setter)
    time.sleep(0.1)
print("parameters set")


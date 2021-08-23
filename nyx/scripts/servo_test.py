from nyx.autopilot import mission
from nyx.config import load_mission_parameters
import time

mission_manager = mission.Mission(True, load_mission_parameters())

mission_manager.release_payload()

time.sleep(5)

mission_manager.close_payload()
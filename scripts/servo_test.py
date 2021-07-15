from nyx import mission
import time

mission_manager = mission.Mission(True)

mission_manager.release_payload()

time.sleep(5)

mission_manager.close_payload()
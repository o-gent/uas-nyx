# Nyx

## config.json
Stores Ardupilot parameters as well as any program parameters which could change from mission to mission, such as the payload drop point

## __init__.py

## bomb_computer.py


## camera.py
Controls capturing images

see ./scripts/camera_testing.py for useage

camera backends & parameters https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html#ga023786be1ee68a9105bf2e48c700294d
CAP_DSHOW needs to be used for Windows and the ELP 13MP IMX214

VideoCapture docs https://docs.opencv.org/3.4/d8/dfe/classcv_1_1VideoCapture.html#a57c0e81e83e60f36c83027dc2a188e80

## main.py
Class to cordinate the mission stages

MISSION_STAGES are executed depending on the current state. A MISSION_STAGE consists of:

```python
""" VERSION 1, one time action """
def random_mission_stage():
    # carry out an action once

    # move on
    self.state_manager.change_state(StateList.NEW_STATE) # change state


""" VERSION 2, carry out an action every target_time seconds until a condition is met """
@target_loop(target_time=2.0)
def random_mission_stage_2():
    if condition:
        self.state_manager.change_state(StateList.NEW_STATE) # change state
        return True # stop the loop
    else:
        # carry out action (until the condition is met)
        return False # continue the loop
```

@target_loop will execute the function every X seconds, unless the function takes longer than the X sections, in which case it will execute immediatly after the function completes. This means the computer isn't doing unneccessary work, allowing background threads to continue (and sometimes polling something very quickly causes problems)

## mission.py

## nn_ocr.py

## state.py

## target_recognition.py

## utils.py

import erebus.main as main


# tests have to be run in order on a fresh SITL..
# Probably a better way to do this

def test_preflight_checks():
    pass


def test_wait_for_arm():
    # check the SITL is connected
    assert main.mission.vehicle.armed != None 
    
    main.state_manager.change_state(main.WAIT_FOR_ARM)
    assert main.mission.vehicle.armed == False
    
    main.mission.vehicle.armed = True
    while main.mission.vehicle.armed == False:
        main.mission.vehicle.armed = True

    main.states[main.state.state_manager.state]()

    assert main.state_manager.state == main.TAKE_OFF_ONE


def test_take_off_one():

    assert main.state_manager.state == main.TAKE_OFF_ONE

    main.states[main.state.state_manager.state]()
    
    # why the hell is the local frame altitude negative
    assert -main.mission.vehicle.location.local_frame.down >= 20

    pass

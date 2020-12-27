from dataclasses import dataclass
from typing import Tuple
import numpy as np
import math

# constants
MASS = 5.5 # kg
AG = 9.81 # m/s
TIMESTEP = 0.01 # s
CD_vertical = 2.0
CD_horiztonal = 2.0
AREA_vertical = 5.0 # m^2
AERA_horizontal = 5.0 # m^2

history = []


@dataclass
class Bomb:
    """ 
    it's not a bomb (but it is) 
    X, Y are ground position with positive X in direction of the aircraft when dropped.
    Z is height from ground
    """
    time: float
    # distance
    S_x: float
    S_y: float
    S_z: float
    # velocity
    V_x: float
    V_y: float
    V_z: float
    # acceleration
    A_x: float
    A_y: float
    A_z: float
    # drag
    D_x: float
    D_y: float
    D_z: float

    def position(self) -> Tuple[float, float, float]:
        return (self.S_x, self.S_y, self.S_z)
    
    def velocity(self) -> Tuple[float, float, float]:
        return (self.V_x, self.V_y, self.V_z)
    
    def acceleration(self) -> Tuple[float, float, float]:
        return (self.A_x, self.A_y, self.A_z)

    def state(self):
        return np.array([
            [self.S_x, self.V_x, self.A_x],
            [self.S_y, self.V_y, self.A_y],
            [self.S_z, self.V_z, self.A_z]
        ])
    
    def __str__(self):
        return f"""
        position: {self.S_x}, {self.S_y}, {self.S_z} 
        velocity: {self.V_x}, {self.V_y}, {self.V_z}
        acceleration: {self.A_x}, {self.A_y}, {self.A_z}
        """
        

def bomb_drop(height, speed, wind_speed, wind_bearing, debug=False) -> Tuple[float, float]:
    """ 
    Predict the X Y co-ordinate of payload impact
    should probably use https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.odeint.html
    but i don't want to figure it out... 

    height: of drop point in (meters)
    speed: aircraft ground speed in (m/s)
    wind_speed: (m/s)
    wind_bearing: angle difference between aircraft and wind bearing (degrees)

    returns the X,Y co-ord of bomb impact
    """
    wind_x = math.cos(math.radians(wind_bearing)) * wind_speed
    wind_y = math.sin(math.radians(wind_bearing)) * wind_speed
    bomb = Bomb(0, 0, 0, height, speed, 0, 0, 0, 0, AG, 0, 0, 0)

    while bomb.S_z > 0:
        bomb = time_integration(bomb, TIMESTEP, wind_x, wind_y)
        if debug:
            history.append(bomb)

    return bomb.S_x, bomb.S_y


def time_integration(state: Bomb, timestep: float, wind_x:float, wind_y: float) -> Bomb:
    """
    Calculate the next timestep based on the last values
    
    state: all attributes from previous time step
    would like to avoid passing the wind speeds but don't want to use globals

    returns the new state
    """
    # work out airfow vector
    F_x = wind_x + state.V_x
    F_y = wind_y + state.V_y
    F_z = state.V_z

    
    ## resolve Z
    # new height using SUVAT, height decreasing
    state.S_z = state.S_z - (state.V_z * timestep + 0.5 * state.A_z * timestep ** 2.0)
    # vertical speed
    state.V_z = state.V_z + state.A_z * timestep
    # vertical drag force
    state.D_z 

    ## resolve X
    

    ## resolve Y
    

    return state

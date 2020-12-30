"""
To calculate the predicted landing point of the bomb

Currently uses a euler forward method to time integrate the bomb position

TODO:
 - test the speed of prediction
 - change to use a scipy ODE solver
 - refine constants used
 - compare to actual data
"""

from dataclasses import dataclass
from os import stat
from typing import Tuple
import numpy as np
from numpy import array
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from typing import List
import utils


# constants
AG = array([0, 0, -9.81]) # m/s
RHO = 1.225 

MASS = 5.5 # kg
TIMESTEP = 0.01 # s
CD = array([2.0, 2.0, 2.0])
AREA = array([5.0, 5.0, 5.0])

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
    S: array
    # velocity
    V: array
    # acceleration
    A: array
    # drag
    D: array
    # wind speed
    W: array
    
    def __str__(self):
        return f"""
        position: {self.S}
        velocity: {self.V}
        acceleration: {self.A}
        """
        

def bomb_drop(height, speed, wind_speed, wind_bearing, debug=False) -> array:
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
    
    bomb = Bomb(
        0.0, 
        array([0,0,height]), # distance X Y Z
        array([speed,0,0]), # velocity
        array([0,0,0]), # acceleration
        array([0,0,0]),  # drag
        array([wind_x, wind_y, 0]) # wind speed 
    )

    while bomb.S[2] > 0:
        bomb = time_integration(bomb)
        bomb.time += TIMESTEP
        if debug:
            history.append(bomb.__dict__.copy())

    return bomb


def time_integration(state: Bomb) -> Bomb:
    """
    Calculate the next timestep based on the last values
    
    state: all attributes from previous time step

    returns the new state
    """

    # airfow
    F = state.W + state.V
    # distances
    state.S = state.S + (state.V * TIMESTEP + 0.5 * state.A * TIMESTEP ** 2.0)
    # velocities
    state.V = state.V + state.A * TIMESTEP
    
    # wait for the parachute to deploy before calculating drag
    if state.time > 1:
        # drag - sign stuff to put in opposite direction to velocity, probably a better way to do this
        state.D = 0.5 * CD * RHO * -np.sign(F) * (F ** 2) * AREA
    
    # acceleration
    state.A = AG + state.D/MASS
    
    return state


def bomb_plot(history: List[dict]):
    """ 
    given a history, plot it
    """
    # convert history to X, Y, Z arrays
    x, y, z = [], [], []
    for state in history:
        x.append(state['S'][0])
        y.append(state['S'][1])
        z.append(state['S'][2])

    fig = plt.figure()
    
    ax = fig.add_subplot(131, projection='3d')
    ax.plot3D(x,y,z)
    utils.set_axes_equal(ax)

    # er this is doesn't make much sense but yeah
    # https://stackoverflow.com/questions/6063876/matplotlib-colorbar-for-scatter
    ax2 = fig.add_subplot(132)
    ax2.scatter(x,y,c=z, cmap='jet')
    plt.gca().set_aspect('equal', adjustable='box')
    f = plt.scatter(x,y,c=z, cmap='jet')
    plt.colorbar(f)

    ax3 = fig.add_subplot(133)
    ax3.scatter(x,z,c=y, cmap='jet')
    plt.gca().set_aspect('equal', adjustable='box')
    f = plt.scatter(x,z,c=y, cmap='jet')
    plt.colorbar(f)

    plt.show()


if __name__ == "__main__":
    bomb_drop(30,15,2,0, debug=True)
    bomb_plot(history)

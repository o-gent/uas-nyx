"""
To calculate the predicted landing point of the bomb

Currently uses a euler forward method to time integrate the bomb position

TODO:
 - test the speed of prediction ~ 0.011s, fast enough
 - check time step independance
 - change to use a scipy ODE solver
 - refine constants used
 - compare to actual data
 - some funky sign stuff going on - it works though
"""

import math
from dataclasses import dataclass
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from numpy import array, ndarray


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
    S: ndarray
    # velocity
    V: ndarray
    # acceleration
    A: ndarray
    # drag
    D: ndarray
    # wind speed
    W: ndarray
    
    def __str__(self):
        return f"""
        position: {self.S}
        velocity: {self.V}
        acceleration: {self.A}
        """
        

def drop_point(
        target_position: Tuple[float, float],
        height: float,
        speed: float,
        wind_speed: float,
        wind_bearing: int
        ) -> Tuple[float, float]:
    """ 
    return where we should be when dropping the bomb 
    RELATIVE TO HOME POINT
    """
    bomb = bomb_drop(height, speed, wind_speed, wind_bearing)
    landing_position: Tuple[float, float] = (bomb.S[0], bomb.S[1]) # X, Y relative to aircraft
    # calculate drop position
    X = target_position[0] - landing_position[0] 
    Y = target_position[1] - landing_position[1]
    return (X, Y)


def bomb_drop(height, speed, wind_speed, wind_bearing, debug=False) -> Bomb:
    """ 
    Predict the X Y co-ordinate of payload impact
    positive X in direction of aircraft

    should probably use https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.odeint.html
    but i don't want to figure it out... 

    height: of drop point in (meters)
    speed: aircraft ground speed in (m/s)
    wind_speed: (m/s)
    wind_bearing: angle difference between aircraft and wind bearing (degrees)

    returns the X,Y co-ord of bomb impact
    """
    
    # wing speed at 0 degrees is towards the aircraft
    
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
    
    # ax = fig.add_subplot(131, projection='3d')
    # ax.plot3D(x,y,z)
    # utils.set_axes_equal(ax)

    marker_size = 5

    # er this is doesn't make much sense but yeah
    # https://stackoverflow.com/questions/6063876/matplotlib-colorbar-for-scatter
    #ax2 = fig.add_subplot(132)
    ax2 = fig.add_subplot(121)
    ax2.scatter(x, y, c=z,s=marker_size, cmap='viridis')
    plt.gca().set_aspect('equal', adjustable='box')
    f = plt.scatter(x, y, c=z, s=marker_size, cmap='viridis')
    ax2.set_ylabel('Y', rotation=90)
    ax2.set_xlabel('X')
    cbar = plt.colorbar(f)
    cbar.set_label('Z', rotation=0)

    #ax3 = fig.add_subplot(133)
    ax3 = fig.add_subplot(122)
    ax3.scatter(x,z,c=y,s=marker_size, cmap='viridis')
    plt.gca().set_aspect('equal', adjustable='box')
    f = plt.scatter(x,z,c=y, s=marker_size, cmap='viridis')
    ax3.set_ylabel('Z', rotation=90)
    ax3.set_xlabel('X')
    cbar = plt.colorbar(f)
    cbar.set_label('Y', rotation=0)

    plt.show()


if __name__ == "__main__":
    import time
    start = time.perf_counter()
    bomb_drop(30.0,18.0,2.0,45, debug=True)
    print(time.perf_counter()-start)
    bomb_plot(history)
    print(drop_point((0.0,0.0),30.0,18.0,2.0,45))

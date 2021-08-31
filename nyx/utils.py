import logging
import time
import functools

import numpy as np

# any file that imports utils initialises the logger config, useful for when running single files
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s, [%(levelname)s], %(module)-5s, %(message)s",
    handlers=[
        logging.FileHandler(f"runtime/logs/log_{time.strftime('%Y%m%d-%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("main")


def target_loop(f_py=None, target_time=1.0):
    """
    base code for each state, while loop with a target time per loop
    target functions must return a bool of if they want to break the loop
    decorator with parameters 
    https://stackoverflow.com/questions/5929107/decorators-with-parameters
    """
    assert callable(f_py) or f_py is None
    def _decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            while True:
                start = time.time()    
                # run the actual function and check if break needed
                ended: bool = func(*args, **kwargs)
                if ended:
                    break
                sleep_time = target_time - (time.time()-start)
                #print(sleep_time)
                if sleep_time < 0: 
                    logger.warning(f"running behind!!")
                    sleep_time = 0
                time.sleep(sleep_time)
            return True
        return wrapper
    return _decorator(f_py) if callable(f_py) else _decorator


def timer(name:str):
    """ eh seems wack but time """
    def decorate(func):
        def call(*args, **kwargs):
            start = time.perf_counter_ns()
            result = func(*args, **kwargs)
            print(f"{name} took {time.perf_counter_ns()-start} ns")
            return result
        return call
    return decorate


def set_axes_equal(ax):
    '''Make axes of 3D plot have equal scale so that spheres appear as spheres,
    cubes as cubes, etc..  This is one possible solution to Matplotlib's
    ax.set_aspect('equal') and ax.axis('equal') not working for 3D.

    Input
      ax: a matplotlib axis, e.g., as output from plt.gca().
    '''

    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    x_middle = np.mean(x_limits)
    y_range = abs(y_limits[1] - y_limits[0])
    y_middle = np.mean(y_limits)
    z_range = abs(z_limits[1] - z_limits[0])
    z_middle = np.mean(z_limits)

    # The plot bounding box is a sphere in the sense of the infinity
    # norm, hence I call half the max range the plot radius.
    plot_radius = 0.5*max([x_range, y_range, z_range])

    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])


def setup_logger(name, level=logging.INFO):
    """
    Creates a logger context
    """
    # logger = logging.getLogger(name)
    
    # fh = logging.FileHandler(f"logs/{name}_{time.strftime('%Y%m%d-%H%M%S')}.log")
    # fh.setLevel(logging.DEBUG)
    
    # ch = logging.StreamHandler()
    # ch.setLevel(level)
    
    # formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # ch.setFormatter(formatter)
    # fh.setFormatter(formatter)

    # logger.addHandler(ch)
    # logger.addHandler(fh)

    # return logger

    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger(name)

    fileHandler = logging.FileHandler(f"logs/{name}.log")
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    return rootLogger
    
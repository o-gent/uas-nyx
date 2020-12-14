"""
functions and classes to manage multiple processes
"""

from multiprocessing import Process, Pipe
import time
import cv2


def task(func, connection):
    """
    Base function for a task
    - function must accept connection arguement
    """
    while True:
        new = connection.recv()
        if not new:
            time.sleep(0.1)
            continue
        result = func(new)
        connection.send(result)


class Worker:
    """
    manages an individual process
    """
    def __init__(self, func):
        self._send, self._recieve = Pipe()
        self.busy = False
        self.process = Process(target=task, args=(func, self._recieve,))
    
    def send(self, item):
        """ """
        if not self.busy:
            self._send(item)
            self.busy = True
            # indicate success
            return
        else:
            # indicate can't accept new
            return
    
    def recieve(self):
        """ check if worker has finished """
        result = self._recieve.recv()
        if result == None:
            return None
        else:
            self.busy = False
            return result


class WorkerManager:
    """
    Co-ordinates workers for multiprocess tasks 
    """
    
    def __init__(self):
        pass

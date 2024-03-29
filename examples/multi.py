"""
functions and classes to manage multiple processes
"""

from multiprocessing import Process, Pipe
import time
import cv2
from collections import deque


def task(func, connection):
    """
    Base function for a task
    - function must accept connection arguement
    """
    print(f"task started for {func}")
    while True:
        new = connection.recv()
        if type(new) == type(None):
            time.sleep(0.1)
            continue
        
        result = func(new)
        connection.send(result)


class Worker:
    """
    manages an individual process
    """
    def __init__(self, func):
        print(f"Worker started for {func}")
        self._home, self._away = Pipe()
        self.busy = False
        self._process = Process(target=task, args=(func, self._away,))
        self._process.start()
    
    def send(self, item) -> bool:
        """ if item is successfully sent to process then return true else false """
        if not self.busy:
            self._home.send(item)
            self.busy = True
            # indicate success
            return True
        else:
            # indicate can't accept new
            return False
    
    def recieve(self):
        """ check if worker has finished """
        result = None
        if self._home.poll(0.1):
            result = self._home.recv()
        
        if type(result) == type(None):
            return None
        else:
            self.busy = False
            return result


class WorkerManager:
    """
    Co-ordinates workers for multiprocess tasks 
    """
    
    def __init__(self, num_workers, function):
        """ start num_workers amount of threads with passed function """
        self._workers = deque([Worker(function) for i in range(num_workers)])
        self._queue = []
        self._results = []

    def add(self, obj) -> int:
        """ add to the queue, returns the length of the queue """
        self._queue.append(obj)
        return len(self._queue)

    def get(self):
        """ fetch the latest results, erasing current cache """
        results = self._results
        self._results = []
        return results 

    def churn(self):
        """ process one queue item and fetch results """
        try:
            work = self._queue.pop(0) # get the oldest item
        except:
            return
        
        worker = self._workers[0]

        result = worker.recieve()
        if not worker.busy:
            self._workers.rotate(1) # bring the oldest worker to the front
            worker.send(work) # send new work to the free process
            self._results.append(result)
        else:
            print("process was busy, skipping")


from threading import Timer

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


if __name__ == "__main__":
    import numpy as np
    import target_recognition

    def take_image(__) -> np.ndarray:
        """ take an image from the camera and return it """
        print("image taken")
        img = cv2.imread("test_images/field.png")
        return img


    def process_image(image) -> list:
        """ given an image return the colour, position, letter or none """
        print("image recieved")
        result = target_recognition.findCharacters(image)
        if result:
            # work out position
            pass
        
        return result

    results = []
    process = WorkerManager(1, process_image)
    take = Worker(take_image)

    take.send(1)
    start = time.time()
    
    for i in range(100):
        image = take.recieve()
        if image is not None:
            take.send(1)
            process.add(image)
        process.churn()
        results.append(process.get())

    print(time.time() - start)
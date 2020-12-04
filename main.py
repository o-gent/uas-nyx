""" 
co-ordinate everything

- Image capture
- Dronekit
- Image recognition
- Payload calculations

"""

from multiprocessing import Process, Pipe
import time

def take_image(connection):
    """ put an image in the pipe every 0.5 seconds """
    while True:
        connection.send([1])
        print("image taken")
        time.sleep(0.5)


def process_image(connection):
    """ process an image """
    while True:
        image = connection.recv()
        print(f"{image} recieved")
        connection.send(0)
        if image:
            time.sleep(1)
            print("image processed")
            connection.send(1)
        else:
            print("waiting")
            time.sleep(0.2)


if __name__ == "__main__":
    image_parent, image_child = Pipe()
    process_parent, process_child = Pipe()

    image = Process(target=take_image, args=(image_child,))
    image.start()

    process = Process(target=process_image, args=(process_child,))
    process.start()

    process_busy = 0

    while True:
        new_image = image_parent.recv()
        if new_image:
            # queue to the workers
            if not process_busy:
                process_parent.send(new_image)
                process_busy = 1
                print("sent job")
            else:
                result = process_parent.recv()
                if result == 1:
                    process_busy = 0
                else:
                    print("process is busy")
                    process_busy = 1
        time.sleep(0.1)


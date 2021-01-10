""" 
Will have a serial connection to the UAV program
basically a bash console interface but carry out actions when particular commands recieved
"""

import winsound
import os
import serial
import logging
import time
import socket

SOUNDS_PATH = "C:\\Users\\olive\\Downloads" # folder containing the WAV files

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s, [%(levelname)s], %(module)-5s, %(message)s",
    handlers=[
        logging.FileHandler(f"logs/log_{time.strftime('%Y%m%d-%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("main")


def say(state: str):
    """ given a state, annouce the state change (non blocking) """
    file = os.path.join(SOUNDS_PATH, state + ".wav")
    winsound.PlaySound(file, 1)


def process(line: str):
    """ 
    given a bash line, figure out if we carry out an action 
    need some sort of enclosing charachter
    %COMMAND%ARGS%
    """

    pass


def bash():
    """
    act as a pass through to the console and run special actions if commanded
    the script needs to be run twice, one for display and one for input
    I don't like it but can't think of another way.. (input() blocks)
    """
    HOST = "127.0.0.1"
    PORT = 1234
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = soc.connect_ex((HOST, PORT))
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if result == 0:
        # server already started
        soc.connect((HOST,PORT))
        while True:
            line = input("gandalf ~ $")
            soc.sendall(bytes(line, "utf"))

    else:
        port = input("Serial port:")
        conn = serial.Serial(port)
        print("waiting for input console")
        soc.bind((HOST, PORT))
        soc.listen()
        input_conn, addr = soc.accept()
        print(f"got connection from {addr}")
        with input_conn:
            while True:
                line = conn.readline()
                logger.info(line)
                process(line)
                input_line = input_conn.recv(1024).decode("utf")
                if input_line:
                    conn.writelines([input_line])
            


if __name__ == "__main__":
    bash()

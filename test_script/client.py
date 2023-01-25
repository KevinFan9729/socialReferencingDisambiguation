import time
import numpy as np
from numpy import pi
import threading
import socket
import cv2

if __name__ == '__main__':
    #socket setup
    host = "kd-pc29.local"
    port = 8091
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket.socket(socket.AF_INET, SOCK_DGRAM) for UDP connection
    s.connect((host, port)) #198.162.0.11
    s.send('aha'.encode("utf-8"))

import time
import numpy as np
from numpy import pi
import threading
import socket
import cv2

if __name__ == '__main__':
    count = 0
    #socket setup
    host = "kd-pc29.local"
    port = 8100
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket.socket(socket.AF_INET, SOCK_DGRAM) for UDP connection
    while count<=1000000:
        try:
            s.connect((host, port)) #198.162.0.11
            break
        except:
            print("connection failed")
            print("count: ", str(count))
            count+=1
    s.send('aha2'.encode())

import time
import numpy as np
from numpy import pi
import threading
import socket
import cv2

host = "kd-pc29.local"
port = 8091
size = 4
#get speech back from speech_feedback.py, server start this file frist
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen(5)
client, address = s.accept()
data="-1"

def from_client():
    global data
    print("thread started")
    # print(data)
    while True:
        # print("thread is alive")
        data = client.recv(1024)# initail read
        data = data.strip().decode("utf-8")
        print("data is from c1: ")
        print(data)
        s.close()
        break
    print("thread is dead")
    return

def from_client2():
    global data
    host = "kd-pc29.local"
    port = 8100
    size = 4
    #get speech back from speech_feedback.py, server start this file frist
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host,port))
    s.listen(5)
    client, address = s.accept()
    data="-1"
    print("thread started")
    # print(data)
    while True:
        # print("thread is alive")
        data = client.recv(1024).decode()# initail read
        # data = data.strip().decode("utf-8")
        print("data is from c2: ")
        print(data)
        break
    print("thread is dead")
    s.close()
    return

if __name__ == '__main__':
    from_client()
    time.sleep(4)
    from_client2()

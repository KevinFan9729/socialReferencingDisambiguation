import os
import numpy as np
# from tensorflow.keras.models import load_model
import socket
import time
import threading
import pickle
import cv2


#socket setup
host = "kd-pc29.local"
port = 8100
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket.socket(socket.AF_INET, SOCK_DGRAM) for UDP connection
s.connect((host, port)) #198.162.0.11
data = ""

# def listen_head_gesture():
#     global data
#     print("thread started")
#     data = s.recv(352615)# initail read
#     # data = data.strip().decode("utf-8")
#     data = pickle.loads(data)
#     # print(data)
#     # print("thread is alive")
#     data = s.recv(1024)# initail read
#     data = data.strip().decode("utf-8")
#     cv2.imshow("client",data)
#     cv2.waitKey(0)
#     # print("data is: ")
#     # print(data)
#     print("thread is dead")
#     return


def speech_feedback():
    global data
    headBackground=threading.Timer(1, listen_head_gesture)
    headBackground.setDaemon(True)
    headBackground.start()


    # load model
    # home=os.path.abspath(os.getcwd())
    # model_path=os.path.join(home, "my_model")
    # model = load_model(model_path)

    # if data == "Yes":
    #     break
    #
    # if index == 0:
    #     sf="0"
    #     s.send(sf.encode())
    #     print(sf)
    #     # return "No"
    # elif index == 1:
    #     time.sleep(1)
    #     s.send("2".encode())
    #     print(2)
    #     time.sleep(1)
    #     break
    #     # return "Yes"
    # else:
    #     sf="1"
    #     s.send(sf.encode())
    #     print(sf)
    #     # return "Neutral"
    s.close()
if __name__ == '__main__':
    # data = s.recv(1024)# initail read
    # data = pickle.loads(data)
    # # print(data)
    # # print("thread is alive")
    # cv2.imshow("client",data)
    # cv2.waitKey(0)
    # # print("data is: ")
    # # print(data)
    # # feedback = speech_feedback()
    # # print(feedback)
    f = open("recieved.jpg", "wb")
    data = None
    while True:
        m = s.recv(1024)
        data = m
        if m:
            while m:
                m = s.recv(1024)
                data += m
            else:
                break
    f.write(data)
    f.close()
    print("Done receiving")





# confirmation=['yes','yup','right','correct','sure','fine']

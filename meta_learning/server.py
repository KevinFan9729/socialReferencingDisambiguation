import socket
import fetch_api.camera_modules
import cv2
import os
import pickle
import numpy as np

host = "kd-pc29.local"
port = 8100
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket.socket(socket.AF_INET, SOCK_DGRAM) for UDP connection

s.bind((host,port))
s.listen(5)
client, address = s.accept()


if __name__ == '__main__':
    # test_img = cv2.imread("/home/fetch/Documents/Kevin/one_shot_learning/test2.jpg")
    # test_img = cv2.resize(test_img,(200,200))
    # data_str = pickle.dumps(test_img)
    # print(len(data_str))
    # client.send(data_str)
    f = open("/home/fetch/Documents/Kevin/meta_learning/test2.jpg", "rb")
    l = os.path.getsize("test2.jpg")
    m = f.read(l)
    client.sendall(m)
    f.close()
    print("Done sending...")
    s.close()
    # test_img = np.reshape(test_img,(-1,1))

    # print(test_img.shape)
    # cv2.imshow("win",test_img)
    # cv2.waitKey(0)

import os
import pickle
import numpy as np
import speech_recognition as sr
from speech_classifier import data_prep
from tensorflow.keras.models import load_model
import tensorflow as tf
import socket
import time
import threading


#socket setup
# host = "kd-pc29.local"
# port = 8091
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket.socket(socket.AF_INET, SOCK_DGRAM) for UDP connection
# s.connect((host, port)) #198.162.0.11

#socket setup (server)
host = "kd-pc29.local"
port = 8091
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket.socket(socket.AF_INET, SOCK_DGRAM) for UDP connection
# s.connect((host, port)) #198.162.0.11
s.bind((host,port))
s.listen(5)
client, address = s.accept()
client2, address2 = s.accept()



data = ""
disconnect = ""

# def listen_head_gesture():
#     global data
#     print("thread started")
#     # data = s.recv(1024)# initail read
#     data = client.recv(1024)# initail read
#     data = data.strip().decode("utf-8")
#     # print(data)
#     while (data!="Yes"):
#         # print("thread is alive")
#         # data = s.recv(1024)# initail read
#         data = client.recv(1024)# initail read
#         data = data.strip().decode("utf-8")
#         # print("data is: ")
#         # print(data)
#     print("thread is dead")
#     return

def listen_disconnect():
    global disconnect
    print("thread started")
    # data = s.recv(1024)# initail read
    # disconnect = client.recv(1024)# initail read
    # disconnect = disconnect.strip().decode("utf-8")
    disconnect = client2.recv(1024)# initail read
    disconnect = disconnect.strip().decode("utf-8")
    # print(disconnect)
    while (disconnect!="disconnect|"):
        # print("thread is alive")
        # data = s.recv(1024)# initail read
        # disconnect = client.recv(1024)# initail read
        # disconnect = disconnect.strip().decode("utf-8")
        disconnect = client2.recv(1024)# initail read
        disconnect = disconnect2.strip().decode("utf-8")
        # print(disconnect)
    print("disconnect is: ")
    print(disconnect)
    print("thread is dead")
    return


def speech_feedback():
    # global data
    global disconnect
    discBackground=threading.Timer(1, listen_disconnect)
    discBackground.setDaemon(True)
    discBackground.start()
    #speech-to-text recognizer and mic
    r = sr.Recognizer()
    mic = sr.Microphone()
    time.sleep(25)

    # load model
    home=os.path.abspath(os.getcwd())
    model_path=os.path.join(home, "my_model")
    with tf.device('/cpu:0'):
        model = load_model(model_path)

    #load tokenizer
    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    #main loop
    while True:
        #listen and speech-to-text transcription
        print("disconnect")
        print(disconnect)
        if disconnect == "disconnect|":
            break
        try:
            with mic as source:
                print("Listening...")
                r.adjust_for_ambient_noise(source)
                # audio = r.record(source=mic, duration=10)
                audio = r.listen(source)
            user_speech=r.recognize_google(audio)
        except sr.UnknownValueError:
            print("No speech detected, try again...")
            # if data == "Yes":
            #     break
            if disconnect == "disconnect|":
                break
            continue
        print(user_speech)
        processed=data_prep(user_speech,tokenizer)
        with tf.device('/cpu:0'):
            pred=model.predict(processed)
        index=np.argmax(pred[0])
        if disconnect == "disconnect|":
            break
        # if data == "Yes":
        #     break

        if index == 0:
            sf="0"
            # s.send(sf.encode())
            client.send(sf.encode())
            client2.send(sf.encode())
            print(sf)
            # return "No"
        elif index == 1:
            time.sleep(1)
            # s.send("2".encode())
            client.send("2".encode())
            client2.send("2".encode())
            print(2)
            time.sleep(1)
            # break
            # return "Yes"
        else:
            sf="1"
            # s.send(sf.encode())
            client.send(sf.encode())
            client2.send(sf.encode())
            print(sf)
            # return "Neutral"
    s.close()
if __name__ == '__main__':
    feedback = speech_feedback()
    # print(feedback)






# confirmation=['yes','yup','right','correct','sure','fine']

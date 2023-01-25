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
host = "kd-pc29.local"
port = 8500
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket.socket(socket.AF_INET, SOCK_DGRAM) for UDP connection
s.connect((host, port)) #198.162.0.11
data = ""
disconnect = ""

def listen_head_gesture():
    global data
    print("thread started")
    data = s.recv(1024)# initail read
    data = data.strip().decode("utf-8")
    # print(data)
    while (data!="Yes" and data !="disconnect"):
        # print("thread is alive")
        data = s.recv(1024)# initail read
        data = data.strip().decode("utf-8")
        # print("data is: ")
        # print(data)
    print("thread is dead")
    return


def speech_obj_check():
    global data
    headBackground=threading.Timer(1, listen_head_gesture)
    headBackground.setDaemon(True)
    headBackground.start()
    #speech-to-text recognizer and mic
    r = sr.Recognizer()
    mic = sr.Microphone()
    time.sleep(15)

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
        try:
            with mic as source:
                print("Listening...")
                r.adjust_for_ambient_noise(source)
                # audio = r.record(source=mic, duration=10)
                audio = r.listen(source)
            user_speech=r.recognize_google(audio)
        except sr.UnknownValueError:
            print("No speech detected, try again...")
            if data == "Yes":
                break
            continue
        print(user_speech)
        processed=data_prep(user_speech,tokenizer)
        with tf.device('/cpu:0'):
            pred=model.predict(processed)
        index=np.argmax(pred[0])
        if data == "Yes":
            break
        if data == "disconnect":
            break

        if index == 0:
            sf="0"
            s.send(sf.encode())
            print(sf)
            # return "No"
        elif index == 1:
            time.sleep(1)
            s.send("2".encode())
            print(2)
            time.sleep(1)
            break
            # return "Yes"
        else:
            sf="1"
            s.send(sf.encode())
            print(sf)
            # return "Neutral"
    s.close()
if __name__ == '__main__':
    feedback = speech_obj_check()
    # print(feedback)






# confirmation=['yes','yup','right','correct','sure','fine']

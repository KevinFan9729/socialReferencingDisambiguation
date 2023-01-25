import cv2
import sys
import rospy
# from fetch_api.camera_modules import RGBCamera, YoloDetector
from fuzzyDecision import AmbiguityFuzzy
import threading
import os
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import speech_recognition as sr
from nltk.tag import HunposTagger
import utils
import numpy as np
import time
import socket
from kf_robot import kf_Robot

#server
host = "kd-pc29.local"
port = 8200
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket.socket(socket.AF_INET, SOCK_DGRAM) for UDP connection
# s.connect((host, port)) #198.162.0.11
s.bind((host,port))
# data = ""
s.listen(5)
client, address = s.accept()
client.send(("Fetch is ready").encode())



printOnce = 0
runOnce = 0

class FetchInput():
    def __init__(self):
        self.user_cmd = ""
        # self.mode = ""
        self.short_term_memory = None
        self.saved_view =None
        self.detected_objs=[]

    def get_confidence(self, boxes):
        confidence=[]
        for box in boxes:
            confidence.append(box[-1])
        return confidence

    def get_user_input_gui(self):
        while True:
            self.user_cmd = client.recv(1024).decode() #recive user label from the gui
            print("inside of keyboard")
            print(self.user_cmd )
            printOnce = 0
            # runOnce = 0
            if self.user_cmd=="":
                continue
            # cmd = self.user_cmd.split("|")
            # self.user_cmd=cmd[0]
            # self.mode = =cmd[1]
            if not("|" in self.user_cmd):
                client.send(self.user_cmd.encode())#send typed user label back to gui
            # break

    def speech_label(self,robot):
        adj=[]
        noun=[]
        r = sr.Recognizer()
        mic = sr.Microphone()
        stops = stopwords.words('english')
        home = os.path.abspath(os.getcwd())
        speech =  os.path.join(home, 'speech')
        model = os.path.join(speech, 'Hunpos', 'english.model')
        binary = os.path.join(speech, 'Hunpos', 'hunpos-tag')
        label=""
        # global user_cmd
        print("Please give fetch your command!")
        userSpeech=""
        while True:
            try:
                if self.user_cmd == "":
                    with mic as source:
                        print("Listening...")
                        r.adjust_for_ambient_noise(source)
                        # audio = r.record(source=mic, duration=10)
                        audio = r.listen(source)
                    userSpeech=r.recognize_google(audio)
            except:
                    continue
            if userSpeech != "":
                tokens = word_tokenize(userSpeech)
                ht = HunposTagger(model,binary)
                tagged=ht.tag(tokens)
                # remove stop words
                tagged = [t for t in tagged if not t[0] in stops]
                #extract adjectives and nouns
                for t in tagged:
                    if t[1] == b'JJ':
                        adj.append(t[0])
                    if t[1] == b'NN':
                        noun.append(t[0])
                label=(' '.join(adj) + " " + ' '.join(noun)).strip()
                self.user_cmd=label
            if self.user_cmd == "":
                continue
            print("userSpeech")
            print(userSpeech)
            print("User input: "+self.user_cmd)
            client.send(self.user_cmd.encode())#send speech user label back to gui
            sound_ls = ['/home/fetch_admin/robot_speech/ui1.wav',
            '/home/fetch_admin/robot_speech/ui2.wav']
            sound= np.random.choice(sound_ls)
            robot.speaker.play(sound)
            time.sleep(3.5)#3
            robot.speaker.soundhandle.stopAll()
            break
            # if label!="":
            #     user_cmd=label
            #     return

    def fuzzy_input_extract(self, detected_objs, detected_confidence):
        global printOnce
        # print(0)
        if self.user_cmd == "":# dummy code, maybe the entire ambiguity block will not invoke if user command is empty
            confidence=0
            count=0
            #print((confidence, count))
            return
        # print(1)
        userInput=self.user_cmd
        userInput=userInput.lower()
        indices = [i for i, x in enumerate(detected_objs) if x == userInput]
        count=len(indices)
        # print(2)
        if count ==0:
            confidence = 0
            if printOnce == 0:
                print((confidence, count))
                printOnce = 1
            return (confidence, count)
        # print(3)
        targetConfLs= [detected_confidence[i] for i in indices]
        confidence=max(targetConfLs)

        if printOnce == 0:
            print((confidence, count))
            printOnce = 1
        # print("end of the function")
        return (confidence, count)

    def input_and_ambiguity(self, long_term_memory={},robot=None):
        # client.send(("Fetch is ready").encode())
        rgb = robot.rgbCamera
        yd = robot.yoloDetector
        aFuzzyCtrl= AmbiguityFuzzy()
        keyBackground=threading.Thread(target=self.get_user_input_gui)
        keyBackground.daemon=True
        keyBackground.start()

        speechBackground=threading.Thread(target=self.speech_label, args =(robot,))
        speechBackground.daemon=True
        speechBackground.start()
        sound_ls = ['/home/fetch_admin/robot_speech/ready1.wav',
        '/home/fetch_admin/robot_speech/ready2.wav',
        '/home/fetch_admin/robot_speech/ready3.wav',]
        sound= np.random.choice(sound_ls)
        robot.speaker.play(sound)
        time.sleep(2.5)
        robot.speaker.soundhandle.stopAll()
        # while self.user_cmd=="":#hold the program if there is no input
        #     continue
        # if not("|" in self.user_cmd):
        #     msg= client.recv(1024)#issues, may get stuck
        #     self.user_cmd = msg.decode()
        while not("|" in self.user_cmd):
            continue
        self.user_cmd=self.user_cmd.split("|")[0]
        # msg = client.recv(1024)#hold the program for confirmation
        # self.user_cmd = msg.decode()

        print("User input: "+ self.user_cmd)
        # cv2.imshow("window_dn", yd.getDetectionImage())
        detection = yd.detect()
        boxes = detection[0]
        self.detected_objs = detection[1]

        # memory case 1, the user input match the label of detected objects
        if self.user_cmd in self.detected_objs:
            self.saved_view= rgb.getRGBImage()
            coord_3d_base, coord_3d_map = yd.get_item_3d_coordinates_base_map(self.user_cmd, self.saved_view) #3d coordinates in the base link
            # print("coord_3d_base")
            # print(coord_3d_base)
            # note that the pick and place coorindates are with respect to the base link
            #short_term_memory should have the bounding box, object 3d coordinates
            indices = [i for i, x in enumerate(self.detected_objs) if x == self.user_cmd]
            box_selected = []
            for i in indices:
                box_selected+=[boxes[i][:-1]]
            self.short_term_memory = {
            "bounding_boxes": box_selected,
            "coord_3d": coord_3d_base,
            "coord_3d_map": coord_3d_map
            }
            print("test memory")
            print(self.short_term_memory)
            #================================
            #write object images to short_term_memory folder for the model to use
            home = os.path.abspath(os.getcwd())
            short_mem_path = os.path.join(home, "meta_learning","short_term_memory")
            for i in range(len(self.short_term_memory["bounding_boxes"])):
                obj_name = "obj"+"_"+str(i)+".png"
                obj_name = os.path.join(short_mem_path, obj_name)
                X0,Y0,X1,Y1 =self.short_term_memory["bounding_boxes"][i]
                cropped_image = self.saved_view[Y0-10:Y1+10, X0-10:X1+10]
                cv2.imwrite(obj_name, cropped_image)
            #================================

        # memory case 2, the user input does not match the label of detected objects, the object is novel
        else:
            self.saved_view= rgb.getRGBImage()
            print("all seen objects")
            print(self.detected_objs) #all detected objs name
            obj_not_to_include = utils.get_non_pickable_item_index(self.detected_objs)

            print("indices of non-pickable objects")
            print(obj_not_to_include)
            pickable_objs= []
            box_selected = []
            for item in range(len(self.detected_objs)):
                if not(item in obj_not_to_include):
                    pickable_objs+=[self.detected_objs[item]]
                    box_selected+=[boxes[item][:-1]]
            if len(pickable_objs) == 0:
                # self.robot.speaker.say("Sorry I don't see any objects I can pick up")
                return
            coord_3d_base=[]
            coord_3d_map=[]
            print("pickable objects")
            print(pickable_objs)
            unique_objs = list(dict.fromkeys(pickable_objs))
            print("unique_objs")
            print(unique_objs)
            for obj in unique_objs:
                c,c_map= yd.get_item_3d_coordinates_base_map(obj, self.saved_view)
                coord_3d_base+=c
                coord_3d_map+=c_map
            self.short_term_memory = {
            "bounding_boxes": box_selected,
            "coord_3d": coord_3d_base,
            "coord_3d_map": coord_3d_map
            }
            print("test memory")
            print(self.short_term_memory)
            #write object images to short_term_memory folder for the model to use
            home = os.path.abspath(os.getcwd())
            short_mem_path = os.path.join(home, "meta_learning","short_term_memory")
            for i in range(len(self.short_term_memory["bounding_boxes"])):
                obj_name = "obj"+"_"+str(i)+".png"
                obj_name = os.path.join(short_mem_path, obj_name)
                X0,Y0,X1,Y1 =self.short_term_memory["bounding_boxes"][i]
                cropped_image = self.saved_view[Y0-10:Y1+10, X0-10:X1+10]
                cv2.imwrite(obj_name, cropped_image)

        detected_confidence = self.get_confidence(boxes)
        print("run fuzzy extraction")
        visionCrispSet=self.fuzzy_input_extract(self.detected_objs, detected_confidence)
        if self.user_cmd in long_term_memory:
            visionCrispSet[0] = 1.0
            visionCrispSet[1] = 1 #count the number of detected object in the support set later when we have a one-shot model
        # aFuzzyCtrl.determine(visionCrispSet)
        ambLvl=aFuzzyCtrl.determine(visionCrispSet[0],visionCrispSet[1])
        print("In fuzzy amb ", ambLvl)
        return ambLvl



if __name__ == '__main__':
    rospy.init_node("input_and_ambiguity_check")
    # robot = kf_Robot()
    input=FetchInput()
    input.input_and_ambiguity()

    # rgb = RGBCamera()
    # yd = YoloDetector()
    # aFuzzyCtrl= AmbiguityFuzzy()
    # while 1:
    #     #print("in the loop") #in the loop
    #     try:
    #         cv2.imshow("window_rgb", rgb.getRGBImage())
    #         # print("show")
    #     except:
    #         continue
    #         # print("continue")
    #     try:
    #         cv2.imshow("window_dn", yd.getDetectionImage())
    #         detection = yd.detect()
    #         boxes = detection[0]
    #         detected_obj = detection[1]
    #         detected_confidence = get_confidence(boxes)
    #         # fuzzy_input_extract(user_cmd, detected_obj, detected_confidence)
    #         # print(detected_obj)
    #         if runOnce==0:
    #             print("run fuzzy extraction")
    #             visionCrispSet=fuzzy_input_extract(user_cmd, detected_obj, detected_confidence)
    #             runOnce=1
    #             # aFuzzyCtrl.determine(visionCrispSet)
    #             aFuzzyCtrl.determine(visionCrispSet[0],visionCrispSet[1])
    #     except:
    #         continue
    #     if cv2.waitKey(5) & 0xFF == ord('q'):
    #         break

# high level intergration
# 1. get user input and check for ambiguity -- input_and_ambiguity_check, get an ambiguity level
# 2. logic to check ambiguity level, and determine if the robot needs to disambiguate -- in this file
#   2(a): disambiguation needed: -- call attention check to get human attention
#       (I): disambigute via pointing and checking head gesture
#       (II): pick and place
#   2(b): disambiguation not needed: call pick and place

# use subporcess.check_output?
# run different py files in seperate threads?
# import module and use the imported variable directly?
    #e.g. in first.py a=5. in the second py, do import first, print(first.a)

from input_and_ambiguity_check import FetchInput
from gesture_detection.FetchDNNwithCalibration import headGesture
# from attention_check import Attention
from kf_robot import kf_Robot
from disambiguation import point_to_disambiguate
import threading
import time
import rospy
from numpy import pi
import numpy as np
import os
import cv2
import socket
import utils
import traceback
from timeit import default_timer as timer

#server
host = "kd-pc29.local"
port = 8100
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket.socket(socket.AF_INET, SOCK_DGRAM) for UDP connection
# s.connect((host, port)) #198.162.0.11
s.bind((host,port))
fb_lbl=""
# data = ""
s.listen(5)
client, address = s.accept()

#client of the speech feedback
# host = "kd-pc29.local"
port = 8091
s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket.socket(socket.AF_INET, SOCK_DGRAM) for UDP connection
s1.connect((host, port)) #198.162.0.11



class SocialReferencingArch():
    def __init__(self):
        self.robot = kf_Robot()
        self.gesture_pos = [-0.22157120621, -0.279244163166]
        self.short_term_memory = None
        self.long_term_memory = None
        self.robot_input = FetchInput()
        self.user_cmd = ""
        # self.human_attention = Attention()
        self.ambiguity_Level = 1.0
        self.view=None
    def input_block(self, robot):
        self.ambiguity_Level = self.robot_input.input_and_ambiguity(robot=robot)
        self.user_cmd = self.robot_input.user_cmd
        self.view = self.robot_input.saved_view
        self.short_term_memory = self.robot_input.short_term_memory #update short term memory from the input view
    def move_to_gesture_pos(self):
        self.robot.base.goto(self.gesture_pos[0], self.gesture_pos[1], theta = -pi/2)
        #maybe need to check the coordinate of the robot? and move the robot left or right?
    def update_short_term_view(self):
        self.view= self.robot.rgbCamera.getRGBImage()
        coord_3d, up = self.robot.yoloDetector.get_item_3d_coordinates(self.user_cmd, self.view)
        print(len(coord_3d))
        # cv2.imshow("window2",robot.yoloDetector.getDetectionImage())
        # cv2.waitKey(0)
        if len(coord_3d) == 0: #label is not found in the current view
            detected_objs = robot.yoloDetector.detect()[1] #names of all detected objects in the view
            #remove non-pickable objects
            detected_objs = utils.get_pickable_item_in_view(detected_objs)
        unique_objs = list(dict.fromkeys(detected_objs))
        for obj in unique_objs:
            c,u= robot.yoloDetector.get_item_3d_coordinates(obj, savedView)
            coord_3d+=c #get the 3d-coordinates of all detected objects (base-link frame)
        return coord_3d
    def distance_check(self, reference, check_ls):
        dist_ls=[]
        print("reference")
        print(reference)
        print("check_ls")
        print(check_ls)
        for i in check_ls:
            print(i)
            dist_ls+=[(reference[0]-i[0])**2 + (reference[1]-i[1])**2  + (reference[2]-i[2])**2]
        # temp_y = [abs(x[1]) for x in coord_3d]
        print("dist_ls")
        print(dist_ls)
        index = np.argmin(dist_ls)
        # target = coord_3d[index]
        return index
    def speech_obj_thread(self):
        global fb_lbl
        print("thread started")
        fb_lbl = s1.recv(1024)# initail read
        fb_lbl = fb_lbl.strip().decode("utf-8")
        # print(data)
        while (fb_lbl!="0" and fb_lbl!="No"):
            # print("thread is alive")
            fb_lbl = s1.recv(1024)# initail read
            fb_lbl = fb_lbl.strip().decode("utf-8")
            # print("data is: ")
            # print(data)
        print("thread is dead")
        return
    def head_lbl(self):
        global fb_lbl
        fb_lbl = headGesture()

    def objection_check(self):
        global fb_lbl
        # host = "kd-pc29.local"
        # port = 8500
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket.socket(socket.AF_INET, SOCK_DGRAM) for UDP connection
        # # s.connect((host, port)) #198.162.0.11
        # s.bind((host,port))
        # fb_lbl=""
        # # data = ""
        # s.listen(5)
        # client, address = s.accept()

        #head gesture
        headBackground = threading.Timer(0.1, self.head_lbl)
        headBackground.setDaemon(True)
        headBackground.start()

        speechBackground=threading.Timer(0.1, self.speech_obj_thread)
        speechBackground.setDaemon(True)
        speechBackground.start()

        start = timer()
        time_elapsed = 0.0
        objection = ""
        while time_elapsed<=4.0:
            if fb_lbl == 'No' or fb_lbl== '0':
                objection = 'objection'
                break
            end = timer()
            time_elapsed = end - start
        temp = 'disconnect|'
        s1.send(temp.encode())
        print("disconnect sent")
        s1.close()
        return objection



    def run(self):
        # self.robot.base.move_backward_mod(distance=0.1)
        # self.move_to_gesture_pos()
        # time.sleep(2)
        # self.robot.head.move_down_center()
        self.robot.torso.move_to(0.169)
        # self.robot.torso.move_to(0.12)
        self.robot.head.move_home()
        self.robot.head.move_down_center(0.15)
        # self.robot.arm.safe_stow()
        # self.robot.speaker.say("I am ready! Which item do you want me to pick up?")
        # sound_ls = ['/home/fetch_admin/robot_speech/ready1.wav',
        # '/home/fetch_admin/robot_speech/ready2.wav',
        # '/home/fetch_admin/robot_speech/ready3.wav',]
        # sound= np.random.choice(sound_ls)
        # self.robot.speaker.play(sound)
        # time.sleep(2)
        # self.robot.speaker.soundhandle.stopAll()
        self.input_block(self.robot)
        print("ambiguity_Level")
        print(self.ambiguity_Level)

        self.robot.head.move_down_center(0.15)
        time.sleep(1)
        self.robot.head.move_home()

        objection = self.objection_check()
        client.send(self.user_cmd.encode("utf-8"))#send the meta_learning model the user label (anchor)

        if objection == "objection":
            print("objection")
            print("fb_lbl: "+fb_lbl)
            self.robot.speaker.say("Sorry, it seems I got something terribly wrong, let's try again.")
            time.sleep(5)
            self.robot.speaker.soundhandle.stopAll()
            # self.robot.base.move_backward_mod(distance=0.1)
            # self.move_to_gesture_pos()
            return
if __name__ == '__main__':
    rospy.init_node("test_final")
    arch=SocialReferencingArch()
    # arch.run()
    # time.sleep(1)
    # s.close()
    try:
        arch.run()
        time.sleep(3)
        s.close()
    except:
        print(traceback.format_exc())
        time.sleep(3)
        s.close()

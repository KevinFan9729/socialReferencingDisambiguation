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
import glob
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
        # self.gesture_pos = [1.313,-0.318]#robohub coordinate
        # self.gesture_pos = [-0.507, -0.037]#E5 coordinate
        # self.gesture_pos = [-0.2365, -1.2272] #E5 new coordinate
        # self.gesture_pos = [-0.28795, -0.42707]#steven's old map
        # self.gesture_pos = [0.426282, -0.161012]
        # self.gesture_pos = [0.456282, -0.161012]
        # self.gesture_pos = [0.370117880988, -0.297434874061] #steven's new get_pose_map

        # self.gesture_pos = [-0.156793796789, -0.212407004395]
        self.gesture_pos = [-0.22157120621, -0.279244163166]
        self.short_term_memory = None
        self.long_term_memory = None
        self.robot_input = FetchInput()
        self.user_cmd = ""
        # self.human_attention = Attention()
        self.ambiguity_Level = 1.0
        self.view=None
        self.person_3d = None
        self.person_3d_map = None
    def input_block(self, robot):
        self.ambiguity_Level = self.robot_input.input_and_ambiguity(robot=robot)
        self.user_cmd = self.robot_input.user_cmd
        self.user_cmd = self.user_cmd.lower()
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
        while (fb_lbl!="0" and fb_lbl!="No"):#while speech is not confirmational
            # print("thread is alive")
            try:
                fb_lbl = s1.recv(1024)# initail read
            except Exception as e:
                print("An exception has occured.")
                print(e)
                print("Speech thread in SocialReferencingArch is dead.")
                return
            fb_lbl = fb_lbl.strip().decode("utf-8")
            # print("data is: ")
            # print(data)
        print("Speech thread in SocialReferencingArch is dead.")
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
        while time_elapsed<=3.0:
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

    def find_person(self):
        try:
            person_3d, person_3d_map = self.robot.yoloDetector.get_item_3d_coordinates_base_map(self.user_cmd, self.robot.rgbCamera.getRGBImage())
        except:
            self.person_3d = None
            self.person_3d_map = None
        self.person_3d = person_3d
        self.person_3d_map = person_3d_map

    def reorder(self, ls, order):
        reorder_ls = [None] * len(order)
        for i in range(len(order)):
            reorder_ls[i] = ls[order[i]]
        return reorder_ls

    def run(self):

        self.robot.base.move_backward_mod(distance=0.1)
        self.move_to_gesture_pos()
        time.sleep(2)
        # self.robot.head.move_down_center()
        self.robot.torso.move_to(0.169)
        # self.robot.torso.move_to(0.12)
        self.robot.head.move_home()
        self.robot.head.move_down_center(0.15)
        self.robot.arm.safe_stow()
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
        long_mem_classes_ls = []
        home = os.path.abspath(os.getcwd())
        long_mem_path = os.path.join(home, "meta_learning","long_term_memory")

        #check long term memory before learning and disambigute
        for class_ in os.listdir(long_mem_path):
            long_mem_classes_ls.append(class_)

        if self.user_cmd in self.robot.yoloDetector.detect()[1]:
            msg = self.user_cmd+'*'#yolo know the object
        else:
            msg = self.user_cmd #yolo does not know the object
            if not(self.user_cmd in long_mem_classes_ls):# object is not in robot's long_term_memory, robot needs to imagine.
                sound_ls = ['/home/fetch_admin/robot_speech/imagination1.wav',
                '/home/fetch_admin/robot_speech/imagination2.wav',
                '/home/fetch_admin/robot_speech/imagination3.wav',]
                sound= np.random.choice(sound_ls)
                self.robot.speaker.play(sound)
                time.sleep(5)
                self.robot.speaker.soundhandle.stopAll()

        client.send(msg.encode("utf-8"))#send the meta_learning model the user label (anchor)

        # client.send(self.user_cmd.encode("utf-8"))#send the meta_learning model the user label (anchor)

        data = client.recv(1024)# initail read
        idx = data.strip().decode("utf-8")
        order_ls=[]
        try:
            order_ls = list(map(int, idx.split(',')))
        except:
            print("error at order list generation... moving on...")
        s.close()# need to test
        long_mem_classes_ls = []
        for class_ in os.listdir(long_mem_path):
            long_mem_classes_ls.append(class_)

        if (self.user_cmd in long_mem_classes_ls): #the user label is matching item in the long term memory
            # data = client.recv(1024)# initail read
            # idx = data.strip().decode("utf-8")
            # s.close()# need to test
            if idx !="-1" and len(order_ls) == 1:
                item_coord = self.short_term_memory["coord_3d"][int(idx)]
                item_coord_map = self.short_term_memory["coord_3d_map"][int(idx)]
                ###debug code
                # for i in range(len(self.short_term_memory["bounding_boxes"])):
                #     X0,Y0,X1,Y1 =self.short_term_memory["bounding_boxes"][i] #target bounding box
                #     cropped_image = self.view[Y0-10:Y1+10, X0-10:X1+10]
                #     print(i)
                #     cv2.imshow("test",cropped_image)
                #     cv2.waitKey(0)
                # X0,Y0,X1,Y1 =self.short_term_memory["bounding_boxes"][int(idx)] #target bounding box
                # print("final index")
                # print(int(idx))
                # query = self.view[Y0-10:Y1+10, X0-10:X1+10]
                # cv2.imshow("query",query)
                # cv2.waitKey(0)

                #pick up and place
                # robot_pos_map = self.robot.base.get_pose_map()
                sound_ls = ['/home/fetch_admin/robot_speech/learnt1.wav',
                '/home/fetch_admin/robot_speech/learnt2.wav',
                '/home/fetch_admin/robot_speech/learnt3.wav',]
                sound= np.random.choice(sound_ls)
                self.robot.speaker.play(sound)
                time.sleep(2)
                self.robot.speaker.soundhandle.stopAll()
                # self.robot.speaker.say("Aha, I remember!")
                robot_pos_map = self.robot.base.get_pose_amcl()
                print('robot_pos_map')
                print(robot_pos_map)
                # new_robot_pos_map = [robot_pos_map[0]+0.3,(robot_pos_map[1] + item_coord[1]*1.2),robot_pos_map[2]]
                # new_robot_pos_map = [robot_pos_map[0]-0.3,(robot_pos_map[1] + item_coord[1]*1.0),robot_pos_map[2]]

                new_robot_pos_map = [(item_coord_map[0]-0.175),robot_pos_map[1]-0.1,robot_pos_map[2]]

                print('new_robot_pos_map')
                print(new_robot_pos_map)
                # self.robot.base.goto(new_robot_pos_map[0], new_robot_pos_map[1], theta = -pi/1.65)
                self.robot.base.goto(new_robot_pos_map[0], new_robot_pos_map[1], theta = -pi/2)
                robot_pos_map = self.robot.base.get_pose_amcl()
                apporch_dist = abs((abs(item_coord_map[1])-abs(robot_pos_map[1]))-0.75)
                print("displacement")
                print(apporch_dist)
                self.robot.base.move_forward_mod(distance=apporch_dist)#move to the pickup position

                # stop = raw_input("stop?")
                # if stop == "s":
                #     print("stopping the program")
                #     return

                print('robot_pickup_pos_map')
                # print(self.robot.base.get_pose_map())
                print(self.robot.base.get_pose_amcl())
                time.sleep(1)
                self.robot.head.move_home()
                self.robot.head.move_down_center(0.7)
                # robot.head.look_at(item_coord[0]-0.55,0,item_coord[2]-0.2)#look at the object
                # robot.torso.move_to(0.2)
                time.sleep(2)
                # savedView= self.robot.rgbCamera.getRGBImage()
                coord_3d, coord_3d_map = self.robot.yoloDetector.get_item_3d_coordinates_base_map(self.user_cmd, self.robot.rgbCamera.getRGBImage())
                print(len(coord_3d))
                # cv2.imshow("window2",robot.yoloDetector.getDetectionImage())
                # cv2.waitKey(0)
                if len(coord_3d) == 0: #label is not found in the current view
                    detected_objs = self.robot.yoloDetector.detect()[1] #names of all detected objects in the view
                    #remove non-pickable objects
                    detected_objs = utils.get_pickable_item_in_view(detected_objs)

                    if len(detected_objs) == 0:
                        #look down and try again:
                        self.robot.head.move_down(0.2)
                        time.sleep(1)
                        # coord_3d, _ = self.robot.yoloDetector.get_item_3d_coordinates(self.user_cmd, self.robot.rgbCamera.getRGBImage())
                        detected_objs = self.robot.yoloDetector.detect()[1] #names of all detected objects in the view
                        #remove non-pickable objects
                        detected_objs = utils.get_pickable_item_in_view(detected_objs)
                        if len(detected_objs)==0:
                            sound= '/home/fetch_admin/robot_speech/notarget.wav'
                            self.robot.speaker.play(sound)
                            # self.robot.speaker.say("Sorry I don't see any objects I can pick up")
                            s1.send("disconnect|".encode())
                            print("disconnect sent")
                            s1.close()
                            return

                    unique_objs = list(dict.fromkeys(detected_objs))
                    coord_3d=[]
                    coord_3d_map=[]
                    for obj in unique_objs:
                        c,c_map= self.robot.yoloDetector.get_item_3d_coordinates_base_map(obj, self.robot.rgbCamera.getRGBImage())
                        coord_3d+=c #get the 3d-coordinates of all detected objects (base-link frame
                        coord_3d_map+=c_map
                if len(coord_3d)>1: #detecting mutiple objects close up
                    index = self.distance_check(item_coord_map,coord_3d_map)
                    target = coord_3d[index]
                elif len(coord_3d) == 1:
                    target= coord_3d[0]
                else:
                    target = []
                    print("no detection")
                print("first target")
                print(target)

                if len(target)!=0:
                    sound_ls = ['/home/fetch_admin/robot_speech/pickup1.wav',
                    '/home/fetch_admin/robot_speech/pickup2.wav']
                    sound= np.random.choice(sound_ls)
                    self.robot.head.look_at(target[0],target[1],target[2])
                    # time.sleep(3)
                    # target = []
                    # # savedView= robot.rgbCamera.getRGBImage()
                    # while len(target)==0:#keep trying if target is not found
                    #     for obj in unique_objs:
                    #         c,_= self.robot.yoloDetector.get_item_3d_coordinates(obj, savedView)
                    #         coord_3d+=c #get the 3d-coordinates of all detected objects (base-link frame
                    #     # coord_3d, _ = self.robot.yoloDetector.get_item_3d_coordinates('cup', self.robot.rgbCamera.getRGBImage())
                    #     target=coord_3d[0] #target is the most confident detection
                    #     print("seeking target...")
                    # print("final target")
                    # print(target)

                    #second social referencing check for objection
                    self.robot.head.move_home()
                    time.sleep(1)
                    # self.robot.head.move_down_center(0.7)
                    objection = self.objection_check()
                    if objection == "objection":
                        print("objection")
                        # self.robot.speaker.say("Sorry, it seems I got something terribly wrong, let's try again.")
                        self.robot.base.move_backward_mod(distance=0.1)
                        self.move_to_gesture_pos()
                        return

                    #before pickup
                    self.robot.speaker.play(sound)
                    time.sleep(3)
                    self.robot.speaker.soundhandle.stopAll()
                    self.robot.head.look_at(target[0],target[1],target[2])
                    self.robot.torso.move_to(0.3)
                    self.robot.vertical_pick(target)
                    self.robot.vertical_place([target[0]+0.1, target[1], target[2]])
                    return
        print("long_mem_classes_ls")
        print(long_mem_classes_ls)

        if self.ambiguity_Level > 0.5:# disambigute
            sound_ls = ['/home/fetch_admin/robot_speech/confusion1.wav',
            '/home/fetch_admin/robot_speech/confusion2.wav',
            '/home/fetch_admin/robot_speech/confusion3.wav']
            # sound_ls = ['/home/fetch_admin/robot_speech/confusion1.wav',
            # '/home/fetch_admin/robot_speech/confusion2.wav']
            sound= np.random.choice(sound_ls)
            self.robot.speaker.play(sound)
            # self.robot.speaker.say("Hum... I am not sure what you are referring to...")#robot explains it is not sure verbally
            rospy.sleep(3)
            self.robot.speaker.soundhandle.stopAll()
            # self.human_attention.checkAttention(self.robot) #human feedback is needed, check human attention

            # self.robot.head.move_down_center()

            if len(order_ls)>=2:
                print("before reodering")
                print(self.short_term_memory['bounding_boxes'])
                print(self.short_term_memory['coord_3d'])
                print(self.short_term_memory['coord_3d_map'])
                print("========================================")
                print(order_ls)
                print("========================================")

                self.short_term_memory['bounding_boxes'] = self.reorder(self.short_term_memory['bounding_boxes'],order_ls)
                self.short_term_memory['coord_3d']  = self.reorder(self.short_term_memory['coord_3d'],order_ls)
                self.short_term_memory['coord_3d_map']  = self.reorder(self.short_term_memory['coord_3d_map'],order_ls)

                print("after reodering")
                print(self.short_term_memory['bounding_boxes'])
                print(self.short_term_memory['coord_3d'])
                print(self.short_term_memory['coord_3d_map'])

            #do pointing
            disam_result=point_to_disambiguate(self.short_term_memory,self.robot)
            item_coord =disam_result[0]
            print("item_coord")
            print(item_coord)

            print("done")
            self.robot.arm.safe_stow()

            if not(self.user_cmd in self.robot_input.detected_objs):# the object is novel
                #one-shot, update long term memory (support set)
                index = disam_result[1]
                novel_class_path = os.path.join(long_mem_path, self.user_cmd)
                try:
                    os.mkdir(novel_class_path)
                except OSError:
                    pass
                novel_obj_name =self.user_cmd +".png"
                novel_obj_name = os.path.join(novel_class_path, novel_obj_name)
                # test memory
                # {'bounding_boxes': [[422, 411, 488, 476]], 'coord_3d': [array([ 1.11766739, -0.20123148,  0.83372125])]}
                X0,Y0,X1,Y1 =self.short_term_memory["bounding_boxes"][index] #target bounding box
                cropped_image = self.view[Y0-10:Y1+10, X0-10:X1+10]
                cv2.imwrite(novel_obj_name, cropped_image)


            #pick up and place
            # self.robot.base.move_forward_mod(distance=0.55)#move to the pickup position
            # self.robot.base.move_forward_mod(distance=0.45)#move to the pickup position

            # robot_pos_map = self.robot.base.get_pose_map()
            robot_pos_map = self.robot.base.get_pose_amcl()
            print('robot_pos_map')
            print(robot_pos_map)

            # new_robot_pos_map = [robot_pos_map[0]+0.3,(robot_pos_map[1] + item_coord[1]*1.2),robot_pos_map[2]]
            # new_robot_pos_map = [robot_pos_map[0]-0.3,(robot_pos_map[1] + item_coord[1]*1.0),robot_pos_map[2]]
            # stop = raw_input("stop?")
            # if stop == "s":
            #     print("stopping the program")
            #     return
            new_robot_pos_map = [(item_coord[0]-0.175),robot_pos_map[1]-0.1,robot_pos_map[2]]

            self.robot.base.goto(new_robot_pos_map[0], new_robot_pos_map[1], theta = -pi/2)
            print('new_robot_pos_map')
            print(new_robot_pos_map)
            robot_pos_map = self.robot.base.get_pose_amcl()
            apporch_dist = abs((abs(item_coord[1])-abs(robot_pos_map[1]))-0.75)
            print("displacement")
            print(apporch_dist)
            self.robot.base.move_forward_mod(distance=apporch_dist)#move to the pickup position

            # new_robot_pos_map = [(robot_pos_map[0] + item_coord[1]*1.0),robot_pos_map[1]-0.1,robot_pos_map[2]]

            print('robot_pickup_pos_map')
            # print(self.robot.base.get_pose_map())
            print(self.robot.base.get_pose_amcl())
            time.sleep(1)
            self.robot.head.move_home()
            # self.robot.head.move_down_center(0.7)
            # robot.head.look_at(item_coord[0]-0.55,0,item_coord[2]-0.2)#look at the object
            # robot.torso.move_to(0.2)
            time.sleep(1)
            self.robot.head.move_down(0.45)
            time.sleep(1)
            savedView= self.robot.rgbCamera.getRGBImage()
            coord_3d, coord_3d_map = self.robot.yoloDetector.get_item_3d_coordinates_base_map(self.user_cmd, self.robot.rgbCamera.getRGBImage())
            print(len(coord_3d))

            # stop = raw_input("stop?")
            # if stop == "s":
            #     print("stopping the program")
            #     return

            if len(coord_3d) == 0: #label is not found in the current view
                detected_objs = self.robot.yoloDetector.detect()[1] #names of all detected objects in the view
                print("all objects in view")
                print(detected_objs)
                #remove non-pickable objects
                detected_objs = utils.get_pickable_item_in_view(detected_objs)
                print("1st pickable:")
                unique_objs = list(dict.fromkeys(detected_objs))
                print(unique_objs)


                if len(detected_objs) == 0:
                    #look down and try again:
                    self.robot.head.move_down(0.45)
                    time.sleep(1)
                    savedView= self.robot.rgbCamera.getRGBImage()
                    # cv2.imwrite("savedView2.png", savedView)
                    print("The robot sees:")
                    print(detected_objs)
                    detected_objs = self.robot.yoloDetector.detect()[1]
                    detected_objs = utils.get_pickable_item_in_view(detected_objs)
                    print("2nd pickable:")
                    print(detected_objs)
                    if self.user_cmd in detected_objs: #YOLO knows the object name
                        coord_3d, coord_3d_map = self.robot.yoloDetector.get_item_3d_coordinates_base_map(self.user_cmd, self.robot.rgbCamera.getRGBImage())
                    else: #YOLO does not know the object name
                        print("YOLO does not know the object name")
                        unique_objs = list(dict.fromkeys(detected_objs))
                        coord_3d=[]
                        coord_3d_map=[]
                        for obj in unique_objs:
                            c,c_map= self.robot.yoloDetector.get_item_3d_coordinates_base_map(obj, savedView)
                            coord_3d+=c #get the 3d-coordinates of all detected objects (base-link frame
                            coord_3d_map+=c_map
                    if len(coord_3d)==0:
                        sound= '/home/fetch_admin/robot_speech/notarget.wav'
                        self.robot.speaker.play(sound)
                        # self.robot.speaker.say("Sorry I don't see the object you want me to pick up")
                        s1.send("disconnect|".encode())
                        print("disconnect sent")
                        s1.close()
                        return
                else:
                    # unique_objs = list(dict.fromkeys(detected_objs))
                    coord_3d=[]
                    coord_3d_map=[]
                    # print("unique items")
                    # print(unique_objs)
                    # cv2.imwrite("savedView.png", savedView)
                    # cv2.imwrite("currentView.png", self.robot.rgbCamera.getRGBImage())
                    # a=raw_input("continue?")#pause the program
                    for obj in unique_objs:
                        print(obj)
                        c,c_map= self.robot.yoloDetector.get_item_3d_coordinates_base_map(obj, self.robot.rgbCamera.getRGBImage())
                        coord_3d+=c #get the 3d-coordinates of all detected objects (base-link frame
                        coord_3d_map+=c_map
            print(coord_3d)
            if len(coord_3d)>1: #detecting mutiple objects close up
                # temp_y = [abs(x[1]) for x in coord_3d] #ALL Y values we see
                # print("All y values")
                # print(temp_y)
                # index = np.argmin(temp_y)
                index = self.distance_check(item_coord,coord_3d_map)
                target = coord_3d[index]
            elif len(coord_3d) == 1:
                print("Only one target")
                target= coord_3d[0]
            else:
                target = []
                print("no detection")
                return
            print("first target")
            print(target)
            if len(target)!=0:
                self.robot.head.look_at(target[0],target[1],target[2])
                sound_ls = ['/home/fetch_admin/robot_speech/pickup1.wav',
                '/home/fetch_admin/robot_speech/pickup2.wav']
                sound= np.random.choice(sound_ls)

                # self.robot.speaker.say("I found the target ")
                # time.sleep(2)
                # target = []
                # while len(target)==0:#keep trying if target is not found
                #     coord_3d, _ = self.robot.yoloDetector.get_item_3d_coordinates(self.user_cmd, self.robot.rgbCamera.getRGBImage())
                #     try:
                #         target=coord_3d[0] #target is the most confident detection
                #     except IndexError:
                #         detected_objs = self.robot.yoloDetector.detect()[1]
                #         detected_objs = utils.get_pickable_item_in_view(detected_objs)
                #         print("3rd pickable:")
                #         print(detected_objs)
                #         unique_objs = list(dict.fromkeys(detected_objs))
                #         coord_3d=[]
                #         for obj in unique_objs:
                #             c,_= self.robot.yoloDetector.get_item_3d_coordinates(obj, self.robot.rgbCamera.getRGBImage())
                #             coord_3d+=c
                #         target=coord_3d[0]
                #     print("seeking target...")
                # print("final target")
                # print(target)

                #second social referencing check for objection
                self.robot.head.move_home()
                time.sleep(1)
                # self.robot.head.move_down_center(0.7)
                objection = self.objection_check()
                print('check variable')
                print(objection)
                if objection == "objection":
                    print("objection")
                    # self.robot.speaker.say("Sorry, it seems I got something terribly wrong, let's try again.")
                    self.robot.base.move_backward_mod(distance=0.1)
                    self.move_to_gesture_pos()
                    return

                #before pickup
                self.robot.speaker.play(sound)
                time.sleep(3)
                self.robot.speaker.soundhandle.stopAll()
                self.robot.head.look_at(target[0],target[1],target[2])
                self.robot.torso.move_to(0.3)
                self.robot.vertical_pick(target)
                self.robot.vertical_place([target[0]+0.1, target[1], target[2]])
                return
            # time.sleep(2)
            # self.robot.head.move_home()
            # # self.robot.head.look_at(item_coord[0],item_coord[1],item_coord[2])
            # self.robot.head.move_down_center()
            # self.robot.vertical_pick(item_coord)
            # self.robot.vertical_place([item_coord[0], item_coord[1], item_coord[2]])
        else:# no ambiguity, robot can pick up the object directly
            item_coord, item_coord_map = self.robot.yoloDetector.get_item_3d_coordinates_base_map(self.user_cmd, self.robot.rgbCamera.getRGBImage())
            item_coord=item_coord[0]
            item_coord_map=item_coord_map[0]
            self.robot.arm.safe_stow()#go to stow and ready to pick up
            robot_pos_map = self.robot.base.get_pose_amcl()
            # robot_pos_map = self.robot.base.get_pose_map()
            print('robot_pos_map')
            print(robot_pos_map)
            # print(item_coord[1])
            # new_robot_pos_map = [robot_pos_map[0]+0.3,(robot_pos_map[1] + item_coord[1]*1.2),robot_pos_map[2]]
            # new_robot_pos_map = [robot_pos_map[0]-0.3,(robot_pos_map[1] + item_coord[1]*1.0),robot_pos_map[2]]
            # apporch_dist = abs(item_coord[0]-0.2-0.65)
            # stop = raw_input("stop?")
            # if stop == "s":
            #     print("stopping the program")
            #     return
            # new_robot_pos_map = [(robot_pos_map[0] + item_coord[1]*1.0),robot_pos_map[1]-0.1,robot_pos_map[2]]
            new_robot_pos_map = [(item_coord_map[0]-0.175),robot_pos_map[1]-0.1,robot_pos_map[2]]

            print('new_robot_pos_map')
            print(new_robot_pos_map)
            # self.robot.base.goto(new_robot_pos_map[0], new_robot_pos_map[1], theta = -pi/1.65)
            self.robot.base.goto(new_robot_pos_map[0], new_robot_pos_map[1], theta = -pi/2)
            robot_pos_map = self.robot.base.get_pose_amcl()
            apporch_dist = abs((abs(item_coord_map[1])-abs(robot_pos_map[1]))-0.75)
            print("displacement")
            print(apporch_dist)

            self.robot.base.move_forward_mod(distance=apporch_dist)#move to the pickup position
            print('robot_pickup_pos_map')
            # print(self.robot.base.get_pose_map())
            print(self.robot.base.get_pose_amcl())
            time.sleep(1)
            self.robot.head.move_home()
            self.robot.head.move_down_center()
            # robot.head.look_at(item_coord[0]-0.55,0,item_coord[2]-0.2)#look at the object
            # robot.torso.move_to(0.2)
            time.sleep(2)
            savedView= self.robot.rgbCamera.getRGBImage()
            coord_3d, coord_3d_map = self.robot.yoloDetector.get_item_3d_coordinates_base_map(self.user_cmd, savedView)
            print(len(coord_3d))
            # cv2.imshow("window2",robot.yoloDetector.getDetectionImage())
            # cv2.waitKey(0)
            if len(coord_3d) == 0: #label is not found in the current view
                detected_objs = self.robot.yoloDetector.detect()[1] #names of all detected objects in the view
                #remove non-pickable objects
                detected_objs = utils.get_pickable_item_in_view(detected_objs)

                if len(detected_objs) == 0:
                    #look down and try again:
                    self.head.move_down(0.2)
                    time.sleep(1)
                    coord_3d, coord_3d_map = self.robot.yoloDetector.get_item_3d_coordinates_base_map(self.user_cmd, self.robot.rgbCamera.getRGBImage())
                    if len(coord_3d)==0:
                        sound= '/home/fetch_admin/robot_speech/notarget.wav'
                        self.robot.speaker.play(sound)
                        # self.robot.speaker.say("Sorry I don't see any objects I can pick up")
                        s1.send("disconnect|".encode())
                        print("disconnect sent")
                        s1.close()
                        return
                coord_3d=[]
                coord_3d_map=[]
                unique_objs = list(dict.fromkeys(detected_objs))
                for obj in unique_objs:
                    c,c_map= self.robot.yoloDetector.get_item_3d_coordinates_base_map(obj, savedView)
                    coord_3d+=c #get the 3d-coordinates of all detected objects (base-link frame
                    coord_3d_map+=c_map
            if len(coord_3d)>1: #detecting mutiple objects close up
                index = self.distance_check(item_coord_map,coord_3d_map)
                target = coord_3d[index]
            elif len(coord_3d) == 1:
                target= coord_3d[0]
            else:
                target = []
                print("no detection")
                return
            print("first target")
            print(target)
            if len(target)!=0:
                self.robot.head.look_at(target[0],target[1],target[2])
                sound_ls = ['/home/fetch_admin/robot_speech/pickup1.wav',
                '/home/fetch_admin/robot_speech/pickup2.wav']
                sound= np.random.choice(sound_ls)
                # time.sleep(2)
                # target = []
                # # savedView= robot.rgbCamera.getRGBImage()
                # while len(target)==0:#keep trying if target is not found
                #     coord_3d, _ = self.robot.yoloDetector.get_item_3d_coordinates(self.user_cmd, self.robot.rgbCamera.getRGBImage())
                #     target=coord_3d[0] #target is the most confident detection
                #     print("seeking target...")
                # print("final target")
                # print(target)

                #second social referencing check for objection
                self.robot.head.move_home()
                time.sleep(1)
                # self.robot.head.move_down_center(0.7)
                objection = self.objection_check()
                if objection == "objection":
                    print("objection")
                    # self.robot.speaker.say("Sorry, it seems I got something terribly wrong, let's try again.")
                    self.robot.base.move_backward_mod(distance=0.1)
                    self.move_to_gesture_pos()
                    return

                #before pickup
                self.robot.speaker.play(sound)
                time.sleep(3)
                self.robot.speaker.soundhandle.stopAll()
                self.robot.head.look_at(target[0],target[1],target[2])
                self.robot.torso.move_to(0.3)
                self.robot.vertical_pick(target)
                self.robot.vertical_place([target[0]+0.1, target[1], target[2]])
                return
            # self.robot.base.move_forward_mod(distance=0.45)#move to the pickup position
            # time.sleep(2)
            # self.robot.torso.move_to(.3)
            # self.robot.head.move_home()
            # self.robot.head.move_down_center()
            # coord_3d, _ = self.robot.yoloDetector.get_item_3d_coordinates(self.user_cmd, self.robot.rgbCamera.getRGBImage())
            # coord_3d = coord_3d[0]
            # self.robot.vertical_pick(coord_3d)
            # self.robot.vertical_place([coord_3d[0], coord_3d[1], coord_3d[2]])

if __name__ == '__main__':
    rospy.init_node("test_final")
    arch=SocialReferencingArch()
    # arch.run()
    # time.sleep(1)
    # s.close()
    try:
        arch.run()
        # time.sleep(3)
        # s.close()
    except Exception as e:
        print(e)
        # time.sleep(3)
        # s.close()

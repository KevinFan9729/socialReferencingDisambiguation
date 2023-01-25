import rospy
from kf_robot import kf_Robot
import time
from gesture_detection.FetchDNNwithCalibration import headGesture
import numpy as np
from numpy import pi
import threading
import socket
import cv2

host = "kd-pc29.local"
port = 8091
size = 4
#client
#get speech back from speech_feedback.py, server start this file frist
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind((host,port))
# s.listen(5)
# client, address = s.accept()


#client test
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket.socket(socket.AF_INET, SOCK_DGRAM) for UDP connection
s.connect((host, port)) #198.162.0.11



data="-1"

def speech_thread_func(userHeadGesture):
    global data
    print("thread started")
    # data = client.recv(1024)# initail read
    data = s.recv(1024)# initail read
    data = data.strip().decode("utf-8")
    # print("data is: ")
    # print(data)
    while (data!="2" and userHeadGesture!="Yes"):#while speech is not confirmational
        # print("thread is alive")
        # data = client.recv(1024)# initail read
        try:
            data = s.recv(1024)# initail read
        except Exception as e:
            print("An exception has occured.")
            print(e)
            print("speech thread in disambigution is dead.")
            return
        data = data.strip().decode("utf-8")
        # print("data is: ")
        # print(data)
    print("speech thread in disambigution is dead.")
    return

# def point_to_disambiguate(userCMD, robot):
def point_to_disambiguate(short_term_memory, robot):
    global data
    time.sleep(0.5)
    # savedView= robot.rgbCamera.getRGBImage()
    # coord_3d, up = robot.yoloDetector.get_item_3d_coordinates(userCMD, savedView)#(base-link frame)
    # print(len(coord_3d))
    # # cv2.imshow("window2",robot.yoloDetector.getDetectionImage())
    # # cv2.waitKey(0)
    # if len(coord_3d) == 0: #label is not found in the current view
    #     detected_objs = robot.yoloDetector.detect()[1] #names of all detected objects in the view
    #     #remove non-pickable objects
    #     detected_objs = list(filter(('person').__ne__, detected_objs))
    #     detected_objs = list(filter(('bed').__ne__, detected_objs))
    #     detected_objs = list(filter(('diningtable').__ne__, detected_objs))
    #     detected_objs = list(filter(('tvmonitor').__ne__, detected_objs))
    #     detected_objs = list(filter(('chair').__ne__, detected_objs))
    #     detected_objs = list(filter(('cellphone').__ne__, detected_objs))
    #     detected_objs = list(filter(('toilet').__ne__, detected_objs))
    #     detected_objs = list(filter(('suitcase').__ne__, detected_objs))
    #
    #     if len(detected_objs) == 0:
    #         robot.speaker.say("Sorry I don't see any objects I can pick up")
    #         return
    #     unique_objs = list(dict.fromkeys(detected_objs))
    #     for obj in unique_objs:
    #         c,u= robot.yoloDetector.get_item_3d_coordinates(obj, savedView)
    #         coord_3d+=c #get the 3d-coordinates of all detected objects (base-link frame)

    # print(coord_3d)
    coord_3d = short_term_memory["coord_3d"]
    coord_3d_map =short_term_memory["coord_3d_map"]
    robot.gripper.close()
    view_len = len(coord_3d)
    print("view_len")
    print(view_len)
    for index, c in enumerate(coord_3d):
        robot.head.look_at(c[0],c[1],c[2])
        # c[0]=0.7
        # c[2]+=0.05
        # pc=[0.6, c[1], c[2]+0.03]
        pc=[0.55, c[1], c[2]+0.03]
        # pc=[0.5, c[1], c[2]+0.05]

        # if view_len ==1: # only one object in view
        #     view_len = -1 #only one object flag
        #     break
        # if view_len == -1:
            # return c , index
        robot.pointing(pc)
        print("pointing at")
        print(pc)
        sound_ls = ['/home/fetch_admin/robot_speech/question1.wav',
        '/home/fetch_admin/robot_speech/question2.wav']
        sound= np.random.choice(sound_ls)
        robot.speaker.play(sound)
        time.sleep(1)
        robot.speaker.soundhandle.stopAll()
        userHeadGesture=""
        speechBackground=threading.Timer(1, speech_thread_func, args = (userHeadGesture,))
        speechBackground.setDaemon(True)
        speechBackground.start()
        time.sleep(1)
        robot.head.move_home()
        robot.head.move_down_center(0.15)

        while True:
            if data=="2":
                print("speech Yes")
                sound='/home/fetch_admin/robot_speech/confirmation.wav'
                robot.speaker.play(sound)
                time.sleep(3)
                robot.speaker.soundhandle.stopAll()
                s.close()
                return coord_3d_map[index] , index
            elif data == "0":
                print("speech No")
                data = "-1"
                break

            userHeadGesture=headGesture()
            # if data!="2" and data!="": #make sure that speech_feedback is not dead, prevent broken pipe
            #     try:
            #         s.send(userHeadGesture.encode())
            #         # client.send(userHeadGesture.encode())
            #     except:
            #         pass
            if userHeadGesture == 'Yes' or data=="2" or data == u'':
                print("head or speech yes")
                sound='/home/fetch_admin/robot_speech/confirmation.wav'
                robot.speaker.play(sound)
                time.sleep(3)
                robot.speaker.soundhandle.stopAll()
                s.close()
                # robot.head.look_at(c[0],c[1],c[2])
                return coord_3d_map[index] , index
            elif userHeadGesture == 'No' or data=="0":
                print("head or speech no")
                print('No')
                data = "-1"
                # view_len-=1
                break
            print((userHeadGesture,data))
            # print(data)
            # robot.speaker.say("I am still not sure, is this the object you are referring to?")
            robot.head.look_at(c[0],c[1],c[2])
            robot.pointing(pc)
            # time.sleep(1)
            robot.head.move_home()
            robot.head.move_down_center(0.15)
            # time.sleep(3)
    # client.send("Yes".encode())
    # s.send("Yes".encode())
    print("Are you messing with me?")
    #robot.speaker.say("Are you messing with me?")
# def test_gesture_detect(robot):
#     while True:
#         userHeadGesture=headGesture()
#         print(userHeadGesture)
#         break
        # robot.speaker.say(userHeadGesture)
def test_speech_detect():
    global data
    userHeadGesture=""
    speechBackground=threading.Timer(1, speech_thread_func, args = (userHeadGesture,))
    speechBackground.setDaemon(True)
    speechBackground.start()
    while True:
        print(data)
        if data == "2":
            print("yes!!!")
            break
if __name__ == '__main__':

    # print('1')
    rospy.init_node("test_disambiguation")
    # print('2')

    robot = kf_Robot()
    # gesture_pos = [0.410, -0.138]# maybe an issue, the robot seems to draft to the right (robot's right)
    gesture_pos = [-0.22157120621, -0.279244163166]
    robot.base.goto(gesture_pos[0], gesture_pos[1], theta = -pi/2)
    time.sleep(1.0)
    robot.torso.move_to(0.3)
    robot.head.move_home()
    # robot.head.move_down_center()
    robot.arm.safe_stow()
    # robot.torso.move_to(0.12)
    robot.torso.move_to(0.169)
    # print('3')
    time.sleep(1.0)
    point_to_disambiguate('cup',robot)
    robot.arm.safe_stow()
    robot.torso.move_to(0.0)
    # test_pointing('cup', robot)

    # test_gesture_detect(robot)
    # test_speech_detect()

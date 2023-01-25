from kf_robot import kf_Robot
import time
from gesture_detection.FetchDNNwithCalibration import headGesture
from numpy import pi
import threading
import socket
import cv2
import rospy
import numpy as np

def point_to_disambiguate(userCMD, robot):
    global data
    time.sleep(0.5)
    savedView= robot.rgbCamera.getRGBImage()
    coord_3d, up = robot.yoloDetector.get_item_3d_coordinates(userCMD, savedView)#(base-link frame)
    print(len(coord_3d))
    # cv2.imshow("window2",robot.yoloDetector.getDetectionImage())
    # cv2.waitKey(0)
    if len(coord_3d) == 0: #label is not found in the current view
        detected_objs = robot.yoloDetector.detect()[1] #names of all detected objects in the view
        #remove non-pickable objects
        detected_objs = list(filter(('person').__ne__, detected_objs))
        detected_objs = list(filter(('bed').__ne__, detected_objs))
        detected_objs = list(filter(('diningtable').__ne__, detected_objs))
        detected_objs = list(filter(('tvmonitor').__ne__, detected_objs))
        detected_objs = list(filter(('chair').__ne__, detected_objs))
        detected_objs = list(filter(('cellphone').__ne__, detected_objs))
        detected_objs = list(filter(('toilet').__ne__, detected_objs))

        if len(detected_objs) == 0:
            robot.speaker.say("Sorry I don't see any objects I can pick up")
            return
        unique_objs = list(dict.fromkeys(detected_objs))
        for obj in unique_objs:
            c,u= robot.yoloDetector.get_item_3d_coordinates(obj, savedView)
            coord_3d+=c #get the 3d-coordinates of all detected objects (base-link frame)

    print(coord_3d)
    robot.gripper.close()
    for c in coord_3d:
        robot.head.look_at(c[0],c[1],c[2])

        pc=[0.6, c[1], c[2]+0.03]

        robot.pointing(pc)
        print("pointing at")
        print(pc)
        userHeadGesture=""
        # speechBackground=threading.Timer(1, speech_thread_func, args = (userHeadGesture,))
        # speechBackground.setDaemon(True)
        # speechBackground.start()
        time.sleep(1)
        robot.head.move_home()
        return c #return the first coordinate for testing
        # while True:
        #     userHeadGesture=headGesture()
        #     if userHeadGesture == 'Yes' or data=="2" or data == u'':
        #         if userHeadGesture=='Yes':
        #             print("head yes")
        #         print('Yes')
        #         sound='/home/fetch_admin/sounds/confirmation.wav'
        #         robot.speaker.play(sound)
        #         time.sleep(3)
        #         robot.speaker.soundhandle.stopAll()
        #         # robot.speaker.say("Thank you for your clarification")
        #         s.close()
        #         # robot.head.look_at(c[0],c[1],c[2])
        #         return c
        #     elif userHeadGesture == 'No' or data=="0":
        #         if userHeadGesture=='No':
        #             print("head no")
        #         print('No')
        #         data = "-1"
        #         break
        #     print((userHeadGesture,data))
        #     # print(data)
        #     # robot.speaker.say("I am still not sure, is this the object you are referring to?")
        #     robot.head.look_at(c[0],c[1],c[2])
        #     robot.pointing(pc)
        #     time.sleep(1)
        #     robot.head.move_home()
        #     time.sleep(3)
    print("Are you messing with me?")

if __name__ == '__main__':

    # print('1')
    rospy.init_node("test_disambiguation")
    # print('2')

    robot = kf_Robot()
    # gesture_pos = [1.127, -0.34]#robohub coordinate
    gesture_pos = [-0.507, -0.037] #E5 coordinate
    robot.base.goto(gesture_pos[0], gesture_pos[1], theta = 2*pi)
    time.sleep(1.0)
    robot.torso.move_to(0.3)
    robot.head.move_home()
    # robot.head.move_down_center()
    robot.arm.safe_stow()
    # robot.torso.move_to(0.12)
    robot.torso.move_to(0.169)
    # print('3')
    time.sleep(1.0)
    item_coord = point_to_disambiguate('cup',robot)
    print("item_coord")
    print(item_coord)
    robot.arm.safe_stow()
    robot_pos_map = robot.base.get_pose_map()
    print('robot_pos_map')
    print(robot_pos_map)
    print("dispalcement")
    print(item_coord[1])
    # new_robot_pos_map = [robot_pos_map[0]+0.3,(robot_pos_map[1] + item_coord[1]*1.2),robot_pos_map[2]]
    new_robot_pos_map = [robot_pos_map[0]+0.3,(robot_pos_map[1] + item_coord[1]*1.0),robot_pos_map[2]]
    print('new_robot_pos_map')
    print(new_robot_pos_map)
    robot.base.goto(new_robot_pos_map[0], new_robot_pos_map[1], theta = 2*pi)


    robot.base.move_forward_mod(distance=0.3)#move to the pickup position
    print('robot_pickup_pos_map')
    print(robot.base.get_pose_map())
    time.sleep(1)
    robot.head.move_home()
    robot.head.move_down_center()
    # robot.head.look_at(item_coord[0]-0.55,0,item_coord[2]-0.2)#look at the object
    # robot.torso.move_to(0.2)
    time.sleep(2)
    savedView= robot.rgbCamera.getRGBImage()
    coord_3d, up = robot.yoloDetector.get_item_3d_coordinates('cup', savedView)
    print(len(coord_3d))
    # cv2.imshow("window2",robot.yoloDetector.getDetectionImage())
    # cv2.waitKey(0)
    if len(coord_3d) == 0: #label is not found in the current view
        detected_objs = robot.yoloDetector.detect()[1] #names of all detected objects in the view
        #remove non-pickable objects
        detected_objs = list(filter(('person').__ne__, detected_objs))
        detected_objs = list(filter(('bed').__ne__, detected_objs))
        detected_objs = list(filter(('diningtable').__ne__, detected_objs))
        detected_objs = list(filter(('tvmonitor').__ne__, detected_objs))
        detected_objs = list(filter(('chair').__ne__, detected_objs))
        detected_objs = list(filter(('cellphone').__ne__, detected_objs))
        detected_objs = list(filter(('toilet').__ne__, detected_objs))

        if len(detected_objs) == 0:
            robot.speaker.say("Sorry I don't see any objects I can pick up")
        unique_objs = list(dict.fromkeys(detected_objs))
        for obj in unique_objs:
            c,u= robot.yoloDetector.get_item_3d_coordinates(obj, savedView)
            coord_3d+=c #get the 3d-coordinates of all detected objects (base-link frame
    if len(coord_3d)>1: #detecting mutiple objects close up
        temp_y = [abs(x[1]) for x in coord_3d]
        index = np.argmin(temp_y)
        target = coord_3d[index]
    elif len(coord_3d) == 1:
        target= coord_3d[0]
    else:
        target = []
        print("no detection")
    print("first target")
    print(target)
    if len(target)!=0:
        robot.head.look_at(target[0],target[1],target[2])
        time.sleep(3)
        # savedView= robot.rgbCamera.getRGBImage()
        coord_3d, _ = robot.yoloDetector.get_item_3d_coordinates('cup', robot.rgbCamera.getRGBImage())
        target=coord_3d[0] #target is the most confident detection
        print("final target")
        print(target)
        robot.vertical_pick(target)
        robot.vertical_place([target[0], target[1], target[2]])

            # sorted(np.absolute(coord_3d), key=itemgetter(1)))# the one that has the smallest y-value is the target



    # robot.torso.move_to(0.0)

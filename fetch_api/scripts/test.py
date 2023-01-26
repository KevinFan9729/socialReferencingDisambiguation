from fetch_api.robot import Robot
import rospy
from numpy import pi
import thread
import time
from fetch_api.camera_modules import Get3Dcoordinates
import math

def record_obj_on_map(robot, obj_name):
    while True:
        # pose_base = robot.yoloDetector.get_item_3d_coordinates(obj_name, robot.rgbCamera.getRGBImage())#object position in the base link frame
        # pos_cam= robot.yoloDetector.get_item_3d_coordinates_cam_map(obj_name, robot.rgbCamera.getRGBImage())[0]#object position in camera frame
        # pos_map = robot.yoloDetector.get_item_3d_coordinates_cam_map(obj_name, robot.rgbCamera.getRGBImage())[1]# object position in map frame
        # print("object position in base link frame")
        # print(pose_base)
        # print("object position in camera frame")
        # print(pos_cam)
        # print("object position in map frame")
        # print(pos_map)

        ##amcl_pos is more accurate
        #rostopic echo /amcl_pose
        # robot_map = robot.base.get_pose_map()
        # print("robot position in map frame")
        # print(robot_map)


        gesture_pos = [0.118, -0.226]
        robot.base.goto(gesture_pos[0], gesture_pos[1], theta = 2*pi)
        time.sleep(5)
        robot.base.move_forward_mod(second=1.95)
        # pick_up_pos = [0.562657954821, -0.282996935049]
        # robot.base.goto(pick_up_pos[0], pick_up_pos[1], theta = 2*pi)

        # x_dist_map = math.sqrt((robot_map[0] - pos_map[0])**2)
        # print("distance")
        # print(x_dist_map)
        break
        # dist = np.sqrt(pos_cam[0]**2 + pos_cam[0]**2 + pos_cam[0]**2)




if __name__ == '__main__':
    rospy.init_node("test_pick_place")

    robot = Robot()
    record_obj_on_map(robot, 'cup')

    ###Uncomment if you want collision avoidance (recommended)

    # robot.scene.clear()
    # pause = [False]
    # thread = thread.start_new_thread(robot.scene.update, (pause, ))
    # time.sleep(2)
    #
    # pause[0] = True
    # robot.torso.move_to(.3)
    # # robot.arm.safe_tuck()
    # # robot.head.move_home()
    # # robot.head.move_down_center(0.6)
    # time.sleep(2)
    # robot.arm.safe_stow()

    #

    # while 1:
    #     print(robot.yoloDetector.get_item_list())
    #     obj_name = raw_input("Which object do you want to pick?")
    #     # obj_name = "cup"
    #     coord_3d, up = robot.yoloDetector.get_item_3d_coordinates(obj_name, robot.rgbCamera.getRGBImage())
    #     print("Picking " + obj_name + ": ", coord_3d[0])
    #     # coord_3d = coord_3d[0]
    #
    #     # robot.vertical_pick(coord_3d)
    #     #
    #     # robot.vertical_place([coord_3d[0], coord_3d[1], coord_3d[2]])
    #     break

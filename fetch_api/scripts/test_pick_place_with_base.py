from fetch_api.robot import Robot
import rospy
from numpy import pi
import thread
import time
import tf2_ros
import tf2_py as tf2
import tf2_ros
from tf2_sensor_msgs.tf2_sensor_msgs import do_transform_cloud, transform_to_kdl
import PyKDL

def do_transform_point(point, transform):
    p = transform_to_kdl(transform) * PyKDL.Vector(*point)
    return p

if __name__ == '__main__':
    rospy.init_node("test_pick_place")

    robot = Robot()

    ###Uncomment if you want collision avoidance (recommended)
    # robot.scene.clear()
    # pause = [False]
    # thread = thread.start_new_thread(robot.scene.update, (pause, ))
    # time.sleep(2)

#     tf_buffer = tf2_ros.Buffer()
#     tf_listener = tf2_ros.TransformListener(tf_buffer)
#
#     trans_rgb_map = tf_buffer.lookup_transform("map", "base_link",
#                                                           # msg.header.stamp,
#                                                           rospy.Time(0),
#                                                           rospy.Duration(1.0))
#
#     trans = tf_buffer.lookup_transform("base_link", "map",
#                                        #msg.header.stamp,
#                                        rospy.Time().now(),
#                                        rospy.Duration(1.0))
# #
    # pause[0] = True
    # print(robot.base.get_pose_map())
    # robot.arm.safe_tuck()
    # gesture_pos = [1.313,-0.318] #robohub coordinate
    # gesture_pos = [0.426282, -0.161012]
    gesture_pos = [-0.156793796789, -0.212407004395]
    # intermediate_pos= [gesture_pos[0]-1.15*gesture_pos[0], gesture_pos[1]+gesture_pos[1]*2]
    # robot.base.goto(intermediate_pos[0], intermediate_pos[1], theta = 2*pi)
    # time.sleep(2)
    # robot.base.goto(gesture_pos[0], gesture_pos[1], theta = 2*pi)
    robot.base.goto(gesture_pos[0], gesture_pos[1], theta = -pi/2)

    # robot.arm.safe_tuck()
    # robot.head.move_home()
    # robot.head.move_down_center(0.6)
    robot.torso.move_to(.3)
    robot.arm.safe_stow()
    robot.torso.move_to(.0)
    #95 cm away from the table

    while 1:

        robot.base.move_forward_mod(distance=0.45)
        # robot.base.move_forward_mod(distance=0.55)

        time.sleep(1)



        # map_point = do_transform_point(coord_3d, trans_rgb_map)
        # print(map_point)
        # print(do_transform_point(map_point, trans))
        robot.torso.move_to(.3)
        robot.head.move_home()
        robot.head.move_down_center(0.6)
        print(robot.yoloDetector.get_item_list())
        obj_name = raw_input("Which object do you want to pick?")
        # obj_name = "cup"
        time.sleep(1)
        coord_3d, up = robot.yoloDetector.get_item_3d_coordinates(obj_name, robot.rgbCamera.getRGBImage())
        print("Picking " + obj_name + ": ", coord_3d[0])
        coord_3d = coord_3d[0]
        robot.vertical_pick(coord_3d)

        robot.vertical_place([coord_3d[0], coord_3d[1], coord_3d[2]])
        # coord_3d = [0.65268985, 0.04819747, 0.82]
        # robot.vertical_pick(coord_3d)
        # robot.vertical_place(coord_3d)
        break

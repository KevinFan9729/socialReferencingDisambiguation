import rospy
from fetch_api.robot import Robot
from math import pi
import math
from moveit_msgs.msg import MoveItErrorCodes
import time
# from torso_control import TorsoControl
# from head_control import HeadControl
# from gripper_control import GripperControl



class kf_Robot(Robot):

    def tuck(self):
        self.arm.pause[0] = False
        self.gripper.open()
        self.head.move_home()
        self.arm.tuck()

    def wave_ready(self):
        self.arm.pause[0] = False
        self.gripper.open()
        self.arm.move_joint_positions([1.6, -0.3, -0.2, -1.6, 1.2, 0, 0], blocking=True)


    def wave(self, initial_time, duration=50):
        wave_count = 0
        self.torso.move_to(0.2)
        self.wave_ready()
        # time.sleep(1)

        pos = self.arm.get_pose()
        pos = list(pos)

        while True:
            t = time.time() - initial_time
            # pos[3] = 0.3 * math.sin(2 * t) - 1.2
            # pos[1] = 0.15 * math.sin(2 * t) - 0.1
            joint_1 = [-0.9, -1.5]
            joint_2 = [0.05, -0.25]
            pos[3] = joint_1[wave_count%2]
            pos[1] = joint_2[wave_count%2]
            wave_count+=1
            # print(wave_count)
            self.arm.move_joint_positions(pos,blocking=True)# set blocking to False causes odd issues
            # self.torso.move_to(0.15 * math.sin(4 * t) + 0.15)
            if t >= duration:
                # self.torso.move_to(0.3)
                self.arm.safe_stow()
                # self.torso.move_to(0)
                return

    # def wave_ready(self): #local method
    #     self.pause[0] = False
    #     gripper.open()
    #     while not rospy.is_shutdown():
    #         result = self.move_group.moveToJointPosition(self.joint_names, [1.6, -0.3, -0.2, -1.6, 1.2, 0, 0],
    #                                                      0.02)  # move the elbow_flex_joint with a sinusoidal function center around -1.6
    #         if result.error_code.val == MoveItErrorCodes.SUCCESS:
    #             self.pause[0] = True
    #             return
    #
    # def wave(self, initial_time, duration=50):
    #     wave_count = 0
    #     self.wave_ready(gripper)
    #
    #     pos = self.get_pose()
    #     pos = list(pos)
    #
    #     while True:
    #         t = time.time() - initial_time
    #         # pos[3] = 0.3 * math.sin(2 * t) - 1.2
    #         # pos[1] = 0.15 * math.sin(2 * t) - 0.1
    #         joint_1 = [-0.9, -1.5]
    #         joint_2 = [0.05, -0.25]
    #         pos[3] = joint_1[wave_count%2]
    #         pos[1] = joint_2[wave_count%2]
    #         wave_count+=1
    #
    #         self.move_joint_positions(pos)
    #         torso.move_to(0.15 * math.sin(4 * t) + 0.15)
    #         if t > duration:
    #             torso.move_to(0.2)
    #             self.tuck()
    #             torso.move_to(0)
    #             return

    def confusion_ready(self):
        self.arm.pause[0] = False
        self.gripper.open()
        while not rospy.is_shutdown():
            result = self.arm.move_group.moveToJointPosition(self.arm.joint_names, [1.6, -0.3, 0.1, -1.8, -0.5, -1, 0], 0.02)  # move the elbow_flex_joint with a sinusoidal function center around -1.6
            # can try to move the forearm_roll_joint at indexed 4 or the upperarm_roll_joint at indexed 2
            # indexed 5 joint lower
            if result.error_code.val == MoveItErrorCodes.SUCCESS:
                self.arm.pause[0] = True
                return

    def confusion(self, duration=50):

        self.confusion_ready()
        self.head.move_down()

        pos = self.arm.get_pose()
        pos = list(pos)

        initial_time = time.time()

        while True:
            t = time.time() - initial_time
            pos[4] = 0.15 * math.sin(2 * t) - 0
            pos[2] = 0.3 * math.sin(2 * t) + 0
            self.arm.move_joint_positions(pos)
            # head.head_sweep(0.5*math.sin(2*t)+0)
            if t > duration:
                self.arm.tuck()
                aelf.head.move_home()
                return

    def pointing(self, coord_3d):
        # move the arm to 3d coordinate
        self.arm.move_cartesian_position([coord_3d[0], coord_3d[1], coord_3d[2]], [0.0, 0.0, 2 * pi + 0.01])
        # self.gripper.close()

if __name__ == '__main__':
    import time

    initial_time = time.time()
    rospy.init_node("test_kf_robot")

    kf_robot = kf_Robot()

    kf_robot.torso.move_to(0.3)
    # kf_robot.arm.tuck()
    initial_time = time.time()
    # kf_robot.wave(initial_time, 15)

    # kf_robot.arm.move_cartesian_position_speed([0.6478926483367018, -0.16955347545496427, 0.8426119154023802], 4.)

    # kf_robot.arm.tuck()

    # while True:
    #     t = time.time()-initial_time
    #     kf_robot.arm.wave(t)
    #     if t > 100:
    #         break

    # kf_robot.arm.wave(initial_time, 25)
    # kf_robot.arm.confusion_ready()
    # kf_robot.arm.confusion(initial_time, 25)

    # kf_robot.arm.stow()
    # kf_robot.torso.move_to(0.4)
    # kf_robot.arm.tuck()
    # time.sleep(5)
    # kf_robot.arm.move_joint_positions(
    #     [1.6, -0.3, -0.2, -1.6, 1.2, 0, 0])  # move the elbow_flex_joint with a sinusoidal function center around -1.6
    # time.sleep(5)
    # kf_robot.arm.move_joint_position("shoulder_pan_joint", .5)
    # time.sleep(5)



    coord_3d = [0.8, 0, 0.5] #center  # [0.6478926483367018, -0.16955347545496427, 0.8426119154023802]
    coord_3d_b = [0.7, 0.3, 1.2] # human right
    coord_3d_c= [0.65, -0.3, 0.9]  # human left
    kf_robot.pointing(coord_3d_b)
    kf_robot.gripper.close()
    # kf_robot.arm.pointing(coord_3d_b)
    # kf_robot.arm.pointing(coord_3d_c)
    # kf_robot.arm.tuck()
    # kf_robot.arm.move_cartesian_position([coord_3d[0], coord_3d[1], coord_3d[2]], [pi / 2, 0.0, 2 * pi + 0.01])


    # y left to right, x into the page and out of the page, z height, angle of the gripper roll, pitch, yaw in rads, yaw may needs to be dynamic
    # print("somehow reached goal even though it makes no sense")
    # time.sleep(15)
    # kf_robot.arm.tuck()
    # time.sleep(5)
    # kf_robot.torso.move_to(0.0)
    # kf_robot.arm.scene.clear()

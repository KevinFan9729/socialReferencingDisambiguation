import rospy
import geometry_msgs.msg
import trajectory_msgs.msg
import control_msgs.msg
from geometry_msgs.msg import PoseWithCovarianceStamped
import yaml
import time
import tf
import actionlib
import moveit_commander
from nav_msgs.msg import Odometry
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from math import sin, cos
from socket import *
IP="kd-pc29.local"
PORT=8080

s = socket(AF_INET, SOCK_STREAM)
try:
    s.connect((IP, PORT))
except error:
    s = None

class BaseControl(object):
    """ Move base and navigation """

    def __init__(self):
        ## Create publisher to move the base
        self._pub = rospy.Publisher('/cmd_vel', geometry_msgs.msg.Twist, queue_size=10)
        self.tf_listener = tf.TransformListener()

        ##action client for navigation
        self.client = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        rospy.loginfo("Waiting for move_base...")
        if not self.client.wait_for_server():
            rospy.logerr("Could not connect to move_base... Did you roslaunch fetch_navigation fetch_nav.launch map_file:=/home/fetch_admin/map_directory/5427_updated.yaml?")
        else:
            rospy.loginfo("Got move_base")

        self.actual_positions = (0, 0, 0)
        self.actual_vel = (0, 0, 0)
        # self.amcl_sub = rospy.Subscriber("/amcl_pose")

        ## subscribe to odom to get the robot current position
        def callback(msg):
            p = msg.pose.pose.position
            self.actual_positions = (p.x, p.y, p.z)
        self._sub = rospy.Subscriber("/amcl_pose", PoseWithCovarianceStamped, callback)
        self.actual_positions = (0, 0, 0)

        while self._pub.get_num_connections() == 0:
            rospy.sleep(0.1)

        if s:
            s.send(",".join([str(d) for d in list(self.get_pose())]))

    def move_forward(self, speed=0.2):
        tw = geometry_msgs.msg.Twist()
        tw.linear.x =abs(speed)
        self._pub.publish(tw)
        if s:
            s.send(",".join([str(d) for d in list(self.get_pose())]))

    def move_forward_mod(self, second=None, distance=None, speed=0.3):
        tw = geometry_msgs.msg.Twist()
        if (second is None) and (distance is None):
            tw.linear.x = abs(speed)
            self._pub.publish(tw)
        elif (second is not None) and (distance is None):
            cur_time = time.time()
            while time.time() - cur_time < second:
                tw.linear.x = abs(speed)
                self._pub.publish(tw)
            # self.get_pose()

        elif (second is None) and (distance is not None):
            cur_time = time.time()
            while time.time() - cur_time < 1:
                tw.linear.x = abs(0)
                self._pub.publish(tw)
            # init_pos = self.get_pose_map()
            init_pos = self.get_pose_amcl()
            print(init_pos)
            dx = 0
            dy = 0
            while max(dx, dy) < distance:
                tw.linear.x = abs(speed)
                self._pub.publish(tw)
                # cur_pos = self.get_pose_map()
                cur_pos = self.get_pose_amcl()
                dx = abs(cur_pos[0] - init_pos[0])
                dy = abs(cur_pos[1] - init_pos[1])
                # old_pos = copy.copy(cur_pos)
            print(cur_pos)
        elif (second is not None) and (distance is not None):
            print("only one of second or distance!")

    def move_backward(self, speed=-0.2):
         tw = geometry_msgs.msg.Twist()
         tw.linear.x = -abs(speed)
         self._pub.publish(tw)
         if s:
             s.send(",".join([str(d) for d in list(self.get_pose())]))

    def move_backward_mod(self, second=None, distance=None, speed=-0.2):
        tw = geometry_msgs.msg.Twist()
        if (second is None) and (distance is None):
            tw.linear.x = -abs(speed)
            self._pub.publish(tw)
        elif (second is not None) and (distance is None):
            cur_time = time.time()
            while time.time() - cur_time < second:
                tw.linear.x = -abs(speed)
                self._pub.publish(tw)
            # self.get_pose()

        elif (second is None) and (distance is not None):
            cur_time = time.time()
            while time.time() - cur_time < 1:
                tw.linear.x = -abs(0)
                self._pub.publish(tw)
            init_pos = self.get_pose_map()
            print(init_pos)
            dx = 0
            dy = 0
            while max(dx, dy) < distance:
                tw.linear.x = -abs(speed)
                self._pub.publish(tw)
                cur_pos = self.get_pose_map()
                dx = abs(cur_pos[0] - init_pos[0])
                dy = abs(cur_pos[1] - init_pos[1])
                # old_pos = copy.copy(cur_pos)
            print(cur_pos)
        elif (second is not None) and (distance is not None):
            print("only one of second or distance!")

    def move_left(self, angle=0.2):
        tw = geometry_msgs.msg.Twist()
        tw.angular.z = abs(angle)
        self._pub.publish(tw)
        if s:
            s.send(",".join([str(d) for d in list(self.get_pose())]))

    def move_right(self, angle=-0.2):
        tw = geometry_msgs.msg.Twist()
        tw.angular.z = -abs(angle)
        self._pub.publish(tw)
        if s:
            s.send(",".join([str(d) for d in list(self.get_pose())]))

    ## get 3D position of the robot
    def get_pose_amcl(self):
        return self.actual_positions

    def get_pose_map(self):
        # self.move_forward(speed=0.01)

        now = rospy.Time.now()
        self.tf_listener.waitForTransform('/map', '/base_link', now, rospy.Duration(4.0))
        (trans, rot) = self.tf_listener.lookupTransform('/map', '/base_link', now)# get robot map coordinates from the base_link frame

        # (trans, rot) = self.tf_listener.lookupTransform('/map', '/base_link', rospy.Time(0))# get robot map coordinates from the base_link frame
        new_rot = tf.transformations.euler_from_quaternion(rot)# Return Euler angles from quaternion for specified axis sequence
        # print(trans, new_rot)
        self.actual_positions = [trans[0], trans[1], new_rot[2]]
        return self.actual_positions


    def __del__(self):
        self._pub.publish(geometry_msgs.msg.Twist())
        move_goal = MoveBaseGoal()
        self.client.send_goal(move_goal)
        self.client.wait_for_result()

    ##### Navigation
    def goto(self, x, y, theta=None, frame="map", quaternions=[0,0]):
        move_goal = MoveBaseGoal()
        move_goal.target_pose.pose.position.x = x
        move_goal.target_pose.pose.position.y = y
        if theta:
            move_goal.target_pose.pose.orientation.z = sin(theta/2.0)
            move_goal.target_pose.pose.orientation.w = cos(theta/2.0)
        else:
            move_goal.target_pose.pose.orientation.z = quaternions[0]
            move_goal.target_pose.pose.orientation.w = quaternions[1]
        move_goal.target_pose.header.frame_id = frame
        move_goal.target_pose.header.stamp = rospy.Time.now()
        self.client.send_goal(move_goal)
        self.client.wait_for_result()
        if s:
            s.send(",".join([str(d) for d in list(self.get_pose())]))


    def goto_relative(self, dx, dy, dtheta, frame="map"):
        move_goal = MoveBaseGoal()
        move_goal.target_pose.pose.position.x = self.actual_positions[0] + dx
        move_goal.target_pose.pose.position.y = self.actual_positions[1] + dy
        move_goal.target_pose.pose.orientation.z = self.actual_positions[2] + sin(dtheta/2.0)
        move_goal.target_pose.pose.orientation.w = self.actual_positions[2] + cos(dtheta/2.0)
        move_goal.target_pose.header.frame_id = frame
        move_goal.target_pose.header.stamp = rospy.Time.now()
        self.client.send_goal(move_goal)
        self.client.wait_for_result()
        if s:
            s.send(",".join([str(d) for d in list(self.get_pose())]))

if __name__ == '__main__':
    rospy.init_node("test_base")
    base_control = BaseControl()
    time.sleep(0.1)
    print(base_control.get_pose_amcl())
    count = 10
    while count:
        time.sleep(1)
        print(base_control.get_pose_amcl())
        count-=1
    # base_control.goto(-3.780, -1.070, -1.5)

    # for i in range(0,10):
    #     base_control.move_forward()

    # base_control.move_right(45)
    #base_control.move_forward(1.0)
    #time.sleep(2)
    #base_control.move_forward()
    # base_control.move_right()

import rospy
import threading
from socket import *
import sys
import time

#recive data from headandGaze, run this file first

host = "kd-pc29.local"
port = 8090
size = 1
# s = socket(AF_INET, SOCK_STREAM) #socket.socket(socket.AF_INET, SOCK_DGRAM) for UDP connection
# s.bind((host,port))
# s.listen(5)
# client, address = s.accept()
# stop=0

class Attention():
    def __init__(self):#this is the server
        self.s = socket(AF_INET, SOCK_STREAM) #socket.socket(socket.AF_INET, SOCK_DGRAM) for UDP connection
        self.s.bind((host,port))
        self.s.listen(5)
        self.client, self.address = self.s.accept()
        self.data=[]

    def checkAttention(self,robot):
        def threadGetFeedback(self):
            while self.data[0]!="2":
                # print("thread is alive")
                self.data = self.client.recv(size)# initail read
                self.data = [self.data.strip().decode("utf-8")]
            print("thread is dead")

        self.data = self.client.recv(size)
        self.data = [self.data.strip().decode("utf-8")]
        print("outside "+self.data[0])
        attentionBackground=threading.Timer(1, threadGetFeedback,args=(self,))
        attentionBackground.setDaemon(True)
        attentionBackground.start()
        speech=robot.speaker
        while self.data[0]!="2":

            print("inside "+self.data[0])
            if self.data[0] == "1": # "semi-attention"
                speech.say("Hi, please look at me!")
                time.sleep(4.5)
                speech.soundhandle.stopAll()
                # stop=0
            elif self.data[0] == "0": # "no attention"
                # stop=0
                sound= np.random.choice('/home/fetch_admin/robot_speech/attention.wav')
                robot.speaker.play(sound)
                # speech.say("Hello, may I have your attention please?")
                time.sleep(4.5)
                speech.soundhandle.stopAll()
                robot.head.move_home()
                initial_time = time.time()
                print("wave")
                # robot.wave(initial_time, 10)
                # time.sleep(2)
            # data = self.client.recv(size)
            # data = data.strip().decode("utf-8")

        self.client.close()
        print("finished")





if __name__ == '__main__':
    from kf_robot import kf_Robot
    rospy.init_node("test")
    robot=kf_Robot()
    acheck=Attention()
    acheck.checkAttention(robot)

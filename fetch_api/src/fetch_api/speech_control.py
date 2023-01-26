import rospy
from sound_play.msg import SoundRequest
from sound_play.libsoundplay import SoundClient
import os
import time


class SpeechControl(object):
    """ Robot Speech interface """

    def __init__(self): #rosrun sound_play soundplay_node.py needs to run on the robot!
        self.soundhandle = SoundClient()
        rospy.sleep(rospy.Duration(1))
        self.ready = rospy.Subscriber("robotsound", SoundRequest, self.sound_ready)
        rospy.sleep(1)
    def sound_ready(self, msg):
        pass
        # print('this is ', msg)
    def say(self, sentence, voice = 'voice_rab_diphone', volume=1.0):
        #voice = 'voice_ked_diphone', 'voice_rab_diphone', 'voice_kal_diphone', 'voice_don_diphone'
        # while self.ready.get_num_connections() < 1:  #wait for the connection
        #     pass
        # print("speech connected")
        self.soundhandle.say(sentence, voice, volume, blocking =False)
    def play(self, path, blocking= False, volume=1.0):
        # while self.ready.get_num_connections() < 1:  #wait for the connection
        #     pass
        # print("speech connected")
        self.soundhandle.playWave(path, blocking =blocking, volume=volume)

if __name__ == '__main__':
    rospy.init_node("test_speech", anonymous=True)
    speech_module = SpeechControl()
    # speech_module.say("Hello, I am Fetch, your butler for the day. How may I help you?")
    # rospy.sleep(3)
    sound='/home/fetch_admin/robot_speech/confusion2.wav'
    print(sound)
    speech_module.play(sound)
    # rospy.sleep(3)
    # print(sound)
    # speech_module.play(sound)
    # rospy.sleep(3)
    # print(sound)
    # speech_module.play(sound)
    # rospy.sleep(3)
    # speech_module.soundhandle.stopAll()
    # print(sound)
    # speech_module.play(sound)
    rospy.sleep(3)
    speech_module.soundhandle.stopAll()

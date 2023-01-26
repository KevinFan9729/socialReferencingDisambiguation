import rospy
from sound_play.msg import SoundRequest
from sound_play.libsoundplay import SoundClient
import time


class SpeechControl(object):
    """ Robot Speech interface """

    def __init__(self): #rosrun sound_play soundplay_node.py needs to run on the robot!
        self.soundhandle = SoundClient()
        rospy.sleep(rospy.Duration(1))
        self.ready = rospy.Subscriber("robotsound", SoundRequest, self.sound_ready)
        time.sleep(0.5)

    def sound_ready(self, msg):
        print('this is ', msg)
    def say(self, sentence, voice = 'voice_rab_diphone', volume=1.0):
        #voice = 'voice_ked_diphone', 'voice_rab_diphone', 'voice_kal_diphone', 'voice_don_diphone'
        self.soundhandle.say(sentence, voice, volume)

if __name__ == '__main__':
    rospy.init_node("test_speech", anonymous=True)
    # r = rospy.Rate(1)
    speech_module = SpeechControl()
    print(speech_module.ready.get_num_connections())
    while speech_module.ready.get_num_connections() < 1:  #wait for the connection
        pass
        # speech_module.soundhandle.playWave("/home/fetch_admin/sounds/confirmation.wav")
        # print(speech_module.ready.get_num_connections())
        # speech_module.say("Hello, I am Fetch. How may I help you?")
        # speech_module.soundhandle.playWave("/home/fetch_admin/sounds/confirmation.wav")
        # rospy.sleep(5)
    # speech_module.say("Hello, I am Fetch. How may I help you?")
    speech_module.soundhandle.playWave("/home/fetch_admin/sounds/confirmation.wav")
    # print(speech_module.ready.get_num_connections())
    time.sleep(3)
    # speech_module.soundhandle.playWave("/home/fetch_admin/sounds/confirmation.wav")
    # print(speech_module.ready.get_num_connections())
    # time.sleep(3)
    # speech_module.say("Hello, I am Fetch. How may I help you?")
    # print(speech_module.ready.get_num_connections())
    # rospy.sleep(5)
    speech_module.soundhandle.stopAll()
    # time.sleep(2)
    # speech_module.say("Hello, I am Fetch. How may I help you?")

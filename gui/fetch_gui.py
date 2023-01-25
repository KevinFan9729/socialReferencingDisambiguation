from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock,mainthread
from kivy.animation import Animation
from kivy.uix.screenmanager import ScreenManager, Screen
import socket
import threading

# Window.fullscreen = 'auto'


host = "kd-pc29.local"
# host = '198.162.0.11'
# host = socket.gethostname()
port = 8200
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))#(ip and port)
# s.connect((socket.gethostname(),1234))#(ip and port)
s.settimeout(5)

type_play = True
fetch_ready=""
obj_lbl = ""
speech_lbl=""
# count=0


class LoadingScreen(Screen):
    pass

class InputScreen(Screen):
    def __init__(self,**kwargs):
        super(InputScreen, self).__init__(**kwargs)
        self.flip = 0
        self.animate_fading_in(self.ids.logo_img)
        # self.animate_fading(self.ids.Instruc_lbl)
        self.animate_fading_instruc()
        self.animate_fading_in(self.ids.obj_input,3)
        self.animate_fading_in(self.ids.submit_btn,2)
        # Clock.schedule_interval(self.check_speech_lbl, 0.1) #listen speech label from fetch
        # speechBackground=threading.Thread(target=self.check_speech_lbl)
        # speechBackground.daemon=True
        # speechBackground.start()
        # Clock.schedule_interval(self.test, 0.1)
        Clock.schedule_once(self.test2, 1.5)
  
    def test(self,*args):
        global speech_lbl,obj_lbl
        while True:
            s.setblocking(1)
            speech_lbl = s.recv(1024).decode()
            obj_lbl=speech_lbl
            print("test speech "+speech_lbl)
            if speech_lbl != "" and speech_lbl!="Fetch is ready":
                self.ids.submit_btn.text = "Confirm"
                self.update_speech_text()
                # self.ids.obj_input.text = speech_lbl
                break
    # def test(self,*args):
    #     while True:
    #         s.setblocking(1)
    #         msg = s.recv(1024).decode()
    #         print("test speech "+msg)
    #         if msg != "" and msg!="Fetch is ready":
    #             self.ids.submit_btn.text = "Confirm"
    #             self.ids.obj_input.text = msg
    #             break
        # print(1)
    def test2(self,*args):
        speechBackground=threading.Thread(target=self.test)
        speechBackground.daemon=True
        speechBackground.start()
    
    def animate_fading_in(self,id_name,opacity=1,duration=3):
        anim = Animation(opacity=opacity, duration=duration)
        anim.start(id_name)

    def animate_fading_instruc(self,*args):
        anim = Animation(opacity=1, duration=3)
        anim += Animation(opacity=0, duration=1)
        anim.bind(on_complete = self.animate_fading_instruc)
        if self.flip == 0:
            anim.start(self.ids.Instruc_lbl)
            self.flip+=1
        elif self.flip == 1:
            anim.start(self.ids.Instruc_lbl_2)
            self.flip-=1
    def fb_lbl_animation(self,*args):
        self.animate_fading_in(self.ids.feedback_lbl,duration=2)
    def check_lbl(self,*args):
        global obj_lbl
        if obj_lbl=="":
            msg = s.recv(1024)#buffer size 
            print("inside of check")
            obj_lbl=msg.decode()
            print("obj_lbl"+obj_lbl)
    def update_lbl(self,*args):
        while True:
            print("updateobj_lbl"+obj_lbl)
            if obj_lbl!="" and obj_lbl!="Fetch is ready":
                self.ids.obj_input.text = obj_lbl
                Clock.unschedule(self.check_lbl)
                break
    def check_speech_lbl(self,*args):#listen label from the speech side
        global obj_lbl
        while True:
            msg = s.recv(1024).decode()
            if msg == "Fetch is ready" or msg == "":
                continue
            print("inside of speech check")
            obj_lbl=msg
            print("obj_lbl"+obj_lbl)
        # if obj_lbl=="" or obj_lbl!="Fetch is ready":
        #     msg = s.recv(1024)#buffer size 
        #     print("inside of speech check")
        #     obj_lbl=msg.decode()
        #     print("obj_lbl"+obj_lbl)
        # else:
        #     self.ids.obj_input.text = obj_lbl
            # self.ids.submit_btn.text = "Confirm"
            # self.send_user_lbl()
            # Clock.unschedule(self.check_speech_lbl)#free resources


            
    def send_user_lbl(self):
        lbl = self.ids.obj_input.text
        # print(lbl)
        # s.send(lbl.encode())
        if self.ids.submit_btn.text != "Confirm":
            print('first hit')
            print("lbl"+lbl)
            s.send(lbl.encode())
            self.ids.submit_btn.text = "Confirm"
            self.ids.obj_input.hint_text=""
            self.ids.Instruc_lbl.opacity = 0
            self.ids.Instruc_lbl_2.opacity = 0
            # self.ids.obj_input.text = ""
            Animation.cancel_all(self.ids.Instruc_lbl)
            Animation.cancel_all(self.ids.Instruc_lbl_2)
            anim = Animation(opacity=1, duration=5)
            anim += Animation(opacity=0, duration=1)
            anim.bind(on_complete = self.fb_lbl_animation)
            # anim.start(self.ids.receive_lbl)
            Clock.schedule_interval(self.check_lbl, 0.1) #listen feedback from fetch
            Clock.schedule_once(self.update_lbl, 0.1)

        else:
            self.ids.feedback_lbl.opacity = 0
            Animation.cancel_all(self.ids.feedback_lbl)
            lbl = self.ids.obj_input.text
            self.ids.receive_lbl.pos_hint= {'x': 0, 'y': -0.05}
            self.animate_fading_in(self.ids.receive_lbl)
            lbl=lbl+"|c"
            print("here")
            print("lbl"+lbl)
            s.sendall(lbl.encode())
            print("sent")
            self.ids.submit_btn.text = "Fetch is on the job"
            self.ids.obj_input.text = ""
            self.ids.obj_input.disabled = True
            self.ids.obj_input.opacity = 0
            self.ids.submit_btn.disabled = True
    @mainthread
    def update_speech_text(self):
        self.ids.obj_input.text = speech_lbl
        self.ids.obj_input.hint_text=""
        self.ids.Instruc_lbl.opacity = 0
        self.ids.Instruc_lbl_2.opacity = 0
        # self.ids.obj_input.text = ""
        Animation.cancel_all(self.ids.Instruc_lbl)
        Animation.cancel_all(self.ids.Instruc_lbl_2)
        # anim = Animation(opacity=1, duration=5)
        # anim += Animation(opacity=0, duration=1)
        # anim.bind(on_complete = self.fb_lbl_animation)
        self.fb_lbl_animation()
        # anim.start(self.ids.receive_lbl)
            


        


        # self.ids.Instruc_lbl.disabled = True
        # self.ids.Instruc_lbl_2 = True


class Type_effect_lbl(Label):

    def __init__(self,**kwargs):
        super(Type_effect_lbl, self).__init__(**kwargs)
        # self.memory_str = self.type_str
        self.typewriter = Clock.create_trigger(self.typeit, 0.2)
        self.typewriter()

    def typeit(self, *args):
        self.text += self.type_str[0]
        self.type_str = self.type_str[1:]
        if self.repeat_str != "":
            if len(self.type_str) == 0:
                self.type_str = self.repeat_str #reset
                self.text = ""
        if len(self.type_str) > 0 and type_play:
            self.typewriter()


class fetch_gui(App):
    def check_fetch(self,*args):
        global fetch_ready
        if fetch_ready=="":
            msg = s.recv(1024)#buffer size 
            print("inside of check")
            fetch_ready=msg.decode()
            print("in main class")
            print("mainfetch_ready"+fetch_ready)
            print("mainobj_lbl"+obj_lbl)
            
    def update_screen(self,*args):
        global type_play
        while True:
             if fetch_ready!="":
                type_play=False
                # self.sm.current = 'InputSCR'
                Clock.unschedule(self.check_fetch)
                break
    
    def build(self):
        global fetch_ready
        # time.sleep(3)
        # self.grid = GridLayout()
        # self.grid.cols = 1
        # self.grid.size_hint = (0.6, 0.7)
        # self.grid.pos_hint = {"center_x": 0.5, "center_y":0.5}
        # Window.clearcolor = (1,1,1,1)
        # #add widgets to window
        # self.grid.add_widget(Image(source="fetch_logo.png",width=100,keep_ratio=True))
        # return self.grid
        # screen_kv=Builder.load_file("fetch_gui.kv")
        self.sm = ScreenManager()
        # self.sm.add_widget(LoadingScreen(name="LoadingSCR"))
        self.sm.add_widget(InputScreen(name="InputSCR"))
        # self.sm.current = 'LoadingSCR'
        self.sm.current = 'InputSCR'
        Clock.schedule_interval(self.check_fetch, 0.1) #listen feedback from fetch
        Clock.schedule_once(self.update_screen, 0.1)
        return self.sm
if __name__=="__main__":
    fetch_gui().run()
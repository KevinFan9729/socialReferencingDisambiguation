# -*- coding: utf-8 -*-
"""
Final working version That uses CAFFE DNN for face detection
Note that opencv DNN module must be avaiable. 4.2.0.32 is the latest version of opencv that support python 2.7
Recalibration is done in a background daemon thread.
Currently the recalibration is done in every 4 seconds.

@author: Kevin Fan
"""
import cv2
import numpy as np
import time
import threading

# use the fetch camera conrtol
# make sure make a ros node.
# call detect


p0=0
p1=0

# Parameters for lucas kanade optical flow
lk_params = dict( winSize  = (15,15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))



#function to get coordinates
def get_coords(p1):
    try: return int(p1[0][0][0]), int(p1[0][0][1])
    except: return int(p1[0][0]), int(p1[0][1])


def recalibrate():
    global p0
    global p1
    t=threading.Timer(4, recalibrate)#after 4 second, run function
    t.setDaemon(True)
    t.start()
    # print(threading.current_thread().isDaemon())
    try:
        face_found = False
        while not face_found:
            ret, frame = cap.read()#if face is not detected, a new frame need to be re-captured
            height, width = frame.shape[:2]#orginal height and width 640*480
            #frame_gray1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                        1.0, (300, 300), (104.0, 117.0, 123.0))
            net.setInput(blob)
            faces = net.forward()

            for i in range(faces.shape[2]):
                confidence = faces[0, 0, i, 2]#same as faces[0][0][i][2]
                if confidence > 0.5:
                    box = faces[0, 0, i, 3:7] * np.array([width, height, width, height])
                    (x,y,w,h) = box.astype("int")
                    #cv2.rectangle(frame, (x, y), (w, h), (0, 0, 255), 2)
                    print("I am re-calibrating the face center")
                    face_found = True
                    face_center = (x+(w-x)/2), (y+(h-y)/3)
                    p0 = np.array([[face_center]], np.float32)
                    cv2.circle(frame, get_coords(p0), 4, (0,0,255))
    except:
         print("re-calibration failed")
         p0 = p1


modelFile = "res10_300x300_ssd_iter_140000.caffemodel"
configFile = "deploy.prototxt.txt"

# modelFile = "res_ssd_300Dim.caffeModel"
# configFile = "deploy.prototxt.txt"
net = cv2.dnn.readNetFromCaffe(configFile, modelFile)


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 45)
fps = cap.get(cv2.CAP_PROP_FPS)
print ("Frames per second using video.get(cv2.CAP_PROP_FPS) :" +str(fps))
font = cv2.FONT_HERSHEY_SIMPLEX

#define movement threshold
x_gesture_threshold = 110
#y movement is less sensitive, thus smaller threshold
y_gesture_threshold = 80

#find the face in the image
face_found = False
#while not face_found:
while not face_found:
# while True:#30 fps video capture, around 20 fps running the face detection
    # Take first frame and find corners in it
    ret, frame = cap.read()
    # print(frame.shape)
    height, width = frame.shape[:2]#orginal height and width 640*480
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                        1.0, (300, 300), (104.0, 117.0, 123.0))
    net.setInput(blob)
    faces = net.forward()
    for i in range(faces.shape[2]):
        confidence = faces[0, 0, i, 2]#same as faces[0][0][i][2]
        if confidence > 0.5:
            box = faces[0, 0, i, 3:7] * np.array([width, height, width, height])
            (x,y,w,h) = box.astype("int")
            #cv2.rectangle(frame, (x, y), (w, h), (0, 0, 255), 2)
            face_found = True
            face_center = (x+(w-x)/2), (y+(h-y)/3)
            p0 = np.array([[face_center]], np.float32)

    # cv2.imshow('image',frame)
    # cv2.waitKey(1)

gesture = False
x_movement = 0
y_movement = 0
gesture_show = 30 #number of frames a gesture is shown
timeFlag=0


recalibrate()

while True:
    try:
        ret,frame = cap.read()
    except:
        continue
    old_gray = frame_gray.copy()
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #Calculates an optical flow for a sparse feature set using the iterative Lucas-Kanade method with pyramids
    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
    cv2.circle(frame, get_coords(p1), 4, (0,0,255), -1)
    cv2.circle(frame, get_coords(p0), 4, (255,0,0))
    # cv2.imshow('image',frame)
    # cv2.waitKey(1)
    #get the xy coordinates for points p0 and p1
    a,b = get_coords(p0), get_coords(p1)
    x_movement += abs(a[0]-b[0])
    y_movement += abs(a[1]-b[1])

    if timeFlag==0:
        detection_time=time.time()+60*0.1 #check for 6 seconds
        timeFlag=1#prevent reference time from resetting prematurely
    text = 'x_movement: ' + str(x_movement)
    if not gesture: cv2.putText(frame,text,(50,50), font, 0.8,(0,0,255),2)
    text = 'y_movement: ' + str(y_movement)
    if not gesture: cv2.putText(frame,text,(50,100), font, 0.8,(0,0,255),2)


    if x_movement > x_gesture_threshold:
        gesture = 'No'
        timeFlag=0
    if y_movement > y_gesture_threshold:
        gesture = 'Yes'
        timeFlag=0
    timeTest=time.time()

    # print('Current Time: '+ str(timeTest))
    # print('termination Time: '+ str(detection_time))
    # print(timeTest>detection_time)
    # print('\n')
    if timeTest>detection_time:
        gesture = 'Natural'
        timeFlag=0
    if gesture and gesture_show > 0:
        cv2.putText(frame,'Gesture Detected: ' + gesture,(50,50), font, 1.2,(0,0,255),3)
        gesture_show -=1
    if gesture_show == 0:
        gesture = False
        x_movement = 0
        y_movement = 0
        gesture_show = 30 #number of frames a gesture is shown

    #print distance(get_coords(p0), get_coords(p1))
    p0 = p1 #update the old point to for the next computation of optic flow
    #find the face in the image
    # end=time.perf_counter()

    cv2.imshow('image',frame)
    #out.write(frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # if cv2.waitKey(100) & 0xFF == ord('q'): #10 fps, 1/10=0.1 sec, 0.1*1000=100 milsec
    #     break

cv2.destroyAllWindows()
cap.release()

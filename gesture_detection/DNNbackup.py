# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 03:40:59 2020

@author: hp
"""
import cv2
import numpy as np
import time
import threading

p0=0
p1=0



#function to get coordinates
def get_coords(p1):
    try: return int(p1[0][0][0]), int(p1[0][0][1])
    except: return int(p1[0][0]), int(p1[0][1])


def recalibrate():
    global p0
    global p1
    threading.Timer(3, recalibrate).start()#after 2 second, run function
    print(threading.current_thread().isDaemon())
    try:
        face_found = False
        while not face_found:
            ret, frame = cap.read()#if face is not detected, a new frame need to be re-captured
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
                    cv2.rectangle(frame, (x, y), (w, h), (0, 0, 255), 2)
                    print("I am re-calibrating the face center")
                    face_found = True
                    face_center = (x+(w-x)/2), (y+(h-y)/3)
                    p0 = np.array([[face_center]], np.float32)
                    cv2.circle(frame, get_coords(p0), 4, (0,0,255))
    except:
         print("re-calibration failed")
         p0 = p1

         
# detector1 = MTCNN()
# detector2 = dlib.get_frontal_face_detector()
modelFile = "res10_300x300_ssd_iter_140000.caffemodel"
configFile = "deploy.prototxt.txt"
net = cv2.dnn.readNetFromCaffe(configFile, modelFile)


cap = cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_SIMPLEX 
while(True):
    ret, frame = cap.read()
    if ret == True:
        #frame = cv2.resize(frame, (640,480), fx=0.5, fy=0.5)
        height, width = frame.shape[:2]
        #img2 = frame.copy()
        # detect faces in the image
        # faces1 = detector1.detect_faces(img)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # faces2 = detector2(gray, 1)
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                        1.0, (300, 300), (104.0, 117.0, 123.0))
        net.setInput(blob)
        faces = net.forward()
        # [,frame,no of detections,[classid,class score,conf,x,y,h,w]

        for i in range(faces.shape[2]):
            confidence = faces[0, 0, i, 2]#same as faces[0][0][i][2]
            if confidence > 0.5:
                box = faces[0, 0, i, 3:7] * np.array([width, height, width, height])
                (x,y,w,h) = box.astype("int")
                cv2.rectangle(frame, (x, y), (w, h), (0, 0, 255), 2)
                # cv2.circle(frame, (x,y), 4, (255,0,0))
                # cv2.circle(frame, (w,y), 4, (255,0,0))
                # cv2.circle(frame, (x,h), 4, (255,0,0))
                # cv2.circle(frame, (w,h), 4, (255,0,0))

                #cv2.circle(img2, (int(x+(w-x)/2),int(y+(h-y)/3)), 4, (0,255,0))#face center
                
                face_center = (x+(w-x)/2), (y+(h-y)/3)
                p0 = np.array([[face_center]], np.float32)
                cv2.circle(frame, get_coords(p0), 4, (0,0,255))
                
        # cv2.putText(frame, 'dnn', (30, 30), font, 1, (255, 255, 0), 2, cv2.LINE_AA)
        

        cv2.imshow("dnn", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break



           
cap.release()
cv2.destroyAllWindows()

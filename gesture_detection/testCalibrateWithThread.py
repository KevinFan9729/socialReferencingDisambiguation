import cv2
import numpy as np
import time
import threading


p0=0
p1=0

def recalibrate():
    global p0
    global p1

    t=threading.Timer(3, recalibrate)#after 2 second, run function
    t.setDaemon(True)
    t.start()

    print(threading.current_thread().isDaemon())
    try:
        face_found = False
        while not face_found:
            ret, frame = cap.read()#if face is not detected, a new frame need to be re-captured
            frame_gray1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(frame_gray1, 1.1, 3)

            if len(faces)!=0:
                for (x,y,w,h) in faces:
                    cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2) #b,g,r
                    print("I am re-calibrating the face center")
                    face_found = True
                face_center = x+w/2, y+h/3
                p0 = np.array([[face_center]], np.float32)
    except:
         print("re-calibration failed")
         p0 = p1



cap = cv2.VideoCapture(0)

# Parameters for lucas kanade optical flow
lk_params = dict( winSize  = (15,15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

#path to face cascde
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')

#face_cascade = cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml')
#function to get coordinates
def get_coords(p1):
    try: return int(p1[0][0][0]), int(p1[0][0][1])
    except: return int(p1[0][0]), int(p1[0][1])

#define font and text color
font = cv2.FONT_HERSHEY_SIMPLEX


# used to record the time when we processed last frame
start = 0

# used to record the time at which we processed current frame
end = 0

fps=0


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
    # start=time.perf_counter()
    ret, frame = cap.read()
    # print(frame.shape)
    frame=cv2.resize(frame,(640,480))# resize image to size of fetch camera 640*480
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(frame_gray, 1.1, 4)
    if len(faces)!=0:
        for (x,y,w,h) in faces:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2) #b,g,r
            # cv2.circle(frame, (x,y), 4, (255,0,0))
            # cv2.circle(frame, (x+w,y+h), 4, (0,255,0))
            cv2.circle(frame, (x+w,y), 4, (0,0,255))
            face_found = True

        face_center = x+w/2, y+h/3
        p0 = np.array([[face_center]], np.float32)


    #cv2.circle(frame, get_coords(p0), 4, (0,0,255))
    # end=time.perf_counter()
    # if((end-start)!=0):
    #     fps=1/(end-start)
    #     fps=int(fps)
    #
    # print(fps)
    cv2.imshow('image',frame)
    cv2.waitKey(1)
face_center = x+w/2, y+h/3
#p0 is the center of the face
p0 = np.array([[face_center]], np.float32)

gesture = False
x_movement = 0
y_movement = 0
gesture_show = 30 #number of frames a gesture is shown
timeFlag=0
calibrationFlag=0



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
    if calibrationFlag==0:
        calbiartion_time=time.time()+2 #check for 10 seconds
        calibrationFlag=1#prevent reference time from resetting prematurely
    text = 'x_movement: ' + str(x_movement)
    if not gesture: cv2.putText(frame,text,(50,50), font, 0.8,(0,0,255),2)
    text = 'y_movement: ' + str(y_movement)
    if not gesture: cv2.putText(frame,text,(50,100), font, 0.8,(0,0,255),2)

    #while time.time()<detection_time:

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
    # if timeTest>calbiartion_time:


    cv2.imshow('image',frame)
    #out.write(frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
cap.release()

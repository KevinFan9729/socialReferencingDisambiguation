# from kf_robot import kf_Robot
import os,glob
import cv2
import numpy as np


def preprocess(img, size=224, interpolation =cv2.INTER_AREA):
    #extract image size
    h, w = img.shape[:2]
    #check color channels
    c = None if len(img.shape) < 3 else img.shape[2]
    #square images have an aspect ratio of 1:1
    if h == w:
        return cv2.resize(img, (size, size), interpolation= interpolation)
    elif h>w:#height is larger
        diff= h-w
        img=cv2.copyMakeBorder(img,0,0,int(diff/2.0),int(diff/2.0),cv2.BORDER_CONSTANT, value = 0)
        # img=cv2.copyMakeBorder(img,0,0,int(diff/2.0),int(diff/2.0),cv2.BORDER_REPLICATE)
    elif h<w:
        diff= w-h
        # img=cv2.copyMakeBorder(img,int(diff/2.0),int(diff/2.0),0,0,cv2.BORDER_REPLICATE)
        img=cv2.copyMakeBorder(img,int(diff/2.0),int(diff/2.0),0,0,cv2.BORDER_CONSTANT, value = 0)
    img = cv2.resize(img, (size, size), interpolation = interpolation)
    img=img/255.0#rescale color channels
    return img


home = os.path.abspath(os.getcwd())
# robot = kf_Robot()
# data = client.recv(1024)
# data = data.strip().decode("utf-8")
# if data == 'yolo':
target_path = os.path.join(home, 'meta_learning', 'robot_imagination')
imaginations = glob.glob(os.path.join(target_path,"*")) #*wildcard
recent_imagination = max(imaginations, key=os.path.getctime)#get the latest
image = cv2.imread(recent_imagination)


# load the COCO class names
with open('object_detection_classes_coco.txt', 'r') as f:
   class_names = f.read().split('\n')

# get a different color array for each of the classes
COLORS = np.random.uniform(0, 255, size=(len(class_names), 3))


model = cv2.dnn.readNet(model='/home/fetch/Documents/Kevin/frozen_inference_graph.pb',config='/home/fetch/Documents/Kevin/ssd_mobilenet_v2_coco_2018_03_29.pbtxt',framework='TensorFlow')
# image = preprocess(img = image, size = 300, interpolation =cv2.INTER_AREA)
print(image)
image2= preprocess(image)
print(image2[12][0])
anchor_show = image2

cv2.imshow('image', anchor_show)
cv2.waitKey(0)

crop_y,crop_x,crop_height,crop_width,max_confidence = -1,-1,-1,-1,-1
image_height, image_width, _ = image.shape
# create blob from image
blob = cv2.dnn.blobFromImage(image=image, size=(300, 300), mean=(104, 117, 123), swapRB=True)
# set the blob to the model
model.setInput(blob)
# forward pass through the model to carry out the detection
output = model.forward()
# loop over each of the detection
for detection in output[0, 0, :, :]:
   # extract the confidence of the detection
   confidence = detection[2]
   # draw bounding boxes only if the detection confidence is above...
   # ... a certain threshold, else skip
   if confidence > .4:
       # get the class id
       class_id = detection[1]
       # map the class id to the class

       # class_name = class_names[int(class_id)-1]
       # color = COLORS[int(class_id)]
       # get the bounding box coordinates
       box_x = detection[3] * image_width
       box_x = np.clip(int(round(box_x)), 0, None)
       box_y = detection[4] * image_height
       box_y = np.clip(int(round(box_y)), 0, None)
       # get the bounding box width and height
       box_width = detection[5] * image_width
       box_width = np.clip(int(round(box_width)), 0, None)
       box_height = detection[6] * image_height
       box_height = np.clip(int(round(box_height)), 0, None)
       # draw a rectangle around each detected object
       print(box_x)
       print(box_y)
       print(box_width)
       print(box_height)
       # print(class_name)
       print(confidence)
       print("==============")


       cv2.rectangle(image, (int(box_x), int(box_y)), (int(box_width), int(box_height)), (255,0,0), thickness=2)

       # put the FPS text on top of the frame
       # cv2.putText(image, class_name, (int(box_x), int(box_y - 5)), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
       if confidence>max_confidence:
           max_confidence = confidence
           crop_y = box_y
           crop_x = box_x
           crop_height = box_height
           crop_width = box_width

print(crop_x)
print(crop_y)
print(crop_width)
print(crop_height)

image_cropped = image[crop_y:crop_height, crop_x:crop_width]

cv2.imshow('image', image)
cv2.imwrite('crop_result.png', image_cropped)
cv2.waitKey(0)
cv2.destroyAllWindows()


# box = robot.yoloDetector.cb(imag)
# box = robot.yoloDetector.boxes[0]
# img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#
# print(box)
# X0,Y0,X1,Y1 = box[:-1]
# cropped_image = imag[Y0-10:Y1+10, X0-10:X1+10]
# corp_name ='cropped.png'
# corp_name = os.path.join(target_path, corp_name)
# cv2.imwrite(corp_name, cropped_image)

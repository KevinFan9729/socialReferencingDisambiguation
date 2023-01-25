import os
import cv2
import glob
import numpy as np

def preprocess(img, size=224, interpolation =cv2.INTER_AREA):
    #extract image size
    h, w = img.shape[:2]
    #check color channels
    c = None if len(img.shape) < 3 else img.shape[2]
    #square images have an aspect ratio of 1:1
    if h == w:
        return cv2.resize(img, (size, size), interpolation)
    elif h>w:#height is larger
        diff= h-w
        img=cv2.copyMakeBorder(img,0,0,int(diff/2.0),int(diff/2.0),cv2.BORDER_CONSTANT, value = 0)
        # img=cv2.copyMakeBorder(img,0,0,int(diff/2.0),int(diff/2.0),cv2.BORDER_REPLICATE)
    elif h<w:
        diff= w-h
        # img=cv2.copyMakeBorder(img,int(diff/2.0),int(diff/2.0),0,0,cv2.BORDER_REPLICATE)
        img=cv2.copyMakeBorder(img,int(diff/2.0),int(diff/2.0),0,0,cv2.BORDER_CONSTANT, value = 0)
    img = cv2.resize(img, (size, size), interpolation)
    img=img/255.0#rescale color channels
    return img


home = os.path.abspath(os.getcwd())
imagination_out_path = os.path.join(home, "robot_imagination")
imaginations = glob.glob(os.path.join(imagination_out_path,"*")) #*wildcard
recent_imagination = max(imaginations, key=os.path.getctime)#get the latest
anchor = cv2.imread(recent_imagination)
anchor = preprocess(anchor)
anchor = np.expand_dims(anchor, axis=0)
print(type(anchor[0][0][0][0]))
print(anchor[0][0][0])



anchor_show = np.uint8(anchor[0])
# anchor_show=cv2.cvtColor(anchor_show, cv2.COLOR_RGB2BGR)
cv2.imshow("anchor",anchor_show)
cv2.waitKey(0)
cv2.destroyAllWindows()

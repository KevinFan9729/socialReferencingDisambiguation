# from kf_robot import kf_Robot
import cv2
import numpy as np
import os


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
imag = cv2.imread('crop_result.png')

print(imag)
cv2.imshow('w',imag)
cv2.waitKey(0)

imag =preprocess(imag)
cv2.imshow('w',imag)
cv2.waitKey(0)
print(imag)

cv2.imwrite('test.png',imag*255)

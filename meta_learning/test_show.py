import os
import cv2
import numpy as np
import glob

home = os.path.abspath(os.getcwd())
imagination_out_path = os.path.join(home, "robot_imagination","*")
imaginations = glob.glob(os.path.join(home, "robot_imagination","*"))
# print(imaginations)
recent_imagination = max(imaginations, key=os.path.getctime)
print(recent_imagination)

# img_path=os.path.join(home, "blue cup", "blue cup.png")
# img = cv2.imread(img_path)
# font = cv2.FONT_HERSHEY_SIMPLEX
# def preprocess(image):
#     image=cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     image=image/255.0#rescale color channels
#     image=cv2.resize(image, (200,200))
#     return image
#
# img = preprocess(img)
# img = np.expand_dims(img, axis=0)
# query_show = np.float32(img[0])
# query_show=cv2.cvtColor(query_show, cv2.COLOR_RGB2BGR)
# text = "Similarity: " +str(0.96)
# cv2.putText(query_show,text,(50,190), font, 0.6,(0,0,255),2)
# cv2.imshow("query",query_show)
# cv2.waitKey(0)

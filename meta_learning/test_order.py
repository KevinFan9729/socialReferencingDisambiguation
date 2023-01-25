import os
import cv2
import numpy as np

home = os.path.abspath(os.getcwd())
short_mem_path = os.path.join(home, "short_term_memory")
short_mem_ls = []
for image in sorted(os.listdir(short_mem_path)):
    img = cv2.imread(os.path.join(short_mem_path,image))
    # img = preprocess(img)
    short_mem_ls.append(img)

print(os.listdir(short_mem_path))

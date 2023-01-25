import os
import sys
sys.path.insert(1,'/home/fetch/Documents/Kevin/stable_diffusion/optimizedSD')
# # import robot_imagination.py
from robot_imagination import robot_imagine
# model = "/home/fetch/Documents/Kevin/stable_diffusion/models/ldm/stable-diffusion-v1/model.ckpt"
config = "/home/fetch/Documents/Kevin/stable_diffusion/optimizedSD/v1-inference.yaml"
robot_imagine(config = config)
# # robot_imagine()
# os.chdir('/home/fetch/Documents/Kevin/stable_diffusion/optimizedSD')
cwd = os.getcwd()

# print the current directory
print("Current working directory is:", cwd)
# from stable_diffusion.optimizedSD import robot_imagination

from fetch_api.camera_modules import YoloDetector, RGBCamera
import rospy
from numpy import pi

if __name__ == '__main__':
    rospy.init_node("distance_check")

    while 1:
        yolo=YoloDetector()
        rgb=RGBCamera()
        print(yolo.get_item_list())
        obj_name = raw_input("Which object do you want to pick?")
        # obj_name = "cup"
        coord_3d, up = yolo.get_item_3d_coordinates(obj_name, rgb.getRGBImage())
        print("Picking " + obj_name + ": ", coord_3d[0])
        coord_3d = coord_3d[0]
        break

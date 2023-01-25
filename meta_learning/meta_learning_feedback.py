import os
import cv2
import socket
import threading
import numpy as np
import glob
import os
import sys
sys.path.insert(1,'/home/fetch/Documents/Kevin/stable_diffusion/optimizedSD')
from robot_imagination import robot_imagine


#socket setup
host = "kd-pc29.local"
port = 8100
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket.socket(socket.AF_INET, SOCK_DGRAM) for UDP connection
s.connect((host, port)) #198.162.0.11

user_cmd = ""
# user_cmd = 'red cup'

def loss(margin=1):
    """Provides 'constrastive_loss' an enclosing scope with variable 'margin'.

  Arguments:
      margin: Integer, defines the baseline for distance for which pairs
              should be classified as dissimilar. - (default is 1).

  Returns:
      'constrastive_loss' function with data ('margin') attached.
  """

    # Contrastive loss = mean( (1-true_value) * square(prediction) +
    #                         true_value * square( max(margin-prediction, 0) ))
    def contrastive_loss(y_true, y_pred):
        """Calculates the constrastive loss.

      Arguments:
          y_true: List of labels, each label is of type float32.
          y_pred: List of predictions of same length as of y_true,
                  each label is of type float32.

      Returns:
          A tensor containing constrastive loss as floating point value.
      """

        square_pred = tf.math.square(y_pred)
        margin_square = tf.math.square(tf.math.maximum(margin - (y_pred), 0))
        return tf.math.reduce_mean(
            (1 - y_true) * square_pred + (y_true) * margin_square
        )

    return contrastive_loss

def listen_user_cmd():
    global user_cmd
    print("thread started")
    user_cmd = s.recv(1024)# initail read
    user_cmd = user_cmd.strip().decode("utf-8")
    # print(data)
    while (user_cmd ==""):
        # print("thread is alive")
        user_cmd = s.recv(1024)# initail read
        user_cmd = user_cmd.strip().decode("utf-8")
        # print("data is: ")
        # print(data)
    print("thread is dead")
    return

# def preprocess(image):
#     image=cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     image=image/255.0#rescale color channels
#     image=cv2.resize(image, (200,200))
#     return image

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
    # img=img/255.0#rescale color channels
    img = cv2.normalize(img, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    return img

def find_order(sim_ls):
    order = [None] * len(sim_ls)
    for i in range(len(sim_ls)):
        index = sim_ls.index(max(sim_ls))
        order[i] = index
        sim_ls[index] = -1
    return order


def meta_learning_feedback():
    global user_cmd
    background=threading.Timer(1, listen_user_cmd)
    background.setDaemon(True)
    background.start()
    long_mem_classes_ls = []
    #load model
    home = os.path.abspath(os.getcwd())
    # model_path=os.path.join(home, "model", "val0.9714_newdata_vgg16")



    while True:
        # print(user_cmd)
        # print(user_cmd == "")
        if user_cmd == "":
            continue #keep looping
        else:
            short_mem_path = os.path.join(home, "short_term_memory")
            short_mem_ls = []
            for image in sorted(os.listdir(short_mem_path)):
                img = cv2.imread(os.path.join(short_mem_path,image))
                # img = preprocess(img)
                short_mem_ls.append(img)
                os.remove(os.path.join(short_mem_path,image)) #clear memory in short memory
            if len(short_mem_ls) == 0:
                print("no image found in short term memory")
                return


            long_mem_path = os.path.join(home, "long_term_memory")
            user_cmd=str(user_cmd)
            user_cmd_ls = user_cmd.split("*")
            print(user_cmd_ls)
            user_cmd = user_cmd_ls[0]
            print(long_mem_path)
            print(user_cmd)
            class_path = os.path.join(long_mem_path, str(user_cmd))
            for class_ in os.listdir(long_mem_path):
                long_mem_classes_ls.append(class_)
            print(sys.argv[1])
            print(sys.argv)

            if len(sys.argv) >= 3 and sys.argv[2] == "true":#imagination is on.
                # if not(user_cmd in long_mem_classes_ls):
                # if len(user_cmd_ls) is 1 that mean there is at least one * in the string, meaning yolo knows the object, don't need to imagine
                if not(user_cmd in long_mem_classes_ls) and len(user_cmd_ls)==1:#if we don't have an actual example of the required item in the long-term memory
                    print('imagination mode is on')
                    config = "/home/fetch/Documents/Kevin/stable_diffusion/optimizedSD/v1-inference.yaml"
                    robot_imagine(config = config, obj=user_cmd) #imagine the likeness of the object based on the user label.

                    # data = 'yolo'
                    # s.send(data.encode())#let yolo know it is time to crop the image
                    #load object detection
                    imagination_out_path = os.path.join(home, "robot_imagination")
                    imaginations = glob.glob(os.path.join(imagination_out_path,"*")) #*wildcard
                    recent_imagination = max(imaginations, key=os.path.getctime)#get the latest
                    image = cv2.imread(recent_imagination)

                    obj_dect_path = '/home/fetch/Documents/Kevin/meta_learning/frozen_inference_graph.pb'
                    obj_dect_config = '/home/fetch/Documents/Kevin/meta_learning/ssd_mobilenet_v2_coco_2018_03_29.pbtxt'
                    obj_dect = cv2.dnn.readNet(model=obj_dect_path,config=obj_dect_config,framework='TensorFlow')
                    crop_y,crop_x,crop_height,crop_width,max_confidence = -1,-1,-1,-1,-1
                    image_height, image_width, _ = image.shape
                    # create blob from image
                    blob = cv2.dnn.blobFromImage(image=image, size=(300, 300), mean=(104, 117, 123), swapRB=True)
                    # set the blob to the model
                    obj_dect.setInput(blob)
                    # forward pass through the model to carry out the detection
                    output = obj_dect.forward()
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
                           # print(box_x)
                           # print(box_y)
                           # print(box_width)
                           # print(box_height)
                           # # print(class_name)
                           # print(confidence)
                           # print("==============")


                           # cv2.rectangle(image, (int(box_x), int(box_y)), (int(box_width), int(box_height)), (255,0,0), thickness=2)

                           # put the FPS text on top of the frame
                           # cv2.putText(image, class_name, (int(box_x), int(box_y - 5)), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                           if confidence>max_confidence:
                               max_confidence = confidence
                               crop_y = box_y
                               crop_x = box_x
                               crop_height = box_height
                               crop_width = box_width
                    print('confidence')
                    print(confidence)
                    image_cropped = image[crop_y:crop_height, crop_x:crop_width]
                    if crop_x!= -1:#only save the crop when it is vaild
                        cv2.imwrite('/home/fetch/Documents/Kevin/meta_learning/robot_imagination/crop_result.png', image_cropped)
                    imagination_out_path = os.path.join(home, "robot_imagination")
                    imaginations = glob.glob(os.path.join(imagination_out_path,"*")) #*wildcard
                    recent_imagination = max(imaginations, key=os.path.getctime)#get the latest
                    anchor = cv2.imread(recent_imagination)
                    anchor = preprocess(anchor)
                    anchor = np.expand_dims(anchor, axis=0)
                    similarity_ls = []
                    import tensorflow as tf
                    from tensorflow.keras.models import load_model
                    config = tf.compat.v1.ConfigProto(
                            device_count = {'GPU': 0}
                        )
                    sess = tf.compat.v1.Session(config=config)
                    model_path=os.path.join(home, "model", "0.97_image_net_vgg19")
                    with tf.device('/cpu:0'):
                        model = load_model(model_path,custom_objects={ 'contrastive_loss': loss(1) })

                    for i in range(len(short_mem_ls)):
                        query = preprocess(short_mem_ls[i])#query image in the short term memory
                        query = np.expand_dims(query, axis=0)
                        similarity = model.predict([query,anchor])
                        similarity_ls += [similarity]
                        # print("query index", i)
                        query_show = (query[0])
                        anchor_show = anchor[0]
                        # query_show=cv2.cvtColor(query_show, cv2.COLOR_RGB2BGR)
                        # anchor_show=cv2.cvtColor(anchor_show, cv2.COLOR_RGB2BGR)
                        cv2.imshow("query",query_show)
                        cv2.imshow("anchor",anchor_show)
                        print("pair similarity", similarity)
                        # print("query index", i)
                        cv2.waitKey(0)
                        # and finally destroy/close all open windows
                        cv2.destroyAllWindows()
                    if max(similarity_ls) >=0.5:
                        idx = similarity_ls.index(max(similarity_ls))
                        data = str(idx)
                        long_mem_path = '/home/fetch/Documents/Kevin/meta_learning/long_term_memory'
                        novel_class_path = os.path.join(long_mem_path, user_cmd)
                        try:
                            os.mkdir(novel_class_path)
                        except OSError:
                            pass
                        novel_obj_name =user_cmd +".png"
                        novel_obj_name = os.path.join(novel_class_path, novel_obj_name)
                        cv2.imwrite(novel_obj_name, short_mem_ls[idx])
                        # temp = short_mem_ls[idx]*255
                        # temp= np.uint8(temp)
                        # cv2.imwrite(novel_obj_name, temp)

                        s.send(data.encode())
                        s.close()
                        print("imagination is highly similar to an item in view")
                        print("max similarity", max(similarity_ls))
                        print("index "+ data)
                        return
                    else:
                        order = find_order(similarity_ls)
                        data = ','.join(str(x) for x in order)
                        s.send(data.encode())
                        s.close()









            if not(user_cmd in long_mem_classes_ls): #if user cmd is not in long term memory, break and you cannot do classification
                s.close()
                return
            for imag_path in os.listdir(class_path):#loop through images in one class folder
                try:
                    anchor = cv2.imread(os.path.join(class_path,imag_path)) #anchor in the long term memory
                    h,w,c = anchor.shape
                    if h==w==224:
                        pass
                    else:
                        anchor = preprocess(anchor)
                    anchor = np.expand_dims(anchor, axis=0)
                except:
                    print("failed to load the anchor image")
                    return
                maximum = 0
                idx = -1
                import tensorflow as tf
                from tensorflow.keras.models import load_model
                config = tf.compat.v1.ConfigProto(
                        device_count = {'GPU': 0}
                    )
                sess = tf.compat.v1.Session(config=config)
                model_path=os.path.join(home, "model", "0.97_image_net_vgg19")
                with tf.device('/cpu:0'):
                    model = load_model(model_path,custom_objects={ 'contrastive_loss': loss(1) })
                for i in range(len(short_mem_ls)):
                    query = preprocess(short_mem_ls[i])#query image in the short term memory
                    # query = np.array(query)
                    # anchor = np.array(query)
                    query = np.expand_dims(query, axis=0)
                    print(query.shape)
                    print(anchor.shape)
                    # print(query[0:25])
                    # print("==============")
                    # print(anchor[0:25])
                    similarity = model.predict([query,anchor])
                    query_show = query[0]
                    anchor_show = anchor[0]
                    # query_show=cv2.cvtColor(query_show, cv2.COLOR_RGB2BGR)
                    # anchor_show=cv2.cvtColor(anchor_show, cv2.COLOR_RGB2BGR)
                    # color = (0,0,255)
                    # if similarity[0][0]>0.6:
                    #     color = (0,255,0)
                    # text = "Similarity: " +str(round(similarity[0][0],2))
                    # font = cv2.FONT_HERSHEY_SIMPLEX
                    # cv2.putText(anchor_show,text,(50,190), font, 0.6,color,2)
                    cv2.imshow("query",query_show)
                    cv2.imshow("anchor",anchor_show)
                    print("pair similarity", similarity)
                    print("query index", i)
                    cv2.waitKey(0)
                    # and finally destroy/close all open windows
                    # cv2.destroyAllWindows()
                    if similarity > maximum:
                        maximum = similarity
                        idx = i
                if maximum>0.5:#highly similar #0.6
                    data = str(idx) #index of the short term memory image that matches with the anchor image
                    s.send(data.encode())
                    s.close()
                    print("max similarity", maximum)
                    print("index "+ data)
                    return
                print("similarity too low", maximum)
                s.send("-1".encode())
                s.close()




if __name__ == '__main__':
    meta_learning_feedback()

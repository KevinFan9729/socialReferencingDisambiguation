import os
import cv2
import socket
import threading
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model


#socket setup
host = "kd-pc29.local"
port = 8100
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket.socket(socket.AF_INET, SOCK_DGRAM) for UDP connection
s.connect((host, port)) #198.162.0.11
user_cmd = ""

##run a python script in a specific environment
#conda run -n <environment> <script_name>
#or
#subprocess.run('source activate 'environment-name' && "enter command here" && source deactivate', shell=True)
#or
# subprocess.run('bash -c "conda deactivate; python -V"', shell=True)
# subprocess.run('bash -c "conda activate kfpy3; python -V"', shell=True)
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
    img=img/255.0#rescale color channels
    return img

def meta_learning_feedback():
    global user_cmd
    background=threading.Timer(1, listen_user_cmd)
    background.setDaemon(True)
    background.start()
    long_mem_classes_ls = []
    #load model
    home = os.path.abspath(os.getcwd())
    # model_path=os.path.join(home, "model", "val0.9714_newdata_vgg16")
    model_path=os.path.join(home, "model", "0.97_image_net_vgg19")
    with tf.device('/cpu:0'):
        model = load_model(model_path,custom_objects={ 'contrastive_loss': loss(1) })


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
                img = preprocess(img)
                short_mem_ls.append(img)
                os.remove(os.path.join(short_mem_path,image)) #clear memory in short memory
            if len(short_mem_ls) == 0:
                print("no image found in short term memory")
                return
            # if len(sys.argv) > 1 and sys.argv[1] == "true":#imagination is on.
            #

            long_mem_path = os.path.join(home, "long_term_memory")
            user_cmd=str(user_cmd)
            print(long_mem_path)
            print(user_cmd)
            class_path = os.path.join(long_mem_path, str(user_cmd))
            for class_ in os.listdir(long_mem_path):
                long_mem_classes_ls.append(class_)
            if not(user_cmd in long_mem_classes_ls): #if user cmd is not in long term memory, break and you cannot do classification
                s.close()
                return
            for imag_path in os.listdir(class_path):#loop through images in one class folder
                try:
                    anchor = cv2.imread(os.path.join(class_path,imag_path)) #anchor in the long term memory
                    anchor = preprocess(anchor)
                    anchor = np.expand_dims(anchor, axis=0)
                except:
                    print("failed to load the anchor image")
                    return
                max = 0
                idx = -1
                for i in range(len(short_mem_ls)):
                    query = short_mem_ls[i]#query image in the short term memory
                    # query = np.array(query)
                    # anchor = np.array(query)
                    query = np.expand_dims(query, axis=0)
                    print(query.shape)
                    print(anchor.shape)

                    similarity = model.predict([query,anchor])
                    query_show = np.float32(query[0])
                    anchor_show = np.float32(anchor[0])
                    query_show=cv2.cvtColor(query_show, cv2.COLOR_RGB2BGR)
                    anchor_show=cv2.cvtColor(anchor_show, cv2.COLOR_RGB2BGR)
                    # color = (0,0,255)
                    # if similarity[0][0]>0.6:
                    #     color = (0,255,0)
                    # text = "Similarity: " +str(round(similarity[0][0],2))
                    # font = cv2.FONT_HERSHEY_SIMPLEX
                    # cv2.putText(anchor_show,text,(50,190), font, 0.6,color,2)
                    # cv2.imshow("query",query_show)
                    # cv2.imshow("anchor",anchor_show)
                    print("pair similarity", similarity)
                    print("query index", i)
                    cv2.waitKey(0)
                    # and finally destroy/close all open windows
                    # cv2.destroyAllWindows()
                    if similarity > max:
                        max = similarity
                        idx = i
                if max>0.5:#highly similar #0.6
                    data = str(idx) #index of the short term memory image that matches with the anchor image
                    s.send(data.encode())
                    s.close()
                    print("max similarity", max)
                    print("index "+ data)
                    return
                print("similarity too low", max)
                s.send("-1".encode())
                s.close()




if __name__ == '__main__':
    meta_learning_feedback()

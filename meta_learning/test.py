import os
import random
import cv2
import matplotlib.pyplot as plt
from tensorflow import keras
from sklearn.model_selection import train_test_split
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers

random.seed(15)#fixed random state

home=os.path.abspath(os.getcwd())
data_path=os.path.join(home, 'test')
# data_path=os.path.join(home, 'test2')
# pos_path=os.path.join(data_path, 'positive')
# anchor_path=os.path.join(data_path, 'anchor')
pairs=[]
classes=[]
labels=[]


for file in os.listdir(data_path):
    classes.append(file)

def load_image():
    pass
def make_pairs():#makes pairs of data
    labels=[]
    pairs=[]
    try:
        for class_ in classes:
            class_path = os.path.join(data_path, class_)
            for img_path in os.listdir(class_path):
                image1 = cv2.imread(os.path.join(class_path, img_path)).astype("float32")
                image_select=random.choice(os.listdir(class_path))
                image2 = cv2.imread(os.path.join(class_path, image_select)).astype("float32")
                image1=preprocess(image1)
                image2=preprocess(image2)
                pairs+=[[image1, image2]]
                labels+=[1]#objects belong to the same class


                class_select = random.choice(classes)
                while class_select == class_:# keep trying if select the current class
                    class_select = random.choice(classes)
                class_path2 = os.path.join(data_path, class_select)
                image_select=random.choice(os.listdir(class_path2))
                image2 = cv2.imread(os.path.join(class_path2, image_select)).astype("float32")
                image2=preprocess(image2)
                pairs+=[[image1, image2]]
                labels+=[0]#objects don't belong to the same class
    except:
        print(os.path.join(class_path2, image_select))
        return

    return np.array(pairs).astype("float32"), np.array(labels).astype("float32")


# def preprocess(image):
#     image=cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     image=image/255.0#rescale color channels
#     image=cv2.resize(image, (200,200))
#     return image
def preprocess(img, size=200, interpolation =cv2.INTER_AREA):
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
    return cv2.resize(img, (size, size), interpolation)


pairs, labels = make_pairs()
# imgplot = plt.imshow(pairs[0][0])
X_train, X_val, y_train, y_val = train_test_split(pairs, labels, test_size=0.4, random_state=15)

x_train_1 = X_train[:, 0]
x_train_2 = X_train[:, 1]

x_val_1 = X_val[:, 0]
x_val_2 = X_val[:, 1]


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

#model = keras.models.load_model('val0.915_newdata')
#model = keras.models.load_model('val0.9716_newdata', custom_objects={ 'contrastive_loss': loss(1) })
model_path=os.path.join(home, "model", "val0.9714_newdata_vgg16")
with tf.device('/cpu:0'):
    model = keras.models.load_model(model_path,custom_objects={ 'contrastive_loss': loss(1) })
#model = keras.models.load_model('val0.967_newdata_dup', custom_objects={ 'contrastive_loss': loss(1) })


index = 0
a = x_train_1[index]
b = x_train_2[index]
while True:
    cv2.imshow("a",b)
    cv2.imshow("b",b)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
camera = np.expand_dims(b, axis=0)
memory = np.expand_dims(b, axis=0)

plt.figure()
plt.imshow(a)
plt.figure()
plt.imshow(b)

pair =[camera,memory]
with tf.device('/cpu:0'):
    print(model.predict(pair))
#CUDA_VISIBLE_DEVICES=-1

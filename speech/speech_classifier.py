# -*- coding: utf-8 -*-
"""
Created on Fri May 20 11:13:02 2022

@author: Kevin Fan
"""

import os
import pickle
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

def data_prep(input_str, tokenizer):
    sequence = tokenizer.texts_to_sequences([input_str])
    return pad_sequences(sequence,maxlen=50)



if __name__ == "__main__":
    #Data
    home=os.path.abspath(os.getcwd())
    data_path=home+'\data\data.xlsx'
    data=pd.read_excel(data_path)
    #tokenizer = Tokenizer(num_words=50000, oov_token="<OOV>")#unknown words will be replaced by oov_token
    tokenizer = Tokenizer(oov_token="<OOV>")#unknown words will be replaced by oov_token
    text=data['speech'].values.tolist()
    labels=data['label'].values.tolist()
    tokenizer.fit_on_texts(text)
    word_index = tokenizer.word_index
    sequences = tokenizer.texts_to_sequences(text)
    padded = pad_sequences(sequences,maxlen=50)
    X_train, X_test, y_train, y_test = train_test_split(padded,labels,test_size=0.3,random_state=15)
    X_train=np.array(X_train)
    X_test=np.array(X_test)
    y_train=np.array(y_train)
    y_train = tf.keras.utils.to_categorical(y_train, 3)
    y_test=np.array(y_test)
    y_test = tf.keras.utils.to_categorical(y_test, 3)

    # save tokenizer
    with open('tokenizer.pickle', 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

    class_weight = { 0: 2.0, 1: 1.0, 2: 0.2}
                    
    #Model building
    max_features=10000
    # Input for variable-length sequences of integers
    inputs = keras.Input(shape=(None,), dtype="int32")
    # Embed each integer in a 128-dimensional vector
    x = layers.Embedding(max_features, 64)(inputs)
    # Add 2 bidirectional LSTMs
    x = layers.Bidirectional(layers.LSTM(64, return_sequences=True))(x)
    x = layers.Bidirectional(layers.LSTM(32))(x)
    x = layers.Dropout(0.5)(x)
    # Add a classifier
    outputs = layers.Dense(3, activation="softmax")(x)

    model = keras.Model(inputs, outputs)
    model.summary()

    model.compile("adam", "CategoricalCrossentropy", metrics=["accuracy"])
    model.fit(X_train, y_train, class_weight=class_weight, batch_size=32, epochs=10, validation_data=(X_test, y_test))



    model.save('my_model_2')
    # model.save('my_model_2.h5')
    print("not conformational, conformational, neutral")
    a="I don't think that is the right one"
    test_str=data_prep(a, tokenizer)
    model.predict(test_str)




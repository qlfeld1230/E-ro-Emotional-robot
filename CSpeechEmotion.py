#based aria.py
import os

# from keras import regularizers
import keras
# from keras.callbacks import ModelCheckpoint
# from keras.layers import Conv1D, MaxPooling1D, AveragePooling1D, Dense, Embedding, Input, Flatten, Dropout, Activation, LSTM
from keras.models import Model, Sequential, model_from_json
# from keras.preprocessing import sequence

#os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
"""
import os
if os.name == 'nt':
    from keras_preprocessing.sequence import pad_sequences
else:
    from keras.preprocessing.sequence import pad_sequences
"""

# from keras.preprocessing.text import Tokenizer
# from keras.utils import to_categorical
import librosa
import librosa.display
# from matplotlib.pyplot import specgram
# from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import LabelEncoder

# import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# import tensorflow as tf


class CSpeechEmotion:
    def __init__(self):
        #opt = keras.optimizers.rmsprop(lr=0.00001, decay=1e-6)
        opt = keras.optimizers.RMSprop(lr=0.00001, decay=1e-6)  # for envy 
        #opt = keras.optimizers.RMSprop(learning_rate=0.00001, decay=1e-6)  # for victus


        self.lb = LabelEncoder()
        #y = ['positive','negative','positive','negative','positive','negative']
        self.y = ["female_angry",
        "female_calm",
        "female_fearful",
        "female_happy",
        "female_sad",
        "male_angry",
        "male_calm",
        "male_fearful",
        "male_happy",
        "male_sad"]
        """
        self.y = ["angry",
        "neutral",
        "scared",
        "happy",
        "sad",
        "angry",
        "neutral",
        "scared",
        "happy",
        "sad"]
        """


        self.lb.fit(self.y)

        json_file = open('model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.loaded_model = model_from_json(loaded_model_json)
        # load weights into new model
        self.loaded_model.load_weights("/home/pi/resource/saved_models/Emotion_Voice_Detection_Model.h5")
        print("Loaded model from disk")

    def getEmotion(self):
        for ix in range(1):
         
            #X, sample_rate = librosa.load('output2151.wav', res_type='kaiser_fast',duration=2.5,sr=22050*2,offset=0.5)
            X, sample_rate = librosa.load('/home/pi/output.wav', sr=22050*2)
            print(sample_rate, X.shape)
            sample_rate = np.array(sample_rate)
            print(sample_rate)
            mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=13),axis=0)
            featurelive = mfccs
            #featurelive
            #print("featurelive:", featurelive.shape)
            livedf2 = featurelive
            livedf2= pd.DataFrame(data=livedf2)
            livedf2 = livedf2.stack().to_frame().T
            print("livedf2:", livedf2.shape)
            twodim= np.expand_dims(livedf2, axis=2)
            twodim = np.resize(twodim, (1,216,1))
            print("twodim:", twodim.shape)
            livepreds = self.loaded_model.predict(twodim, batch_size=16, verbose=1) # reduce batch_size when exceeds 10% of system memory

            # 이값이 가장 큰게 결과임
            print("livepreds", livepreds) # livepreds [[1.1828284e-21 0.0000000e+00 5.9115671e-26 2.1881303e-36 5.3028497e-28 1.0000000e+00 1.3952966e-30 2.3253836e-27 2.6276625e-23 1.6358005e-11]]
            print(type(livepreds))
            print ("max:", np.max(livepreds))  # 최대값

            livepreds1=livepreds.argmax(axis=1)

            print("livepreds1", livepreds1) # livepreds1 [5]
            liveabc = livepreds1.astype(int).flatten()
            print("liveabc", liveabc) # liveabc [5]
            livepredictions = (self.lb.inverse_transform((liveabc))) # livepredictions ['male_angry']
            print("livepredictions", livepredictions)

            preddf = pd.DataFrame({'predictedvalues': livepredictions})
            print("preddf[:10]", preddf[:10])

            print(preddf)

            return livepreds[0]
            
            
            
            
            
            
        """
        230306_121415 envy anaconda tflite install

        conda create -n tflite_emot python=3.7 # Python 3.7.16 installed
        conda activate tflite_emot
        python -m pip install tflite-runtime
        pip install keras




        """

if __name__ == "__main__":
    obj = CSpeechEmotion()
    obj.getEmotion()
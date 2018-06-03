import sys, skvideo.io, json, base64
import numpy as np
from PIL import Image
from io import BytesIO, StringIO
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
import os
import sys
import pickle
from keras.optimizers import SGD, Adam, Nadam
from keras.callbacks import *
from keras.objectives import *
from keras.metrics import binary_accuracy
from keras.models import load_model
import keras.backend as K
#import keras.utils.visualize_util as vis_util

from models import *
from utils.loss_function import *
from utils.metrics import *
from utils.SegDataGenerator import *
import time
import sklearn
from sklearn.model_selection import train_test_split
import os

file = sys.argv[-1]

if file == 'run.py':
    print ("Error loading video")
    quit

road_th = float(sys.argv[1])
veh_th = float(sys.argv[2])


# Define encoder function
def encode(array):
    pil_img = Image.fromarray(array)
    buff = BytesIO()
    pil_img.save(buff, format="PNG")
    return base64.b64encode(buff.getvalue()).decode("utf-8")

video = skvideo.io.vread(file)

answer_key = {}

# Frame numbering starts at 1
frame = 1

model = zerg_model(batch_shape=[1, 320, 320, 3])
model.load_weights('terran_model.h5')

for rgb_frame in video:
    
    img = cv2.resize(rgb_frame, (320, 320), interpolation = cv2.INTER_CUBIC)
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    seg = model.predict(img.reshape(1,320,320,3))
    seg = seg.reshape(320,320,2)
    seg_road = (seg[:,:,0] > road_th).astype(np.uint8)
    seg_vehicle = (seg[:,:,1] > veh_th).astype(np.uint8)
    
    seg_road_fullsize = cv2.resize(seg_road, (800, 600), interpolation = cv2.INTER_NEAREST)
    seg_vehicle_fullsize = cv2.resize(seg_vehicle, (800, 600), interpolation = cv2.INTER_NEAREST)

    answer_key[frame] = [encode(seg_vehicle_fullsize), encode(seg_road_fullsize)]
    
    # Increment frame
    frame+=1

# Print output in proper json format
print (json.dumps(answer_key))
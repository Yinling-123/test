'''
Title           :make_predictions_gender.py
Description     :This script makes predictions using the trained model and generates a submission file.
Date Modified   :20170309
usage           :python make_predictions_gender.py
python_version  :2.7.11
'''

import sys
import os

caffe_python = '/home/yinling/Desktop/demogesture/demo/caffe/python/'
sys.path.insert(0, caffe_python)
import caffe
caffe.set_mode_gpu() 

import glob
import cv2
import numpy as np
from caffe.proto import caffe_pb2

#Size of images
IMAGE_WIDTH = 224
IMAGE_HEIGHT = 224

'''
Image processing helper function
'''
def transform_img(img, img_width=IMAGE_WIDTH, img_height=IMAGE_HEIGHT):

    #Image Resizing
    img = cv2.resize(img, (img_width, img_height), interpolation = cv2.INTER_CUBIC)

    return img


'''
Reading mean image, caffe model and its weights 
'''
#Read mean image
mean_blob = caffe_pb2.BlobProto()
with open('/home/yinling/ubuntu/morph_run/mean.binaryproto') as f:
    mean_blob.ParseFromString(f.read())
mean_array = np.asarray(mean_blob.data, dtype=np.float32).reshape(
    (mean_blob.channels, mean_blob.height, mean_blob.width))


#Read model architecture and trained model's weights
net = caffe.Net('/home/yinling/ubuntu/morph_run/gender_deploy.prototxt',
                '/home/yinling/ubuntu/morph_run/0309gender/gender_iter_5000.caffemodel',
                caffe.TEST)

#Define image transformers
transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
transformer.set_mean('data', mean_array.mean(1).mean(1))
transformer.set_transpose('data', (2,0,1))


'''
Making predicitions
'''
##Reading image paths
test_img_paths = [img_path for img_path in glob.glob("/home/yinling/ubuntu/agr_train/cacd_data1/train1/1/*jpg")]

test_ids = []
preds = []

#Making predictions
for img_path in test_img_paths:
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    img = transform_img(img, img_width=IMAGE_WIDTH, img_height=IMAGE_HEIGHT)
    
    net.blobs['data'].data[...] = transformer.preprocess('data', img)
    out = net.forward()
    pred_probas = out['prob']

    test_ids = test_ids + [img_path.split('/')[-1][:-4]]
    preds = preds + [pred_probas.argmax()]

    print img_path
    print pred_probas.argmax()
    print '-----------------'


'''
Making submission file
'''
with open("gender_pred0309_5000_1.csv","w") as f:
    f.write("id,label\n")
    for i in range(len(test_ids)):
        f.write(str(test_ids[i])+","+str(preds[i])+"\n")
f.close()

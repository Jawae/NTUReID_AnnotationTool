from __future__ import division
import time

import os
import torch 
import torch.nn as nn
from torch.autograd import Variable

import numpy as np
import cv2
import argparse

from yolov3 import DarknetTorch, nmsYOLO

def preprocess(orig_img, dim):
    orig_dim = orig_img.shape[1],orig_img.shape[0]
    #const AR resize with padding
    w, h = dim
    ow, oh = orig_dim
    ratio = min(w/ow,h/oh)
    wnew,hnew = int(ow*ratio),int(oh*ratio)
    img_resized = cv2.resize(orig_img,(wnew,hnew),interpolation=cv2.INTER_CUBIC)
    img = np.full((h,w,3),128)
    img[(h-hnew)//2:hnew+(h-hnew)//2,(w-wnew)//2:wnew+(w-wnew)//2,  :] = img_resized

    #make image RGB and transpose for pytorch BGR -> RGB | H W C -> C H W 
    img_ = img[:,:,::-1].transpose((2,0,1)).copy()
    img_ = torch.from_numpy(img_).float().div(255.).unsqueeze(0)
    return(img_,orig_img,orig_dim)

def mark_classes_saveinstances(x,orig_img,id_,i,save_path,class_names,padding,show_video):
    r = padding
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    label = class_names[int(x[-1])]
    if label=="person":
        if id_%3==0:
            cropped = orig_img[x[2].int()-r:x[4].int()+r,x[1].int()-r:x[3].int()+r]
            cv2.imwrite(os.path.join(save_path,str(id_)+'_'+str(i)+".jpg"),cropped)
        if show_video:
            cv2.rectangle(orig_img,tuple(x[1:3].int()),tuple(x[3:5].int()),(0,255,0))
            font_sz = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, 1 , 1)[0]  
            txtcorner = tuple(x[1:3].int())
            txtcorner = txtcorner[0]+font_sz[0]+2,txtcorner[1]+font_sz[1]+2,
            cv2.rectangle(orig_img,tuple(x[1:3].int()),txtcorner,(255,0,0))
            cv2.putText(orig_img,label,(x[1].int(),txtcorner[1]), cv2.FONT_HERSHEY_PLAIN,1,(255,255,255))


def person_image_extractor(video_file,save_path,show_video=False,skipFrame=90,padding=10):
    confthres = 0.65
    nmsthres = 0.4

    CUDA = torch.cuda.is_available()
    device = torch.device("cuda" if CUDA else "cpu")

    num_classes = 80
    fclasses = open("./yolov3/coco.names","r")
    class_names = fclasses.read().split("\n")[:-1]

    print("Loading network...")
    YOLO = DarknetTorch("./yolov3/yolov3.cfg")
    YOLO.loadWeights("./yolov3/yolov3.weights")
    print("Network load success!")

    # Change image resolution from default 320 here
    # Increased resolution means better accuracy.
    # Decreased resolution means faster evaluation.
    YOLO.netparams["height"] = str(416)
    dim = int(YOLO.netparams["height"])
    assert dim % 32 == 0 and dim > 32

    # if CUDA:
    #     print("Running on GPU.")
    # else: 
    #     print("No GPU found. Running on CPU")
    YOLO = YOLO.to(device)

    # Specify testing 
    YOLO.eval()

    cap = cv2.VideoCapture(video_file)
    assert cap.isOpened(), 'Cannot open source'

    currFrame=0
    start = time.time()
    while cap.isOpened():
        ret,frame = cap.read()
        if ret == True:
            if currFrame%skipFrame == 0:
                img,orig_img,orig_dim = preprocess(frame,(dim,dim))

                orig_dim = torch.FloatTensor(orig_dim).to(device)
                img = img.to(device)

                with torch.no_grad():
                    output = YOLO(Variable(img), CUDA)

                output = nmsYOLO(output, device, confthres, num_classes, nmsthres)	#####################

                if show_video:
                    if type(output) == int:
                        currFrame += 1
                        # print("FPS of the video is %f."%( currFrame / (time.time() - start)))
                        cv2.imshow("frame", orig_img)
                        key = cv2.waitKey(1)
                        if key & 0xFF == ord('q'):
                            break
                        continue
                else:
                    if type(output) == int:
                        key = cv2.waitKey(1)
                        if key & 0xFF == ord('q'):
                            break
                        currFrame += 1
                        continue


                # ratio = torch.min(dim/orig_dim)[0]	########## TORCH 0.5 WARNING

                # #scale output
                # output[:,[1,3]] = (output[:,[1,3]] - (dim - ratio*orig_dim[0])/2)/ratio
                # output[:,[2,4]] = (output[:,[1,3]] - (dim - ratio*orig_dim[1])/2)/ratio

                # for i in range(output.shape[0]):
                # 	output[i,[1,3]] = torch.clamp(output[i,[1,3]], 0.0, orig_dim[0])
                # 	output[i,[2,4]] = torch.clamp(output[i,[2,4]], 0.0, orig_dim[1])

                orig_dim = orig_dim.repeat(output.size(0), 1)
                scaling_factor = torch.min(dim/orig_dim,1)[0].view(-1,1)

                output[:,[1,3]] -= (dim - scaling_factor*orig_dim[:,0].view(-1,1))/2
                output[:,[2,4]] -= (dim - scaling_factor*orig_dim[:,1].view(-1,1))/2

                output[:,1:5] /= scaling_factor

                for i in range(output.shape[0]):
                    output[i, [1,3]] = torch.clamp(output[i, [1,3]], 0.0, orig_dim[i,0])
                    output[i, [2,4]] = torch.clamp(output[i, [2,4]], 0.0, orig_dim[i,1])


                list(map(lambda x,i: mark_classes_saveinstances(x,orig_img,currFrame,i,save_path,
                                                                class_names,padding,show_video),output,range(len(output))))
                
                if show_video:
                    cv2.imshow("frame", orig_img)
                    key = cv2.waitKey(1)
                    if key & 0xFF == ord('q'):
                        break
        else:
            break
        currFrame += 1
            # print("FPS of the video is %f."%( currFrame / (time.time() - start)))
    cap.release()
    cv2.destroyAllWindows()
    name = os.path.split(video_file)[-1].split('.')[0]
    print(name+'Extraction Completed')
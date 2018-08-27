import os
import zipfile
import shutil
import requests
from .gdrive_downloader import gdrive_downloader

dataset = {
    'yolov3': '1COpYUrl9QTRnrtShEy68_we39eTa6A_z'
}

def yolov3_downloader():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    weight_exist = os.path.join(dir_path,'yolov3.weights')
    print(weight_exist)
    if not os.path.isfile(weight_exist):
        id = dataset['yolov3']
        print("Downloading Yolo-V3 Weight")
        gdrive_downloader(weight_exist, id)
        print("Download Completed")    
    else:
        print("Yolo-V3 Weight Check Success!")
        
    
    

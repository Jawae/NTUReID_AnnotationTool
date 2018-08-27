from tkinter import *
from tkinter import filedialog
import os
import csv
import matplotlib
from tqdm import tqdm
matplotlib.use('TkAgg')
from datetime import datetime
from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from person_image_extractor import person_image_extractor
from tkinter.ttk import Separator, Style
from shutil import copyfile
from yolov3 import yolov3_downloader

def askdirectory(var):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirname = filedialog.askdirectory(initialdir=dir_path)
    if dirname:
        var.set(dirname)

def askfilename(var):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename = filedialog.askopenfilename(initialdir=dir_path)
    if filename:
        var.set(filename)

def VideoDirInput(status,name):
    optionFrame = Frame(window)
    optionLabel = Label(optionFrame, width=20)
    optionLabel["text"] = name
    optionLabel.pack(side=LEFT)
    text = status
    var1 = StringVar(window)
    var1.set(text)
    w = Entry(optionFrame, width = 40,textvariable= var1)
    w.pack(side = LEFT)
    dirBut = Button(optionFrame, text='Open', width = 6,command = lambda: askdirectory(var1))
    dirBut.pack(side = LEFT)
    
    optionFrame.pack()
    return w, var1

def SaveDirInput(status,name):
    optionFrame = Frame(window)
    optionLabel = Label(optionFrame, width=20)
    optionLabel["text"] = name
    optionLabel.pack(side=LEFT)
    text = status
    var2 = StringVar(window)
    var2.set(text)
    w = Entry(optionFrame, width = 40,textvariable= var2)
    w.pack(side = LEFT)
    dirBut = Button(optionFrame, text='Open', width = 6,command = lambda:askdirectory(var2))
    dirBut.pack(side = LEFT)
    optionFrame.pack()
    return w, var2

def TimeFileInput(status,name):
    optionFrame = Frame(window)
    optionLabel = Label(optionFrame, width=20)
    optionLabel["text"] = name
    optionLabel.pack(side=LEFT)
    text = status
    var3 = StringVar(window)
    var3.set(text)
    w = Entry(optionFrame, width = 40,textvariable= var3)
    w.pack(side = LEFT)
    fileBut = Button(optionFrame, text='Open', width = 6,command = lambda:askfilename(var3))
    fileBut.pack(side = LEFT)
    
    optionFrame.pack()
    return w, var3

def SearchDirInput(status,name):
    optionFrame = Frame(window)
    optionLabel = Label(optionFrame, width=20)
    optionLabel["text"] = name
    optionLabel.pack(side=LEFT)
    text = status
    var4 = StringVar(window)
    var4.set(text)
    w = Entry(optionFrame, width = 40,textvariable= var4)
    w.pack(side = LEFT)
    dirBut = Button(optionFrame, text='Open',width = 6, command = lambda: askdirectory(var4))
    dirBut.pack(side = LEFT)
    
    optionFrame.pack()
    return w, var4

def DateInput(status,name):
    optionFrame = Frame(window)
    optionLabel = Label(optionFrame, width=20)
    optionLabel["text"] = name
    optionLabel.pack(side=LEFT)
    text = status
    var5 = StringVar(window)
    var5.set(text)
    w = Entry(optionFrame, width = 10,textvariable= var5)
    w.pack(side = LEFT)
    
    optionFrame.pack()
    return w, var5

def PersonVideoInput(status,name):
    optionFrame = Frame(window)
    optionLabel = Label(optionFrame, width=20)
    optionLabel["text"] = name
    optionLabel.pack(side=LEFT)
    text = status
    var6 = StringVar(window)
    var6.set(text)
    w = Entry(optionFrame, width = 40,textvariable= var6)
    w.pack(side = LEFT)
    dirBut = Button(optionFrame, text='Open', width = 6,command = lambda: askdirectory(var6))
    dirBut.pack(side = LEFT)
    
    optionFrame.pack()
    return w, var6

def SaveImageInput(status,name):
    optionFrame = Frame(window)
    optionLabel = Label(optionFrame, width=20)
    optionLabel["text"] = name
    optionLabel.pack(side=LEFT)
    text = status
    var7 = StringVar(window)
    var7.set(text)
    w = Entry(optionFrame, width = 40,textvariable= var7)
    w.pack(side = LEFT)
    dirBut = Button(optionFrame, text='Open',width = 6, command = lambda: askdirectory(var7))
    dirBut.pack(side = LEFT)
    
    optionFrame.pack()
    return w, var7

def SkiFrameInput(status,name):
    optionFrame = Frame(window)
    optionLabel = Label(optionFrame, width=20)
    optionLabel["text"] = name
    optionLabel.pack(side=LEFT)
    text = status
    var8 = StringVar(window)
    var8.set(text)
    w = Entry(optionFrame, width = 10,textvariable= var8)
    w.pack(side = LEFT)
    
    optionFrame.pack()
    return w, var8

    
def video_merge(var):
    video_path = var.get()
    camera_name = os.path.split(video_path)[-1]
    date = os.path.split(os.path.split(os.path.split(video_path)[0])[0])[-1]
    video_list=[f for f in os.listdir(video_path) if not f.startswith('.')]
    if len(video_list) > 1:
        for video in video_list:
            label = video.split('.')[0].split('(')[-1].split(')')[0] 
            if not label.isdigit():
                index = '1'
                time = video[-13:-4]
            else:
                index = label
            globals()['video'+index]=VideoFileClip(os.path.join(video_path,video))
        video_order = []
        for i in range(len(video_list)):
            video_order.append(globals()['video'+str(i+1)])
        final_clip = concatenate_videoclips(video_order)
        final_clip.write_videofile(os.path.join(os.path.split(video_path)[0],date+'_'+time+'_'+camera_name+".mp4"))
    else:
        video = video_list[0]
        time = video[-13:-4]
        extention= video.split('.')[-1]
        src = os.path.join(video_path,video)
        dst = os.path.join(os.path.split(video_path)[0],date+'_'+time+'_'+camera_name+'.'+extention)
        copyfile(src,dst)
    print('Video Merge Complete')
    
def video_split(search_dir,save_dir,date,timefile):
    search_dir = search_dir.get()
    save_dir = save_dir.get()
    timefile = timefile.get()
    date = date.get()
    with open(timefile, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            name = row[0].lower()
            if not os.path.exists(os.path.join(save_dir,date,name)):
                os.makedirs(os.path.join(save_dir,date,name))
            apperance = row[1]
            record_list = row[2:-1]
            for record in record_list:
                if record[0] == ' ':
                    record = record[1:]
                camera_group = record.split(' ')[0]
                time = record.split(' ')[1]
                camera_path = os.path.join(search_dir,date,camera_group)
                if os.path.exists(camera_path):
                    print(camera_path)
                    video_list=[f for f in os.listdir(camera_path) if not f.startswith('.')]
                    video_list=[f for f in video_list if ('.' in f)]
                    if len(video_list) > 0:
                        time_point = datetime.strptime(time, '%H:%M.%S')
                        for video in video_list:
                            start_time = video.split('_')[1]
                            start_time = datetime.strptime(start_time, '%Hh%Mm%Ss')
                            delta = time_point - start_time
                            delta = delta.seconds
                            camera = video.split('.')[0].split('_')[-1]
                            extention = video.split('.')[-1]
                            ffmpeg_extract_subclip(os.path.join(camera_path,video), t1=delta-30, t2=delta+30,targetname=os.path.join(save_dir,date,name,name+'_'+date+'_'+camera+'.'+extention))
    print('Video Split Complete')

def image_extraction(input_folder,save_path,skipFrame):
    yolov3_downloader()
    input_folder = input_folder.get() 
    save_path = save_path.get()
    skipFrame = int(skipFrame.get())
    show_video=False
    person_dir=[d for d in os.listdir(input_folder) if os.path.isdir(input_folder)]
    person_dir=[d for d in os.listdir(input_folder) if not d.startswith('.')]
    
    for person_name in tqdm(person_dir):
        video_list = [f for f in os.listdir(os.path.join(input_folder,person_name)) if not f.startswith('.')]
        for video in video_list:
            video_file = os.path.join(input_folder,person_name,video)
            save_video = os.path.join(save_path,person_name,video.split('.')[0])
            person_image_extractor(video_file=video_file,save_path=save_video,skipFrame=skipFrame,show_video=show_video)
    print('Image Extraction Complete')
    
if __name__ == '__main__':
    window = Tk()
    window.title('NTU-ReID Video Tool')
    window.geometry('700x400')
    
    TitleLabel = Label(window, text='NTU-ReID Video Tool')
    TitleLabel.config(font=("Courier", 22))
    TitleLabel.pack()
    
    w1, var1 = VideoDirInput("", "Video Folder")
    mergeBut = Button(window, text='Merge', command = lambda: video_merge(var1))
    mergeBut.pack()
    
    l1 = Canvas(window, width=700, height=10)
    l1.pack()
    l1.create_line(0, 6, 700, 6)
    
    w4, search_dir, = SearchDirInput("", "Search Folder")
    w3, save_dir = SaveDirInput("", "Save Folder")
    w2, timefile = TimeFileInput("", "Time CSV File")
    w5, date = DateInput("07-17-1", "Date")
    timeBut = Button(window, text='Split', command = lambda: video_split(search_dir,save_dir,date,timefile))
    timeBut.pack()
    
    l2 = Canvas(window, width=700, height=10)
    l2.pack()
    l2.create_line(0, 6, 700, 6)

    w6, input_folder = PersonVideoInput("", "Extracted Video Folder")
    w7, save_path = SaveImageInput("", "Image Save Folder")
    w8, skipFrame = DateInput("90", "Skip Frame")
    extractBut = Button(window, text='Image Extraction', command = lambda: image_extraction(input_folder,save_path,skipFrame))
    extractBut.pack()
    
    window.mainloop()
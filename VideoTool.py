from tkinter import *
from tkinter import filedialog
import os
import csv
import matplotlib
from tqdm import tqdm
matplotlib.use('TkAgg')
from datetime import datetime, timedelta
from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from person_image_extractor import person_image_extractor
from tkinter.ttk import Separator, Style
from shutil import copyfile
from yolov3 import yolov3_downloader
import shutil
from shutil import copyfile

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

def video_split(search_dir,save_dir):
    search_dir = search_dir.get()
    save_dir = save_dir.get()
    timefile = os.path.join(search_dir,'data.csv')
    copyfile(timefile, os.path.join(save_dir,os.path.basename(timefile)))
    with open(timefile, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            id = row[0]
            name = row[1].lower()
            name = id+'-'+name
            if not os.path.exists(os.path.join(save_dir,name)):
                os.makedirs(os.path.join(save_dir,name))
            apperance = row[2]
            record_list = row[3:-1]
            for record in record_list:
                if record[0] == ' ':
                    record = record[1:]
                camera_group = record.split(' ')[0]
                time_list = record.split(' ')[1:]
                if len(time_list)>2:
                    time_list = [time_list[0],time_list[-2]]
                else:
                    time_list = time_list[0:1]
                camera_path = os.path.join(search_dir,camera_group)
                for time in time_list:
                    if os.path.exists(camera_path):
                        video_dir_list=[f for f in os.listdir(camera_path) if not f.startswith('.')]
                        for video_dir in video_dir_list:
                            temp_dir = os.path.join(camera_path,video_dir)
                            video_list=[f for f in os.listdir(temp_dir) if not f.startswith('.')]
                            video_list=[f for f in video_list if ('.' in f)]
                            video_list.sort()
                            time_point = datetime.strptime(time, '%H:%M.%S')
                            time_list = []
                            if len(video_list) > 0:
                                # print(video_list)
                                for video in video_list:
                                    start_time = video.split('.')[0].split('_')[2].split('-')[0]
                                    time_list.append(start_time)
                                    end_time = video.split('.')[0].split('_')[2].split('-')[1]
                                    time_list.append(end_time)

                                for i in range(len(video_list)):
                                    video = video_list[i]
                                    start_time = time_list[i*2]
                                    start_time = datetime.strptime(start_time, '%Hh%Mm%Ss')

                                    end_time = time_list[i*2+1]
                                    end_time = datetime.strptime(end_time, '%Hh%Mm%Ss')

                                    delta = 30

                                    d = timedelta(seconds=delta)

                                    clip_start = time_point - d
                                    clip_end = time_point + d

                                    start_checker = clip_start - start_time
                                    end_checker = end_time - clip_end
                                    third_checker = end_time - clip_start


                                    if start_checker.days == 0 and end_checker.days == 0:
                                        camera = video.split('.')[0].split('_')[0]
                                        extention = video.split('.')[-1]
                                        date = video.split('_')[1]
                                        ffmpeg_extract_subclip(os.path.join(temp_dir,video_list[i]), t1=start_checker.seconds, t2=start_checker.seconds+2*delta,targetname=os.path.join(save_dir,name,camera+'_'+date+'_'+str(time_point.hour)+'h'+str(time_point.minute)+'m'+str(time_point.second)+'s'+'_'+name+'.'+extention))
                                    else:
                                        end_checker2 = clip_end - start_time
                                        if start_checker.days == -1 and end_checker2.days == 0:
                                            if i == 0:
                                                camera = video.split('.')[0].split('_')[0]
                                                extention = video.split('.')[-1]
                                                date = video.split('_')[1]
                                                ffmpeg_extract_subclip(os.path.join(temp_dir,video_list[i]), t1=0, t2=end_checker2.seconds,targetname=os.path.join(save_dir,name,camera+'_'+date+'_'+str(time_point.hour)+'h'+str(time_point.minute)+'m'+str(time_point.second)+'s'+'_'+name+'.'+extention))
                                            else:
                                                camera = video.split('.')[0].split('_')[0]
                                                extention = video.split('.')[-1]
                                                date = video.split('_')[1]
                                                end_time2 = time_list[(i-1)*2+1]
                                                end_time2 = datetime.strptime(end_time2, '%Hh%Mm%Ss')
                                                start_checker3 = end_time2 - clip_start
                                                if start_checker3.days == -1:
                                                    ffmpeg_extract_subclip(os.path.join(temp_dir,video_list[i]), t1=0, t2=end_checker2.seconds,targetname=os.path.join(save_dir,name,camera+'_'+date+'_'+str(time_point.hour)+'h'+str(time_point.minute)+'m'+str(time_point.second)+'s'+'_'+name+'.'+extention))
                                        elif start_checker.days == 0 and end_checker.days == -1:
                                            if third_checker.days == 0:
                                                if i == (len(video_list)-1):
                                                    total_time = end_time - start_time
                                                    camera = video.split('.')[0].split('_')[0]
                                                    extention = video.split('.')[-1]
                                                    date = video.split('_')[1]
                                                    ffmpeg_extract_subclip(os.path.join(temp_dir,video_list[i]), t1=start_checker.seconds, t2=total_time.seconds,targetname=os.path.join(save_dir,name,camera+'_'+date+'_'+str(time_point.hour)+'h'+str(time_point.minute)+'m'+str(time_point.second)+'s'+'_'+name+'.'+extention))
                                                else:
                                                    start_time2 = time_list[(i+1)*2]
                                                    start_time2 = datetime.strptime(start_time2, '%Hh%Mm%Ss')
                                                    end_checker2 = clip_end - start_time2
                                                    if end_checker2.days == 0:
                                                        temp_save=os.path.join(save_dir,'temp')
                                                        if not os.path.isdir(temp_save):
                                                            os.makedirs(temp_save)

                                                        camera = video.split('.')[0].split('_')[0]
                                                        extention = video.split('.')[-1]
                                                        date = video.split('_')[1]

                                                        total_time = end_time - start_time
                                                        ffmpeg_extract_subclip(os.path.join(temp_dir,video_list[i]), t1=start_checker.seconds, t2=total_time.seconds,targetname=os.path.join(temp_save,'temp1.'+extention))
                                                        ffmpeg_extract_subclip(os.path.join(temp_dir,video_list[i+1]), t1=0, t2=end_checker2.seconds,targetname=os.path.join(temp_save,'temp2.'+extention))
                                                        v1 = VideoFileClip(os.path.join(temp_save,'temp1.'+extention))
                                                        v2 = VideoFileClip(os.path.join(temp_save,'temp2.'+extention))
                                                        final_clip = concatenate_videoclips([v1,v2])
                                                        print(os.path.join(save_dir,camera+'_'+date+'_'+time+'_'+name+'.'+extention))
                                                        final_clip.write_videofile(os.path.join(save_dir,name,camera+'_'+date+'_'+str(time_point.hour)+'h'+str(time_point.minute)+'m'+str(time_point.second)+'s'+'_'+name+'.mp4'))
                                                        shutil.rmtree(temp_save)
                                                    else:
                                                        total_time = end_time - start_time
                                                        camera = video.split('.')[0].split('_')[0]
                                                        extention = video.split('.')[-1]
                                                        date = video.split('_')[1]
                                                        ffmpeg_extract_subclip(os.path.join(temp_dir,video_list[i]), t1=start_checker.seconds, t2=total_time.seconds,targetname=os.path.join(save_dir,name,camera+'_'+date+'_'+str(time_point.hour)+'h'+str(time_point.minute)+'m'+str(time_point.second)+'s'+'_'+name+'.'+extention))
    

                                       
    print('Video Split Complete')

def image_extraction(input_folder,save_path,skipFrame):
    yolov3_downloader()
    input_folder = input_folder.get() 
    save_path = save_path.get()
    skipFrame = int(skipFrame.get())
    show_video=False
    person_dir=[d for d in os.listdir(input_folder) if (os.path.isdir(os.path.join(input_folder, d)) and (not d.startswith('.')))]
    print(person_dir)
    
    for person_name in tqdm(person_dir):
        video_list = [f for f in os.listdir(os.path.join(input_folder,person_name)) if not f.startswith('.')]
        for video in video_list:
            video_file = os.path.join(input_folder,person_name,video)
            save_video = os.path.join(save_path,person_name,video.split('.')[0])
            person_image_extractor(video_file=video_file,save_path=save_video,skipFrame=skipFrame,show_video=show_video)
    print('Image Extraction Complete')
    csv=[f for f in os.listdir(input_folder) if f.split('.')[-1].lower()=='csv'][0]
    copyfile(os.path.join(input_folder,csv), os.path.join(save_path,csv))
    
if __name__ == '__main__':
    window = Tk()
    window.title('NTU-ReID Video Tool')
    window.geometry('700x300')
    
    TitleLabel = Label(window, text='NTU-ReID Video Tool')
    TitleLabel.config(font=("Courier", 22))
    TitleLabel.pack()
    
    l1 = Canvas(window, width=700, height=10)
    l1.pack()
    l1.create_line(0, 6, 700, 6)
    
    w4, search_dir, = SearchDirInput("", "Search Folder")
    # w2, timefile = TimeFileInput("", "Time CSV File")
    w3, save_dir = SaveDirInput("", "Save Folder")
    # timefile = os.path.join(search_dir.get(),'data.csv')
    # print(timefile)
    timeBut = Button(window, text='Split', command = lambda: video_split(search_dir,save_dir))
    timeBut.pack()
    
    l2 = Canvas(window, width=700, height=10)
    l2.pack()
    l2.create_line(0, 6, 700, 6)

    w6, input_folder = PersonVideoInput("", "Extracted Video Folder")
    w7, save_path = SaveImageInput("", "Image Save Folder")
    w8, skipFrame = DateInput("30", "Skip Frame")
    extractBut = Button(window, text='Image Extraction', command = lambda: image_extraction(input_folder,save_path,skipFrame))
    extractBut.pack()
    
    window.mainloop()
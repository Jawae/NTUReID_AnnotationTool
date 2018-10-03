from tkinter import *   # from x import * is bad practice
from tkinter.ttk import *
import tkinter.filedialog
from tkinter import ttk
import os
from PIL import Image, ImageTk, ImageOps
from shutil import copyfile
import csv
import platform

OS = platform.system()

class Mousewheel_Support(object):    

    # implemetation of singleton pattern
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, root, horizontal_factor = 2, vertical_factor=2):
        
        self._active_area = None
        
        if isinstance(horizontal_factor, int):
            self.horizontal_factor = horizontal_factor
        else:
            raise Exception("Vertical factor must be an integer.")

        if isinstance(vertical_factor, int):
            self.vertical_factor = vertical_factor
        else:
            raise Exception("Horizontal factor must be an integer.")

        if OS == "Linux" :
            root.bind_all('<4>', self._on_mousewheel,  add='+')
            root.bind_all('<5>', self._on_mousewheel,  add='+')
        else:
            # Windows and MacOS
            root.bind_all("<MouseWheel>", self._on_mousewheel,  add='+')

    def _on_mousewheel(self,event):
        if self._active_area:
            self._active_area.onMouseWheel(event)

    def _mousewheel_bind(self, widget):
        self._active_area = widget

    def _mousewheel_unbind(self):
        self._active_area = None

    def add_support_to(self, widget=None, xscrollbar=None, yscrollbar=None, what="units", horizontal_factor=None, vertical_factor=None):
        if xscrollbar is None and yscrollbar is None:
            return

        if xscrollbar is not None:
            horizontal_factor = horizontal_factor or self.horizontal_factor

            xscrollbar.onMouseWheel = self._make_mouse_wheel_handler(widget,'x', self.horizontal_factor, what)
            xscrollbar.bind('<Enter>', lambda event, scrollbar=xscrollbar: self._mousewheel_bind(scrollbar) )
            xscrollbar.bind('<Leave>', lambda event: self._mousewheel_unbind())

        if yscrollbar is not None:
            vertical_factor = vertical_factor or self.vertical_factor

            yscrollbar.onMouseWheel = self._make_mouse_wheel_handler(widget,'y', self.vertical_factor, what)
            yscrollbar.bind('<Enter>', lambda event, scrollbar=yscrollbar: self._mousewheel_bind(scrollbar) )
            yscrollbar.bind('<Leave>', lambda event: self._mousewheel_unbind())

        main_scrollbar = yscrollbar if yscrollbar is not None else xscrollbar
        
        if widget is not None:
            if isinstance(widget, list) or isinstance(widget, tuple):
                list_of_widgets = widget
                for widget in list_of_widgets:
                    widget.bind('<Enter>',lambda event: self._mousewheel_bind(widget))
                    widget.bind('<Leave>', lambda event: self._mousewheel_unbind())

                    widget.onMouseWheel = main_scrollbar.onMouseWheel
            else:
                widget.bind('<Enter>',lambda event: self._mousewheel_bind(widget))
                widget.bind('<Leave>', lambda event: self._mousewheel_unbind())

                widget.onMouseWheel = main_scrollbar.onMouseWheel

    @staticmethod
    def _make_mouse_wheel_handler(widget, orient, factor = 1, what="units"):
        view_command = getattr(widget, orient+'view')
        
        if OS == 'Linux':
            def onMouseWheel(event):
                if event.num == 4:
                    view_command("scroll",(-1)*factor, what)
                elif event.num == 5:
                    view_command("scroll",factor, what) 
                
        elif OS == 'Windows':
            def onMouseWheel(event):        
                view_command("scroll",(-1)*int((event.delta/120)*factor), what) 
        
        elif OS == 'Darwin':
            def onMouseWheel(event):        
                view_command("scroll",event.delta, what)
        
        return onMouseWheel

class Scrolling_Area(Frame, object):

    def __init__(self, master, width=None, anchor=N, height=None, mousewheel_speed = 2, scroll_horizontally=True, xscrollbar=None, scroll_vertically=True, yscrollbar=None, background=None, inner_frame=Frame, **kw):
        Frame.__init__(self, master, class_="Scrolling_Area", background=background)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._width = width
        self._height = height

        self.canvas = Canvas(self, background=background, highlightthickness=0, width=width, height=height)
        self.canvas.grid(row=0, column=0, sticky=N+E+W+S)

        if scroll_vertically:
            if yscrollbar is not None:
                self.yscrollbar = yscrollbar
            else:
                self.yscrollbar = Scrollbar(self, orient=VERTICAL)
                self.yscrollbar.grid(row=0, column=1,sticky=N+S)
        
            self.canvas.configure(yscrollcommand=self.yscrollbar.set)
            self.yscrollbar['command']=self.canvas.yview
        else:
            self.yscrollbar = None

        if scroll_horizontally:
            if xscrollbar is not None:
                self.xscrollbar = xscrollbar
            else:
                self.xscrollbar = Scrollbar(self, orient=HORIZONTAL)
                self.xscrollbar.grid(row=1, column=0, sticky=E+W)
            
            self.canvas.configure(xscrollcommand=self.xscrollbar.set)
            self.xscrollbar['command']=self.canvas.xview
        else:
            self.xscrollbar = None

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        self.innerframe = inner_frame(self.canvas, **kw)
        self.innerframe.pack(anchor=anchor)
        
        self.canvas.create_window(0, 0, window=self.innerframe, anchor='nw', tags="inner_frame")

        self.canvas.bind('<Configure>', self._on_canvas_configure)

        Mousewheel_Support(self).add_support_to(self.canvas, xscrollbar=self.xscrollbar, yscrollbar=self.yscrollbar)

    @property
    def width(self):
        return self.canvas.winfo_width()

    @width.setter
    def width(self, width):
        self.canvas.configure(width= width)

    @property
    def height(self):
        return self.canvas.winfo_height()
        
    @height.setter
    def height(self, height):
        self.canvas.configure(height = height)
        
    def set_size(self, width, height):
        self.canvas.configure(width=width, height = height)

    def _on_canvas_configure(self, event):
        width = max(self.innerframe.winfo_reqwidth(), event.width)
        height = max(self.innerframe.winfo_reqheight(), event.height)

        self.canvas.configure(scrollregion="0 0 %s %s" % (width, height))
        self.canvas.itemconfigure("inner_frame", width=width, height=height)

    def update_viewport(self):
        self.update()

        window_width = self.innerframe.winfo_reqwidth()
        window_height = self.innerframe.winfo_reqheight()
        
        if self._width is None:
            canvas_width = window_width
        else:
            canvas_width = min(self._width, window_width)
            
        if self._height is None:
            canvas_height = window_height
        else:
            canvas_height = min(self._height, window_height)

        self.canvas.configure(scrollregion="0 0 %s %s" % (window_width, window_height), width=canvas_width, height=canvas_height)
        self.canvas.itemconfigure("inner_frame", width=window_width, height=window_height)
# --- functions ---
def all_children (window) :
    _list = window.winfo_children()
    for item in _list :
        if item.winfo_children() :
            _list.extend(item.winfo_children())
    return _list

def browse():
    image_size = int(ent3.get())
    widget_list = all_children(frame)
    for item in widget_list:
        item.pack_forget()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    scrolling_area = Scrolling_Area(frame)
    scrolling_area.pack(expand=1, fill=BOTH)
    filez = tkinter.filedialog.askdirectory(parent=window, title='Open Person Folder',initialdir=dir_path)
    ent1.insert(20, filez)
    
    csv_dir = os.path.abspath(os.path.join(filez, os.pardir))
    csv_path = os.path.join(csv_dir,[f for f in os.listdir(csv_dir) if f.split('.')[-1].lower()=='csv'][0])
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            name = row[0]+'-'+row[1].lower()
            if name == os.path.split(filez)[-1]:
                target_name = name
                u_color = row[2].split('_')[0]
                l_color = row[2].split('_')[1]
                u_type = row[2].split('_')[2]
                l_type = row[2].split('_')[3]
                gender = row[2].split('_')[4]
                accessory = row[2].split('_')[5]

                NameLabel.config(text='Name:'+target_name + '('+gender+')')
                ULabel.config(text='Upper :'+u_color +' '+u_type)
                LLabel.config(text='Lower :'+l_color+' '+l_type)
                AccessLabel.config(text='Accessory:'+accessory)

    cams = [d for d in os.listdir(filez) if not d.startswith('.')]

    # remove previous IntVars
    intvar_dict.clear()

    # remove previous Checkboxes
    for cb in checkbutton_list:
        cb.destroy()
        checkbutton_list.clear() 

    for cam in cams:
        rowFrame = Frame(scrolling_area.innerframe)
        rowFrame.pack(anchor="w")
        dirs = [d for d in os.listdir(os.path.join(filez,cam)) if not d.startswith('.')]
        tkinter.Label(rowFrame, text=cam.split('_')[-1]).pack(side=tkinter.LEFT)

        for filename in dirs:
            # create IntVar for filename and keep in dictionary
            path = os.path.join(filez,cam,filename)
            intvar_dict[path] = tkinter.IntVar()

            # create Checkbutton for filename and keep on listfile = "fb.png"

            try:
                image = Image.open(os.path.join(filez,cam,filename))
                width, _ = image.size
                if width <= 30:
                    pass
                else:
                    image.thumbnail((image_size,image_size))
                    photo = ImageTk.PhotoImage(image)
                    c = tkinter.Checkbutton(rowFrame, image=photo, variable=intvar_dict[path])
                    c.image = photo
                    c.pack(side=tkinter.LEFT)
                    # c.pack()
                    checkbutton_list.append(c)
            except:
                pass

def save_path():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filez = tkinter.filedialog.askdirectory(parent=window, title='Select Save Folder',initialdir=dir_path)
    ent2.insert(20, filez)

# def csv_path():
#     dir_path = os.path.dirname(os.path.realpath(__file__))
#     filez = tkinter.filedialog.askopenfilename(parent=window, title='Select CSV File',initialdir=dir_path)
#     ent0.insert(20, filez)

def test():
    for key, value in intvar_dict.items():
        if value.get() > 0:
            path = key.split('/')[-4:]
            dst = os.path.join(ent2.get(),*path)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            copyfile(key, dst)
    print('Done')
    widget_list = all_children(frame)
    for item in widget_list:
        item.pack_forget()
    dir_path = os.path.dirname(os.path.realpath(__file__))

# --- main ---

# to keep all IntVars for all filenames
intvar_dict = {}
 # to keep all Checkbuttons for all filenames
checkbutton_list = []

window = tkinter.Tk()
window.geometry('700x400')

TitleLabel = Label(window, text='NTU-ReID Annotation Tool')
TitleLabel.config(font=("Courier", 22))
TitleLabel.pack()

# ent0 = tkinter.Entry(window)
# ent0.pack()
# btn0 = tkinter.Button(window, text="Open CSV File", command=csv_path)
# btn0.pack()

frm = tkinter.Frame(window)
frm.pack()
frm_l = tkinter.Frame(frm)
frm_m = tkinter.Frame(frm)
frm_r = tkinter.Frame(frm)
frm_l.pack(side='left')
frm_m.pack(side='left')
frm_r.pack(side='right')

ent1 = tkinter.Entry(frm_l)
ent1.pack()
btn1 = tkinter.Button(frm_l, text="Open Person Path", command=browse)
btn1.pack()
tkinter.Label(frm_l,text='Image Size').pack()
ent3 = tkinter.Entry(frm_l,width = 3)
ent3.pack()
ent3.insert(20, '128')

NameLabel = Label(frm_m, text='Name: None')
NameLabel.pack()
ULabel = Label(frm_m, text='Upper : None')
ULabel.pack()
LLabel = Label(frm_m, text='Lower : None')
LLabel.pack()
AccessLabel = Label(frm_m, text='Accessory: None')
AccessLabel.pack()

ent2 = tkinter.Entry(frm_r)
ent2.pack()
btn2 = tkinter.Button(frm_r, text="Select Save Path", command=save_path)
btn2.pack()
btn3 = tkinter.Button(frm_r, text="Save", command=test)
btn3.pack()

l1 = Canvas(window, width=700, height=10)
l1.pack()
l1.create_line(0, 6, 700, 6)






frame = tkinter.Frame()
frame.pack(fill="both", expand=True)

window.mainloop() 
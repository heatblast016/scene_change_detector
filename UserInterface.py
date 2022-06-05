import tkinter as tk
from datetime import datetime
from tkinter import ttk
from tkinter import Grid
from PIL import Image
from PIL import ImageTk
import cv2 as cv
from UserParams import UserParams
from ttkthemes import ThemedTk
from ttkwidgets import TickScale


class UserInterface:

    def __init__(self, width, height, paramUpdate, cameraUpdate, parameters, drawBoxes, galleryDir, camera=0):

        self.root = ThemedTk(theme="equilux")
        self.videoStream = None
        self.closed = False
        # Tkinter initialization
        photo = tk.PhotoImage(file = "SceneChangeLogo_final.png")
        self.root.iconphoto(False, photo)
        self.width = width
        self.height = height
        self.drawBoxes = drawBoxes
        self.camera = camera
        style = ttk.Style()
        style.configure("BW.TLabel", foreground="black", background="white")
        self.root.wm_title("Scene Change Detection")

        tabControl = ttk.Notebook(self.root)
        # configure background, user parameters, and themes

        # Add tabs
        self.cameraTab = ttk.Frame(tabControl)
        tabControl.add(self.cameraTab, text="Camera", padding=20)

        self.galleryTab = ttk.Frame(tabControl)
        tabControl.add(self.galleryTab, text="Gallery", padding=20)

        tabControl.pack(expand=1, fill="both")



        motionLim, sens, camFPS, record, drawBoxes = parameters.getParams()
        # User Parameter Labels
        self.timingVar = tk.StringVar() 
        labelTiming = ttk.Label(self.cameraTab,textvariable = self.timingVar )
        labelTiming.grid_propagate(0)
        labelTiming.grid(row=1,column=3,padx=20) 
        self.senseVar = tk.StringVar()
        labelSense = ttk.Label(self.cameraTab,textvariable = self.senseVar ).grid(row=3, column=3,
                                                                                    padx=20)
        self.fpsVar = tk.StringVar()
        labelFPS = ttk.Label(self.cameraTab, textvariable = self.fpsVar).grid(row=5, column=3,
                                                                                    padx=10)
        # Set User Parameter Label Values
        self.timingVar.set("Time before and after recording: %.2f seconds" % motionLim)
        self.senseVar.set("Threshold for movement: %d percent" % sens)
        self.fpsVar.set("Camera FPS: %.2f frames per second" % camFPS)
        # User Parameter Sliders
        self.timingScale = ttk.Scale(self.cameraTab, from_=1, to=10, orient="horizontal")
        self.timingScale.grid(row=2, column=3, ipadx=30)
        self.timingScale.set(motionLim)
        self.sensScale = ttk.Scale(self.cameraTab, from_=1, to=100, orient="horizontal")
        self.sensScale.grid(row=4, column=3, ipadx=30)
        self.sensScale.set(sens)
        self.FPSScale = ttk.Scale(self.cameraTab, from_=1, to=120, orient="horizontal")
        self.FPSScale.grid(row=6, column=3, ipadx=30)
        self.FPSScale.set(camFPS)

        #Recording checkbox and draw contours checkbox
        self.recordChecked = tk.IntVar()
        self.buttonRecord = ttk.Checkbutton(self.cameraTab, text="Recording", variable=self.recordChecked)
        self.buttonRecord.grid(row=10, column=1, columnspan=1)

        self.boxChecked = tk.IntVar()
        self.buttonBox = ttk.Checkbutton(self.cameraTab, text="Draw Contours", variable=self.boxChecked)
        self.buttonBox.grid(row=10, column=2, columnspan=1)

        def updateCamNegative():
            cameraUpdate(-1)
            self.recordChecked.set(0)
            paramUpdate(self.timingScale.get(), self.sensScale.get(), self.FPSScale.get(),
                        self.recordChecked.get(), self.boxChecked.get())

        def updateCamPositive():
            cameraUpdate(1)
            self.recordChecked.set(0)
            paramUpdate(self.timingScale.get(), self.sensScale.get(), self.FPSScale.get(),
                        self.recordChecked.get(), self.boxChecked.get())

        # Init camera
        buttonLeft = ttk.Button(self.cameraTab, text="<", command=updateCamNegative).grid(row=0, column=0)
        labelCam = ttk.Label(self.cameraTab, text="Camera").grid(row=0, column=1)
        buttonRight = ttk.Button(self.cameraTab, text=">", command=updateCamPositive).grid(row=0, column=2)

        if record:
            self.recordChecked.set(1)
        else:
            self.recordChecked.set(0)

        if drawBoxes:
            self.boxChecked.set(1)
        else:
            self.boxChecked.set(0)

        # internal function for serializing user preferences
        def updateParams():
            paramUpdate(self.timingScale.get(), self.sensScale.get(), self.FPSScale.get(),
                        self.recordChecked.get(), self.boxChecked.get())
            self.drawBoxes = self.boxChecked.get()

        applyButton = ttk.Button(self.cameraTab, text='Apply',
                                 command=updateParams).grid(row=7, column=3,
                                                            columnspan=2)

        # gallery stream
        self.showVidStream = None
        self.showVidObj = None

        self.accessedFile = tk.StringVar()
        self.accessedFile.set("None")
        self.accessedLabel = ttk.Label(self.galleryTab, textvariable=self.accessedFile).grid(row=1, column=1)

        # script for opening file into stream
        def openFile():
            openFileDir = tk.filedialog.askopenfilename(initialdir = galleryDir
                                                        + "/VideoRecordings", title="Select a File", filetypes=(("avi files", "*.avi"), ("all files", "*.*"))) #Change the different selection settings
            fileDir = openFileDir[len(galleryDir)+1:]  # +1 to remove an additional slash at the beginning of the string
            self.accessedFile.set("Current file: " + fileDir)
            if not fileDir:
                self.showVidStream = None
                self.accessedFile.set("Current file: None")     
            else:
                self.showVidStream = cv.VideoCapture(openFileDir)
        
        self.galleryButton = ttk.Button(self.galleryTab, text='Search', command=openFile).grid(row=1, column=2, columnspan=2)

        self.root.wm_protocol("WM_DELETE_WINDOW", self.close)
        self.root.update()

    # play imported video frame by frame
    def videoUpdate(self):
        if self.showVidStream is None:
            return

        ret, frame = self.showVidStream.read()
        if frame is not None:
            image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image = ImageTk.PhotoImage(image)

            if self.showVidObj is None:
                # check if video has been initialized
                self.showVidObj = tk.Label(self.galleryTab, image=image)
                self.showVidObj.grid(row=2, column=0, columnspan=3, rowspan=9)        

            self.showVidObj.configure(image=image)
            self.showVidObj.image = image
        else:
            # case if video ends
            self.showVidStream.release()
            self.showVidObj.configure(image=None)

        self.root.update()
        self.root.update_idletasks()
        
    def streamUpdate(self, frame, cnts, isMotion):
        # Update Slider Values 
        if self.timingScale.get() < 10:
            self.timingVar.set("Time before and after recording: %.2f seconds" %
                           self.timingScale.get())
        else:
            self.timingVar.set("Time before and after recording: %.1f seconds" %
                           self.timingScale.get())
        self.senseVar.set("Threshold for movement: %d percent" % self.sensScale.get())
        self.fpsVar.set("Camera FPS: %.2f frames per second" % self.FPSScale.get())

        # Draw Contours
        if self.drawBoxes:
            for c in cnts:
                (x, y, w, h) = c
                cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if isMotion:
            cv.putText(frame, "Status: {}".format("Movement"), (10, 20),
                       cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        else:
            cv.putText(frame, "Status: {}".format("No Movement"), (10, 20),
                       cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # convert frame into readable image
        image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)

        if self.videoStream is None:
            self.videoStream = tk.Label(self.cameraTab, image=image)
            self.videoStream.grid(row=1, column=0, columnspan=3, rowspan=9)
            # otherwise, simply update the panel
        else:
            self.videoStream.configure(image=image)
            self.videoStream.image = image

        self.root.update()
        self.root.update_idletasks()
        # update roots

    def close(self):
        self.root.destroy()
        self.closed = True

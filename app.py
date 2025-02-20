# import picamzero as picam
import numpy as np
import cv2
import pypupilext as pp
from matplotlib import pyplot as plt
from matplotlib.backend_bases import MouseEvent
from pythonosc import udp_client
from constants import osc_ip, osc_port, debug, roi_size
import time

class Cursor:
    """
    A cross hair cursor. from https://matplotlib.org/stable/gallery/event_handling/cursor_demo.html#sphx-glr-gallery-event-handling-cursor-demo-py
    """
    def __init__(self, ax):
        self.ax = ax
        self.horizontal_line = ax.axhline(color='k', lw=0.8, ls='--')
        self.vertical_line = ax.axvline(color='k', lw=0.8, ls='--')
        # text location in axes coordinates
        self.text = ax.text(0.72, 0.9, '', transform=ax.transAxes)
        self.roi_center = None

    def set_cross_hair_visible(self, visible):
        need_redraw = self.horizontal_line.get_visible() != visible
        self.horizontal_line.set_visible(visible)
        self.vertical_line.set_visible(visible)
        self.text.set_visible(visible)
        return need_redraw

    def on_mouse_move(self, event):
        if not event.inaxes:
            need_redraw = self.set_cross_hair_visible(False)
            if need_redraw:
                self.ax.figure.canvas.draw()
        else:
            self.set_cross_hair_visible(True)
            x, y = event.xdata, event.ydata
            # update the line positions
            self.horizontal_line.set_ydata([y])
            self.vertical_line.set_xdata([x])
            self.text.set_text(f'x={x:1.2f}, y={y:1.2f}')
            self.ax.figure.canvas.draw()
    
    def on_mouse_click(self, event):
        x, y  = event.xdata, event.ydata
        self.roi_center = [x, y]

class PupilTracker:
    def __init__(self, osc_ip, osc_port):
        global debug
        self.debug = debug
        self.model = pp.PuReST()
        if self.debug:
            self.models = [pp.ElSe(), pp.ExCuSe(), pp.PuRe, pp.PuReST(), pp.Starburst(), pp.Swirski2D()]
        #TODO CHANGE FOR PI
        self.cam = cv2.VideoCapture(0)
        # self.cam = picam.Camera()
        self.ROI = [0, 0, -1, -1] #x, y, w, h
        self.roi_center = None
        self.pupilID = 1
        self.history = []
        self.graph = None
        self.oscClient = udp_client.SimpleUDPClient(osc_ip, osc_port)
        print(f"Initialised OSC client to {osc_ip}:{osc_port}")
    
    def send_pupil(self, x, y, d):
        id = self.pupilID
        self.oscClient.send_message(f"/cue/eye{id}D/name", d)
        self.oscClient.send_message(f"/cue/eye{id}X/name", x)
        self.oscClient.send_message(f"/cue/eye{id}Y/name", y)
        print(f"sent d{d}x{x}y{y}")
        
    def init_graph(self, cv2Image, title):
        plt.ion()
        self.graph = plt.imshow(cv2Image)
        self.cursor = Cursor(self.graph.axes)
        self.graph.figure.canvas.mpl_connect('motion_notify_event', self.cursor.on_mouse_move)
        self.graph.figure.canvas.mpl_connect('button_press_event', self.cursor.on_mouse_click)
        plt.title(f"Confidence: {title}")
        plt.pause(0.25)

    def update_graph(self, cv2Image, title):
        self.graph.remove()
        self.graph = plt.imshow(cv2Image)
        plt.title(f"Confidence: {title}")
        plt.pause(0.25)

    def draw_pupil_and_show(self, cv2Image, pupil):
        x, y = pupil.center
        x = int(x)
        y  = int(y)
        dMaj = int(pupil.majorAxis())
        dMin = int(pupil.minorAxis())
        angle = pupil.angle
        colourImg = cv2.cvtColor(cv2Image, cv2.COLOR_GRAY2RGB)
        cv2.ellipse(colourImg, (x, y), (dMin//2, dMaj//2), angle, 0, 360, (0, 0, 255), 1)
        if self.graph == None:
            self.init_graph(colourImg, pupil.confidence)
        else:
            self.update_graph(colourImg, pupil.confidence)
    
    def collect_image(self):
        if self.debug:
            if self.cam.isOpened():
                rval, img = self.cam.read()
            else:
                print("something went wrong with the image")
        else:
            img = self.cam.capture()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        x, y, w, h = self.ROI
        return img[x:x+w, y:y+h]
        
    def track_pupil(self, cv2Image):
        #use model
        pupil = self.model.run(cv2Image)

        x, y = pupil.center
        d = pupil.majorAxis()
        x = int(x)
        y = int(y)
        d = int(d)
        #Normalise
        return x, y, d
        #detect outliers
        pass
        return None
    
    def run_verbose(self):
        first_run = True
        while(True):
            t0 = time.time()
            img = self.collect_image()
            t1 = time.time()
            print(f"image collected in {t1  - t0} seconds")
            plt.imshow(img)
            plt.show()
            pupil = self.track_pupil(img)
            t2 = time.time()
            print(f"pupil identified in {t2 - t1} seconds")
            if self.debug or first_run:
                self.draw_pupil_and_show(img, pupil)
                t3  = time.time()
                print(f"pupil drawn in {t3 - t2} seconds")
            if pupil == None:
                print("Pupil invalid.")
                continue
            #set ROI
            if self.cursor.roi_center != None and self.roi_center != self.cursor.roi_center:
                global roi_size
                w, h = roi_size
                x = self.cursor.roi_center[0] - w//2
                y = self.cursor.roi_center[1] - h//2
                self.roi_center = self.cursor.roi_center
                self.ROI = [x, y, w, h]
            #send off
            self.send_pupil(pupil)
            t4 = time.time()
            print(f"pupil sent in {t3 - t4} seconds")
            print(f"TOTAL TIME: {t4 - t0} seconds")
        self.cam.release()
    
    def run(self):
        first_run = True
        while(True):
            img = self.collect_image()
            pupil = self.track_pupil(img)
            if self.debug or first_run:
                self.draw_pupil_and_show(img, pupil)
            if pupil == None:
                print("Pupil invalid.")
                continue
            #set ROI
            if self.cursor.roi_center != None and self.roi_center != self.cursor.roi_center:
                global roi_size
                w, h = roi_size
                x = self.cursor.roi_center[0] - w//2
                y = self.cursor.roi_center[1] - h//2
                self.roi_center = self.cursor.roi_center
                self.ROI = [x, y, w, h]
            self.send_pupil(pupil.x)

if __name__ == "__main__":
    tracker = PupilTracker(osc_ip, osc_port)
    tracker.run_verbose()
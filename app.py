import numpy as np
import cv2
from matplotlib import pyplot as plt
from matplotlib.backend_bases import MouseEvent
from pythonosc import udp_client
from appConstants import osc_ip, osc_port, verbose, ndi_stream_names, hyperparams
import time
from components.cameras.NDICam import NDICam
from components.OscClient import OscClient
from components.PupilTracker import PupilTracker
from components.PupilVisualiser import PupilVisualiser

class App:
    def __init__(self):
        global ndi_stream_names
        global osc_ip
        global osc_port
        global hyperparams
        self.cameras = []
        self.cam_rois = [None for i in range(len(ndi_stream_names))]
        self.networker = OscClient(osc_ip, osc_port)
        for name in ndi_stream_names:
            self.cameras.append(NDICam(name))
        self.tracker = PupilTracker()
        self.visualiser = PupilVisualiser(len(ndi_stream_names))
        self.verbose = verbose

    def start_threaded(self):
        #TODO THIS
        pass

    def first_run(self):
        #self.pupilHist = np.zeros(len(self.cameras), 1000, 3)
        # get images from all cameras
        for idx, cam in enumerate(self.cameras):
            img = cam.capture()
            while type(img) == type(None):
                img = cam.capture()
            # self.cam_rois[idx] = self.tracker.get_eye_roi(img) #bit buggy - only sometimes works. Need to test on irl data
            self.cam_rois[idx] = self.tracker.get_eye_roi(img)

    def run(self):
        # self.first_run()
        global verbose
        while(True):
            ppls = []
            imgs = []
            for idx, cam in enumerate(self.cameras):
                img = cam.capture()
                if type(img) != type(None):
                    if self.cam_rois[idx] != None:
                        x, y, w, h = self.cam_rois[idx]
                        cropped = img[x:x+w, y:y+h]
                    else:
                        cropped = img
                    pupils = self.tracker.get_all_pupils(cropped)
                    confidences = [pupil.confidence for pupil in pupils]
                    if np.mean(confidences) == -100:
                        #we've probably lost the eye. re-find it.
                        self.cam_rois[idx] = self.tracker.get_eye_roi(img)
                        x, y, w, h = self.cam_rois[idx]
                        cropped = img[x:x+w, y:y+h]
                        pupils = self.tracker.get_all_pupils(cropped)
                    imgs.append(cropped)
                    ppls.append(pupils)
            if len(imgs) != 0:
                self.visualiser.draw_all_pupils_single(imgs[0], ppls[0])
                # self.visualiser.draw_all_pupils_multicam(imgs, ppls)

if __name__ == "__main__":
    app = App()
    app.run()
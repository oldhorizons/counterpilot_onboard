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
        # set all camera ROIs
        #basic set ROI
        if self.tracker.ROI == [0, 0, -1, -1]:
            self.tracker.ROI = self.tracker.get_roi(img)
            print(f"ROI: {self.tracker.ROI}")


    def run(self):
        #self.first_run()
        while(True):
            for idx, cam in enumerate(self.cameras):
                img = cam.capture()
                pupil = self.tracker.detect_pupil_agreement(img, None)
                if pupil != None:
                    x, y, d = self.tracker.normalise_pupil(pupil)
                    #send off
                    self.networker.send_pupil(idx, x, y, d)
            

if __name__ == "__main__":
    app = App()
    app.run()